from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class ProjectSchema(BaseModel):
    # TODO: Add the validator for Project ID 
    id : Optional[ObjectId] = Field(None, alias="_id")  # Mongo Default Key , ObjectId : Bson MongoDB format, this is optional because we get it only in retrive not in insert
    project_id : str = Field(..., min_length=1) # to handle empty input

    # @validator('project_id')
    # def validate_project_id(cls, value):
    #     if not value.isalnum():
    #         raise ValueError("Project ID must only contain alphanumeric characters.")
    #     return value
    
    class Config:
        arbitrary_types_allowed = True # to allow fields in your model to have types that are not built-in Python types or Pydantic-compatible types.