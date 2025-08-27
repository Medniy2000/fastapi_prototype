from fastapi import APIRouter

from src.app.interfaces.api.v1.routers import v1_router

api_router = APIRouter(prefix="/api")


api_router.include_router(v1_router)
