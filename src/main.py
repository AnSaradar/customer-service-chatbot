from fastapi import FastAPI
from routes import base_router, data_router, admin_router, nlp_router
from llm import LLMProviderFactory
from vectordb import VectorDBProviderFactory
from llm.prompt_templates import TemplateParser
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import Settings, get_settings
from controllers import AdminController
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

        is_config_initilized = await AdminController(db_client=app.db_client).initilze_admin_config()
        logger.info(f"Config initialization:{is_config_initilized}")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")

    # =================LLM Initialization=================
    try:
        llm_provider_factory = LLMProviderFactory(settings)

        # Generation Client
        app.generation_client = llm_provider_factory.create(provider = settings.GENERATION_BACKEND)
        app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)
        
        # Embedding Client
        app.embedding_client = llm_provider_factory.create(provider = settings.EMBEDDING_BACKEND)
        app.embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID, embedding_size = settings.EMBEDDING_MODEL_SIZE)

        logger.info(f"LLM Generation Model has beed initialized : {settings.GENERATION_MODEL_ID}")
        logger.info(f"LLM Embedding Model has beed initialized : {settings.EMBEDDING_MODEL_ID}")

    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")

    # =================VectorDB Initialization=================
    try:
        vector_db_provider_factory = VectorDBProviderFactory(settings)

        app.vectordb_client = vector_db_provider_factory.create(provider = settings.VECTORDB_BACKEND)
        app.vectordb_client.connect()

        logger.info("VectorDB provider has been initialized successfully")
    
    except Exception as e:
        logger.error(f"Error initializing VectorDB: {str(e)}")

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
