import json
import datetime as dt
from typing import Callable, List
from loguru import logger
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord, TopicPartition, AIOKafkaClient


class KafkaClient:
    __message_broker_url: str

    __request_timeout_ms = 1000 * 50  # 50 seconds
    __retry_backoff_ms = 1000 * 20  # 10 seconds

    def __init__(self, message_broker_url: str) -> None:
        self.message_broker_url = message_broker_url

    async def is_healthy(self) -> bool:
        client = AIOKafkaClient(bootstrap_servers=self.message_broker_url)
        try:
            await client.bootstrap()
            metadata = await client.fetch_all_metadata()
            # Check if brokers is a method or property
            brokers = metadata.brokers() if callable(metadata.brokers) else metadata.brokers
            return len(brokers) > 0
        except Exception as ex:
            logger.error(f"{ex}")
            return False
        finally:
            await client.close()

    async def produce_messages(self, topic: str, partition: int, messages: List[dict], **kwargs: dict) -> None:
        producer = AIOKafkaProducer(
            bootstrap_servers=self.message_broker_url,
            request_timeout_ms=self.__request_timeout_ms,
            retry_backoff_ms=self.__retry_backoff_ms,
        )
        await producer.start()
        try:
            for message in messages:
                message_ = json.dumps(message, ensure_ascii=False)
                await producer.send_and_wait(
                    topic=topic,
                    partition=partition,
                    timestamp_ms=dt.datetime.now(dt.UTC).timestamp(),
                    value=message_.encode(),
                )
        finally:
            await producer.stop()

    async def __callback(self, message: ConsumerRecord, aggregator: Callable, handlers_by_event: dict) -> None:
        """
        Callback for queue consuming
        Processes received messages via queue
        """
        try:
            message_str = message.value.decode("utf-8")
            message_json = json.loads(message_str) or {}
            await aggregator(message_json, handlers_by_event)
        except Exception as e:  # noqa
            logger.warning(
                f"Got message with incorrect data! {e} " f"[{message.topic}*{message.partition}*{message.offset}]"
            )

    async def consume(
        self, topic: str, partitions: List[int], aggregator: Callable, handlers_by_event: dict, **kwargs: dict
    ) -> None:
        partitions_str = "*".join(str(i) for i in partitions)
        auto_offset_reset = kwargs.get("auto_offset_reset", "latest") or "latest"
        enable_auto_commit = kwargs.get("enable_auto_commit", True)
        consumer = AIOKafkaConsumer(
            group_id=f"GROUP_#_{topic}_#_{partitions_str}",
            bootstrap_servers=self.message_broker_url,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit,
            request_timeout_ms=self.__request_timeout_ms,
            retry_backoff_ms=self.__retry_backoff_ms,
        )
        partitions_ = [TopicPartition(topic, partition) for partition in partitions]
        consumer.assign(partitions_)
        try:
            partitions_str = "*".join(str(queue) for queue in partitions)
            logger.info(f"Partitions {partitions_str}|{topic} consume starting..")
            await consumer.start()
            async for message in consumer:
                await self.__callback(message, aggregator, handlers_by_event)
        finally:
            await consumer.stop()
