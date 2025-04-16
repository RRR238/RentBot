from Prompts import get_key_attributes_prompt,get_location_info_prompt, get_location_info_2_prompt
from Shared.Elasticsearch import Vector_DB
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING
import webbrowser
import json
import time
from Shared.LLM import LLM
from Shared.Geolocation import get_coordinates
from utils import convert_text_to_dict, processing_dict, prepare_filters

vdb = Vector_DB('rent-bot-index')
llm = LLM()
# collection = []
#
location_chat_history = [
                        {"role": "system", "content": "You are an assistant that extracts structured information about locations from user queries in Slovak language."},
                         {"role": "user", "content": get_location_info_prompt.format(user_prompt="Luxusný penthouse v Bratislave - Starom Meste s výhľadom na hrad, terasa min. 20 m², 2 parkovacie miesta, rozloha nad 100 m², rozpočet do 2500 € mesačne")},
                         {"role": "assistant", "content": """ústredná lokalita = Bratislava - Staré Mesto"""},
                         {"role": "user", "content": get_location_info_prompt.format(user_prompt="Malý domček v Senci pri jazere, 700 € mesačne")},
                         {"role": "assistant", "content": """ústredná lokalita = Senecké jazero"""},
                         {"role": "user", "content": get_location_info_prompt.format(user_prompt="Luxusný 2-izbový byt v Bratislave")},
                         {"role": "assistant", "content": """ústredná lokalita = Bratislava"""}
#                          {"role": "user", "content": get_location_info_prompt.format(user_prompt="Domček na polosamote pri Žiline, vhodný aj ako chalupa, bez nutnosti veľkej rekonštrukcie, nájom do 600 €, bez nutnosti veľkej záhrady.")},
#                          {"role": "assistant", "content": """ústredná lokalita = Žilina
# lokalizačný rozsah = vonkajší
# vzdialenostná kategória = 3"""},
#                          {"role": "user", "content": get_location_info_prompt.format(user_prompt="Štýlový loft pri Hlavnej stanici v Bratislave, ideálne s vysokými stropmi a industriálnym dizajnom, 800 € max, okolo 65 m²")},
#                          {"role": "assistant", "content": """ústredná lokalita = Hlavná stanica Bratislava
# lokalizačný rozsah = vonkajší
# vzdialenostná kategória = 1"""},
# {"role": "user", "content": get_location_info_prompt.format(user_prompt="Malý domček v Senci pri jazere, 700 € mesačne")},
#                          {"role": "assistant", "content": """ústredná lokalita = Senecke jazero
# lokalizačný rozsah = vonkajší
# vzdialenostná kategória = 1"""}
                        ]
while True:
    query = input('enter query: ')
    #if query == 'q':
        # with open('get_key_attributes_prompt_testing.json', 'w',encoding="utf-8") as json_file:
        #     json.dump(collection, json_file, ensure_ascii=False, indent=4)
        # break

    #response = llm.generate_answer(get_key_attributes_prompt.format(user_prompt=query))
    primary_location = llm.generate_answer(get_location_info_prompt.format(user_prompt=query))
    secundary_location = llm.generate_answer(get_location_info_2_prompt.format(user_prompt=query, primary_location=primary_location))
    # collection.append({"query":query,
    #                   "response":response})
    #print(response)
    print(primary_location)
    print(secundary_location)
    # try:
    #     key_attributes_dict = convert_text_to_dict(response)
    #     processed_dict = processing_dict(key_attributes_dict)
    #     print(key_attributes_dict)
    #     print(processed_dict)
    #     filters = prepare_filters(processed_dict)
    #     print(filters)
    #     embedding = llm.get_embedding(query, model='text-embedding-3-large')
    #     results = vdb.filtered_vector_search(embedding, 15, filter=filters)
    #     for i in results:
    #         print(i['_source']['metadata']['source_url'], i['_score'])
    # except Exception as e:
    #     print(e)
