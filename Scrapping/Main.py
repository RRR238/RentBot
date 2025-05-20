from Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from Reality_sk import Reality_sk_processor
from dotenv import load_dotenv
import os
from Rent_offers_repository import Rent_offers_repository
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
import json

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


if __name__ == "__main__":
    processor_nehnutelnosti.delete_invalid_offers()
    processor_nehnutelnosti.process_offers(1,33)
    processor_reality.process_offers(1,240)

