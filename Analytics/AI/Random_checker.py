from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Shared.LLM import LLM
import re
from Shared.Geolocation import get_coordinates
import json
from sqlalchemy.inspection import inspect
from datetime import datetime
from Scrapping.Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from dotenv import load_dotenv
import os

load_dotenv()

repository = Rent_offers_repository(CONN_STRING)
vdb = Vector_DB_Qdrant('rent-bot-index')
llm = LLM()
nehnutelnosti_base_url = os.getenv('nehnutelnosti_base_url')
auth_token_nehnutelnosti = os.getenv('auth_token_nehnutelnosti')
processor_nehnutelnosti = Nehnutelnosti_sk_processor(nehnutelnosti_base_url,
                                                auth_token_nehnutelnosti,
                                                repository,
                                                    llm,
                                                vdb
                                                     )


file_path = "Descriptions.json.json"

# Open and load the JSON content
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
    
