from fastapi import APIRouter, Depends

from src.app.interfaces.api.core.dependencies import validate_auth_data
from src.app.interfaces.api.v1.endpoints.users.schemas.resp_schemas import MeResp
from src.app.domain.users.container import container as services_container

router = APIRouter(prefix="/users")


@router.get(path="/me/", response_model=MeResp, name="users:me")
async def get_users(
    auth_data: dict = Depends(validate_auth_data),
) -> dict:
    user = await services_container.users_service.get_first(filter_data={"uuid": auth_data["uuid"]})
    if user:
        return user.dict()
    return {}
