from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    project_id: str
    chunk_size : Optional[int] = 500
    overlap_size : Optional[int] = 20
    do_reset : Optional[int] = 1