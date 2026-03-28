import json
import os
import re
import time
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langdetect import detect
from lxml import etree, html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

import Scrapping.DOM_identifiers as DOM_identifiers
from Analytics.AI.utils import create_chain
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Scrapping.property_models import (
    KeyAttributes,
    Prices,
    ProcessingError,
    PropertyDetail,
    PriceUpdate,
    RentOfferInsert,
)
from Shared.Geolocation import get_coordinates
from Shared.LLM import LLM
from Shared.Vector_database.Vector_DB_interface import Vector_DB_interface

load_dotenv()

nehnutelnosti_base_url = os.getenv('nehnutelnosti_base_url')
auth_token_nehnutelnosti = os.getenv('auth_token_nehnutelnosti')


class Nehnutelnosti_sk_processor:

    _energy_extraction_system_prompt = (
        'Z nasledujúceho opisu nehnuteľnosti extrahuj cenu **čisto za energie**, ak je to možné. '
        'Pozor – uveď **iba cenu za energie**! Ak je v texte uvedené „cena nájmu <cena> vrátane energií", odpíš: None. '
        'Odpovedz IBA číslom. Ak nie je možné určiť konkrétnu sumu, odpíš: None.'
    )

    def __init__(
        self,
        base_url: str,
        auth_token: str,
        db_repository: Rent_offers_repository,
        llm: LLM,
        vector_db: Vector_DB_interface,
        chat_model: ChatOpenAI = None,
        source: str = 'Nehnutelnosti.sk',
        user_agent: str = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        ),
    ):
        self.auth_token = auth_token
        self.base_url = base_url
        self.user_agent = user_agent
        self.processed_offers: int = 0
        self.failed_offers: int = 0
        self.failed_pages: int = 0
        self.errors: list[ProcessingError] = []
        self.db_repository: Rent_offers_repository = db_repository
        self.llm = llm
        self.vdb = vector_db
        self.source = source
        self._energy_chain = create_chain(
            chat_model or ChatOpenAI(model_name='gpt-4o', temperature=0.0),
            self._energy_extraction_system_prompt,
            human_template='{input}',
        )

    def get_page(
        self,
        url: str,
    ) -> requests.Response:
        headers = {
            'User-Agent': self.user_agent,
            'Authorization': self.auth_token,
        }
        return requests.get(url, headers=headers)

    def get_details_links(
        self,
        soup: BeautifulSoup,
        keyword: str = 'detail',
    ) -> list:
        detail_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if keyword not in href:
                continue
            if href.startswith('http'):
                full_url = href
            else:
                parsed_url = urlparse(self.base_url)
                full_url = f'{parsed_url.scheme}://{parsed_url.netloc}{href}'
            if 'test' not in full_url.lower():
                detail_links.append(full_url)
        return list(set(detail_links))

    def process_detail(
        self,
        detail_link: str,
    ) -> PropertyDetail:
        resp = self.get_page(detail_link)
        if resp.status_code != 200:
            raise Exception(f'Failed to fetch page: {detail_link}, Status Code: {resp.status_code}')

        soup = BeautifulSoup(resp.text, 'html.parser')
        other_properties = self.get_other_properties(soup)
        location = self.get_location(soup)

        year_of_construction = int(other_properties['Rok výstavby:']) if 'Rok výstavby:' in other_properties else None
        approval_year = int(other_properties['Rok kolaudácie:']) if 'Rok kolaudácie:' in other_properties else None
        last_reconstruction_year = int(other_properties['Rok poslednej rekonštrukcie:']) if 'Rok poslednej rekonštrukcie:' in other_properties else None
        balconies = int(other_properties['Počet balkónov:']) if 'Počet balkónov:' in other_properties else None
        ownership = other_properties.get('Vlastníctvo:')
        floor = int(other_properties['Podlažie:']) if 'Podlažie:' in other_properties else None
        positioning = other_properties.get('Umiestnenie:')

        for key in ['Rok výstavby:', 'Rok kolaudácie:', 'Rok poslednej rekonštrukcie:',
                    'Počet balkónov:', 'Vlastníctvo:', 'Podlažie:', 'Umiestnenie:',
                    'Počet izieb / miestností:']:
            other_properties.pop(key, None)

        return PropertyDetail.model_validate({
            'title': self.get_title(soup),
            'location': location,
            'key_attributes': self.get_key_attributes(soup),
            'year_of_construction': year_of_construction,
            'approval_year': approval_year,
            'last_reconstruction_year': last_reconstruction_year,
            'balconies': balconies,
            'ownership': ownership,
            'other_properties': other_properties,
            'prices': self.get_price(soup),
            'floor': floor,
            'positioning': positioning,
            'description': self.get_description(soup),
            'preview_image': self.get_preview_image(detail_link),
            'coordinates': get_coordinates(location),
        })

    @staticmethod
    def get_title(
        soup: BeautifulSoup,
        element: str = 'h1',
        element_class: tuple = (
            'MuiTypography-root MuiTypography-h4 mui-1wj7mln',
            'MuiTypography-root MuiTypography-h4 mui-hrlyv4',
        ),
    ) -> Optional[str]:
        for cls in element_class:
            try:
                return soup.find(element, class_=cls).text.strip()
            except:
                continue
        return None

    @staticmethod
    def get_location(
        soup: BeautifulSoup,
        element: str = 'p',
        element_class: tuple = (
            'MuiTypography-root MuiTypography-body2 MuiTypography-noWrap mui-3vjwr4',
            'MuiTypography-root MuiTypography-body2 MuiTypography-noWrap mui-kri7tw',
        ),
    ) -> Optional[str]:
        for i in element_class:
            try:
                return soup.find(element, class_=element_class).text.strip()
            except:
                continue
        return None

    @staticmethod
    def get_key_attributes(
        soup: BeautifulSoup,
    ) -> KeyAttributes:
        icons = DOM_identifiers.nehnutelnosti_icons
        xpaths_1 = DOM_identifiers.nehnutelnosti_xpaths_1
        xpaths_2 = DOM_identifiers.nehnutelnosti_xpaths_2

        dom = etree.HTML(str(soup))
        container = soup.find('div', 'MuiBox-root mui-1e434qh')
        paragraphs = container.find_all('p') if container else []

        raw = {
            'house': False,
            'loft': False,
            'mezonet': False,
            'apartmen': False,
            'flat': False,
            'studio': False,
            'double_studio': False,
            'rooms': None,
            'size': None,
            'property_status': None,
        }

        for idx, para in enumerate(paragraphs):
            svg = para.find('svg')
            path_data = svg.find('path')['d']
            try:
                attribute = dom.xpath(xpaths_1[idx])[0].lower()
            except:
                attribute = dom.xpath(xpaths_2[idx])[0].lower()

            for icon_key, icon_value in icons.items():
                if icon_value != path_data:
                    continue
                if 'dom' in attribute:
                    raw['house'] = True
                elif 'byt' in attribute and 'iný byt' not in attribute:
                    raw['flat'] = True
                    try:
                        raw['rooms'] = int(icon_key[0])
                    except:
                        raw['rooms'] = None
                elif 'iný byt' in attribute:
                    raw['flat'] = True
                elif 'apartmán' in attribute:
                    raw['apartmen'] = True
                elif 'garsónka' in attribute:
                    raw['studio'] = True
                elif 'mezonet' in attribute:
                    raw['mezonet'] = True
                elif 'loft' in attribute:
                    raw['loft'] = True
                else:
                    if raw[icon_key] == False:
                        raw[icon_key] = True
                    else:
                        raw[icon_key] = attribute

        if raw['size']:
            try:
                raw['size'] = float(raw['size'].split()[0].replace(',', '.'))
            except:
                raw['size'] = raw['size'].split()[0]

        return KeyAttributes.model_validate(raw)

    @staticmethod
    def get_price(
        soup: BeautifulSoup,
        rent_element: str = 'p',
        rent_class: tuple = (
            'MuiTypography-root MuiTypography-h3 mui-fm8hb4',
            'MuiTypography-root MuiTypography-h3 mui-9867wo',
        ),
        meter_squared_element: str = 'p',
        meter_squared_class: str = 'MuiTypography-root MuiTypography-label2 mui-ifbhxp',
    ) -> Prices:
        raw: dict = {'rent': None, 'energies': None, 'meter_squared': None}

        price_rent = None
        for cls in rent_class:
            try:
                price_rent = soup.find(rent_element, cls).text.strip()
                break
            except:
                continue

        price_energies = None
        try:
            for p in soup.find_all('p', class_='MuiTypography-root MuiTypography-label2 mui-gsg6ma'):
                if '€' in p.text:
                    price_energies = p.text.strip()
                    break
        except:
            pass

        ms_tag = soup.find('p', 'MuiTypography-root MuiTypography-label2 mui-ifbhxp')
        price_ms = (
            soup.find(meter_squared_element, meter_squared_class).text.strip()
            if ms_tag and '€' in ms_tag.text.strip()
            else None
        )

        if price_rent:
            try:
                raw['rent'] = int(price_rent.replace('\xa0', '').split('€')[0].strip().replace(',', '.'))
            except:
                raw['rent'] = None

        if price_energies:
            try:
                raw['energies'] = int(
                    price_energies.replace('\xa0', '').split('€')[0].strip().replace('+ ', '').replace(',', '.')
                )
            except:
                raw['energies'] = None

        if price_ms:
            try:
                raw['meter_squared'] = float(price_ms.replace('\xa0', '').split('€')[0].strip().replace(',', '.'))
            except:
                raw['meter_squared'] = None

        return Prices.model_validate(raw)

    @staticmethod
    def get_other_properties(
        soup: BeautifulSoup,
        element: str = 'div',
        element_class: str = 'MuiGrid2-root MuiGrid2-container MuiGrid2-direction-xs-row MuiGrid2-spacing-xs-1 mui-lgq25d',
    ) -> dict:
        container = soup.find(element, element_class)
        paragraphs = container.find_all('p') if container else []
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        return dict(zip(paragraph_texts[::2], paragraph_texts[1::2]))

    @staticmethod
    def get_description(
        soup: BeautifulSoup,
        id: str = 'detail-description',
    ) -> Optional[str]:
        desc = soup.find(id=id)
        if desc:
            return desc.text.strip().replace('Čítať ďalej', '')
        print('Element not found')
        return None

    @staticmethod
    def get_images_url(
        detail_link: str,
    ) -> str:
        parts = detail_link.split('/detail/')
        return f'{parts[0]}/detail/galeria/foto/{parts[1]}'

    @staticmethod
    def get_preview_image(
        detail_link: str,
        wait_for_load_page: float = 2,
        wait_for_load_images: float = 0.5,
    ) -> Optional[str]:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        options.add_argument('--disable-logging')
        options.add_argument('--silent')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service(ChromeDriverManager().install(), log_output=os.devnull)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(Nehnutelnosti_sk_processor.get_images_url(detail_link))
        time.sleep(wait_for_load_page)

        for _ in range(5):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(wait_for_load_images)

        for img in driver.find_elements(By.TAG_NAME, 'img'):
            try:
                src = img.get_attribute('src') or img.get_attribute('data-src')
                if src and 'static' not in src and not src.endswith('.png'):
                    return src
            except:
                continue

        return None

    def process_offers_single_page(
        self,
        page_url: Optional[str] = None,
        current_page: int = 0,
        custom_links: Optional[list] = None,
        sleep: int = 3,
    ) -> None:
        if page_url:
            page = self.get_page(page_url)
            detail_links = self.get_details_links(BeautifulSoup(page.text, 'html.parser'))
        else:
            detail_links = custom_links

        for process_n, link in enumerate(detail_links, start=1):
            print(f'processing: {process_n}/{len(set(detail_links))} on page: {current_page} from: {self.source}')
            try:
                results = self.process_detail(link)
                price_energies = (
                    results.prices.energies
                    if results.prices.energies
                    else self.extract_energy_price(results.description, results.prices.rent)
                )

                if self.db_repository.record_exists(link):
                    item = self.db_repository.get_offer_by_id_or_url(link)
                    if item.price_rent != results.prices.rent or item.price_energies != price_energies:
                        self.db_repository.update_offer(
                            link,
                            {
                                'price_rent': results.prices.rent,
                                'price_energies': price_energies,
                            },
                        )
                        self.processed_offers += 1
                        continue

                if self.db_repository.find_duplicates(
                    price_rent=results.prices.rent,
                    price_energies=results.prices.energies,
                    size=results.key_attributes.size,
                    rooms=results.key_attributes.rooms,
                    ownership=results.ownership.lower() if results.ownership else None,
                    lat=results.coordinates[0] if results.coordinates else None,
                    lon=results.coordinates[1] if results.coordinates else None,
                    url=link,
                ):
                    print(f'Duplicate found for offer: {link}')
                    continue

                embedding = self.embedd_rent_offer(self.llm, results.title, results.description)
                results.source_url = link

                if results.title and 'mezonet' in results.title.lower():
                    property_type = 'mezonet'
                elif results.title and 'penthouse' in results.title.lower():
                    property_type = 'penthouse'
                else:
                    property_type = next(
                        key for key, val in results.key_attributes.model_dump().items()
                        if val == True
                    )

                print('writing rent offer to DB...')
                new_offer = self.db_repository.insert_rent_offer(
                    RentOfferInsert.model_validate({
                        'title': results.title,
                        'location': results.location,
                        'property_type': property_type.lower() if property_type else None,
                        'property_status': results.key_attributes.property_status.lower() if results.key_attributes.property_status else None,
                        'rooms': results.key_attributes.rooms,
                        'size': results.key_attributes.size,
                        'year_of_construction': results.year_of_construction,
                        'approval_year': results.approval_year,
                        'last_reconstruction_year': results.last_reconstruction_year,
                        'balconies': results.balconies,
                        'ownership': results.ownership.lower() if results.ownership else None,
                        'price_rent': results.prices.rent,
                        'price_ms': results.prices.meter_squared,
                        'price_energies': price_energies,
                        'price_total': results.prices.rent + price_energies if price_energies else results.prices.rent,
                        'description': results.description,
                        'other_properties': results.other_properties,
                        'floor': results.floor,
                        'positioning': results.positioning.lower() if results.positioning else None,
                        'source': self.source,
                        'source_url': results.source_url,
                        'latitude': results.coordinates[0] if results.coordinates else None,
                        'longtitude': results.coordinates[1] if results.coordinates else None,
                        'preview_image': results.preview_image,
                    })
                )

                keys_to_exclude = {
                    'created_at', '_sa_instance_state', 'title', 'location',
                    'description', 'other_properties', 'floor', 'positioning',
                    'source', 'score', 'preview_image',
                }
                filtered_offer = {k: v for k, v in new_offer.__dict__.items() if k not in keys_to_exclude}

                result = self.vdb.insert_data([{'embedding': embedding, 'metadata': filtered_offer}])
                if not result:
                    self.db_repository.delete_by_source_urls([results.source_url])
                    raise RuntimeError('Vector DB write failed after DB write.')

                self.processed_offers += 1
                print('detail processed successfully')
                time.sleep(sleep)

            except Exception as e:
                print(f'failed to process offer: {link} on page: {page_url}, error: {e}')
                self.failed_offers += 1
                self.errors.append(ProcessingError.model_validate({'link': link, 'error': str(e)}))

    def process_offers(
        self,
        start_page: int = 1,
        end_page: Optional[int] = None,
    ) -> None:
        last_page = self.last_page_number_check()
        current_page = start_page

        while True:
            if end_page and current_page > end_page:
                break
            if current_page > last_page:
                break

            url = f'{self.base_url}&page={current_page}'
            try:
                self.process_offers_single_page(page_url=url, current_page=current_page)
            except Exception as e:
                print(f'failed to process page: {url}, error: {e}')
                self.failed_pages += 1

            current_page += 1

        with open(f'errors_{self.source.replace(".sk", "")}.json', 'w', encoding='utf-8') as out_file:
            json.dump([e.model_dump() for e in self.errors], out_file, ensure_ascii=False, indent=4)

        print(
            f'failed to process pages: {self.failed_pages}'
            f'\nfailed to process offers: {self.failed_offers}'
            f'\nsuccessfully processed offers: {self.processed_offers}'
        )

    def last_page_number_check(
        self,
        element_id: str = "nav[aria-label='pagination navigation'] a",
    ) -> int:
        response = self.get_page(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        page_numbers = [
            int(button['href'].split('page=')[-1])
            for button in soup.select(element_id)
            if 'page=' in button['href']
        ]
        return max(page_numbers) if page_numbers else 1

    @staticmethod
    def embedd_rent_offer(
        llm: LLM,
        title: str,
        description: str,
        other_attributes: Optional[dict] = None,
    ) -> list:
        description_sk_only = Nehnutelnosti_sk_processor.remove_non_slovak_sections(description)

        if other_attributes:
            other_attributes_formatted = '\n'.join(
                f"{k.strip().replace('\xa0', '').rstrip(':')}: {v}"
                for k, v in other_attributes.items()
            )
            text_to_embedd = (
                f'NADPIS:\n{title}\n\n'
                f'ZÁKLADNÉ ÚDAJE:\n{other_attributes_formatted}\n\n'
                f'OPIS:\n{description_sk_only}'
            )
        else:
            text_to_embedd = f'NADPIS:\n{title}\n\nOPIS:\n{description_sk_only}'

        return llm.get_embedding(text_to_embedd, 'text-embedding-3-large')

    @staticmethod
    def remove_non_slovak_sections(
        text: str,
    ) -> str:
        slovak_sections = []
        for section in text.split('\n'):
            stripped = section.strip()
            if not stripped:
                continue
            try:
                if detect(stripped) == 'sk':
                    slovak_sections.append(stripped)
            except:
                continue
        return '\n'.join(slovak_sections)

    def extract_energy_price(
        self,
        description: Optional[str],
        price_rent: Optional[int],
    ) -> Optional[int]:
        if not description:
            return price_rent
        lt = description.lower().replace(' ', '')
        manually = self.extract_energy_price_by_pattern(lt)

        if manually is None:
            generated = self._energy_chain.invoke({'input': description}).content.strip()
            try:
                generated = int(re.sub(r'\D', '', generated))
                energies = None if generated >= price_rent else generated
            except:
                energies = None
        else:
            try:
                energies = int(manually.strip())
            except:
                energies = None

        return energies

    @staticmethod
    def extract_energy_price_by_pattern(
        lt: str,
    ) -> Optional[str]:
        patterns = [
            r'energie:(\d+)',                    # energie:100
            r'\+(\d+)energie',                   # +100energie
            r'\+(\d+)€energie',                  # +100€energie
            r'\+(\d+)eurenergie',                # +100eurenergie
            r'energievrátaneinternetuatv:(\d+)', # energievrátaneinternetuatv:300
            r'\+(\d+),-',                        # +100,-
            r'\+energie(\d+)',                   # +energie100
            r'cenanezahŕňaenergie(\d+)',         # cenanezahŕňaenergie250
        ]
        for pattern in patterns:
            match = re.search(pattern, lt)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def is_update_newer(
        url: str,
        reference_time: datetime,
        update_xpath: str = '/html/body/div[7]/div[2]/div/div[1]/div[2]/p/span[2]',
    ) -> bool:
        response = requests.get(url)
        tree = html.fromstring(response.content)
        element = tree.xpath(update_xpath)

        if not element:
            return False
        try:
            date_part = element[0].text_content().strip().split(':')[1].strip()
            scraped_date = datetime.strptime(date_part, '%d. %m. %Y')
            if reference_time.tzinfo:
                reference_time = reference_time.replace(tzinfo=None)
            return scraped_date > reference_time
        except (IndexError, ValueError):
            return False

    def delete_invalid_offers(
        self,
    ) -> None:
        invalid = 0
        deleted_from_db_not_from_vdb = []
        all_urls = self.db_repository.get_all_source_urls()

        for case_nr, url in enumerate(all_urls, start=1):
            print(f'processing {case_nr}/{len(all_urls)}, invalid URLs found: {invalid}')
            try:
                response = requests.get(url, allow_redirects=False, timeout=5)
                if response.status_code == 200:
                    pass
                elif response.status_code in [301, 302, 303, 307, 308]:
                    print(f"Redirected to: {response.headers.get('Location')}")
                    try:
                        self.db_repository.delete_by_source_urls([url])
                    except:
                        continue
                    try:
                        self.vdb.delete_element(source_url=url)
                    except:
                        deleted_from_db_not_from_vdb.append(url)
                    invalid += 1
                else:
                    print(f'Status code: {response.status_code}')
            except requests.RequestException as e:
                print(f'Error checking URL: {e}')

        print(f'deleted {invalid} offers')
        with open('deleted_from_db_not_from_vdb.json', 'w', encoding='utf-8') as out_file:
            json.dump(deleted_from_db_not_from_vdb, out_file, ensure_ascii=False, indent=4)