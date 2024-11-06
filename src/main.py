from fastapi import FastAPI
from routes import base_router

app = FastAPI()

app.include_router(base_router)