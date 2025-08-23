from typing import Optional

from fastapi import Query
from pydantic import BaseModel

from src.app.config.settings import settings


class BaseReq(BaseModel):
    pass


class ListReq(BaseReq):
    limit: int = Query(
        default=settings.API_DEFAULT_LIMIT,
        gt=0,
        description="limit value",
        examples=settings.API_LIMIT_ALLOWED_VALUES_LIST,
    )
    offset: int = Query(default=0, ge=0, description="offset value")
    order_by: Optional[str] = Query(default=None, example="id,-created_at")
