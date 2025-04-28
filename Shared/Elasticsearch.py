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
                        api_key=os.getenv('QDRANT_API_KEY')
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

    def delete_element(self,
                        postgres_id=None,
                        source_url=None):

        if not postgres_id and not source_url:
            raise ValueError("You must provide at least metadata_ids or source_urls.")

        if postgres_id:
            query = {
                "query": {
                    "term": {
                        "metadata.id.keyword": postgres_id
                    }
                }
            }
        else:
            query = {
                "query": {
                    "term": {
                        "metadata.source_url.keyword": source_url
                    }
                }
            }

        response = self.__client.delete_by_query(index=self.index_name,
                                                 body=query,
                                                 conflicts="proceed")
        print(f"Deleted {response['deleted']} documents matching criteria.")

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
                                 num_candidates: int = 500):
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

    def get_element(self,postgres_id=None, source_url=None):

        if postgres_id:
            query = {
                "query": {
                    "term": {
                        "metadata.id.keyword": postgres_id
                    }
                }
            }
        else:
            query = {
                "query": {
                    "term": {
                        "metadata.source_url.keyword": source_url
                    }
                }
            }

        response = self.__client.search(index=self.index_name,
                                        body=query)

        return response['hits']['hits'][0]

    def filtered_vector_search(self,
                               vector_query: list,
                               k:int,
                               filter:list,
                               num_candidates:int = 500):
        # Step 1: Build the metadata filtering query
        vector_query_part = {
                "size": k,  # This specifies how many documents you want to return (top k)
                "query": {
                    "bool": {
                        "filter": filter,
                        #     [
                        #     {"term": {"metadata.property_type.keyword": 'flat'}},
                        #     {"term": {"metadata.rooms": 2}},
                        #     {"range":{"metadata.price_rent":{"lte":1000}}}
                        #     # Add other metadata filters here, for example, 'rooms' and 'price'
                        # ],
                        "should": [
                            {
                                "knn": {
                                    "field": "embedding",  # The field where vectors are stored
                                    "query_vector": vector_query,  # The query vector to search for
                                    "k": k,  # Number of nearest neighbors to return
                                    "num_candidates": num_candidates  # The number of candidates to consider before ranking
                                }
                            }
                        ]
                    }
                }
            }

        # Perform the search with the combined query
        response = self.__client.search(index=self.index_name,
                                        body=vector_query_part)
        return response['hits']['hits']

    def update_metadata_by_url(self,
                               source_url: str,
                               updated_metadata: dict):

        resource = self.get_element(source_url=source_url)
        resource_id = resource["_id"]
        resource_doc = resource["_source"]

        # Step 2: Merge updated metadata
        current_metadata = resource_doc.get("metadata", {})
        current_metadata.update(updated_metadata)

        # Step 3: Update the document in Elasticsearch
        update_body = {
            "doc": {
                "metadata": current_metadata
            }
        }

        self.__client.update(index=self.index_name,
                             id=resource_id, body=update_body)
        print(f"✅ Document with ID {resource_id} updated successfully.")
        return True


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