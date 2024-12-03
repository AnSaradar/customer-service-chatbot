from fastapi import FastAPI
from routes import base_router, data_router, admin_router, nlp_router
from llm import LLMProviderFactory
from vectordb import VectorDBProviderFactory
from llm.prompt_templates import TemplateParser
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import Settings, get_settings
import logging


app = FastAPI()
logging.basicConfig(
    level=logging.INFO,  
    format='%(name)s - %(levelname)s - %(message)s',  # Message format
    datefmt='%Y-%m-%d %H:%M:%S',  
    handlers=[
        logging.StreamHandler(),  # Logs to the console
    ]
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    # App Configurations
    settings = get_settings()

    # Mongo Database Initilization
    try:
        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
        app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")

    # =================LLM Initialization=================
    llm_provider_factory = LLMProviderFactory(settings)

    # Generation Client
    app.generation_client = llm_provider_factory.create(provider = settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)
    
    # Embedding Client
    app.embedding_client = llm_provider_factory.create(provider = settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID, embedding_size = settings.EMBEDDING_MODEL_SIZE)

    # =================VectorDB Initialization=================
    vector_db_provider_factory = VectorDBProviderFactory(settings)

    app.vectordb_client = vector_db_provider_factory.create(provider = settings.VECTORDB_BACKEND)
    app.vectordb_client.connect()

    # =================Template Initialization===================
    app.template_parser = TemplateParser(
        language = settings.PRIMARY_LANGUAGE,
        default_language = settings.DEFAULT_LANGUAGE
    )

    

@app.on_event("shutdown")
async def shutdown():
    app.mongo_conn.close()
    app.vectordb_client.disconnect()



app.include_router(base_router)
app.include_router(data_router)
app.include_router(admin_router)
app.include_router(nlp_router)