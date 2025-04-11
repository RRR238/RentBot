from Shared.Elasticsearch import Vector_DB
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING
import seaborn as sns
import matplotlib.pyplot as plt
import webbrowser
import pandas as pd
import json
import numpy as np
import os
from Shared.LLM import LLM


# vdb = Vector_DB('rent-bot-index')
# repository = Rent_offers_repository(CONN_STRING)
#
#
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
#                 if element['metadata']['size']+3 >= most_similar[1]['_source']['metadata']['size'] or element['metadata']['size']-3 <= most_similar[1]['_source']['metadata']['size']:
#                     if element['metadata']['coordinates'] == most_similar[1]['_source']['metadata']['coordinates']:
#
#             #if most_similar[1]['_score'] >= 0.97:
#                         webbrowser.open(i)
#                         webbrowser.open_new_tab(most_similar[1]['_source']['metadata']['source_url'])
#                         is_duplicate = input('is duplicate (1/0) ?')
#                         duplicates.append({'similarity':most_similar[1]['_score'],
#                                            'is_duplicate':is_duplicate})
#
#                         #print(f"original url: {i}, most similar url: {most_similar[1]['_source']['metadata']['source_url']}, similarity: {most_similar[1]['_score']}")
#                         #similarities.append(most_similar[1]['_score'])
#                         considered.append(most_similar[1]['_source']['metadata']['source_url'])
#         except:
#             pass
#
# with open('duplicates.json', 'w',encoding="utf-8") as json_file:
#             json.dump(duplicates, json_file, ensure_ascii=False, indent=4)

# with open('duplicates.json', 'r', encoding='utf-8') as f:
#     duplicates = json.load(f)
#
# # Ensure 'is_duplicate' is an integer (1 for duplicate, 0 for non-duplicate)
# duplicates = [{'similarity': i['similarity'], 'is_duplicate': int(i['is_duplicate'])} for i in duplicates]
#
# # Create a DataFrame
# df = pd.DataFrame(duplicates)
#
# # Sort data by similarity
# df_sorted = df.sort_values('similarity')
#
# # Calculate the cumulative sum of duplicates and normalize it to get probabilities
# df_sorted['cumulative_duplicates'] = df_sorted['is_duplicate'].cumsum() / df_sorted['is_duplicate'].count()
#
# # Plot CDF: Similarity on x-axis, cumulative probability on y-axis
# plt.figure(figsize=(10, 6))
# plt.plot(df_sorted['similarity'], df_sorted['cumulative_duplicates'], marker='o', linestyle='-', color='b')
# plt.title('Cumulative Distribution Function (CDF) of Duplicates by Similarity')
# plt.xlabel('Similarity Score')
# plt.ylabel('Cumulative Probability of Being a Duplicate')
# plt.grid(True)
# plt.show()
llm = LLM()
vdb = Vector_DB('rent-bot-index')
while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    query = input()
    embedding = llm.get_embedding(query,
                                  'text-embedding-3-large')
    results = vdb.search_similar_documents(query_vector=embedding,k=4)
    for i in results:
        print(i['_source']['metadata']['source_url'])