import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from Scrapping.Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

processor = Nehnutelnosti_sk_processor(
    base_url=os.getenv('nehnutelnosti_base_url'),
    auth_token=os.getenv('auth_token_nehnutelnosti'),
    db_repository=Rent_offers_repository(os.getenv('connection_string')),
    llm=LLM(),
    vector_db=Vector_DB_Qdrant('rent-bot-index'),
)

# fetch listing page and extract first detail link
listing_response = processor.get_page(processor.base_url)
listing_soup = BeautifulSoup(listing_response.text, 'html.parser')
detail_links = processor.get_details_links(listing_soup)

if not detail_links:
    print('No detail links found on listing page.')
    exit(1)

detail_url = detail_links[0]
print(f'Fetching detail: {detail_url}')

detail_response = processor.get_page(detail_url)
detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

output_path = os.path.join(os.path.dirname(__file__), 'detail_snapshot.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(detail_soup.prettify())

print(f'Saved to {output_path}')
