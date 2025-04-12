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
repository = Rent_offers_repository(CONN_STRING)


# sources = repository.get_all_source_urls()
# count = 1
# considered = []
# duplicates = []
# for i in sources:
#     if i not in considered:
#         print(count)
#         count += 1
#         element = vdb.get_element(source_url=i)
#         most_similar = vdb.search_similar_documents(element['embedding'],k=2)
#         try:
#             if element['metadata']['price_rent'] == most_similar[1]['_source']['metadata']['price_rent']:
#                 if element['metadata']['size']+1 >= most_similar[1]['_source']['metadata']['size'] and element['metadata']['size']-1 <= most_similar[1]['_source']['metadata']['size']:
#                     if element['metadata']['coordinates'] == most_similar[1]['_source']['metadata']['coordinates']:
#
#             #if most_similar[1]['_score'] >= 0.97:
#                         # webbrowser.open(i)
#                         # webbrowser.open_new_tab(most_similar[1]['_source']['metadata']['source_url'])
#                         # is_duplicate = input('is duplicate (1/0) ?')
#                         # duplicates.append({'source':i,
#                         #                    'most_similar':most_similar[1]['_source']['metadata']['source_url'],
#                         #                     'similarity':most_similar[1]['_score'],
#                         #                    'is_duplicate':is_duplicate})
#                         duplicates.append(most_similar[1]['_source']['metadata']['source_url'])
#                         #print(f"original url: {i}, most similar url: {most_similar[1]['_source']['metadata']['source_url']}, similarity: {most_similar[1]['_score']}")
#                         #similarities.append(most_similar[1]['_score'])
#                         considered.append(most_similar[1]['_source']['metadata']['source_url'])
#         except:
#             pass
#
#
# print(len(duplicates))
# with open('duplicates.json', 'w',encoding="utf-8") as json_file:
            #json.dump(duplicates, json_file, ensure_ascii=False, indent=4)

# with open('duplicates.json', 'r',encoding="utf-8") as json_file:
#             duplicates = json.load(json_file)
# #repository.delete_by_source_urls(duplicates)
# for i in duplicates:
#     vdb.delete_element(source_url=i)
prompt = """Z nasledujúceho promptu vydedukuj hodnoty pre tieto premenné:

            cena: <tvoja dedukcia> (uveď iba číslo. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
        
            poloha: <tvoja dedukcia> (Uveď mesto A mestský obvod, ak je to možné. Ak nie je možné určiť PRESNE mesto a obvod, priraď hodnotu None.),
        
            počet izieb: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
        
            rozloha: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
        
            typ nehnuteľnosti: <tvoja dedukcia> (vyber iba jednu z nasledujúcich možností: "dom", "loft", "mezonet", "byt", "garzonka". Ak nie je možné určiť, priraď hodnotu None.).
        
            Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.
        
            Prompt: {user_prompt}
        
            Tvoj výstup: """

while True:
    query = input('enter query: ')
    #response = llm.generate_answer(prompt.format(user_prompt=query))
#     print(response)
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
    final_dict = {'price_rent':1000,'rooms':2,'property_type':'flat'}

    embedding = llm.get_embedding(query,model='text-embedding-3-large')
    #results = vdb.search_similar_documents(embedding,k=10)
    results = vdb.filtered_vector_search(embedding,10)
    #print(results)
    for i in results:
        print(i['_source']['metadata']['source_url'], i['_score'])

