from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from llm.LLMEnums import DocumentTypeEnum
from llm.prompt_templates import TemplateParser
import logging
from typing import List
import time


class NLPController(BaseController):
    # I need the {VectorDB Client, Generation Client, Embedding Client}
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser : TemplateParser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

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
        #self.logger.info(f"Collection name:{collection_name}")
        # step2: manage items
        texts = [ c.chunk_text for c in chunks ]
        metadatas = [ c.chunk_metadata for c in  chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, 
                                             document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        #self.logger.info(f"Vectors:{vectors}")

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
            start_time_for_embedding = time.perf_counter() 
            vector = self.embedding_client.embed_text(
                text = text,
                document_type = DocumentTypeEnum.QUERY.value,
            )
            end_time_for_embedding = time.perf_counter() 

            elapsed_time_for_embedding = end_time_for_embedding - start_time_for_embedding

            self.logger.info(f"Embedding Process completed in {elapsed_time_for_embedding} seconds")
            
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
        

    def answer_rag_question(self, project : Project, question : str, limit : int = 5):

        try:
            retrieved_documents = self.search_in_vectordb_collection(
            project = project,
            text = question,
            limit = limit,
            )

            start_time_for_retrieving_prompts = time.perf_counter()

            if not retrieved_documents or len(retrieved_documents) == 0:
                self.logger.error(f"No documents found for question: {question}")
                return []
            

            system_prompt = self.template_parser.get_template(
                group = "rag",
                key = "system_prompt",
            )
            
            documents_prompt = "\n".join([

                self.template_parser.get_template(
                        group = "rag",
                        key = "document_prompt",
                        vars = {
                            "doc_num": i+1,
                            "chunk_text": document.text,
                        },
                    )

                for i,document in enumerate(retrieved_documents)
            ])  

        

            footer_prompt = self.template_parser.get_template(
                group = "rag",
                key = "footer_prompt",
                vars = {
                    "query" : question
                }
            )
            
            full_prompt = "\n\n".join([documents_prompt,footer_prompt])
            
            chat_history = [
                self.generation_client.construct_prompt(
                    prompt = system_prompt ,
                    role = self.generation_client.enums.SYSTEM.value,
                )
            ]

            end_time_for_retrieving_prompts = time.perf_counter()
            elapsed_time_for_retrieving_prompts = end_time_for_retrieving_prompts - start_time_for_retrieving_prompts

            self.logger.info(f"Retrieving and Generating Prompts completed in {elapsed_time_for_retrieving_prompts} seconds")

            start_time_for_generating = time.perf_counter()
            answer = self.generation_client.generate_text(
                prompt = full_prompt,
                chat_history = chat_history,
            )
            
            end_time_for_generating = time.perf_counter() 

            elapsed_time_for_generating = end_time_for_generating - start_time_for_generating

            self.logger.info(f"Answer Generating Process completed in {elapsed_time_for_generating} seconds")

            if not answer:
                self.logger.error(f"Error generating answer for question: {question}")
                return None, [], None

            return answer, chat_history, full_prompt
        
        except Exception as e:
            self.logger.error(f"Error while answering RAG question: {str(e)}")
            return None, [], None
        
    
    
    




    

    


    

