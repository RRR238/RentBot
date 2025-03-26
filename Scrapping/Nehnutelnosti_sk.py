import requests
from bs4 import BeautifulSoup
from lxml import etree
from DOM_identifiers import DOM_identifiers
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

load_dotenv()  # Loads environment variables from .env file

nehnutelnosti_base_url = os.getenv('nehnutelnosti_base_url')
auth_token = os.getenv('auth_token')


class Nehnutelnosti_sk_processor:

    def __init__(self,base_url,auth_token):
        self.auth_token = auth_token
        self.base_url = base_url
        self.processed_offers = []
        self.failed_offers = []
        self.failed_pages = []

    def get_page(self,url):
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Authorization": self.auth_token
        }

        response = requests.get(url,headers=headers)

        return response

    def get_details_links(self, soup):
        links = soup.find_all('a', href=True)
        detail_links = []
        for link in links:
            href = link['href']
            if 'detail' in href:  # Check if the 'href' contains 'detail'
                # If the URL is relative, prepend the domain
                if href.startswith('http'):
                    full_url = href  # It's already a full URL
                else:
                    parsed_url = urlparse(self.base_url)
                    full_url = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"  # Prepend the domain to relative URLs
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
            coordinates = get_coordinates(location)
            # print(f"title: {title} \nlocation: {location} \nkey attributes: {key_attributes} "
            #       f"\nother properties: {other_properties} \nprices: {prices} \ndescription: {description}")
            return {
                    "title":title,
                    "location":location,
                    "key_attributes":key_attributes,
                    "other_properties":other_properties,
                    "prices":prices,
                    "description":description,
                    "images":images,
                    "coordinates":coordinates
                    }
        else:
            raise Exception(f"Failed to fetch page: {detail_link}, "
                            f"Status Code: {resp.status_code}")

    def get_title(self,
                  soup,
                  element_class='MuiTypography-root MuiTypography-h4 mui-1wj7mln'):
        title = soup.find('h1',
                          class_ = element_class
                          ).text.strip()
        return title

    def get_location(self,
                     soup,
                     element_class='MuiTypography-root MuiTypography-body2 MuiTypography-noWrap mui-3vjwr4'):
        location = soup.find('p',
                             class_=element_class
                             ).text.strip()
        return location

    def get_key_attributes(self, soup):
        icons = DOM_identifiers.nehnutelnosti_icons

        xpaths = DOM_identifiers.nehnutelnosti_xpaths

        dom = etree.HTML(str(soup))

        container = soup.find('div', 'MuiBox-root mui-1e434qh')
        paragraphs = container.find_all("p") if container else []

        results = {"house":False,
                   "loft":False,
                   "mezonet":False,
                   "apartmen":False,
                   "rooms":None,
                   "size":None,
                   "property_status":None
                   }
        for i in range(len(paragraphs)):
            svg = paragraphs[i].find("svg")
            path_data = svg.find("path")['d']
            for j in icons.keys():
                if icons[j] == path_data:
                    if "dom" in dom.xpath(xpaths[i])[0].lower():
                        results["house"] = True
                    elif "byt" in dom.xpath(xpaths[i])[0].lower():
                        results["apartmen"] = True
                        results["rooms"] = j[0]
                    else:
                        results[j] = dom.xpath(xpaths[i])[0]

        if results['size']:
            results['size'] = results['size'].split()[0]

        return results

    def get_price(self,soup):
        prices ={"rent":None,
                 "energies":None,
                 "meter squared":None
                 }
        price_rent = soup.find('p',
                               "MuiTypography-root MuiTypography-h3 mui-fm8hb4"
                          ).text.strip()

        paragraphs = soup.find_all('p',
                                   class_="MuiTypography-root MuiTypography-label2 mui-gsg6ma")
        price_energies = None
        for p in paragraphs:
            if "€" in p.text:  # Look for the one containing a price
                price_energies = p.text.strip()
                break
        price_ms = soup.find('p', "MuiTypography-root MuiTypography-label2 mui-ifbhxp"
                                   ).text.strip() if "€" in soup.find('p',
                                "MuiTypography-root MuiTypography-label2 mui-ifbhxp"
                                   ).text.strip() else None

        if price_rent:
            prices["rent"] = (price_rent.replace("\xa0", "")
                              .split("€")[0]
                              .strip())
        if price_energies:
            prices["energies"] = (price_energies.replace("\xa0", ""
                                                        ).split("€")[0]
                                                        .strip()
                                                        .replace("+ ",""))
        if price_ms:
            prices["meter squared"] = (price_ms.replace("\xa0", "")
                                        .split("€")[0]
                                        .strip())
        return prices

    def get_other_properties(self, soup):

        container = soup.find('div',
            'MuiGrid2-root MuiGrid2-container MuiGrid2-direction-xs-row MuiGrid2-spacing-xs-1 mui-lgq25d')
        paragraphs = container.find_all("p") if container else []
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        data_dict = dict(zip(paragraph_texts[::2], paragraph_texts[1::2]))

        return data_dict

    def get_description(self, soup):
        desc = soup.find(id="description-wrapper")
        if desc:
            return desc.text.strip().replace("Čítať ďalej","")
        else:
            print("Element not found")
            return None

    def get_images(self,detail_link, wait_for_load_page=2, wait_for_load_images=0.5):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode (optional)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        parts = detail_link.split("/detail/")
        url = f"{parts[0]}/detail/galeria/foto/{parts[1]}"
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

    def process_offers_single_page(self, page_url, current_page, sleep=5):
        page = self.get_page(page_url)
        detail_links = self.get_details_links(BeautifulSoup(page.text,'html.parser'))
        process_n = 1
        offers = []
        for link in detail_links:
            print(f"processing{process_n}/{len(set(detail_links))} on page {current_page}")
            #check if the link is already in DB - if so, skip case
            if link in self.processed_offers:
                continue
            try:
                results = self.process_detail(link)
                results["source"] = link
                offers.append(results)
                self.processed_offers.append(link)
                time.sleep(sleep)
            except Exception as e:
                print(f"failed to process offer: {link} on page: {page_url}, error: {e}")
                self.failed_offers.append(link)

            process_n+=1
            #save results to DB
        return offers

    def process_offers(self,json_file,start_page=1, end_page=None):
        last_page = self.last_page_number_check()
        current_page = start_page

        all_offers = {}
        while True:
            if end_page:
                if current_page > end_page:
                    break
            if current_page > last_page:
                break

            url = f"{self.base_url}&page={current_page}"
            try:
                all_offers[current_page] = self.process_offers_single_page(url,current_page)
            except Exception as e:
                print(f"failed to process page: {url}, error: {e}")
                self.failed_pages.append(url)

            current_page += 1

        with open(json_file, 'w',encoding="utf-8") as json_file:
            json.dump(all_offers, json_file, ensure_ascii=False, indent=4)

        print(f"failed to process pages: {len(self.failed_pages)} "
              f"\nfailed to process offers: {len(self.failed_offers)}")

    def last_page_number_check(self):
        url = self.base_url
        response = self.get_page(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the currently active page (aria-current="true")
        pagination_buttons = soup.select("nav[aria-label='pagination navigation'] a")

        # Extract page numbers from the "Go to page X" buttons
        page_numbers = []
        for button in pagination_buttons:
            if "page=" in button["href"]:
                page_number = int(button["href"].split("page=")[-1])
                page_numbers.append(page_number)

        # Find the maximum page number
        last_page = max(page_numbers) if page_numbers else 1

        return last_page





processor = Nehnutelnosti_sk_processor(nehnutelnosti_base_url,
                                       auth_token)
#processor.pagination_check()
# page = processor.get_page(nehnutelnosti_base_url)
# links = processor.get_details_links(BeautifulSoup(page.text,'html.parser'))
# print(processor.process_detail(links[0]))
# print(len(links))
# print(links[149])
processor.process_offers('offers_nehnutelnosti_sk.json',1,1)