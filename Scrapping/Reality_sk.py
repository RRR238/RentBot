import os
import re
import time
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Scrapping.Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Scrapping.property_models import KeyAttributes, Prices, PropertyDetail
from Shared.Geolocation import get_coordinates
from Shared.LLM import LLM
from Shared.Vector_database.Vector_DB_interface import Vector_DB_interface

reality_base_url = os.getenv('reality_base_url')
auth_token_reality = os.getenv('auth_token_reality')


class Reality_sk_processor(Nehnutelnosti_sk_processor):

    def __init__(
        self,
        base_url: str,
        auth_token: str,
        db_repository: Rent_offers_repository,
        llm: LLM,
        vector_db: Vector_DB_interface,
        chat_model: ChatOpenAI = None,
        source: str = 'Reality.sk',
        user_agent: str = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        ),
    ):
        super().__init__(
            base_url,
            auth_token,
            db_repository,
            llm,
            vector_db,
            chat_model,
            source,
            user_agent,
        )

    def get_details_links(
        self,
        soup: BeautifulSoup,
        keyword: str = 'byty',
    ) -> list:
        examples = super().get_details_links(soup, keyword)
        final = []
        for link in examples:
            parsed = urlparse(link)
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) >= 3 and path_parts[-1] not in ['predaj', 'prenajom', 'bratislava']:
                if 'test' not in link.lower():
                    final.append(link)
        return final

    def get_location(
        self,
        soup: BeautifulSoup,
        element: str = 'div',
        element_class: str = 'd-inline-block ml-2',
    ) -> Optional[str]:
        loc = super().get_location(soup, element=element, element_class=element_class)
        cleaned_lines = ' '.join([line.strip() for line in loc.splitlines() if line.strip()]).replace('•', '')
        return cleaned_lines.replace('Ukázať na mape', '')

    @staticmethod
    def get_price(
        soup: BeautifulSoup,
    ) -> Prices:
        try:
            price_rent = (
                soup.find('div', 'd-flex flex-wrap no-gutters justify-content-between align-items-center')
                .find('h3', class_='contact-title big col-12 col-md-6 mb-0')
                .text.strip()
                .split('€')[0]
            )
            price_rent = int(re.sub(r'\s+', '', price_rent))
        except:
            price_rent = None

        try:
            price_ms = (
                soup.find('div', 'd-flex flex-wrap no-gutters justify-content-between align-items-center')
                .find('h3', class_='contact-title big col-12 col-md-6 mb-0')
                .find_all('small')[0]
                .text.strip()
                .split('€')[0]
                .replace(',', '.')
            )
            price_ms = int(re.sub(r'\s+', '', price_ms))
        except:
            price_ms = None

        return Prices.model_validate({
            'rent': price_rent,
            'meter_squared': price_ms,
        })

    @staticmethod
    def get_key_attributes(
        soup: BeautifulSoup,
    ) -> KeyAttributes:
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

        info = {}
        labels = soup.find_all('div', class_='info-title')
        values = soup.find_all('div', class_='col-sm-8 col-6')

        for label, value in zip(labels, values):
            key = label.text.strip().replace(':', '')
            info[key] = value.text.strip()

        for j in info.keys():
            if j == 'Druh':
                if 'Garsónka' in info[j]:
                    raw['studio'] = True
                if 'Dvojgarsónka' in info[j]:
                    raw['double_studio'] = True
                elif 'byt' in info[j]:
                    raw['flat'] = True
                    try:
                        raw['rooms'] = int(info[j][0].replace(' ', ''))
                    except:
                        raw['rooms'] = info[j][0]
                elif 'Apartmán' in info[j]:
                    raw['apartmen'] = True
                elif 'dom' in info[j].lower():
                    raw['house'] = True
                elif 'Mezonet' in info[j]:
                    raw['mezonet'] = True
                else:
                    raw[j] = True
            elif j == 'Úžitková plocha':
                try:
                    raw['size'] = float(re.sub(r'\s+', '', info[j].replace('m²', '').replace(',', '.')))
                except:
                    raw['size'] = None

        return KeyAttributes.model_validate(raw)

    @staticmethod
    def get_description(
        soup: BeautifulSoup,
    ) -> Optional[str]:
        description_span = (
            soup.find('div', {'data-show-more-inner': ''})
            .find('span', class_='content-preview')
        )
        if description_span:
            return description_span.get_text(separator=' ').strip()
        return None

    @staticmethod
    def get_other_properties(
        soup: BeautifulSoup,
    ) -> dict:
        info = {}
        for label in soup.find_all('div', class_='info-title'):
            label_text = label.get_text(strip=True)
            value = label.find_next('div')
            if value:
                info[label_text] = value.get_text(strip=True)
        return info

    def get_images_url(
        self,
        detail_link: str,
    ) -> Optional[str]:
        detail_page = self.get_page(detail_link)
        soup = BeautifulSoup(detail_page.text, 'html.parser')
        labels = soup.find_all('div', class_='info-title')
        values = soup.find_all('div', class_='col-sm-8 col-6')

        property_type = None
        for label, value in zip(labels, values):
            if label.text.strip().replace(':', '') == 'Druh':
                property_type = (
                    value.text.strip()
                    .replace(' ', '-')
                    .replace('ý', 'y')
                    .replace('á', 'a')
                    .replace('ó', 'o')
                    .lower()
                )

        if property_type:
            parsed_url = urlparse(detail_link)
            path_segments = parsed_url.path.strip('/').split('/')
            path_segments[0] = property_type + '-foto'
            new_path = '/' + '/'.join(path_segments) + '/'
            return urlunparse(parsed_url._replace(path=new_path))

        return None

    def get_preview_image(
        self,
        detail_link: str,
        wait_for_load_page: float = 3,
        wait_for_load_images: float = 2,
    ) -> Optional[str]:
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument(self.user_agent)

        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
            'headers': {
                'User-Agent': self.user_agent,
                'Authorization': f'Bearer {self.auth_token}',
                'Referer': 'https://www.reality.sk/',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        })

        driver.get(self.get_images_url(detail_link))
        time.sleep(wait_for_load_page)

        try:
            wait = WebDriverWait(driver, wait_for_load_images)
            cookie_button = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//div[@class='message-component message-column']//button[contains(text(), 'Prijať všetko')]",
            )))
            cookie_button.click()
            print('✅ Cookies accepted.')
            time.sleep(2)
        except Exception as e:
            print('⚠️ Cookie button not found or error:', e)

        try:
            current_image = driver.find_element(By.CSS_SELECTOR, '.lg-item.lg-loaded.lg-complete.lg-current img')
            img_src = current_image.get_attribute('src')
            if img_src:
                driver.quit()
                return img_src
        except Exception as e:
            print(f'Error: {e}')
            return None

    def process_detail(
        self,
        detail_link: str,
    ) -> PropertyDetail:
        resp = self.get_page(detail_link)
        if resp.status_code != 200:
            raise Exception(f'Failed to fetch page: {detail_link}, Status Code: {resp.status_code}')

        soup = BeautifulSoup(resp.text, 'html.parser')
        other_properties = self.get_other_properties(soup)
        location = self.get_location(soup, element='div', element_class='d-inline-block ml-2')
        key_attributes = self.get_key_attributes(soup)
        prices = self.get_price(soup)

        year_of_construction = int(other_properties['Rok výstavby:']) if 'Rok výstavby:' in other_properties else None
        approval_year = int(other_properties['Rok kolaudácie:']) if 'Rok kolaudácie:' in other_properties else None
        last_reconstruction_year = int(other_properties['Rok poslednej rekonštrukcie:']) if 'Rok poslednej rekonštrukcie:' in other_properties else None
        balconies = int(other_properties['Počet balkónov:']) if 'Počet balkónov:' in other_properties else None
        ownership = other_properties.get('Vlastníctvo:')
        floor = int(other_properties['Podlažie:']) if 'Podlažie:' in other_properties else None
        positioning = other_properties.get('Umiestnenie:')

        if 'Energie:' in other_properties:
            try:
                energies = int(other_properties['Energie:'].replace(' €', '').replace(' ', ''))
            except:
                energies = other_properties['Energie:'].replace(' €', '')
            prices.energies = energies
        else:
            prices.energies = None

        key_attributes.property_status = other_properties.get('Stav nehnuteľnosti:')

        for key in ['Rok výstavby:', 'Rok kolaudácie:', 'Rok poslednej rekonštrukcie:',
                    'Počet balkónov:', 'Vlastníctvo:', 'Podlažie:', 'Umiestnenie:',
                    'Druh:', 'Typ:', 'Úžitková plocha:', 'Stav nehnuteľnosti:',
                    'Počet izieb / miestností:', 'Energie:']:
            other_properties.pop(key, None)

        return PropertyDetail.model_validate({
            'title': self.get_title(soup, element_class=('detail-title pt-4 pb-2',)),
            'location': location,
            'key_attributes': key_attributes,
            'year_of_construction': year_of_construction,
            'approval_year': approval_year,
            'last_reconstruction_year': last_reconstruction_year,
            'balconies': balconies,
            'ownership': ownership,
            'other_properties': other_properties,
            'prices': prices,
            'floor': floor,
            'positioning': positioning,
            'description': self.get_description(soup),
            'preview_image': self.get_preview_image(detail_link),
            'coordinates': get_coordinates(location),
        })

    def last_page_number_check(
        self,
        element_id: str = 'next-number active',
    ) -> int:
        url = self.base_url + '&page=400'
        response = self.get_page(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        page_numbers = [
            int(button['href'].split('page=')[-1])
            for button in soup.select('.next-number')
            if 'href' in button.attrs and 'page=' in button['href']
        ]

        active_page = soup.find('span', class_=element_id)
        if active_page:
            page_numbers.append(int(active_page.text))

        return max(page_numbers) if page_numbers else 1

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