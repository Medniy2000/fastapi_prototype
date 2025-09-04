from enum import Enum
from typing import Any, Callable, List, Protocol

from src.app.config.settings import settings
from src.app.infrastructure.messaging.clients.kafka_client import KafkaClient
from src.app.infrastructure.messaging.clients.rabbitmq_client import RabbitQueueClientClient


class MessageBrokerProtocol(Protocol):
    async def produce_messages(self, **kwargs: Any) -> None: ...

    async def consume(self, **kwargs: Any) -> None: ...


class BrokerType(Enum):
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"


class MQClientProxy:
    _client: MessageBrokerProtocol
    message_broker_type: str
    SUPPORTED_MESSAGE_BROKERS: dict = {"rabbitmq": RabbitQueueClientClient, "kafka": KafkaClient}

    def __init__(self, message_broker_type: str, message_broker_url: str) -> None:
        client_class = self.SUPPORTED_MESSAGE_BROKERS.get(message_broker_type)
        if not client_class:
            raise ValueError(f"Unsupported message broker type: {message_broker_type}")
        if not message_broker_url:
            raise ValueError("Value for message_broker_url cannot be empty")
        self._client = client_class(message_broker_url)
        self.message_broker_type = message_broker_type

    async def produce_messages(
        self,
        exchanger_name: str,  # Exchange name, Topic
        queue_name: str | int,  # Queue name, Partition
        messages: List[dict],
        **kwargs: dict,
    ) -> None:
        if self.message_broker_type == BrokerType.RABBITMQ.value:
            return await self._client.produce_messages(
                messages=messages,
                queue_name=queue_name,
                exchanger_name=exchanger_name,
                **kwargs,
            )
        elif self.message_broker_type == BrokerType.KAFKA.value:
            return await self._client.produce_messages(
                topic=exchanger_name,
                partition=queue_name,
                messages=messages,
                **kwargs,
            )
        else:
            raise ValueError(f"Unsupported broker type: {self.message_broker_type}")

    async def consume(
        self,
        queues: List[str | int],  # Queue's names, Partitions
        exchanger_name: str,  # Exchange name, Topic
        aggregator: Callable,
        handlers_by_event: dict,
        **kwargs: dict,
    ) -> None:
        if self.message_broker_type == BrokerType.RABBITMQ.value:
            await self._client.consume(
                queues=queues,
                exchanger_name=exchanger_name,
                aggregator=aggregator,
                handlers_by_event=handlers_by_event,
                **kwargs,
            )
        elif self.message_broker_type == BrokerType.KAFKA.value:
            await self._client.consume(
                topic=exchanger_name,
                partitions=queues,
                aggregator=aggregator,
                handlers_by_event=handlers_by_event,
                **kwargs,
            )
        else:
            raise ValueError(f"Unsupported broker type: {self.message_broker_type}")


mq_client = MQClientProxy(message_broker_type="rabbitmq", message_broker_url=settings.MESSAGE_BROKER_URL or "")
