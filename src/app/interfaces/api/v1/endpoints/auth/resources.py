from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Body, Depends

from src.app.application.container import container as app_svc_container
from src.app.interfaces.api.core.dependencies import validate_api_key
from src.app.interfaces.api.v1.endpoints.auth.schemas.req_schemas import SignUpReq
from src.app.interfaces.api.v1.endpoints.auth.schemas.req_schemas import TokenReq
from src.app.interfaces.api.v1.endpoints.auth.schemas.resp_schemas import SignupResp
from src.app.interfaces.api.v1.endpoints.auth.schemas.resp_schemas import TokenResp

router = APIRouter(prefix="/auth")


@router.post(path="/sign-up/", response_model=SignupResp, name="sign-up")
async def sign_up(data: Annotated[SignUpReq, Body()]) -> dict:

    user = await app_svc_container.auth_service.create_auth_user(data=data.model_dump())

    return asdict(user)


@router.post(path="/tokens/", response_model=TokenResp, name="tokens pair")
async def tokens(
    data: TokenReq,
) -> dict:
    """Get new access, refresh tokens [Based on email, password]"""

    user = await app_svc_container.auth_service.get_auth_user_by_phone_number(
        phone_number=data.phone_number, verification_code=data.verification_code
    )

    token_pair = app_svc_container.auth_service.create_tokens_for_user(uuid=str(user.uuid))
    tokens_data = {
        "user_data": {"uuid": str(user.uuid)},
        "access": token_pair.access_token,
        "refresh": token_pair.refresh_token,
    }

    return tokens_data


@router.post(path="/tokens/refresh/", response_model=TokenResp, name="refresh tokens")
async def tokens_refreshed(auth_api_key: str = Depends(validate_api_key)) -> dict:
    """Get new access, refresh tokens [Granted by refresh token in header]"""

    user, token_pair = await app_svc_container.auth_service.refresh_tokens(auth_api_key)
    tokens_data = {
        "user_data": {"uuid": str(getattr(user, "uuid", ""))},
        "access": token_pair.access_token,
        "refresh": token_pair.refresh_token,
    }

    return tokens_data

