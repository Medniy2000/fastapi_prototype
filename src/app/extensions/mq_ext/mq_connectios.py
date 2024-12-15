from asyncio import get_event_loop

import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.channel import Channel
from aio_pika.pool import Pool

from src.app.config.settings import settings


async def get_connection() -> AbstractRobustConnection:
    url = settings.MESSAGE_BROKER_URL
    connection_ = await aio_pika.connect_robust(url)
    return connection_


loop = get_event_loop()

connection_pool: Pool = Pool(get_connection, max_size=2)


async def get_channel() -> Channel:
    async with connection_pool.acquire() as connection:
        return await connection.channel()


channel_pool: Pool = Pool(get_channel, max_size=10)
