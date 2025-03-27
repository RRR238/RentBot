from Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from urllib.parse import urlparse, urlunparse

load_dotenv()  # Loads environment variables from .env file

reality_base_url = os.getenv('reality_base_url')
auth_token_reality = os.getenv('auth_token_reality')

class Reality_sk_processor(Nehnutelnosti_sk_processor):

    def __init__(self,
                 base_url,
                 auth_token):
        super().__init__(base_url,
                         auth_token)

    def get_details_links(self, soup, keyword='byty'):
        examples = super().get_details_links(soup,keyword)
        final = []

        for link in examples:
            parsed = urlparse(link)

            path_parts = [p for p in parsed.path.split("/") if p]  # Remove empty parts from split
            if len(path_parts) >= 3 and not path_parts[-1] in ["predaj",
                                                               "prenajom",
                                                               "bratislava"]:
                if "test" not in link.lower():
                    final.append(link)

        return final

    def get_location(self,
                     soup,
                     element='div',
                     element_class='d-inline-block ml-2'):

        loc = super().get_location(BeautifulSoup(detail.text, 'html.parser'), element=element,
                                     element_class=element_class)
        cleaned_lines = " ".join([line.strip() for line in loc.splitlines() if line.strip()]
                                 ).replace("•","")

        return cleaned_lines

    def get_price(self, soup):

        price_rent = BeautifulSoup(detail.text,'html.parser'
                                   ).find('div',"d-flex flex-wrap no-gutters justify-content-between align-items-center"
                                    ).find('h3', class_='contact-title big col-12 col-md-6 mb-0').text.strip(
                                    ).split("€")[0]

        price_ms = BeautifulSoup(detail.text,'html.parser'
                                 ).find('div',"d-flex flex-wrap no-gutters justify-content-between align-items-center"
                                ).find('h3', class_='contact-title big col-12 col-md-6 mb-0'
                                ).find_all('small'
                                )[0].text.strip(
                                ).split("€")[0]

        return {
                "rent":price_rent,
                 "meter squared":price_ms
                 }

    def get_key_attributes(self, soup):
        results = {
            "house": False,
            "loft": False,
            "mezonet": False,
            "apartmen": False,
            "flat": False,
            "studio": False,
            "rooms": None,
            "size": None,
            "property_status": None
        }

        info = {}
        labels = soup.find_all("div", class_="info-title")
        values = soup.find_all("div", class_="col-sm-8 col-6")

        for label, value in zip(labels, values):
            key = label.text.strip().replace(":", "")  # Remove the colon from labels
            info[key] = value.text.strip()

        for j in info.keys():
            if j == 'Druh':
                if "Garsónka" in info[j]:
                    results["studio"] = True
                elif "byt" in info[j]:
                    results["flat"] = True
                    try:
                        results["rooms"] = int(info[j][0])
                    except:
                        results["rooms"] = info[j][0]
                elif "Apartmán" in info[j]:
                    results["apartmen"] = True
                elif "dom" in info[j]:
                    results["house"] = True
                else:
                    results[j] = True
            elif j == 'Úžitková plocha':
                try:
                    results["size"] = float(info[j].replace("m²",""))
                except:
                    results["size"] = info[j].replace("m²","")
            else:
                pass

        return results

    def get_description(self, soup):

        description_span = (soup.find("div", {"data-show-more-inner": ""})
                            .find("span", class_="content-preview"))

        if description_span:
            description = description_span.get_text(separator=" ").strip()
            return description
        else:
            return None

    def get_other_properties(self, soup):

        info = {}

        # Find all divs with class 'info-title' (labels for each field)
        labels = soup.find_all('div', class_='info-title')

        # Loop through each label and get the corresponding value
        for label in labels:
            label_text = label.get_text(strip=True)  # Get the label text
            value = label.find_next('div')  # Find the next div containing the value
            if value:
                value_text = value.get_text(strip=True)  # Get the value text
                info[label_text] = value_text  # Add the label-value pair to the dictionary

        # Print the extracted information
        return info

    def get_images_url(self,
                       detail_link):

        detail_page = self.get_page(detail_link)
        soup = BeautifulSoup(detail_page.text, 'html.parser')
        labels = soup.find_all("div", class_="info-title")
        values = soup.find_all("div", class_="col-sm-8 col-6")

        property_type = None
        for label, value in zip(labels, values):
            if label.text.strip().replace(":", "") == 'Druh':
                property_type = value.text.strip(
                                ).replace(" ", "-"
                                ).replace("ý","y"
                                ).replace("á","a"
                                ).lower()

        if property_type:
            parsed_url = urlparse(detail_link)
            path_segments = parsed_url.path.strip("/").split("/")
            path_segments[0] = property_type + "-foto"
            new_path = "/" + "/".join(path_segments) + "/"
            new_url = urlunparse(parsed_url._replace(path=new_path))
            return new_url

        return None




processor = Reality_sk_processor(reality_base_url,
                                 auth_token_reality)

page = processor.get_page(reality_base_url)
links = processor.get_details_links(BeautifulSoup(page.text,'html.parser'))
#print(links)
detail = processor.get_page(links[0])
#print(BeautifulSoup(detail.text,'html.parser'))
print(processor.get_title(BeautifulSoup(detail.text,'html.parser'),element_class="detail-title pt-4 pb-2"))
# print(processor.get_location(BeautifulSoup(detail.text,'html.parser'),element='div',element_class="d-inline-block ml-2"))
# print(processor.get_price(BeautifulSoup(detail.text,'html.parser')))
print(processor.get_key_attributes(BeautifulSoup(detail.text,'html.parser')))
#processor.get_description(BeautifulSoup(detail.text,'html.parser'))
#processor.get_other_properties(BeautifulSoup(detail.text,'html.parser'))
print(processor.get_images(links[0]))