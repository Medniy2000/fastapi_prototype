from src.app.infrastructure.messaging.mq_client import mq_client
from src.app.infrastructure.repositories.container import container as repo_container
from src.app.application.common.services.base import AbstractBaseApplicationService
from loguru import logger

class CommonApplicationService(AbstractBaseApplicationService):

    @classmethod
    async def is_healthy(cls) -> bool:
        """Checks if app infrastructure is up and healthy."""
        try:
            is_psql_healthy = await repo_container.common_psql_repository.is_healthy()

            is_redis_healthy = await repo_container.common_redis_repository.is_healthy()

            is_message_broker_healthy = await mq_client.is_healthy()

        except Exception as ex:
            logger.error(f"Application is not healthy. Reason: {ex}")
            return False

        return all([is_psql_healthy, is_redis_healthy, is_message_broker_healthy])
