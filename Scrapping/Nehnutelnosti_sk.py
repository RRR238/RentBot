import requests
from bs4 import BeautifulSoup
from lxml import etree
from DOM_identifiers import DOM_identifiers
import time


class Nehnutelnosti_sk_processor:

    def __init__(self,base_url,auth_token):
        self.auth_token = auth_token
        self.base_url = base_url
        self.processed_offers = []
        self.failed_offers = []
        self.failed_pages = []

    def get_page(self,url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
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
                    full_url = f"https://www.nehnutelnosti.sk{href}"  # Prepend the domain to relative URLs
                detail_links.append(full_url)

        return detail_links

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
            # print(f"title: {title} \nlocation: {location} \nkey attributes: {key_attributes} "
            #       f"\nother properties: {other_properties} \nprices: {prices} \ndescription: {description}")
            return {
                    "title":title,
                    "location":location,
                    "key_attributes":key_attributes,
                    "other_properties":other_properties,
                    "prices":prices,
                    "description":description
                    }
        else:
            raise Exception(f"Failed to fetch page: {detail_link}, Status Code: {resp.status_code}")

    def get_title(self, soup):
        title = soup.find('h1',
                          class_ = 'MuiTypography-root MuiTypography-h4 mui-1wj7mln'
                          ).text.strip()
        return title

    def get_location(self, soup):
        location = soup.find('p',
                             class_='MuiTypography-root MuiTypography-body2 MuiTypography-noWrap mui-3vjwr4'
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
        price_rent = soup.find('p', "MuiTypography-root MuiTypography-h3 mui-fm8hb4"
                          ).text.strip()

        paragraphs = soup.find_all('p', class_="MuiTypography-root MuiTypography-label2 mui-gsg6ma")
        price_energies = None
        for p in paragraphs:
            if "€" in p.text:  # Look for the one containing a price
                price_energies = p.text.strip()
                break
        price_ms = soup.find('p', "MuiTypography-root MuiTypography-label2 mui-ifbhxp"
                                   ).text.strip() if "€" in soup.find('p', "MuiTypography-root MuiTypography-label2 mui-ifbhxp"
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

        container = soup.find('div','MuiGrid2-root MuiGrid2-container MuiGrid2-direction-xs-row MuiGrid2-spacing-xs-1 mui-lgq25d')
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

    def process_offers_single_page(self, page_url, sleep=5):
        page = self.get_page(page_url)
        detail_links = self.get_details_links(BeautifulSoup(page.text,'html.parser'))
        print(detail_links)
        process_n = 1
        for link in detail_links:
            print(f"processing{process_n}/{len(detail_links)}")
            #check if the link is already in DB - if so, skip case
            if link in self.processed_offers:
                continue
            try:
                results = self.process_detail(link)
                results["source"] = link
                print(results)
                self.processed_offers.append(link)
                time.sleep(sleep)
            except Exception as e:
                print(f"failed to process offer: {link} on page: {page_url}, error: {e}")
                self.failed_offers.append(link)

            process_n+=1
            #save results to DB

    def process_offers(self,start_page=1, end_page=None):
        last_page = self.last_page_number_check()
        current_page = start_page

        while True:
            if end_page:
                if current_page > end_page:
                    break
            if current_page > last_page:
                break

            url = f"{self.base_url}&page={current_page}"
            try:
                self.process_offers_single_page(url)
            except Exception as e:
                print(f"failed to process page: {url}, error: {e}")
                self.failed_pages.append(url)

            current_page += 1

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





processor = Nehnutelnosti_sk_processor("https://www.nehnutelnosti.sk/vysledky/prenajom?categories=2&categories=200000",
                                       "Bearer a6693587a95b5087")
#processor.pagination_check()
# page = processor.get_page("https://www.nehnutelnosti.sk/vysledky/prenajom?categories=2&categories=200000")
# links = processor.get_details_links(BeautifulSoup(page.text,'html.parser'))
# processor.process_detail(links[0])
processor.process_offers(1,3)