from typing import Callable, List

from src.app.config.settings import settings
from src.app.extensions.mq_ext.clients.kafka_client import KafkaClient
from src.app.extensions.mq_ext.clients.rabbitmq_client import RabbitQueueClientClient


class MQClientProxy:
    _client: KafkaClient | RabbitQueueClientClient
    message_broker_type: str
    SUPPORTED_MESSAGE_BROKERS: dict = {
        "rabbitmq": RabbitQueueClientClient,
        "kafka": KafkaClient
    }
    
    def __init__(self, message_broker_type: str, message_broker_url: str) -> None:
        client_class = self.SUPPORTED_MESSAGE_BROKERS.get(message_broker_type)
        if not client_class:
            raise ValueError(f"Unsupported message broker type: {message_broker_type}")
        self._client = client_class(message_broker_url)
        self.message_broker_type = message_broker_type

    async def produce_messages(
            self,
            exchanger_name: str,  # Exchange name, Topic
            queue_name: str | int,  # Queue name, Partition
            messages: List[dict],
            **kwargs: dict
    ) -> None:
        if self.message_broker_type == "rabbitmq":
            return await self._client.produce_messages(
                exchanger_name=exchanger_name,
                queue_name=queue_name,
                messages=messages,
                kwargs=kwargs
            )
        elif self.message_broker_type == "kafka":
            return await self._client.produce_messages(
                topic=exchanger_name,
                partition=queue_name,
                messages=messages,
                kwargs=kwargs
            )
    
    async def consume(
            self,
            queues: List[str | int],  # Queue's names, Partitions
            exchanger_name: str,  # Exchange name, Topic
            aggregator: Callable,
            handlers_by_event: dict,
            **kwargs: dict
    ):
        if self.message_broker_type == "rabbitmq":
            await self._client.consume(
                queues=queues,
                exchanger_name=exchanger_name,
                aggregator=aggregator,
                handlers_by_event=handlers_by_event
            )
        
        elif self.message_broker_type == "kafka":
            topic_ = exchanger_name
            partitions_ = queues
            await self._client.consume(
                topic=topic_,
                partitions=partitions_,
                aggregator=aggregator,
                handlers_by_event=handlers_by_event,
                kwargs=kwargs
            )


mq_client = MQClientProxy(
    message_broker_type="rabbitmq",
    message_broker_url=settings.MESSAGE_BROKER_URL
)
