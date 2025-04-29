from Shared.Vector_database.Elasticsearch import Vector_DB
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING
import json
from Shared.LLM import LLM


vdb = Vector_DB('rent-bot-index')
llm = LLM()
repository = Rent_offers_repository(CONN_STRING)


sources = repository.get_all_source_urls()
count = 1
considered = []
duplicates = []
for i in sources:
    if i not in considered:
        print(count)
        count += 1
        element = vdb.get_element(source_url=i)
        most_similar = vdb.search_similar_documents(element['embedding'],k=2)
        try:
            if element['metadata']['price_rent'] == most_similar[1]['_source']['metadata']['price_rent']:
                if element['metadata']['size']+1 >= most_similar[1]['_source']['metadata']['size'] and element['metadata']['size']-1 <= most_similar[1]['_source']['metadata']['size']:
                    if element['metadata']['coordinates'] == most_similar[1]['_source']['metadata']['coordinates']:

            #if most_similar[1]['_score'] >= 0.97:
                        # webbrowser.open(i)
                        # webbrowser.open_new_tab(most_similar[1]['_source']['metadata']['source_url'])
                        # is_duplicate = input('is duplicate (1/0) ?')
                        # duplicates.append({'source':i,
                        #                    'most_similar':most_similar[1]['_source']['metadata']['source_url'],
                        #                     'similarity':most_similar[1]['_score'],
                        #                    'is_duplicate':is_duplicate})
                        duplicates.append(most_similar[1]['_source']['metadata']['source_url'])
                        #print(f"original url: {i}, most similar url: {most_similar[1]['_source']['metadata']['source_url']}, similarity: {most_similar[1]['_score']}")
                        #similarities.append(most_similar[1]['_score'])
                        considered.append(most_similar[1]['_source']['metadata']['source_url'])
        except:
            pass


print(len(duplicates))
with open('duplicates.json', 'w',encoding="utf-8") as json_file:
            json.dump(duplicates, json_file, ensure_ascii=False, indent=4)

# with open('duplicates.json', 'r',encoding="utf-8") as json_file:
#             duplicates = json.load(json_file)
# #repository.delete_by_source_urls(duplicates)
# for i in duplicates:
#     vdb.delete_element(source_url=i)


