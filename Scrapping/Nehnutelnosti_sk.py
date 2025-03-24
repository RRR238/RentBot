import requests
from bs4 import BeautifulSoup, Comment
from lxml import etree
import re


class Nehnutelnosti_sk_processor:

    def __init__(self,base_url,auth_token):
        self.auth_token = auth_token
        self.base_url = base_url

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
            print(f"title: {title} \nlocation: {location} \nkey attributes: {key_attributes} \nother properties: {other_properties} \nprices: {prices}")
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
        icons = {
            "2rooms":"M6 4h12a2 2 0 0 1 2 2v5H4V6a2 2 0 0 1 2-2m-2 9v5a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5zM2 6a4 4 0 0 1 4-4h12a4 4 0 0 1 4 4v12a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4z",
            "3rooms": "M16 4v6h4V6a2 2 0 0 0-2-2zm4 8h-4a2 2 0 0 1-2-2V4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2zM2 6a4 4 0 0 1 4-4h12a4 4 0 0 1 4 4v12a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4z",
            "size": "M6 2c-1.075 0-2.067.528-2.77 1.23C2.528 3.933 2 4.925 2 6v12c0 1.075.528 2.067 1.23 2.77C3.933 21.473 4.925 22 6 22h12c1.075 0 2.067-.527 2.77-1.23S22 19.075 22 18v-8a1 1 0 1 0-2 0v8c0 .425-.223.933-.645 1.355S18.425 20 18 20H6c-.425 0-.933-.223-1.355-.645C4.222 18.933 4 18.425 4 18V6c0-.425.222-.933.645-1.355C5.067 4.222 5.575 4 6 4h8a1 1 0 1 0 0-2zm9.783 8.402q-.21.132-.783.457v.678h3v-.854h-.774q-.43 0-.8.035v-.017q.36-.132.677-.335.853-.57.853-1.222 0-.467-.378-.8Q17.2 8 16.425 8q-.703 0-1.126.325-.413.317-.422.898l1.047.281q0-.325.123-.492a.4.4 0 0 1 .352-.176q.202 0 .308.105t.105.29q0 .238-.246.52-.238.28-.783.65m-1.974-.018q-.413-.405-1.082-.405-.484 0-.88.23a1.52 1.52 0 0 0-.598.659 1.26 1.26 0 0 0-.528-.66 1.58 1.58 0 0 0-.862-.229q-.51 0-.888.238-.38.237-.59.695l-.044-.845H7v4.399h1.496v-2.322q0-.51.22-.766a.7.7 0 0 1 .554-.255q.598 0 .598.757v2.586h1.495v-2.349q0-.484.212-.739a.7.7 0 0 1 .563-.255q.598 0 .598.757v2.586h1.495v-2.93q0-.747-.422-1.152",
            "apartmen_status": "m11.973 4.025.008-.003.022.008c.137.052.331.144.586.293.51.296 1.123.734 1.786 1.262l.474.385.465.392.46.4.446.398.427.39.597.557.52.498.656.644.556.56c.652.679.975 1.16 1.019 1.996l.005.217-.002 2.868-.011.86-.021.617-.022.4q-.01.18-.026.352l-.038.384c-.124 1.062-.347 1.683-.595 2.02-.158.216-.404.442-1.123.474l-.181.003H6c-.787 0-1.064-.222-1.208-.382-.217-.24-.45-.716-.601-1.615l-.053-.359a12 12 0 0 1-.037-.318l-.034-.391-.011-.169-.022-.399-.02-.616-.012-.861L4 12c0-.89.29-1.382.804-1.954l.231-.248.457-.462.595-.588.697-.673.615-.576.439-.403.465-.415.224-.196.487-.417.224-.187.49-.397c.637-.503 1.217-.914 1.698-1.19.24-.138.422-.222.547-.269M11.981 2c.844 0 2.243.908 3.648 2.027l.496.403.49.413.48.417.465.415.444.405.614.574.538.515.674.662.577.58c.802.834 1.514 1.759 1.587 3.322L22 12l-.002 2.904-.012.894-.022.657-.023.43q-.015.212-.032.42l-.041.412c-.272 2.37-1.103 4.18-3.646 4.279L18 22H6c-2.49 0-3.43-1.55-3.785-3.687l-.058-.394a14 14 0 0 1-.047-.406l-.036-.417q-.008-.105-.015-.212l-.023-.43-.022-.656-.012-.894L2 12c0-1.546.597-2.494 1.33-3.306l.263-.282.485-.49.611-.604.717-.692.633-.594.457-.419.479-.427q.121-.108.245-.215l.5-.428.252-.21.507-.41C9.832 2.851 11.163 2 11.981 2m.42 7.292a.421.421 0 0 0-.801-.002l-.791 2.409H8.42a.421.421 0 0 0-.241.766l1.986 1.388-.806 2.601a.421.421 0 0 0 .664.455L12 15.346l1.966 1.563a.42.42 0 0 0 .663-.458l-.827-2.597 2.016-1.387a.421.421 0 0 0-.239-.768h-2.405z",
            "house":"m11.973 4.025.008-.003.022.008c.137.052.331.144.586.293.51.296 1.123.734 1.786 1.262l.474.385.465.392.46.4.446.398.427.39.597.557.52.498.656.644.556.56c.652.679.975 1.16 1.019 1.996l.005.217-.002 2.868-.011.86-.021.617-.022.4q-.01.18-.026.352l-.038.384c-.124 1.062-.347 1.683-.595 2.02-.158.216-.404.442-1.123.474l-.181.003H6c-.787 0-1.064-.222-1.208-.382-.217-.24-.45-.716-.601-1.615l-.053-.359a12 12 0 0 1-.037-.318l-.034-.391-.011-.169-.022-.399-.02-.616-.012-.861L4 12c0-.89.29-1.382.804-1.954l.231-.248.457-.462.595-.588.697-.673.615-.576.439-.403.465-.415.224-.196.487-.417.224-.187.49-.397c.637-.503 1.217-.914 1.698-1.19.24-.138.422-.222.547-.269M11.981 2c.844 0 2.243.908 3.648 2.027l.496.403.49.413.48.417.465.415.444.405.614.574.538.515.674.662.577.58c.802.834 1.514 1.759 1.587 3.322L22 12l-.002 2.904-.012.894-.022.657-.023.43q-.015.212-.032.42l-.041.412c-.272 2.37-1.103 4.18-3.646 4.279L18 22H6c-2.49 0-3.43-1.55-3.785-3.687l-.058-.394a14 14 0 0 1-.047-.406l-.036-.417q-.008-.105-.015-.212l-.023-.43-.022-.656-.012-.894L2 12c0-1.546.597-2.494 1.33-3.306l.263-.282.485-.49.611-.604.717-.692.633-.594.457-.419.479-.427q.121-.108.245-.215l.5-.428.252-.21.507-.41C9.832 2.851 11.163 2 11.981 2M12 14a1 1 0 0 0-1 1v2a1 1 0 1 0 2 0v-2a1 1 0 0 0-1-1"
            }

        xpaths = ['//*[@id="main-detail-content"]/div[1]/div/div[1]/div/div[2]/div/div[2]/div/text()[2]',
                  '//*[@id="main-detail-content"]/div[1]/div/div[1]/div/div[2]/div/div[2]/div/text()[5]',
                  '//*[@id="main-detail-content"]/div[1]/div/div[1]/div/div[2]/div/div[2]/div/text()[8]']

        dom = etree.HTML(str(soup))

        container = soup.find('div', 'MuiBox-root mui-1e434qh')
        paragraphs = container.find_all("p") if container else []

        # for i, paragraph in enumerate(paragraphs):
         # Find the <svg> tag in each paragraph
    #     svg = paragraph.find("svg")
    #
    #     # If SVG is found, get the 'd' attribute from the <path> tag
    #     if svg:
    #         path_data = svg.find("path")['d']
    #         print(f"Icon {i + 1}: Path data is {path_data}")

        results = {"house":False,
                   "rooms":None,
                   "size":None,
                   "apartmen_status":None
                   }
        for i in range(len(paragraphs)):
            svg = paragraphs[i].find("svg")
            path_data = svg.find("path")['d']
            for j in icons.keys():
                if icons[j] == path_data:
                    if "dom" in dom.xpath(xpaths[i])[0].lower():
                        results["house"] = True
                    elif "byt" in dom.xpath(xpaths[i])[0].lower():
                        results["rooms"] = j[0]
                    else:
                        results[j] = dom.xpath(xpaths[i])[0]

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

        return paragraph_texts


processor = Nehnutelnosti_sk_processor("https://www.nehnutelnosti.sk/vysledky/prenajom?categories=2&categories=200000",
                                       "Bearer a6693587a95b5087")

page = processor.get_page("https://www.nehnutelnosti.sk/vysledky/prenajom?categories=2&categories=200000")
links = processor.get_details_links(BeautifulSoup(page.text,'html.parser'))
processor.process_detail(links[0])