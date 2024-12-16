from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class ConfigSchema(BaseModel):
    tempreature : float 
    contact_email : str
    contact_phone : str
    file_max_size : float 

    class Config:
        arbitrary_types_allowed = True

    @validator("tempreature")
    def validate_temperature(cls, value):
        if not (0.0 <= value <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0.")
        return value
    
    @validator("file_max_size")
    def validate_file_max_size(cls, value):
        if value <= 0.0:
            raise ValueError("File max size must be greater than 0.")
        return value
