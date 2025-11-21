from fastapi import Depends
from fastapi.security import HTTPBearer

from src.app.application.container import container as app_svc_container

auth_api_key_schema = HTTPBearer()


async def validate_api_key(auth_api_key: str = Depends(auth_api_key_schema)) -> str:
    auth_api_key_ = str(auth_api_key.credentials).replace("Bearer ", "")  # type: ignore
    return auth_api_key_


async def validate_auth_data(auth_api_key: str = Depends(auth_api_key_schema)) -> dict:
    auth_api_key_ = str(auth_api_key.credentials).replace("Bearer ", "")  # type: ignore
    decoded = app_svc_container.auth_service.verify_access_token(auth_api_key_)
    return decoded.to_dict()