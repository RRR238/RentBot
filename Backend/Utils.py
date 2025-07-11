import requests
from bs4 import BeautifulSoup


def process_types_and_rooms_filters(types:str):
    types_list = types.split(',') if "," in types else [types]
    rooms = [int(i[0]) for i in types_list if 'room' in i or 'plus' in i]
    filtered_types = [t for t in types_list if 'room' not in t.lower() and 'plus' not in t.lower()]
    if len(filtered_types) < len(types_list):
        filtered_types.append('flat')

    return {'types':filtered_types,
            'rooms':rooms}


def filter_vector_search_results(vector_search_results:list[dict],
                                 types:list[str],
                                 rooms:list[int],
                                 price_max:int,
                                 size_min:int,
                                 size_max:int):
    filtered_results = []
    for result in vector_search_results:
        if result['property_type'] in types:
            if result['rooms'] in rooms:
                if result['price_total'] <= price_max:
                    if result['size'] >= size_min:
                        if result['size'] <= size_max:
                            filtered_results.append({'source_url':result['source_url'],
                                                     'price_total':result['price_total'],
                                                     'location':result['location']})

    return filtered_results


def extract_link_preview_image(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        og_image_tag = soup.find("meta", property="og:image")

        if og_image_tag and og_image_tag.get("content"):
            return og_image_tag["content"]
    except Exception as e:
        print(f"Error fetching og:image for {url}: {e}")

    return ""


def add_preview_image(retrieved_offers:dict):
    valid_offers = []
    for offer in retrieved_offers['offers']:
        preview_image = extract_link_preview_image(offer['source_url'])
        if preview_image not in ['https://www.nehnutelnosti.sk/_next/static/media/OG-vybrat-spravne-je-klucove.855914bd.jpg',""]:
            offer['preview_image'] = preview_image
            valid_offers.append(offer)

    return valid_offers

print(extract_link_preview_image('https://www.nehnutelnosti.sk/vysledky/2-izbove-byty/bratislava-ruzinov/prenajom'))