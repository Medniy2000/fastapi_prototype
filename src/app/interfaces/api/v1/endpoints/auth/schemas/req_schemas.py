import re
from typing import Any
from pydantic import field_validator
from src.app.interfaces.api.core.schemas.req_schemas import BaseReq


class TokenReq(BaseReq):
    email: str
    password: str


class SignUpReq(BaseReq):
    email: str
    password: str
