from asyncio import AbstractEventLoop

import pytest

from src.app.config.settings import settings
from src.app.infrastructure.messaging.mq_client import MQClientProxy

MESSAGE_BROKER_URLS = [settings.MESSAGE_BROKER_URL]


@pytest.mark.parametrize("broker_url", MESSAGE_BROKER_URLS, scope="function")
def test_mq_is_healthy_rabbit_mq(e_loop: AbstractEventLoop, broker_url: str) -> None:
    mq_client = MQClientProxy(message_broker_type="rabbitmq", message_broker_url=broker_url)

    is_healthy = e_loop.run_until_complete(mq_client.is_healthy())

    assert is_healthy is True


MESSAGE_BROKER_URLS_FAKE = [settings.MESSAGE_BROKER_URL.replace("dev", "non_dev")]


@pytest.mark.parametrize("broker_url", MESSAGE_BROKER_URLS_FAKE, scope="function")
def test_mq_is_not_healthy_rabbit_mq(e_loop: AbstractEventLoop, broker_url: str) -> None:
    mq_client = MQClientProxy(message_broker_type="rabbitmq", message_broker_url=broker_url)

    is_healthy = e_loop.run_until_complete(mq_client.is_healthy())

    assert is_healthy is not True
