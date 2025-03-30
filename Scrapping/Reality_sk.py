from Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, urlunparse
from PIL import Image
from io import BytesIO

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

        loc = super().get_location(soup, element=element,
                                     element_class=element_class)
        cleaned_lines = " ".join([line.strip() for line in loc.splitlines() if line.strip()]
                                 ).replace("•","")

        return cleaned_lines

    def get_price(self, soup):

        price_rent = soup.find('div',"d-flex flex-wrap no-gutters justify-content-between align-items-center"
                                    ).find('h3', class_='contact-title big col-12 col-md-6 mb-0').text.strip(
                                    ).split("€")[0]

        price_ms = soup.find('div',"d-flex flex-wrap no-gutters justify-content-between align-items-center"
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




# processor = Reality_sk_processor(reality_base_url,
#                                  auth_token_reality)
#
# page = processor.get_page(reality_base_url)
# links = processor.get_details_links(BeautifulSoup(page.text,'html.parser'))
# print(links[0])
# detail = processor.get_page(links[0])
# # #print(BeautifulSoup(detail.text,'html.parser'))
# # print(processor.get_title(BeautifulSoup(detail.text,'html.parser'),element_class="detail-title pt-4 pb-2"))
# # # print(processor.get_location(BeautifulSoup(detail.text,'html.parser'),element='div',element_class="d-inline-block ml-2"))
# # # print(processor.get_price(BeautifulSoup(detail.text,'html.parser')))
# # print(processor.get_key_attributes(BeautifulSoup(detail.text,'html.parser')))
# # #processor.get_description(BeautifulSoup(detail.text,'html.parser'))
# # #processor.get_other_properties(BeautifulSoup(detail.text,'html.parser'))
# print(processor.get_images_url(links[0]))
# imgs = processor.get_images(links[0])
# print(imgs)
# print(imgs[0])



# r = processor.get_page('https://s.unitedclassifieds.sk/jul/_niCsd7zT_fss?st=1KIW2RgpCgH1PV6amN6FcSPRDk8XrlxpnIRCmSGX85E&ts=1742678865&e=0')
# print(r.status_code)
import requests
url = 'https://img.unitedclassifieds.sk/foto/NzAweDU3NS9maWx0ZXJzOnF1YWxpdHkoMTAwKS9qdWw=/_txDjYgRk_fss?st=JJT-J9LJsnvqYWtSTtyJXVPqb0MXNSwTgqNd_gFd70k&amp;ts=1742678882&amp;e=0'

headers = {
    'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.reality.sk/',  # Replace with the actual referring page
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'image',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-storage-access': 'active',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    "Authorization": "8ae3c79ded93973f"
}
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # For automatic driver management
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Optional, opens browser maximized

# Initialize the driver
service = Service(ChromeDriverManager().install())  # Automatically downloads the latest driver
driver = webdriver.Chrome(service=service, options=chrome_options)


# Function to handle the consent popup
def handle_consent_popup():
    try:
        # Wait for the iframe to load where the cookie consent is located
        consent_iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sp_message_iframe_1109517"))  # Adjust the iframe ID if needed
        )

        # Switch to the consent iframe
        driver.switch_to.frame(consent_iframe)

        # Find and click the 'Accept' button (adjust the button text or selector as needed)
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Accept"]'))  # Adjust XPath if necessary
        )
        accept_button.click()

        # Switch back to the main page
        driver.switch_to.default_content()
        print("✅ Consent popup handled.")
    except Exception as e:
        print("❌ Consent popup not found or could not be handled:", e)


# Open the URL
url = "https://www.reality.sk/1-izbovy-byt-foto/kompletne-zariadeny-1-izbovy-byt-s-lodziou-skolska-banska-bystrica/Ju0_KMv9Ive/"
driver.get(url)

# Maximize the window (optional)
driver.maximize_window()

# Handle the consent popup (if it appears)
handle_consent_popup()

# Now proceed with the rest of the scraping logic or image extraction

# Example of waiting for thumbnails and clicking on them
thumbnails = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".lg-thumb-item"))
)


# Function to click on each thumbnail and open high-res images
def click_thumbnails_and_get_images():
    for thumb in thumbnails:
        try:
            # Scroll the thumbnail into view
            driver.execute_script("arguments[0].scrollIntoView(true);", thumb)
            time.sleep(1)  # Give the page time to adjust the view

            # Ensure the thumbnail is clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(thumb))

            # Click the thumbnail to open the high-res image
            thumb.click()

            # Wait for the lightbox or modal to load (adjust the wait time if necessary)
            time.sleep(2)  # Waiting for high-res image to be visible

            # You can extract the image URL or any other information here
            # For example, to get the src of the currently displayed image:
            image_element = driver.find_element(By.CSS_SELECTOR, ".lg-image")
            high_res_image_url = image_element.get_attribute("src")
            print("✅ High-Resolution Image URL:", high_res_image_url)

            # Optionally, you can close the lightbox or modal after getting the image URL
            close_button = driver.find_element(By.CSS_SELECTOR, ".lg-close")
            close_button.click()
            time.sleep(1)  # Give the page time to close the lightbox

        except Exception as e:
            print("❌ Error handling thumbnail:", e)


# Click on thumbnails and get the high-res images
click_thumbnails_and_get_images()

# Close the browser after operation is completed
driver.quit()

# response = requests.get(url, headers=headers)
#
# if response.status_code == 200:
#     image = Image.open(BytesIO(response.content))
#     width, height = image.size
#     print(f"Image dimensions: {width}x{height}")  # Example: 1920x1080
#     if width >= 1000 and height >= 1000:  # Adjust threshold as needed
#         print("High-quality image detected ✅")
#     else:
#         print("Low-quality image ❌")
# else:
#     print(f"Failed to fetch image, status code: {response.status_code}")