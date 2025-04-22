from Prompts import get_key_attributes_prompt,location_extraction_prompt, location_scope_prompt
from Shared.Elasticsearch import Vector_DB
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING
import webbrowser
import json
import time
from Shared.LLM import LLM
from Shared.Geolocation import get_coordinates
from utils import convert_text_to_dict, processing_dict, prepare_filters, get_bounding_box
import ast

vdb = Vector_DB('rent-bot-index')
llm = LLM()
# collection = []
#
chat_history = [
                        {"role": "system", "content": "You are an assistant that extracts structured information about locations from user queries in Slovak language."},
                         {"role": "user", "content": get_key_attributes_prompt.format(user_prompt="Byt s dvomi spálňami a samostatnou pracovňou, s terasou a pivnicou. V tichej časti Petržalky, blízko lesoparku a MHD, do 950 €, výmera min. 80 m², možnosť prenájmu dlhodobo")},
                         {"role": "assistant", "content": """cena: 950
počet izieb: 3
počet izieb MIN: None
počet izieb MAX: None
rozloha: 80
typ nehnuteľnosti: byt
novostavba: None"""}
                        ]

while True:
    query = input('enter query: ')
    #if query == 'q':
        # with open('get_key_attributes_prompt_testing.json', 'w',encoding="utf-8") as json_file:
        #     json.dump(collection, json_file, ensure_ascii=False, indent=4)
        # break

    response = llm.generate_answer(get_key_attributes_prompt.format(user_prompt=query),chat_history=chat_history)
    # location = llm.generate_answer(location_extraction_prompt.format(user_prompt=query))
    # location_list = ast.literal_eval(location)
    # for i in range(len(location_list)):
    #     actual_location = ",".join(location_list[:len(location_list)-i])
    #     print(actual_location)
    #     bb = get_bounding_box(actual_location)
    #     if bb is not None:
    #         print(bb)
    #         break
    # if actual_location:
    #     scope = llm.generate_answer(location_scope_prompt.format(user_prompt=query, anchor_location=actual_location))
    #     print(scope)
    print(response)
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
