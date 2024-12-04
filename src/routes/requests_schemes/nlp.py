from pydantic import BaseModel
from typing import Optional

class IndexProjectRequest(BaseModel):
    project_id : str
    do_reset : Optional[int] = 1


class InfoProjectRequest(BaseModel):
    project_id : str


class IndexSearchRequest(BaseModel):
    # TODO: Add Chat history, and creativity factor (Temprature)
    project_id : str
    text : str
    limit : Optional[int] = 5