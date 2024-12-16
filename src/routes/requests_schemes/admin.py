from pydantic import BaseModel, Field, validator
from typing import Optional
from helpers.config import get_settings

class CreateProjectRequest(BaseModel):
    # TODO: Update the Validator 
    project_id: str = Field(..., min_length=1) # to handle empty input

    # @validator('project_id')
    # def validate_project_id(cls, value):
    #     if not value.isalnum():
    #         raise ValueError("Project ID must only contain alphanumeric characters.")
    #     return value

class ConfigUpdateRequest(BaseModel):
    tempreature : float 
    contact_email : str
    contact_phone : str
    file_max_size : float 
    
    