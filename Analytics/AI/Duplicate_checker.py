from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING

repository = Rent_offers_repository(CONN_STRING)


sources = repository.get_all_source_urls()
count = 1
found_dups = 0
l = len(sources)
for i in sources[:5]:

    print(f"processing: {count}/{l}")
    count += 1
    offer = repository.get_offer_by_id_or_url(i)
    if repository.duplicate_exists(offer.price_rent,
                                    offer.size,
                                    offer.coordinates):
        print(offer.price_rent,
        offer.size,
        offer.coordinates)
        #repository.delete_by_source_urls([i])
        found_dups += 1
        print(f"dups found: {count}")

print(found_dups)