from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    chunk_size : Optional[int] = 500
    overlap_size : Optional[int] = 20
    