from pydantic import BaseModel
from typing import Optional
from helpers.config import get_settings
class ConfigUpdateRequest(BaseModel):
    APP_NAME: Optional[str] = get_settings().APP_NAME
    APP_VERSION: Optional[str] = get_settings().APP_VERSION
    FILE_ALLOWED_TYPES: Optional[list[str]] = get_settings().FILE_ALLOWED_TYPES
    FILE_MAX_SIZE: Optional[int] = get_settings().FILE_MAX_SIZE
    FILE_DEFAULT_CHUNK_SIZE: Optional[int] = get_settings().FILE_DEFAULT_CHUNK_SIZE