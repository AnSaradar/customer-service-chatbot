from fastapi import FastAPI
from routes import base_router, data_router, admin_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import Settings, get_settings
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('uvivorn.error')

@app.on_event("startup")
async def startup():
    settings = get_settings()
    try:
        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
        app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
        logger.info(f"From Main Script: Connected to MongoDB at {settings.MONGODB_URL}")
    except Exception as e:
        logger.error(f"From Main Script: Error connecting to MongoDB: {str(e)}")


@app.on_event("shutdown")
async def shutdown():
    app.mongo_conn.close()



app.include_router(base_router)
app.include_router(data_router)
app.include_router(admin_router)