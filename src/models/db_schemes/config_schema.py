from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
import re

class ConfigSchema(BaseModel):
    temperature : float 
    contact_email : str
    contact_phone : str
    file_max_size : float 

    class Config:
        arbitrary_types_allowed = True

    @validator("temperature")
    def validate_temperature(cls, value):
        if not (0.0 <= value <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0.")
        return value
    
    @validator("file_max_size")
    def validate_file_max_size(cls, value):
        if value <= 0.0:
            raise ValueError("File max size must be greater than 0.")
        return value
    
    @validator("contact_phone")
    def validate_phone_number(cls, value):
        # Regular expression for E.164 phone number format
        e164_regex = re.compile(r"^\+?[1-9]\d{1,14}$")
        if not e164_regex.match(value):
            raise ValueError("Invalid phone number format. Must be in E.164 format (e.g., +1234567890).")
        return value
    
    @validator('contact_email')
    def validate_email(cls, value):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise ValueError('Invalid email format')
        return value
