from typing import Annotated

from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from src.app.application.container import container as services_container
from src.app.config.settings import settings
from src.app.infrastructure.messaging.mq_client import mq_client
from src.app.interfaces.api.v1.endpoints.debug.schemas.req_schemas import MessageReq

router = APIRouter(prefix="/debug")


MESSAGE_EXAMPLES = {
    "SAY_MEOV": {
        "summary": "Example task to say meow",
        "value": {
            "event": "say_meow",
            "data": {},
        },
    }
}


@router.post("/send-message/", status_code=201)
async def send_message(
    request: Request,
    message: Annotated[
        MessageReq,
        Body(openapi_examples=MESSAGE_EXAMPLES),
    ],
) -> None:
    """
    Sends message to message queue. !!!Only for dev, test environments!!!
    """
    request_body = await request.json()
    message_ = message.dict()  # noqa
    await mq_client.produce_messages(
        messages=[request_body], queue_name=settings.DEFAULT_QUEUE, exchanger_name=settings.DEFAULT_EXCHANGER or ""
    )


@router.get("/health-check/", status_code=200)
async def health_check(
    request: Request,
) -> JSONResponse:
    is_healthy = await services_container.common_service.is_healthy()
    status = "OK" if is_healthy else "NOT OK"
    status_code = HTTP_200_OK if is_healthy else HTTP_400_BAD_REQUEST
    resp = JSONResponse(content={"status": status}, status_code=status_code)

    return resp
