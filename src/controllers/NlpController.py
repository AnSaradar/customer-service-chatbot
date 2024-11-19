from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from llm.LLMEnums import DocumentTypeEnum
import logging
from typing import List


class NLPController(BaseController):
    # I need the {VectorDB Client, Generation Client, Embedding Client}
    def __init__(self, vectordb_client, generation_client, embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

        self.logger = logging.getLogger(__name__)
        

    
    def create_collection_name(self, project_id : str): # To standarize the name of the VectorDB collection, each db may have a different naming scheme
        return f"collection_{project_id}".strip()
    

    def reset_vector_db_collection(self, project : Project): # The Project here is a db scheme
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name = collection_name) # Reset the VectorDB collection for the given project
    

    def get_vectordb_collection_info(self, project : Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        try:
            collection_info = self.vectordb_client.get_collection_info(collection_name = collection_name)
            if collection_info is None:
                self.logger.error(f"Error getting {collection_name} info")
                return None
            else:
                self.logger.info(f"Info of {collection_name} retrived successfully")    
                return collection_info
        except Exception as e:
            self.logger.error(f"Error getting {collection_name} info: {str(e)}")
            return None
    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                                   chunks_ids: List[int], 
                                   do_reset: bool = False):
        
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        self.logger.info(f"Collection name:{collection_name}")
        # step2: manage items
        texts = [ c.chunk_text for c in chunks ]
        metadatas = [ c.chunk_metadata for c in  chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, 
                                             document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        self.logger.info(f"Vectors:{vectors}")

        # step3: create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step4: insert into vector db
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadatas=metadatas,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True
    

    def search_in_vectordb_collection(self, project : Project, text : str, limit : int = 5):

        collection_name = self.create_collection_name(project_id=project.project_id)
        
        try:
            # Convert Text to Vector
            vector = self.embedding_client.embed_text(
                text = text,
                document_type = DocumentTypeEnum.QUERY.value,
            )

            #self.logger.info("The Vector is Ready")
            
            if not vector or len(vector) == 0:
                self.logger.error(f"Error embedding text: {text}")
                return []
            
            results = self.vectordb_client.search_by_vector(
                collection_name = collection_name,
                vector = vector,
                limit = limit,
            )

            if not results or len(results) == 0 :
                self.logger.error(f"No results found for text: {text}")
                return []
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error while searching in VectorDB: {str(e)}")
            return []
    
    
    




    

    


    

