from pydantic import BaseModel, Field, validator
from typing import Optional

class RetrievedDocument(BaseModel):
    text : str
    score : float