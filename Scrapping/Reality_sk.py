from Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, urlunparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options
from Shared.Geolocation import get_coordinates
import re
from Rent_offers_repository import Rent_offers_repository

load_dotenv()  # Loads environment variables from .env file

reality_base_url = os.getenv('reality_base_url')
auth_token_reality = os.getenv('auth_token_reality')

class Reality_sk_processor(Nehnutelnosti_sk_processor):

    def __init__(self,
                 base_url,
                 auth_token,
                 db_repository: Rent_offers_repository,
                 source='Reality.sk',
                 user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"):
        super().__init__(base_url,
                         auth_token,
                         db_repository,
                         source,
                         user_agent)

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

        loc = super().get_location(soup, element=element,
                                     element_class=element_class)
        cleaned_lines = " ".join([line.strip() for line in loc.splitlines() if line.strip()]
                                 ).replace("•","")

        return cleaned_lines.replace('Ukázať na mape','')

    def get_price(self, soup):

        price_rent = soup.find('div',"d-flex flex-wrap no-gutters justify-content-between align-items-center"
                                    ).find('h3', class_='contact-title big col-12 col-md-6 mb-0').text.strip(
                                    ).split("€")[0]
        try:
            price_rent = int(re.sub(r'\s+', '', price_rent))
        except:
            pass

        price_ms = soup.find('div',"d-flex flex-wrap no-gutters justify-content-between align-items-center"
                                ).find('h3', class_='contact-title big col-12 col-md-6 mb-0'
                                ).find_all('small'
                                )[0].text.strip(
                                ).split("€")[0].replace(
                                ',','.'
                                )
        try:
            price_ms = int(re.sub(r'\s+', '', price_ms))
        except:
            pass

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
                        results["rooms"] = int(info[j][0].replace(" ",""))
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
                    results["size"] = float(re.sub(r'\s+',
                                            '', info[j].replace(
                                            "m²","").replace(
                                            ',','.')
                                                )
                                            )
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

    def get_images(self,
                   detail_link,
                   wait_for_load_page=3,
                   wait_for_load_images=2):

        chrome_options = Options()
        chrome_options.add_experimental_option(
                                        "excludeSwitches",
                                        ["enable-logging"]
                                        )
        chrome_options.add_argument(
            self.user_agent)

        # Start WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd("Network.enable", {})

        # Set headers
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {
                "User-Agent": self.user_agent,
                "Authorization": f"Bearer {self.auth_token}",  # Adds Authorization header
                "Referer": "https://www.reality.sk/",
                "Accept-Language": "en-US,en;q=0.9"
            }
        })

        images_url = self.get_images_url(detail_link)
        # Open the page first
        driver.get(images_url)

        time.sleep(wait_for_load_page)

        # Refresh the page to apply the cookie
        try:
            # Wait for the button to be clickable
            wait = WebDriverWait(driver, wait_for_load_images)  # Wait up to 10 seconds
            cookie_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//div[@class='message-component message-column']//button[contains(text(), 'Prijať všetko')]")))

            # Click the button
            cookie_button.click()
            print("✅ Cookies accepted.")
            time.sleep(2)
        except Exception as e:
            print("⚠️ Cookie button not found or error:", e)

        # Find all images to determine how many times to click
        images = driver.find_elements(By.CLASS_NAME, "lg-item")
        image_count = len(images)

        # Locate the previous button
        prev_button = driver.find_element(By.CLASS_NAME, "lg-next")

        # Store image URLs
        image_sources = []

        # Loop through each image
        for _ in range(image_count):
            # Find the currently visible image inside the specific div
            try:
                current_image = driver.find_element(By.CSS_SELECTOR,
                                                    ".lg-item.lg-loaded.lg-complete.lg-current img")
                img_src = current_image.get_attribute("src")

                if img_src and img_src not in image_sources:
                    image_sources.append(img_src)

                # Click the previous button to navigate through images
                prev_button.click()
                time.sleep(1)  # Allow time for transition (increased wait time for image change)

            except Exception as e:
                print(f"Error: {e}")

        images = []
        # Print all extracted image URLs
        for src in image_sources:
            images.append(src)

        # Close the driver after finishing
        driver.quit()
        return images

    def process_detail(self,
                       detail_link):

        resp = self.get_page(detail_link)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text,'html.parser')
            title = self.get_title(soup,element_class="detail-title pt-4 pb-2")
            location = self.get_location(soup,element='div',element_class="d-inline-block ml-2")
            key_attributes = self.get_key_attributes(soup)
            other_properties = self.get_other_properties(soup)
            prices = self.get_price(soup)
            description = self.get_description(soup)
            images= self.get_images(detail_link)
            coordinates = [str(i) for i in get_coordinates(location)]
            approval_year = int(
                other_properties['Rok kolaudácie:']) if 'Rok kolaudácie:' in other_properties.keys() else None
            last_reconstruction_year = int(other_properties[
                                               'Rok poslednej rekonštrukcie:']) if 'Rok poslednej rekonštrukcie:' in other_properties.keys() else None
            balconies = int(
                other_properties['Počet balkónov:']) if 'Počet balkónov:' in other_properties.keys() else None
            ownership = other_properties['Vlastníctvo:'] if 'Vlastníctvo:' in other_properties.keys() else None
            floor = int(other_properties['Podlažie:']) if 'Podlažie:' in other_properties.keys() else None
            positioning = other_properties['Umiestnenie:'] if 'Umiestnenie:' in other_properties.keys() else None

            # print(f"title: {title} \nlocation: {location} \nkey attributes: {key_attributes} "
            #       f"\nother properties: {other_properties} \nprices: {prices} \ndescription: {description}")

            if 'Energie:' in other_properties.keys():
                try:
                    energies = int(other_properties['Energie:'].replace(' €',''
                                                                        ).replace(
                                                                        ' ','')
                                                                        )
                except:
                    energies = other_properties['Energie:'].replace(
                                                            ' €', '')
                prices["energies"] = energies
            else:
                prices["energies"] = None

            if 'Stav nehnuteľnosti:' in other_properties.keys():
                key_attributes['property_status'] = other_properties['Stav nehnuteľnosti:']
            else:
                key_attributes['property_status'] = None

            keys_to_remove = [
                'Rok kolaudácie:',
                'Rok poslednej rekonštrukcie:',
                'Počet balkónov:',
                'Vlastníctvo:',
                'Podlažie:',
                'Umiestnenie:',
                "Druh:",
                "Typ:",
                "Úžitková plocha:",
                "Stav nehnuteľnosti:",
                "Počet izieb / miestností:"
            ]

            for key in keys_to_remove:
                print(key)
                if key in other_properties.keys():
                    print(True)
                    del other_properties[key]

            return {
                    "title":title,
                    "location":location,
                    "key_attributes":key_attributes,
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

    def last_page_number_check(self,
                               element_id="next-number active"):
        # Scrape the page content
        url = self.base_url+ "&page=400"
        response = self.get_page(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debugging print to check the structure
        # print(soup.prettify())  # Uncomment this to debug and inspect the page

        # Find all pagination links using the 'next-number' class
        pagination_buttons = soup.select(".next-number")  # Pagination links are using the next-number class

        # Extract page numbers from the href attribute of the pagination links
        page_numbers = []
        for button in pagination_buttons:
            if "href" in button.attrs and "page=" in button["href"]:
                page_number = int(button["href"].split("page=")[-1])  # Extract page number from URL
                page_numbers.append(page_number)

        # Include the currently active page as well, which is in <span class="next-number active">
        active_page = soup.find("span", class_=element_id)
        if active_page:
            page_numbers.append(int(active_page.text))

        # Find the maximum page number (last page)
        last_page = max(page_numbers) if page_numbers else 1

        return last_page


processor = Reality_sk_processor(reality_base_url,
                                 auth_token_reality,
                                 Rent_offers_repository(os.getenv('connection_string')))
# #
# page = processor.get_page(reality_base_url)
# links = processor.get_details_links(BeautifulSoup(page.text,'html.parser'))
# print(links[0])
# detail = processor.get_page(links[0])
# # # # #print(BeautifulSoup(detail.text,'html.parser'))
# print(processor.get_title(BeautifulSoup(detail.text,'html.parser'),element_class="detail-title pt-4 pb-2"))
# print(processor.get_location(BeautifulSoup(detail.text,'html.parser'),element='div',element_class="d-inline-block ml-2"))
# print(processor.get_price(BeautifulSoup(detail.text,'html.parser')))
# print(processor.get_key_attributes(BeautifulSoup(detail.text,'html.parser')))
# processor.get_description(BeautifulSoup(detail.text,'html.parser'))
# print(processor.get_other_properties(BeautifulSoup(detail.text,'html.parser')))
# print(processor.get_images(links[0]))
# print(imgs)
# print(imgs[0])

#processor.process_offers(1,1)
print(processor.process_detail('https://www.reality.sk/byty/moderny-2-izbovy-byt-na-prenajom-v-novostavbe-soho-residence-ii-nove-zamky/JustV9aoX8P/'))
