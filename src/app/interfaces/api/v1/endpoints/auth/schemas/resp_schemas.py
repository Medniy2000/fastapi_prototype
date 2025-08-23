from typing import Optional

from src.app.interfaces.api.core.schemas.resp_schemas import BaseResp


class UserDataResp(BaseResp):
    uuid: str


class TokenResp(BaseResp):
    user_data: UserDataResp
    access: str
    refresh: str


class SignupResp(BaseResp):
    uuid: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
