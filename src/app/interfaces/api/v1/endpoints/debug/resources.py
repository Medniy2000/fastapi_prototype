from typing import Annotated, Dict

from fastapi import APIRouter, Body, Request

from src.app.interfaces.api.v1.endpoints.debug.schemas.req_schemas import MessageReq
from src.app.config.settings import settings
from src.app.infrastructure.messaging.mq_client import mq_client

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
) -> Dict[str, str]:
    return {"status": "ok"}
