from llm import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging
class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str, api_url: str = None,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_tempreature: float = 0.3):
        
        self.api_key = api_key
        self.api_url = api_url


        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_tempreature = default_generation_tempreature


        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.api_url if self.api_url and len(self.api_url) else None
        )

        self.enums = OpenAIEnums

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id : str): #So I can change the generation model in Runtime
        self.generation_model_id = model_id
    
    def set_embedding_model(self, model_id : str, embedding_size : int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    
    def generate_text(self, prompt : str, chat_history : list = [], max_output_tokens : int = None,
                      temperature : float = None) -> str:
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None

        if not self.generation_model_id:
            self.logger.error("OpenAI Embedding model not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens

        temperature = temperature if temperature else self.default_generation_tempreature

        chat_history.append(
            self.construct_prompt(prompt = prompt,  role = OpenAIEnums.USER.value)
        )

        response = self.client.chat.completions.create(
          model = self.generation_model_id,
          messages = chat_history,
          max_tokens = max_output_tokens,
          temperature = temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("OpenAI Client : Failed to generate text.")
            return None
        
        return response.choices[0].message
    


    def embed_text(self, text : str, document_type : str = None):

        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Open AI Embedding model not set.")
            return None

        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text,
        )

        if not response or not response.data or len(response.data) == 0 or response.data[0].embedding:
            self.logger.error("Open AI Client : Failed to embed text.")
            return None
        
        return response.data[0].embedding
    

    def construct_prompt(self, prompt : str, role : str):

        return {
            "role" : role,
            "content" : prompt,
        }
    
    def process_text(self, text : str):
        return text[:self.default_input_max_characters].strip()
    
