from Scrapping.Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from Scrapping.Reality_sk import Reality_sk_processor
from dotenv import load_dotenv
import os
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant

load_dotenv()

nehnutelnosti_base_url = os.getenv('nehnutelnosti_base_url')
auth_token_nehnutelnosti = os.getenv('auth_token_nehnutelnosti')
reality_base_url = os.getenv('reality_base_url')
auth_token_reality = os.getenv('auth_token_reality')
conn_string = os.getenv('connection_string')
llm = LLM()
vdb = Vector_DB_Qdrant('rent-bot-index')

processor_nehnutelnosti = Nehnutelnosti_sk_processor(nehnutelnosti_base_url,
                                                auth_token_nehnutelnosti,
                                                Rent_offers_repository(conn_string),
                                                llm,
                                                vdb
                                                     )

processor_reality = Reality_sk_processor(reality_base_url,
                                    auth_token_reality,
                                    Rent_offers_repository(conn_string),
                                     llm,
                                    vdb
                                     )

if __name__ == "__main__":
    vdb.create_index(3072)
    #processor_nehnutelnosti.delete_invalid_offers()
    processor_nehnutelnosti.process_offers(0,33)
    #processor_reality.process_offers(1,240)

