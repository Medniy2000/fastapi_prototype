import traceback
import uuid
from typing import Any, Dict

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from src.app.config.settings import settings
from src.app.domain.common.exceptions import (
    ValidationError,
    NotFoundError,
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    AppException,
)
from src.app.interfaces.cli.main import app


def _gen_error_id() -> str:
    return str(uuid.uuid4().hex)


def _create_error_resp(exc: AppException, status_code: int) -> JSONResponse:
    """Create standardized error response"""
    extra_ = exc.extra or {}
    content: Dict[str, Any] = {
        "error_id": _gen_error_id(),
        "message": exc.message,
        "details": [],
        "traceback": None,
    }
    if settings.DEBUG:
        details = exc.details or []
        content["details"] = details
        content["traceback"] = traceback.format_exc()

    kwargs: Dict[str, Any] = {"status_code": status_code, "content": content}
    headers = extra_.get("headers", {}) or {}
    if headers:
        kwargs["headers"] = headers

    return JSONResponse(**kwargs)


# ==========================================
# Custom Exceptions
# ==========================================
@app.exception_handler(ValidationError)
async def exception_handler_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    return _create_error_resp(exc, status.HTTP_422_UNPROCESSABLE_TYPE)


@app.exception_handler(NotFoundError)
async def exception_handler_notfound_error(request: Request, exc: NotFoundError) -> JSONResponse:
    return _create_error_resp(exc, status.HTTP_422_UNPROCESSABLE_TYPE)


@app.exception_handler(AlreadyExistsError)
async def exception_handler_already_exists_error(request: Request, exc: AlreadyExistsError) -> JSONResponse:
    return _create_error_resp(exc, status.HTTP_422_UNPROCESSABLE_TYPE)


@app.exception_handler(AuthenticationError)
async def exception_handler_authentication_error(request: Request, exc: AuthenticationError) -> JSONResponse:
    return _create_error_resp(exc, status.HTTP_401_UNAUTHORIZED)


@app.exception_handler(AuthorizationError)
async def exception_handler_authorization_error(request: Request, exc: AuthorizationError) -> JSONResponse:
    return _create_error_resp(exc, status.HTTP_403_FORBIDDEN)


# ==========================================
# FastAPI Exceptions
# ==========================================
@app.exception_handler(RequestValidationError)
async def exception_handler_fastapi_request_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    error_id = _gen_error_id()

    content: Dict[str, Any] = {
        "error_id": error_id,
        "message": str(exc),
        "details": [],
        "traceback": None,
    }

    kwargs: Dict[str, Any] = {"status_code": status.HTTP_422_UNPROCESSABLE_TYPE, "content": content}

    return JSONResponse(**kwargs)


@app.exception_handler(HTTPException)
async def exception_handler_fastapi_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    error_id = _gen_error_id()

    content: Dict[str, Any] = {
        "error_id": error_id,
        "message": str(exc.detail),
        "details": [],
        "traceback": None,
    }
    if settings.DEBUG and exc.status_code >= 500:
        content["traceback"] = traceback.format_exc()

        logger.error(
            f"Unhandled exception [ID: {error_id}]",
            extra={
                "error_id": error_id,
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            },
            exc_info=exc,
        )

    kwargs: Dict[str, Any] = {"status_code": exc.status_code, "content": content}

    return JSONResponse(**kwargs)


# ==========================================
# Generic Exceptions
# ==========================================
@app.exception_handler(Exception)
async def exception_handler_unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    error_id = _gen_error_id()
    logger.error(
        f"Unhandled exception [ID: {error_id}]",
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        },
        exc_info=exc,
    )

    content: Dict[str, Any] = {
        "error_id": error_id,
        "message": "An internal error occurred. Please contact support.",
        "details": [],
        "traceback": None,
    }
    if settings.DEBUG:
        content["message"] = str(exc)
        content["traceback"] = traceback.format_exc()

    kwargs: Dict[str, Any] = {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "content": content}

    return JSONResponse(**kwargs)
