from asyncio import AbstractEventLoop

import pytest

from src.app.infrastructure.messaging.mq_client import MQClientProxy

MESSAGE_BROKER_URLS = ["x_test_kafka_service:29092"]


@pytest.mark.parametrize("broker_url", MESSAGE_BROKER_URLS, scope="function")
def test_mq_is_healthy_kafka(e_loop: AbstractEventLoop, broker_url: str) -> None:
    mq_client = MQClientProxy(message_broker_type="kafka", message_broker_url=broker_url)

    is_healthy = e_loop.run_until_complete(mq_client.is_healthy())

    assert is_healthy is True


MESSAGE_BROKER_URLS_FAKE = ["x_test_kafka_service:29092".replace("92", "99")]


@pytest.mark.parametrize("broker_url", MESSAGE_BROKER_URLS_FAKE, scope="function")
def test_mq_is_not_healthy_kafka(e_loop: AbstractEventLoop, broker_url: str) -> None:
    mq_client = MQClientProxy(message_broker_type="kafka", message_broker_url=broker_url)

    is_healthy = e_loop.run_until_complete(mq_client.is_healthy())

    assert is_healthy is not True
