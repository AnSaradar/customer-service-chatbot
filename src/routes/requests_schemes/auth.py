from pydantic import BaseModel, Field, validator
from typing import Optional

class SuperAdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)



class SuperAdminLoginResponse(BaseModel):
    access_token: str
    token_type: str 

