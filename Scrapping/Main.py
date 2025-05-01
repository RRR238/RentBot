from Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from Reality_sk import Reality_sk_processor
from dotenv import load_dotenv
import os
from Rent_offers_repository import Rent_offers_repository
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant

load_dotenv()

nehnutelnosti_base_url = os.getenv('nehnutelnosti_base_url')
auth_token_nehnutelnosti = os.getenv('auth_token_nehnutelnosti')
reality_base_url = os.getenv('reality_base_url')
auth_token_reality = os.getenv('auth_token_reality')
conn_string = os.getenv('connection_string')

processor_nehnutelnosti = Nehnutelnosti_sk_processor(nehnutelnosti_base_url,
                                                auth_token_nehnutelnosti,
                                                Rent_offers_repository(conn_string),
                                                    LLM(),
                                                Vector_DB_Qdrant('rent-bot-index')
                                                     )

processor_reality = Reality_sk_processor(reality_base_url,
                                    auth_token_reality,
                                    Rent_offers_repository(conn_string),
                                     LLM(),
                                     Vector_DB_Qdrant('rent-bot-index')
                                     )

vdb = Vector_DB_Qdrant('rent-bot-index')
repo = Rent_offers_repository(conn_string)

if __name__ == "__main__":
    processor_nehnutelnosti.delete_invalid_offers()
    # processor_nehnutelnosti.process_offers(1,33)
    # processor_reality.process_offers(1,240)
    # vdb.create_index(3072)
    # urls = repo.get_all_source_urls()
    # total = len(urls)
    # current = 1
    # errors = 0
    # for i in urls:
    #     print(f"processing: {current}/{total}")
    #     offer = repo.get_offer_by_id_or_url(i)
    #     embedding = processor_nehnutelnosti.embedd_rent_offer(LLM(),offer.title, offer.description,offer.other_properties)
    #     keys_to_remove = {"created_at",
    #                       '_sa_instance_state',
    #                       "title",
    #                       "location",
    #                       "description",
    #                       "other_properties",
    #                       "floor",
    #                       "positioning",
    #                       "source",
    #                       'score'}
    #     filtered_offer = {k: v for k, v in offer.__dict__.items() if k not in keys_to_remove}
    #     result = vdb.insert_data([{"embedding": embedding,
    #                                     "metadata": filtered_offer}])
    #     if not result:
    #         print(f"error processing: {i}")
    #         errors +=1
    # print(f"errors: {errors}")

