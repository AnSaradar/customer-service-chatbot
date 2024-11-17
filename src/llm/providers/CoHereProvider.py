from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging
class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_tempreature: float = 0.3):
        
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_tempreature = default_generation_tempreature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.CohereClient(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)
    

    def set_generation_model(self, model_id : str):
        self.generation_model = model_id

    def set_embedding_model(self, model_id : str, embedding_size : int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def generate_text(self, prompt : str, chat_history : list = [], max_output_tokens : int = None,
                      temperature : float = None) -> str:

        if not self.client:
            self.logger.error("CoHere client not initialized.")
            return None

        if not self.generation_model_id:
            self.logger.error("CoHere Embedding model not set")
            return None
        

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens

        temperature = temperature if temperature else self.default_generation_tempreature
        
        response  = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.construct_prompt(prompt = prompt, role = CoHereEnums.USER.value),
            temperature = temperature,
            max_tokens = max_output_tokens
        )

        if not response or response.text:
            self.logger.error("CoHere Client : Failed to generate text.")
            return None

        return response.text



    def embed_text(self, text : str, document_type : str = None):

        if not self.client:
            self.logger.error("CoHere client not initialized.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("CoHere Embedding model not set.")
            return None
        
        input_type = CoHereEnums.DOCUMENT.value 
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CoHereEnums.QUERY.value

        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types = [float],

        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message["content"]:
            self.logger.error("CoHere Client : Failed to embed text.")
            return None

        return response.choices[0].message["content"]
        


    def construct_prompt(self, prompt : str, role : str):
        return {
            "role" : role,
            "content" : self.process_text(text = prompt),
        }

    def process_text(self, text : str):
        return text[:self.default_input_max_characters].strip()


