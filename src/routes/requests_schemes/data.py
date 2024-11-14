from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id : str # file name
    chunk_size : Optional[int] = 500
    overlap_size : Optional[int] = 20
    do_reset : Optional[int] = 0