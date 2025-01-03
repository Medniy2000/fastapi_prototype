from fastapi import APIRouter


from src.app.api.v1.endpoints.auth.resources import router as auth_router
from src.app.api.v1.endpoints.users.resources import router as users_router
from src.app.api.v1.endpoints.debug.resources import router as debug_router


V1_PREFIX = "v1"

v1_router = APIRouter(prefix=f"/{V1_PREFIX}")


v1_router.include_router(auth_router, tags=[f"{V1_PREFIX}: auth"])
v1_router.include_router(users_router, tags=[f"{V1_PREFIX}: users"])
v1_router.include_router(debug_router, tags=[f"{V1_PREFIX}: debug"])
