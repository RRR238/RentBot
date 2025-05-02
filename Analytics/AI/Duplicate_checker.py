from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING

repository = Rent_offers_repository(CONN_STRING)


sources = repository.get_all_source_urls()
count = 1
found_dups = 0
l = len(sources)
for i in sources:

    print(f"processing: {count}/{l}")
    print(f"dups found: {found_dups}")
    count += 1
    offer = repository.get_offer_by_id_or_url(i)
    if repository.duplicate_exists(price=offer.price_rent,
                                    size=offer.size,
                                    coordinates=offer.coordinates,
                                    url=i):

        repository.delete_by_source_urls([i])
        found_dups += 1
        #print(offer.price_rent,offer.size,offer.coordinates)

print(found_dups)