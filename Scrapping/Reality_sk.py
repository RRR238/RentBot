from Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class Reality_sk_processor(Nehnutelnosti_sk_processor):

    def __init__(self):
        super().__init__("https://www.reality.sk/prenajom/?categories_all=%5B2,3%5D",
                         "8ae3c79ded93973f")

    def get_details_links(self, soup, keyword='byty'):
        examples = super().get_details_links(soup,keyword)
        final = []

        for link in examples:
            parsed = urlparse(link)

            path_parts = [p for p in parsed.path.split("/") if p]  # Remove empty parts from split
            if len(path_parts) >= 3 and not path_parts[-1] in ["predaj",
                                                               "prenajom",
                                                               "bratislava"]:
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
                                ).find('h3', class_='contact-title big col-12 col-md-6 mb-0').find_all('small'
                                )[0].text.strip(
                                ).split("€")[0]

        return {
                "rent":price_rent,
                 "meter squared":price_ms
                 }


processor = Reality_sk_processor()

page = processor.get_page("https://www.reality.sk/prenajom/?categories_all=%5B2,3%5D")
links = processor.get_details_links(BeautifulSoup(page.text,'html.parser'))
print(links)
detail = processor.get_page(links[0])
#print(BeautifulSoup(detail.text,'html.parser'))
print(processor.get_title(BeautifulSoup(detail.text,'html.parser'),element_class="detail-title pt-4 pb-2"))
print(processor.get_location(BeautifulSoup(detail.text,'html.parser'),element='div',element_class="d-inline-block ml-2"))
print(processor.get_price(BeautifulSoup(detail.text,'html.parser')))