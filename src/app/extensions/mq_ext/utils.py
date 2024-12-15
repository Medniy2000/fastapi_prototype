import json
from typing import Any

import aio_pika

from src.app.config.settings import settings
from src.app.extensions.mq_ext.mq_connectios import channel_pool


async def produce_messages(
    messages: list,
    queue: str = settings.QUEUE,
) -> None:
    """
    Push messages to queue
    """
    async with channel_pool.acquire() as channel:
        exchanger = await channel.declare_exchange(
            settings.EXCHANGER,
            aio_pika.exchange.ExchangeType.FANOUT,
        )
        for message in messages:
            message_ = json.dumps(message, ensure_ascii=False)
            await exchanger.publish(aio_pika.Message(body=message_.encode()), routing_key=queue)


async def consume_queue(queue_name: str, callback: Any) -> None:
    """
    Consuming new messages in queue
    """
    async with channel_pool.acquire() as channel:
        await channel.set_qos(1)
        exchanger = await channel.declare_exchange(
            settings.EXCHANGER,
            aio_pika.exchange.ExchangeType.FANOUT,
        )
        queue = await channel.declare_queue(
            settings.QUEUE,
            durable=True,
            auto_delete=False,
        )
        await queue.bind(exchanger)
        await queue.consume(callback)
