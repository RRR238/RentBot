from abc import ABC, abstractmethod

class Vector_DB_interface(ABC):
    @abstractmethod
    def create_index(self,
                     vector_dimension:int):
        pass

    @abstractmethod
    def insert_data(self, documents: list[dict]):
        pass

    @abstractmethod
    def delete_element(self, postgres_id=None, source_url=None):
        pass

    @abstractmethod
    def delete_all_documents(self):
        pass

    @abstractmethod
    def delete_collection(self):
        pass

    @abstractmethod
    def search_similar_documents(self,
                                 query_vector,
                                 k: int = 4):

        pass

    @abstractmethod
    def filtered_vector_search(self,
                               vector_query: list,
                               k:int,
                               filter:list[dict]):


        pass

    @abstractmethod
    def get_element(self,
                    postgres_id=None,
                    source_url=None):

        pass

    @abstractmethod
    def update_metadata_by_url(self,
                               source_url:str,
                               updated_metadata: dict):

        pass