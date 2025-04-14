from Prompts import get_key_attributes_prompt,get_location_info_prompt
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
collection = []

while True:
    query = input('enter query: ')
    if query == 'q':
        with open('get_key_attributes_prompt_testing.json', 'w',encoding="utf-8") as json_file:
            json.dump(collection, json_file, ensure_ascii=False, indent=4)
        break

    #response = llm.generate_answer(get_key_attributes_prompt.format(user_prompt=query))
    response = llm.generate_answer(get_location_info_prompt.format(user_prompt=query))
    # collection.append({"query":query,
    #                   "response":response})
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

# with open("Novostavby.json", "r", encoding="utf-8") as file:
#     data = json.load(file)
#
# for i in data:
#     vdb.update_metadata_by_url(i,{"property_status":"novostavba"})