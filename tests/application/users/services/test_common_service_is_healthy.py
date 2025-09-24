from asyncio import AbstractEventLoop
from typing import Generator, Tuple, Any
from unittest.mock import patch

import pytest

from src.app.application.container import container as service_container


@pytest.fixture
def mock_health_services() -> Generator[Tuple[Any, Any, Any], None, None]:
    with (
        patch(
            "src.app.infrastructure.repositories.common_psql_repository.CommonPSQLRepository.is_healthy"
        ) as mock_psql,
        patch(
            "src.app.infrastructure.repositories.common_redis_repository.CommonRedisRepository.is_healthy"
        ) as mock_redis,
        patch("src.app.infrastructure.messaging.mq_client.mq_client.is_healthy") as mock_mq,
    ):
        yield mock_psql, mock_redis, mock_mq


IS_HEALTHY_CASES = [
    {"psql_val": True, "redis_val": True, "mq_val": True, "expected": True},
    {"psql_val": False, "redis_val": True, "mq_val": True, "expected": False},
    {"psql_val": True, "redis_val": False, "mq_val": True, "expected": False},
    {"psql_val": True, "redis_val": True, "mq_val": False, "expected": False},
    {"psql_val": True, "redis_val": False, "mq_val": False, "expected": False},
    {"psql_val": False, "redis_val": True, "mq_val": False, "expected": False},
]


@pytest.mark.parametrize("data", IS_HEALTHY_CASES, scope="function")
def test_common_service_is_healthy(
    e_loop: AbstractEventLoop, mock_health_services: Tuple[Any, Any, Any], data: dict
) -> None:
    mock_psql, mock_redis, mock_mq = mock_health_services
    expected_val, psql_val, redis_val, mq_val = (
        data["expected"],
        data["psql_val"],
        data["redis_val"],
        data["mq_val"],
    )
    mock_psql.return_value = psql_val
    mock_redis.return_value = redis_val
    mock_mq.return_value = mq_val

    result = e_loop.run_until_complete(service_container.common_service.is_healthy())

    assert result is expected_val


IS_HEALTHY_CASES_FAILED = [
    {"psql_val": True, "redis_val": True, "mq_val": False, "expected": False},
    {"psql_val": True, "redis_val": False, "mq_val": False, "expected": False},
    {"psql_val": False, "redis_val": True, "mq_val": False, "expected": False},
]


@pytest.mark.parametrize("data", IS_HEALTHY_CASES_FAILED, scope="function")
def test_common_service_is_healthy_with_psq_exception(
    e_loop: AbstractEventLoop, mock_health_services: Tuple[Any, Any, Any], data: dict
) -> None:
    mock_psql, mock_redis, mock_mq = mock_health_services
    expected_val, psql_val, redis_val, mq_val = (
        data["expected"],
        data["psql_val"],
        data["redis_val"],
        data["mq_val"],
    )
    mock_psql.return_value = psql_val
    mock_redis.return_value = redis_val
    mock_mq.return_value = mq_val
    mock_psql.side_effect = Exception("Connection failed")

    result = e_loop.run_until_complete(service_container.common_service.is_healthy())

    assert result is expected_val


@pytest.mark.parametrize("data", IS_HEALTHY_CASES_FAILED, scope="function")
def test_common_service_is_healthy_with_mq_exception(
    e_loop: AbstractEventLoop, mock_health_services: Tuple[Any, Any, Any], data: dict
) -> None:
    mock_psql, mock_redis, mock_mq = mock_health_services
    expected_val, psql_val, redis_val, mq_val = (
        data["expected"],
        data["psql_val"],
        data["redis_val"],
        data["mq_val"],
    )
    mock_psql.return_value = psql_val
    mock_redis.return_value = redis_val
    mock_mq.return_value = mq_val
    mock_mq.side_effect = Exception("Connection failed")

    result = e_loop.run_until_complete(service_container.common_service.is_healthy())

    assert result is expected_val


@pytest.mark.parametrize("data", IS_HEALTHY_CASES_FAILED, scope="function")
def test_common_service_is_healthy_with_redis_exception(
    e_loop: AbstractEventLoop, mock_health_services: Tuple[Any, Any, Any], data: dict
) -> None:
    mock_psql, mock_redis, mock_mq = mock_health_services
    expected_val, psql_val, redis_val, mq_val = (
        data["expected"],
        data["psql_val"],
        data["redis_val"],
        data["mq_val"],
    )
    mock_psql.return_value = psql_val
    mock_redis.return_value = redis_val
    mock_mq.return_value = mq_val
    mock_redis.side_effect = Exception("Connection failed")

    result = e_loop.run_until_complete(service_container.common_service.is_healthy())

    assert result is expected_val


def test_common_service_is_healthy_real_infrastructure(e_loop: AbstractEventLoop) -> None:
    result = e_loop.run_until_complete(service_container.common_service.is_healthy())

    assert isinstance(result, bool)
    assert result is True
