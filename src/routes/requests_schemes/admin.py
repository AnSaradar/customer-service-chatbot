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
    APP_NAME: Optional[str] = get_settings().APP_NAME
    APP_VERSION: Optional[str] = get_settings().APP_VERSION
    FILE_ALLOWED_TYPES: Optional[list[str]] = get_settings().FILE_ALLOWED_TYPES
    FILE_MAX_SIZE: Optional[int] = get_settings().FILE_MAX_SIZE
    FILE_DEFAULT_CHUNK_SIZE: Optional[int] = get_settings().FILE_DEFAULT_CHUNK_SIZE