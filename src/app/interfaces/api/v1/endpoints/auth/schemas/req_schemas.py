from src.app.interfaces.api.core.schemas.req_schemas import BaseReq


class TokenReq(BaseReq):
    email: str
    password: str


class SignUpReq(BaseReq):
    email: str
    password: str
