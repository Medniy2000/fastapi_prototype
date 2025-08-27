from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Body, Depends

from src.app.interfaces.api.core.dependencies import validate_api_key
from src.app.interfaces.api.core.jwt import JWTHelper
from src.app.interfaces.api.v1.endpoints.auth.schemas.req_schemas import SignUpReq
from src.app.interfaces.api.v1.endpoints.auth.schemas.req_schemas import TokenReq
from src.app.interfaces.api.v1.endpoints.auth.schemas.resp_schemas import SignupResp, TokenResp
from src.app.domain.users.container import container as services_container

router = APIRouter(prefix="/auth")


@router.post(path="/sign-up/", response_model=SignupResp, name="sign-up")
async def sign_up(data: Annotated[SignUpReq, Body()]) -> dict:

    user = await services_container.auth_service.create_auth_user(data=data.model_dump())

    return asdict(user)


@router.post(path="/tokens/", response_model=TokenResp, name="tokens pair")
async def tokens(
    data: TokenReq,
) -> dict:
    """Get new access, refresh tokens [Based on email, password]"""

    user = await services_container.auth_service.get_auth_user(email=data.email, password=data.password)

    new_tokens = await JWTHelper.create_tokens_pair(uuid=str(user.uuid))  # noqa
    tokens_data = {
        "user_data": {"uuid": str(user.uuid)},
        "access": new_tokens["access"],
        "refresh": new_tokens["refresh"],
    }

    return tokens_data


@router.post(path="/tokens/refresh/", response_model=TokenResp, name="refresh tokens")
async def tokens_refreshed(auth_api_key: str = Depends(validate_api_key)) -> dict:
    """Get new access, refresh tokens [Granted by refresh token in header]"""

    refresh_data = await JWTHelper.refresh_auth_data(auth_api_key)
    user = await services_container.users_service.get_first(filter_data={"uuid": refresh_data["uuid"]})
    new_tokens = await JWTHelper.create_tokens_pair(uuid=str(getattr(user, "uuid", "")))
    tokens_data = {
        "user_data": {"uuid": str(getattr(user, "uuid", ""))},
        "access": new_tokens["access"],
        "refresh": new_tokens["refresh"],
    }

    return tokens_data
