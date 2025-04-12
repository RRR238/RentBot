import requests
from bs4 import BeautifulSoup
from lxml import etree
import DOM_identifiers
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
import json
from Shared.Geolocation import get_coordinates
from Rent_offers_repository import Rent_offers_repository
from Shared.LLM import LLM
from Shared.Elasticsearch import Vector_DB

load_dotenv()  # Loads environment variables from .env file

nehnutelnosti_base_url = os.getenv('nehnutelnosti_base_url')
auth_token_nehnutelnosti = os.getenv('auth_token_nehnutelnosti')


class Nehnutelnosti_sk_processor:

    def __init__(self,
                 base_url,
                 auth_token,
                 db_repository:Rent_offers_repository,
                 llm:LLM,
                 vector_db:Vector_DB,
                 source = 'Nehnutelnosti.sk',
                 user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                 ):
        self.auth_token = auth_token
        self.base_url = base_url
        self.user_agent = user_agent
        self.processed_offers = 0
        self.failed_offers = 0
        self.failed_pages = 0
        self.estimated_duplicates = []
        self.db_repository:Rent_offers_repository = db_repository
        self.llm = llm
        self.vdb = vector_db
        self.source = source

    def get_page(self,url):
        headers = {
            "User-Agent":
            self.user_agent,
        "Authorization": self.auth_token
        }

        response = requests.get(url,headers=headers)

        return response

    def get_details_links(self, soup, keyword='detail'):
        links = soup.find_all('a', href=True)
        detail_links = []
        for link in links:
            href = link['href']
            if keyword in href:  # Check if the 'href' contains 'detail'
                # If the URL is relative, prepend the domain
                if href.startswith('http'):
                    full_url = href  # It's already a full URL
                else:
                    parsed_url = urlparse(self.base_url)
                    full_url = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"  # Prepend the domain to relative URLs
                if "test" not in full_url.lower():
                    detail_links.append(full_url)

        return list(set(detail_links))

    def process_detail(self, detail_link):
        resp = self.get_page(detail_link)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text,'html.parser')
            title = self.get_title(soup)
            location = self.get_location(soup)
            key_attributes = self.get_key_attributes(soup)
            other_properties = self.get_other_properties(soup)
            prices = self.get_price(soup)
            description = self.get_description(soup)
            images= self.get_images(detail_link)
            coordinates = [str(i) for i in get_coordinates(location)]
            year_of_construction = int(other_properties['Rok výstavby:']) if 'Rok výstavby:' in other_properties.keys() else None
            approval_year = int(other_properties['Rok kolaudácie:']) if 'Rok kolaudácie:' in other_properties.keys() else None
            last_reconstruction_year = int(other_properties['Rok poslednej rekonštrukcie:']) if 'Rok poslednej rekonštrukcie:' in other_properties.keys() else None
            balconies = int(other_properties['Počet balkónov:']) if 'Počet balkónov:' in other_properties.keys() else None
            ownership = other_properties['Vlastníctvo:'] if 'Vlastníctvo:' in other_properties.keys() else None
            floor = int(other_properties['Podlažie:']) if 'Podlažie:' in other_properties.keys() else None
            positioning = other_properties['Umiestnenie:'] if 'Umiestnenie:' in other_properties.keys() else None
            keys_to_remove = [
                                'Rok výstavby:',
                                'Rok kolaudácie:',
                                'Rok poslednej rekonštrukcie:',
                                'Počet balkónov:',
                                'Vlastníctvo:',
                                'Podlažie:',
                                'Umiestnenie:',
                                'Počet izieb / miestností:'
                            ]
            for key in keys_to_remove:
                if key in other_properties.keys():
                    del other_properties[key]

            # print(f"title: {title} \nlocation: {location} \nkey attributes: {key_attributes} "
            #       f"\nother properties: {other_properties} \nprices: {prices} \ndescription: {description}")
            return {
                    "title":title,
                    "location":location,
                    "key_attributes":key_attributes,
                    "year_of_construction":year_of_construction,
                    "approval_year":approval_year,
                    "last_reconstruction_year":last_reconstruction_year,
                    "balconies":balconies,
                    "ownership":ownership,
                    "other_properties":other_properties,
                    "prices":prices,
                    "floor":floor,
                    "positioning":positioning,
                    "description":description,
                    "images":images,
                    "coordinates":coordinates
                    }
        else:
            raise Exception(f"Failed to fetch page: {detail_link}, "
                            f"Status Code: {resp.status_code}")

    def get_title(self,
                  soup,
                  element = 'h1',
                  element_class='MuiTypography-root MuiTypography-h4 mui-1wj7mln'):
        title = soup.find(element,
                          class_ = element_class
                          ).text.strip()
        return title

    def get_location(self,
                     soup,
                     element='p',
                     element_class='MuiTypography-root MuiTypography-body2 MuiTypography-noWrap mui-3vjwr4'):
        location = soup.find(element,
                             class_=element_class
                             ).text.strip()
        return location

    def get_key_attributes(self, soup):
        icons = DOM_identifiers.nehnutelnosti_icons

        xpaths = DOM_identifiers.nehnutelnosti_xpaths

        dom = etree.HTML(str(soup))

        container = soup.find('div', 'MuiBox-root mui-1e434qh')
        paragraphs = container.find_all("p") if container else []

        results = {
                    "house":False,
                   "loft":False,
                   "mezonet":False,
                   "apartmen":False,
                   "flat":False,
                   "studio":False,
                   "double_studio": False,
                   "rooms":None,
                   "size":None,
                   "property_status":None
                   }
        for i in range(len(paragraphs)):
            svg = paragraphs[i].find("svg")
            path_data = svg.find("path")['d']
            attribute = dom.xpath(xpaths[i])[0].lower()
            for j in icons.keys():
                if icons[j] == path_data:
                    if "dom" in attribute:
                        results["house"] = True
                    elif "byt" in attribute:
                        results["flat"] = True
                        try:
                            results["rooms"] = int(j[0])
                        except:
                            results["rooms"] = j[0]
                    elif "apartmán" in attribute:
                        results["apartmen"] = True
                    elif "garsónka" in attribute:
                        results["studio"] = True
                    else:
                        if results[j]==False:
                            results[j] = True
                        else:
                            results[j] = attribute #dom.xpath(xpaths[i])[0]

        if results['size']:
            try:
                results['size'] = float(results['size'].split()[0].replace(
                                                                    ',','.'))
            except:
                results['size'] = results['size'].split()[0]

        return results

    def get_price(self,
                  soup,
                  rent_element='p',
                  rent_class="MuiTypography-root MuiTypography-h3 mui-fm8hb4",
                  meter_squared_element='p',
                  meter_squared_class="MuiTypography-root MuiTypography-label2 mui-ifbhxp"):

        prices ={"rent":None,
                 "energies":None,
                 "meter squared":None
                 }
        price_rent = soup.find(rent_element,
                               rent_class
                          ).text.strip(
                        )

        price_energies = None
        try:
            paragraphs = soup.find_all('p',
                                       class_="MuiTypography-root MuiTypography-label2 mui-gsg6ma")
            for p in paragraphs:
                if "€" in p.text:  # Look for the one containing a price
                    price_energies = p.text.strip()
                    break
        except:
            pass

        price_ms = soup.find(meter_squared_element,
                             meter_squared_class
                                   ).text.strip() if "€" in soup.find('p',
                                "MuiTypography-root MuiTypography-label2 mui-ifbhxp"
                                   ).text.strip() else None

        if price_rent:
            prices["rent"] = (price_rent.replace("\xa0", "")
                              .split("€")[0]
                              .strip().replace(
                                        ',','.'))
            try:
                prices["rent"] = int(prices["rent"])
            except:
                pass

        if price_energies:
            prices["energies"] = (price_energies.replace("\xa0", ""
                                                        ).split("€")[0]
                                                        .strip()
                                                        .replace(
                                                        "+ ","").replace(
                                                        ',','.'))
            try:
                prices["energies"] = int(prices["energies"])
            except:
                pass

        if price_ms:
            prices["meter squared"] = (price_ms.replace("\xa0", "")
                                        .split("€")[0]
                                        .strip().replace(',','.'))

            try:
                prices["meter squared"] = float(prices["meter squared"])
            except:
                pass

        return prices

    def get_other_properties(self,
                             soup,
                             element = 'div',
                             element_class = 'MuiGrid2-root MuiGrid2-container MuiGrid2-direction-xs-row MuiGrid2-spacing-xs-1 mui-lgq25d'):

        container = soup.find(element,element_class)
        paragraphs = container.find_all("p") if container else []
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        data_dict = dict(zip(paragraph_texts[::2], paragraph_texts[1::2]))

        return data_dict

    def get_description(self, soup, id="description-wrapper"):
        desc = soup.find(id=id)
        if desc:
            return desc.text.strip().replace("Čítať ďalej","")
        else:
            print("Element not found")
            return None

    def get_images_url(self,
                       detail_link):

        parts = detail_link.split("/detail/")
        url = f"{parts[0]}/detail/galeria/foto/{parts[1]}"

        return url

    def get_images(self,
                   detail_link,
                   wait_for_load_page=2,
                   wait_for_load_images=0.5):

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode (optional)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        url = self.get_images_url(detail_link)
        # Open the webpage
        driver.get(url)
        time.sleep(wait_for_load_page)  # Wait for page to load

        # Scroll down multiple times to load all lazy-loaded images
        for _ in range(5):  # Adjust scroll times if needed
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(wait_for_load_images)  # Give time for images to load

        # Find all images
        images = driver.find_elements(By.TAG_NAME, "img")
        image_urls = set()  # Use set to remove duplicates

        for img in images:
            src = img.get_attribute("src") or img.get_attribute("data-src")
            if src and "static" not in src:  # Filter out non-relevant images
                image_urls.add(src)

        images = []
        # Print the extracted image URLs
        for url in set(image_urls):
            if not url.endswith(".png"):
                images.append(url)

        driver.quit()

        return images

    def process_offers_single_page(self,
                                   page_url,
                                   current_page,
                                   sleep=3):

        page = self.get_page(page_url)
        detail_links = self.get_details_links(BeautifulSoup(page.text,'html.parser'))
        process_n = 1
        offers = []
        for link in detail_links:
            print(f"processing: {process_n}/{len(set(detail_links))} on page: {current_page} from: {self.source}")
            try:
                if self.db_repository.record_exists(link):
                    self.processed_offers += 1
                    process_n += 1
                    continue

                results = self.process_detail(link)

                if self.db_repository.duplicate_exists(results['prices']['rent'],
                                                       results['key_attributes']['size'],
                                                       ";".join(results['coordinates'])):

                    print(f"Duplicate found for offer: {link}")
                    process_n += 1
                    continue

                embedding = self.embedd_rent_offer(self.llm,
                                                   results['title'],
                                                   results['description'],
                                                   results['other_properties'])
                results["source_url"] = link
                offers.append(results)
                print(f"writing rent offer to DB...")
                new_offer = self.db_repository.insert_rent_offer({
                    "title": results['title'],
                    "location": results['location'],
                    "property_type": [key for key in results['key_attributes'].keys()
                                            if results['key_attributes'][key] == True][0],
                    "property_status": results['key_attributes']['property_status'],
                    "rooms": results['key_attributes']['rooms'],
                    "size": results['key_attributes']['size'],
                    "year_of_construction":results['year_of_construction'],
                    "approval_year": results['approval_year'],
                    "last_reconstruction_year": results['last_reconstruction_year'],
                    "balconies": results['balconies'],
                    "ownership": results['ownership'],
                    "price_rent": results['prices']['rent'],
                    "price_ms": results['prices']['meter squared'],
                    "price_energies":  results['prices']['energies'],
                    "description": results['description'],
                    "other_properties": results['other_properties'],
                    "floor":results['floor'],
                    "positioning": results['positioning'],
                    "source": self.source,
                    "source_url": results['source_url'],
                    "coordinates": ";".join(results['coordinates'])
                })
                print(f"writing images to DB...")
                # self.db_repository.insert_offer_images(new_offer.id,results['images'][:4]
                #                                         if len(results['images']) >= 4 else results['images'])
                keys_to_remove = {"created_at",
                                  '_sa_instance_state',
                                  "title",
                                  "location",
                                  "description",
                                  "other_properties",
                                  "floor",
                                  "positioning",
                                    "source",
                                  'score'}
                filtered_offer = {k: v for k, v in new_offer.__dict__.items() if k not in keys_to_remove}
                #print(filtered_offer)
                self.vdb.insert_data([{"embedding": embedding,
                                       "metadata": filtered_offer}])
                self.processed_offers += 1
                print(f"detail processed successfully")
                time.sleep(sleep)
            except Exception as e:
                print(f"failed to process offer: {link} on page: {page_url}, error: {e}")
                self.failed_offers += 1

            process_n+=1

        #return offers

    def process_offers(self,start_page=1,
                       end_page=None,
                       json_file=None):

        last_page = self.last_page_number_check()
        current_page = start_page

        #all_offers = {}
        while True:
            if end_page:
                if current_page > end_page:
                    break
            if current_page > last_page:
                break

            url = f"{self.base_url}&page={current_page}"
            try:
                #all_offers[current_page] = self.process_offers_single_page(url,current_page)
                self.process_offers_single_page(url, current_page)
            except Exception as e:
                print(f"failed to process page: {url}, error: {e}")
                self.failed_pages += 1

            current_page += 1

        # with open(json_file, 'w',encoding="utf-8") as json_file:
        #     json.dump(all_offers, json_file, ensure_ascii=False, indent=4)

        print(f"failed to process pages: {self.failed_pages} "
              f"\nfailed to process offers: {self.failed_offers} "
              f"\nsuccessfully processed offers: {self.processed_offers}")

    def last_page_number_check(self,
                               element_id = "nav[aria-label='pagination navigation'] a"):
        url = self.base_url
        response = self.get_page(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        #print(soup)

        # Find the currently active page (aria-current="true")
        pagination_buttons = soup.select(element_id)

        # Extract page numbers from the "Go to page X" buttons
        page_numbers = []
        for button in pagination_buttons:
            if "page=" in button["href"]:
                page_number = int(button["href"].split("page=")[-1])
                page_numbers.append(page_number)

        # Find the maximum page number
        last_page = max(page_numbers) if page_numbers else 1

        return last_page

    @staticmethod
    def embedd_rent_offer(llm:LLM,
                          title,
                          description,
                          other_attributes=None):
        if other_attributes:
            other_attributes_formatted = "\n".join(f"{k.strip().replace(
                                            '\xa0', '').rstrip(
                                                ':')}: {v}"
                                                   for k, v in other_attributes.items())
            text_to_embedd = (
                f"NADPIS:\n{title}\n\n"
                f"ZÁKLADNÉ ÚDAJE:\n{other_attributes_formatted}\n\n"
                f"OPIS:\n{description}"
            )
        else:
            text_to_embedd = (
                f"NADPIS:\n{title}\n\n"
                f"OPIS:\n{description}"
            )

        embedding = llm.get_embedding(text_to_embedd,'text-embedding-3-large')
        #print(text_to_embedd)

        return embedding


# processor = Nehnutelnosti_sk_processor(base_url= nehnutelnosti_base_url,
#                                        auth_token =auth_token_nehnutelnosti,
#                                        db_repository =Rent_offers_repository(os.getenv('connection_string')),
#                                         llm =LLM(),
#                                         vector_db = Vector_DB('rent-bot-index')
#                                         )
#processor.pagination_check()
# page = processor.get_page(nehnutelnosti_base_url)
# links = processor.get_details_links(BeautifulSoup(page.text,'html.parser'))
# print(links)
#print(processor.process_detail('https://www.nehnutelnosti.sk/detail/JuQ7dsNVC-w/arboria--krasny-2-izbovy-byt-s-priestrannou-terasou-na-prenajom-v-projekte-arboria-na-novomestskej-ulici'))
# print(len(links))
# print(links[149])
#processor.process_offers(1,3)




