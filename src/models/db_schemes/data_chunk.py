from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunkSchema(BaseModel):
    id : Optional[ObjectId] = Field(None, alias="_id")
    chunk_text : str = Field(..., min_length=1)
    chunk_metadata : dict
    chunk_order : int = Field(..., gt=0)
    chunk_project_id : ObjectId # Project Mongo DB ID 

    class Config:
        arbitrary_types_allowed = True # to allow fields in your model to have types that are not built-in Python types or Pydantic-compatible types.