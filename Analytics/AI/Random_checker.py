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
import sys

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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


# file_path = "Invalid_total_price.json"
#
# # Open and load the JSON content
# with open(file_path, "r", encoding="utf-8") as file:
#     data = json.load(file)
#
#
data =[
  {
    "source_url": "https://www.reality.sk/byty/prenajom-penthouse-novostavba-safranova-zahrada-4-izb-byt-s-terasou-2x-garazove-statie/JuUemf05CHR/"
  },
  {
    "source_url": "https://www.reality.sk/byty/prestizny-moderny-penthouse-s-jedinecnou-terasou-a-nadhernym-vyhladom-na-mesto/Ju0ulfRG9d2/"
  },
  {
    "source_url": "https://www.reality.sk/byty/prenajom-3-izbovy-penthouse-s-terasou-na-pastierskej-ul-stupava/JuDs0Jc17Nc/"
  },
  {
    "source_url": "https://www.nehnutelnosti.sk/detail/JuyvEp6FWEy/2i-zariadeny-klimatizovany-penthouse-s-terasou"
  },
  {
    "source_url": "https://www.reality.sk/byty/5-izb-penthouse-na-zamockej-bratislava-i-stare-mesto/Ju3hmLNe2tE/"
  },
  {
    "source_url": "https://www.nehnutelnosti.sk/detail/Ju0ulfRG9d2/prestizny-moderny-penthouse-s-jedinecnou-terasou-a-nadhernym-vyhladom-na-mesto"
  },
  {
    "source_url": "https://www.nehnutelnosti.sk/detail/JuUemf05CHR/prenajom-penthousel-novostavba-safranova-zahrada-4-izb-byt-s-terasoul-2x-garazove-statie"
  },
  {
    "source_url": "https://www.reality.sk/byty/orbis-premium-luxusny-penthouse-o-rozlohe-231m2-s-krasnym-vyhladom-na-mesto/JudXcll6w4x/"
  },
  {
    "source_url": "https://www.reality.sk/byty/svoboda-williams-i-34210-i-3-izbovy-penthouse-s-terasami-a-premiovym-vyhladom-leskova-stare-mesto/JuKE1yvwYuF4/"
  },
  {
    "source_url": "https://www.reality.sk/byty/luxusny-penthouse-na-prenajom/Ju_3cQtsESZ/"
  },
  {
    "source_url": "https://www.reality.sk/byty/orbis-premium-luxusny-penthouse-o-rozlohe-231m2-s-krasnym-vyhladom-na-mesto/JuozPT44sAk/"
  },
  {
    "source_url": "https://www.reality.sk/byty/kratkodoby-prenajom-nadstandardneho-3izb-bytu-penthouse-97m-70m-terasa-1x-garaz-v-cene-lopuchova-ul-koliba-unikatny-panoramaticky-vyhlad/JuFY1MveqlH/"
  },
  {
    "source_url": "https://www.reality.sk/byty/bez-provizie-luxusny-4i-byt-na-najvyssom-poschodi-s-velkou-terasou-a-zimnou-zahradou-2-statia-commission-free-luxury-4-bedroom-penthouse/JuWniBqSoZv/"
  },
  {
    "source_url": "https://www.reality.sk/byty/velkometrazny-4-izb-penthouse-s-vyhladmi-na-celu-panoramu-bratislavy/JuLS-kh7FTy/"
  }
]
for i in data:
    resource_metadata = vdb.get_element(source_url=i['source_url'])[0].points[0].payload
    #resource_metadata.update({'price_total':(i['price_rent']+i['price_energies'])})
    #vdb.update_metadata_by_url(i['source_url'],resource_metadata)
    print(resource_metadata)