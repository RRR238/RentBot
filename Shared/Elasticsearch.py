from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
from elasticsearch.helpers import bulk
#from LLM import LLM
import time

load_dotenv()

class Vector_DB:
    def __init__(self,
                 index_name):
        self.__client = Elasticsearch(
                        hosts=os.getenv('ELASTICSEARCH_HOST'),
                        api_key=os.getenv('ELASTICSEARCH_API_KEY')
                        )
        self.index_name = index_name

    def create_index(self,
                     vector_dimension,
                     similarity="cosine"):

        mappings = {
            "mappings": {
                "properties": {
                    "embedding": {
                        "type": "dense_vector",
                        "dims": vector_dimension,
                        "similarity": similarity
                    },
                    "metadata": {
                        "type": "object"
                    }
                }
            }
        }

        if not self.__client.indices.exists(index=self.index_name):
            self.__client.indices.create(index=self.index_name, body=mappings)

    def insert_data(self,
                    documents:list[dict]):

        """documents is of type [{"embedding": embedding,"metadata": metadata},]"""

        actions = []
        for doc in documents:
            action = {
                "_op_type": "index",  # This specifies we want to index the documents
                "_index": self.index_name,  # Specify the index to insert data into
                "_source": doc  # The document data (embedding + metadata)
            }
            actions.append(action)

        # Insert the documents in bulk
        response = bulk(self.__client, actions)

        # Print the result of the bulk insert
        print(f"Inserted {response[0]} documents into Elasticsearch.")

    def delete_by_metadata_id(self, metadata_id):
        query = {
            "query": {
                "term": {
                    "metadata.id": metadata_id  # assumes metadata is a nested object
                }
            }
        }

        response = self.__client.delete_by_query(index=self.index_name, body=query)
        print(f"Deleted {response['deleted']} documents with metadata.id = {metadata_id}")

    def delete_all_documents(self):
        query = {
            "query": {
                "match_all": {}
            }
        }

        response = self.__client.delete_by_query(index=self.index_name, body=query)
        print(f"Deleted {response['deleted']} documents from index '{self.index_name}'")

    def search_similar_documents(self,
                                 query_vector,
                                 similarity_threshold: float = None,
                                 k: int = 10,
                                 num_candidates: int = 100):
        query = {
            "knn": {
                "field": "embedding",
                "query_vector": query_vector,
                "k": k,
                "num_candidates": num_candidates
            }
        }

        response = self.__client.search(index=self.index_name,
                                        body=query)

        if similarity_threshold:
            hits = response["hits"]["hits"]
            filtered_results = [
                hit for hit in hits if hit["_score"] >= similarity_threshold
            ]

            return filtered_results

        return response["hits"]["hits"]

# llm = LLM()
#vdb = Vector_DB('rent-bot-index')

# data = [{"embedding":llm.get_embedding("ahoj, som v meste"),
#          "metadata":{"test":"test",
#                      "timestamp":"now",
#                      "id":7437544330}}]
#
# vdb.insert_data(data)
#vdb.delete_all_documents()

# s = time.time()
# print(vdb.search_similar_documents(llm.get_embedding("ahoj, kde si ?")))
# e = time.time()
# print(e-s)