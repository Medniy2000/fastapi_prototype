import asyncio
import json
from typing import Callable, List

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from aio_pika.channel import Channel
from aio_pika.pool import Pool
from loguru import logger


class RabbitQueueClientClient:
    __message_broker_url: str

    __connection_pool: Pool
    __message_reconnect_timeout: int = 60
    __connections_pool_max_size = 5

    __channel_pool: Pool
    __channel_pool_max_size = 10

    __handlers_by_event: dict
    __aggregator: Callable

    def __init__(self, message_broker_url: str) -> None:
        self.message_broker_url = message_broker_url
        self.__connection_pool: Pool = Pool(self.__get_connection, max_size=self.__connections_pool_max_size)
        self.__channel_pool: Pool = Pool(self.__get_channel, max_size=self.__channel_pool_max_size)

    async def is_healthy(self) -> bool:
        try:
            connection_ = await aio_pika.connect_robust(self.message_broker_url)
            await connection_.close()
            return True
        except Exception as ex:
            logger.error(f"{ex}")
            return False

    async def __get_connection(self) -> AbstractRobustConnection:
        while True:
            try:
                connection_ = await aio_pika.connect_robust(self.message_broker_url)
                break
            except ConnectionError as ex:
                logger.error(f"Connection Error! Reconnect. {ex}")
                await asyncio.sleep(self.__message_reconnect_timeout)
        return connection_

    async def __get_channel(self) -> Channel:
        async with self.__connection_pool.acquire() as connection:
            return await connection.channel()

    async def __callback(self, message: AbstractIncomingMessage) -> None:
        """
        Callback for queue consuming
        Processes received messages via queue
        """
        try:
            async with message.process():
                message_str = message.body.decode("utf-8")
                message_json = json.loads(message_str) or {}
                await self.__aggregator(message_json, self.__handlers_by_event)
        except Exception as e:  # noqa
            logger.warning(f"Got message with incorrect data! {e}")

    async def produce_messages(
        self, messages: List[dict], queue_name: str, exchanger_name: str, **kwargs: dict
    ) -> None:
        exchange_type = kwargs.get("exchange_type", aio_pika.exchange.ExchangeType.DIRECT)
        async with self.__channel_pool.acquire() as channel:
            exchanger_ = await channel.declare_exchange(
                exchanger_name,
                exchange_type,
            )
            for message in messages:
                message_ = json.dumps(message, ensure_ascii=False)
                await exchanger_.publish(aio_pika.Message(body=message_.encode()), routing_key=queue_name)

    async def consume(
        self,
        queues: List[str | int],
        exchanger_name: str,
        aggregator: Callable,
        handlers_by_event: dict,
        **kwargs: dict,
    ) -> None:
        exchange_type = kwargs.get("exchange_type", aio_pika.exchange.ExchangeType.DIRECT.value)

        queues_str = "|".join(str(queue) for queue in queues)
        logger.info(f"Queue {queues_str}|{exchanger_name}|{exchange_type} consume starting..")

        async with self.__channel_pool.acquire() as channel:
            await channel.set_qos(1)
            exchanger = await channel.declare_exchange(
                exchanger_name,
                exchange_type,
            )
            self.__handlers_by_event = handlers_by_event
            self.__aggregator = aggregator

            queues_ = []
            for queue_name in queues:
                queue_ = await channel.declare_queue(
                    queue_name,
                    durable=True,
                    auto_delete=False,
                )
                await queue_.bind(exchanger)
                queues_.append(queue_)

            for i in queues_:
                await i.consume(self.__callback)

            await asyncio.Future()
