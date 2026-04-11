import os
import qdrant_client.models
from dotenv import load_dotenv
from qdrant_client import QdrantClient, AsyncQdrantClient

load_dotenv()
from qdrant_client.models import (
    Distance, VectorParams, PayloadSchemaType,
    SparseVector,
    Prefetch, FusionQuery, Fusion,
)
from qdrant_client.http.models import PointStruct
import uuid
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, FilterSelector, SearchParams, Range, QueryRequest
from Shared.Vector_database.Vector_DB_interface import Vector_DB_interface

SPARSE_VECTOR_NAME = "text-sparse"

class Vector_DB_Qdrant(Vector_DB_interface):
    def __init__(self,
                 index_name):
        self.__client = QdrantClient(
                        url=os.getenv('QDRANT_ENDPOINT'),
                        api_key=os.getenv('QDRANT_API_KEY'),
                    )
        self.__async_client = AsyncQdrantClient(
            url=os.getenv('QDRANT_ENDPOINT'),
            api_key=os.getenv('QDRANT_API_KEY'),
        )
        self.index_name = index_name

    def create_index(self,
                     vector_dimension):

        if not self.__client.collection_exists(
            collection_name=self.index_name,
        ):
            self.__client.create_collection(
                collection_name=self.index_name,
                vectors_config=VectorParams(size=vector_dimension,
                                            distance=Distance.COSINE)
            )

    def create_payload_indexes(self, indexes: list[tuple[str, PayloadSchemaType]]) -> None:
        for field_name, schema in indexes:
            self.__client.create_payload_index(
                collection_name=self.index_name,
                field_name=field_name,
                field_schema=schema,
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
            return True
        else:
            return False

    def delete_element(self,
                       postgres_id=None,
                       source_url=None):
        if not postgres_id and not source_url:
            raise ValueError("You must provide at least postgres_id or source_url.")

        filter_conditions = []
        if postgres_id:
            filter_conditions.append(
                FieldCondition(
                    key="id",
                    match=MatchValue(value=postgres_id)
                )
            )
        if source_url:
            filter_conditions.append(
                FieldCondition(
                    key="source_url",
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

    def enriched_filtered_vector_search(self,
                               vector_query: list,
                               k: int,
                               filter_input,
                               score_threshold: float = None,
                               use_hybrid: bool = False,
                               sparse_vector: SparseVector = None):
        # Determine whether the input is already a Filter object
        if isinstance(filter_input, Filter):
            filters = filter_input
        else:
            # Assume it's a list of dicts with simple filtering
            filters = []
            for i in filter_input:
                if i['type'] == 'term':
                    filters.append(
                        FieldCondition(
                            key=i['key'],
                            match=MatchValue(value=i['value'])
                        )
                    )
                elif i['type'] == 'gte':
                    filters.append(
                        FieldCondition(
                            key=i['key'],
                            range=Range(gte=i['value'])
                        )
                    )
                elif i['type'] == 'lte':
                    filters.append(
                        FieldCondition(
                            key=i['key'],
                            range=Range(lte=i['value'])
                        )
                    )
                else:
                    raise ValueError(f"Unknown filter type: {i['type']}")

            filters = Filter(must=filters)

        if use_hybrid and sparse_vector is not None:
            # Hybrid search: dense + sparse via RRF fusion
            prefetch = [
                Prefetch(
                    query=vector_query,
                    using="",          # default dense vector
                    filter=filters,
                    limit=k * 2,
                ),
                Prefetch(
                    query=sparse_vector,
                    using=SPARSE_VECTOR_NAME,
                    filter=filters,
                    limit=k * 2,
                ),
            ]
            # query_points returns a single QueryResponse; wrap in list for consistent API
            response = self.__client.query_points(
                collection_name=self.index_name,
                prefetch=prefetch,
                query=FusionQuery(fusion=Fusion.RRF),
                limit=k,
                with_payload=True,
                score_threshold=score_threshold,
            )
            return [response]
        else:
            # Dense-only search (original behaviour)
            search_query = [
                QueryRequest(
                    query=vector_query,
                    filter=filters,
                    limit=k,
                    with_payload=True,
                    score_threshold=score_threshold,
                )
            ]
            return self.__client.query_batch_points(
                collection_name=self.index_name,
                requests=search_query
            )

    async def filtered_vector_search_async(self,
                                     vector_query: list,
                                     k: int,
                                     filter: list[dict]):
        filters = []
        for i in filter:
            if i['type'] == 'term':
                filters.append(
                    FieldCondition(
                        key=i['key'],
                        match=MatchValue(value=i['value'])
                    )
                )
            elif i['type'] == 'gte':
                filters.append(
                    FieldCondition(
                        key=i['key'],
                        range=Range(gte=i['value'])
                    )
                )
            else:
                filters.append(
                    FieldCondition(
                        key=i['key'],
                        range=Range(lte=i['value'])
                    )
                )

        search_query = [
            QueryRequest(
                query=vector_query,
                filter=Filter(must=filters),
                limit=k,
                with_payload=True
            )
        ]

        response = await self.__async_client.query_batch_points(
            collection_name=self.index_name,
            requests=search_query
        )

        return response

    from qdrant_client.models import Filter, FieldCondition, MatchValue, Range, QueryRequest

    async def enriched_filtered_vector_search_async(self,
                                                   vector_query: list,
                                                   k: int,
                                                   filter_input,
                                                   use_hybrid: bool = False,
                                                   sparse_vector: SparseVector = None):
        # If already a Filter (i.e., from prepare_multiple_filters_qdrant)
        if isinstance(filter_input, Filter):
            filters = filter_input
        else:
            # Assume it's a list of dicts
            filters = []
            for i in filter_input:
                if i['type'] == 'term':
                    filters.append(
                        FieldCondition(
                            key=i['key'],
                            match=MatchValue(value=i['value'])
                        )
                    )
                elif i['type'] == 'gte':
                    filters.append(
                        FieldCondition(
                            key=i['key'],
                            range=Range(gte=i['value'])
                        )
                    )
                elif i['type'] == 'lte':
                    filters.append(
                        FieldCondition(
                            key=i['key'],
                            range=Range(lte=i['value'])
                        )
                    )
                else:
                    raise ValueError(f"Unknown filter type: {i['type']}")

            filters = Filter(must=filters)

        if use_hybrid and sparse_vector is not None:
            prefetch = [
                Prefetch(
                    query=vector_query,
                    using="",
                    filter=filters,
                    limit=k * 2,
                ),
                Prefetch(
                    query=sparse_vector,
                    using=SPARSE_VECTOR_NAME,
                    filter=filters,
                    limit=k * 2,
                ),
            ]
            response = await self.__async_client.query_points(
                collection_name=self.index_name,
                prefetch=prefetch,
                query=FusionQuery(fusion=Fusion.RRF),
                limit=k,
                with_payload=True,
            )
            return [response]
        else:
            search_query = [
                QueryRequest(
                    query=vector_query,
                    filter=filters,
                    limit=k,
                    with_payload=True
                )
            ]
            return await self.__async_client.query_batch_points(
                collection_name=self.index_name,
                requests=search_query
            )

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
                        key="source_url",
                        match=MatchValue(value=source_url),
                    ),
                ],
            ),
        )
        return True

    def delete_by_qdrant_id(self, qdrant_id: str) -> None:
        self.__client.delete(
            collection_name=self.index_name,
            points_selector=qdrant_client.models.PointIdsList(points=[qdrant_id]),
        )

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
                all_payloads.append({"qdrant_id": point.id, **point.payload})

            if scroll_offset is None:
                break

        return all_payloads