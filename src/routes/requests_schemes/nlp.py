from pydantic import BaseModel
from typing import Optional

class IndexProjectRequest(BaseModel):
    project_id : str
    do_reset : Optional[int] = 1


class IndexSearchRequest(BaseModel):
    text : str
    limit : Optional[int] = 5