from Shared.Elasticsearch import Vector_DB
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING
from Shared.LLM import LLM


vdb = Vector_DB('rent-bot-index')
llm = LLM()
repository = Rent_offers_repository(CONN_STRING)


sources = repository.get_all_source_urls()
count = 1
duplicates = []
found_dups = 0
l = len(sources)
for i in sources:

    print(f"{count}/{l}")
    count += 1
    offer = repository.get_offer_by_id_or_url(i)
    if repository.duplicate_exists(offer.price_rent,
                                    offer.size+1,
                                    offer.coordinates) and repository.duplicate_exists(
                                                            offer.price_rent,
                                                            offer.size - 1,
                                                            offer.coordinates):
        duplicates.append(i)
        repository.delete_by_source_urls([i])
        found_dups += 1

print(found_dups)