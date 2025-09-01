import asyncio
import inspect
from typing import Any, Dict

from loguru import logger

from src.app.config.celery import default_queue
from src.app.config.settings import settings
from src.app.infrastructure.tasks.example_task import say_meow
from src.app.extensions.mq_ext.mq_ext import mq_client

HANDLERS_MAP: dict = {"say_meow": {"handler": say_meow, "celery_queue": default_queue}}


async def queue_processing_aggregator(data: dict, handlers_by_event: Dict[str, Dict[str, Any]]) -> None:
    """Calls required trigger handler depend queue message"""

    event = data.get("event") or ""
    event_data = data.get("data", None)

    handler_info = handlers_by_event.get(event, {}) or {}
    handler_func = handler_info.get("handler", None)
    celery_queue = handler_info.get("celery_queue")
    if not handler_func:
        logger.warning(f"Invalid {str(data)}")
        return None
    if celery_queue:
        handler_func.apply_async(queue=celery_queue, kwargs=event_data)
        logger.info(f"Sent {event} execution {handler_func.__name__}")
    elif inspect.isawaitable(handler_func):
        await handler_func(**event_data)  # type: ignore
        logger.info(f"Sent {event} execution {handler_func.__name__}")  # type: ignore
    else:
        logger.warning(f"Can't process {event} with data: {str(data)}")

    return None


if __name__ == "__main__":

    try:
        e_loop = asyncio.get_running_loop()
    except RuntimeError:
        e_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(e_loop)

    try:
        handlers_by_event_ = HANDLERS_MAP
        aggregator_ = queue_processing_aggregator
        e_loop.run_until_complete(
            mq_client.consume(
                queues=[settings.DEFAULT_QUEUE],
                exchanger_name=settings.DEFAULT_EXCHANGER,
                aggregator=aggregator_,
                handlers_by_event=handlers_by_event_,
            )
        )
    except Exception as e:
        logger.warning(f"Error: {str(e)}")
