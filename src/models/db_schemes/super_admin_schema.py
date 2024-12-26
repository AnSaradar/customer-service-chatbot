from pydantic import BaseModel, Field, validator
import re
from bson.objectid import ObjectId
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SuperAdminSchema(BaseModel):
    username: str
    password: str  # Store only the hashed password

    class Config:
        arbitrary_types_allowed = True

    @validator("username")
    def validate_username(cls, value):
        if not value.strip():
            raise ValueError("Username cannot be empty.")
        return value
    
    @validator("password")
    def hash_password(cls, value):
        # Ensure password is hashed before storing
        if not value:
            raise ValueError("Password cannot be empty.")
        return pwd_context.hash(value)
