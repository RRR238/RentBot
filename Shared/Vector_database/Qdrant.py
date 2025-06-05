import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
import uuid
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, FilterSelector, SearchParams, Range, QueryRequest
from Vector_DB_interface import Vector_DB_interface

load_dotenv()

class Vector_DB_Qdrant(Vector_DB_interface):
    def __init__(self,
                 index_name,
                 vector_dimension):
        self.__client = QdrantClient(
                        url=os.getenv('QDRANT_ENDPOINT'),
                        api_key=os.getenv('QDRANT_API_KEY'),
                    )
        self.index_name = index_name
        self.vector_dimension = vector_dimension

    def create_index(self):

        if not self.__client.collection_exists(
            collection_name=self.index_name,
        ):
            self.__client.create_collection(
                collection_name=self.index_name,
                vectors_config=VectorParams(size=self.vector_dimension,
                                            distance=Distance.COSINE)
            )

    def insert_data(self, documents: list[dict]):
        """
        Inserts a list of documents into the Qdrant collection.
        Each document should be a dictionary with 'embedding' and 'metadata' keys.
        """
        points = []
        for doc in documents:
            point = PointStruct(
                id=str(uuid.uuid4()),  # Generate a unique ID for each point
                vector=doc["embedding"],
                payload=doc.get("metadata", {})  # Optional metadata
            )
            points.append(point)

        # Upsert the points into the collection
        response = self.__client.upsert(
            collection_name=self.index_name,
            points=points
        )

        if response.status == "completed":
            print(f"Inserted {len(points)} documents into Qdrant.")
        else:
            print(f"Upsert operation failed with status: {response.status}")

    def delete_element(self, postgres_id=None, source_url=None):
        if not postgres_id and not source_url:
            raise ValueError("You must provide at least postgres_id or source_url.")

        filter_conditions = []
        if postgres_id:
            filter_conditions.append(
                FieldCondition(
                    key="metadata.id",
                    match=MatchValue(value=postgres_id)
                )
            )
        if source_url:
            filter_conditions.append(
                FieldCondition(
                    key="metadata.source_url",
                    match=MatchValue(value=source_url)
                )
            )

        filter = Filter(must=filter_conditions)

        self.__client.delete(
            collection_name=self.index_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=filter
                )
            )
        )

    def delete_all_documents(self):
        response = self.__client.delete(
            collection_name=self.index_name,
            points_selector=FilterSelector(filter=Filter(must=[]))  # Empty filter deletes all points
        )

        print(f"Deleted points from collection '{self.index_name}': {response.result['status']}")

    def delete_collection(self):
        self.__client.delete_collection(collection_name=self.index_name)

    def search_similar_documents(self,
                                 query_vector,
                                 k: int = 4):

        # Perform the search using Qdrant's query method
        response = self.__client.query_points(
            collection_name=self.index_name,
            query=query_vector,
            limit=k,
            search_params=SearchParams(hnsw_ef=500,
                                       exact=False)
        )

        # Return the filtered results
        return response

    def filtered_vector_search(self,
                               vector_query: list,
                               k:int,
                               filter:list[dict]):


        filters = []
        for i in filter:
            if i['type'] == 'term':
                filters.append(FieldCondition(key=i['key'],
                                              match= MatchValue(
                                                  value=i['value']
                                            )
                                        )
                                    )
            elif i['type'] == 'gte':
                filters.append(FieldCondition(key=i['key'],
                                              range=Range(
                                                  gte=i['value']
                                                               )
                                                            )
                                                        )
            else:
                filters.append(FieldCondition(key=i['key'],
                                              range=Range(
                                                  lte=i['value']
                                              )
                                            )
                                        )

        search_query = [QueryRequest(query=vector_query,
                                    filter=Filter(must=filters),
                                     limit=k,
                                     with_payload= True)]

        response = self.__client.query_batch_points(collection_name=self.index_name,
                                                    requests=search_query
                                                    )

        return response

    def get_element(self,
                    postgres_id=None,
                    source_url=None):

        if postgres_id:
            filter = [FieldCondition(key='postgres_id',
                                          match=MatchValue(
                                              value =postgres_id
                                          )
                                          )
                                        ]
        elif source_url:
            filter = [FieldCondition(key='source_url',
                                     match=MatchValue(
                                         value =source_url
                                     )
                                     )
                      ]
        else:
            raise ValueError('one of parameters must be specified')

        search_query = [QueryRequest(
                                     filter=Filter(must=filter),
                                     with_payload=True)]

        response = self.__client.query_batch_points(collection_name=self.index_name,
                                                    requests=search_query
                                                    )

        return response

    def update_metadata_by_url(self,
                               source_url:str,
                               updated_metadata: dict):

        self.__client.set_payload(
            collection_name=self.index_name,
            payload=updated_metadata,
            points=Filter(
                must=[
                    FieldCondition(
                        key="price",
                        match=MatchValue(value=source_url),
                    ),
                ],
            ),
        )
        return True

    def get_all_metadata(self,
                         batch_size: int = 100):
        all_payloads = []
        scroll_offset = None

        while True:
            response = self.__client.scroll(
                collection_name=self.index_name,
                limit=batch_size,
                with_payload=True,
                with_vectors=False,
                offset=scroll_offset
            )

            if not response or not response[0]:
                break

            points_batch, scroll_offset = response
            for point in points_batch:
                all_payloads.append(point.payload)

            if scroll_offset is None:
                break

        return all_payloads