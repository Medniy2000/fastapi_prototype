from typing import List, Any

from pydantic import BaseModel


class BaseResp(BaseModel):
    pass


class ListResp(BaseResp):
    count: int = 0
    results: List[Any] = []
