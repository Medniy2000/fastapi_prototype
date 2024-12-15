from typing import Callable

from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from src.app.api.routers import api_router
from src.app.common.log_utils import logging_setup
from src.app.config.settings import settings


def init_app() -> FastAPI:
    logging_setup(settings)

    openapi_url = ""
    if settings.SHOW_API_DOCS:
        openapi_url = f"{settings.API}/openapi.json"
    application = FastAPI(
        title=f"{settings.PROJECT_NAME} 🚀🚀🚀",
        debug=settings.DEBUG,
        openapi_url=openapi_url,
        description=f"API docs for {settings.PROJECT_NAME}",
        version="0.0.1",
        contact={
            "name": "Contact Us",
            "email": settings.TEAM_CONTACT_EMAIL,
        },
    )

    register_middleware(application)
    application.include_router(api_router)
    application.add_event_handler(
        "startup",
        on_startup_app_handler(application),
    )
    application.add_event_handler("shutdown", on_shutdown_handler(application))
    logger.info("App running ...")
    return application


def on_startup_app_handler(
    application: FastAPI,
) -> Callable:  # type: ignore
    async def start_app() -> None:
        pass

    return start_app


def on_shutdown_handler(application: FastAPI) -> Callable:  # type: ignore
    async def stop_app() -> None:
        pass
        # TODO call required functions on stop_app

    return stop_app


def register_middleware(application: FastAPI) -> None:
    if settings.CORS_ORIGIN_WHITELIST:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(item) for item in settings.CORS_ORIGIN_WHITELIST],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


app = init_app()
