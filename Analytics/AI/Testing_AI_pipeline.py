from Prompts import get_key_attributes_prompt
from Shared.Elasticsearch import Vector_DB
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING
import webbrowser
import json
import time
from Shared.LLM import LLM
from Shared.Geolocation import get_coordinates

vdb = Vector_DB('rent-bot-index')
llm = LLM()
collection = []

while True:
    query = input('enter query: ')
    if query == 'q':
        with open('get_key_attributes_prompt_testing.json', 'w',encoding="utf-8") as json_file:
            json.dump(collection, json_file, ensure_ascii=False, indent=4)
        break

    response = llm.generate_answer(get_key_attributes_prompt.format(user_prompt=query))
    collection.append({"query":query,
                      "response":response})
    print(response)
#     try:
#         location = response[response.find('poloha')+len("poloha: "):response.find('počet izieb')].strip()
#         print(location.replace(',',''))
#         coordinates = get_coordinates(location.replace(',',''))
#         print(coordinates)
#     except:
#         coordinates = None
#
#     response_text = response.strip()
#
#     # Create a list of key-value pairs by splitting only on the first colon
#     pairs = [line.split(":", 1) for line in response_text.split(',')]
#
#     # Convert it into a dictionary
#     response_dict = {}
#
#     for pair in pairs:
#         if len(pair) == 2:
#             key = pair[0].strip()  # Clean up the key
#             value = pair[1].strip()  # Clean up the value
#
#             # Special case: Convert 'None' string to Python None
#             if value == "None":
#                 value = None
#
#             response_dict[key] = value
#
#     # Assuming coordinates are provided, add them
#
#     # Now remove fields with None and 'poloha' and 'coordinates'
#     filtered_dict = {key: value for key, value in response_dict.items() if
#                      value is not None and key not in ['poloha']}
#     print(filtered_dict)
#     final_dict = {'price_rent':1000,'rooms':2,'property_type':'flat'}
#
#     embedding = llm.get_embedding(query,model='text-embedding-3-large')
#     #results = vdb.search_similar_documents(embedding,k=10)
#     results = vdb.filtered_vector_search(embedding,10)
#     #print(results)
#     for i in results:
#         print(i['_source']['metadata']['source_url'], i['_score'])