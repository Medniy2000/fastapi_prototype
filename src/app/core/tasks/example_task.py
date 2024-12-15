import asyncio
import random
from typing import Any
from src.app.extensions.celery_ext.celery_app import celery_app


@celery_app.task()
def say_meow(*args, **kwargs) -> Any:
    e_loop = asyncio.get_event_loop()
    e_loop.run_until_complete(asyncio.sleep(random.randint(5, 25)))
    return "meow"
