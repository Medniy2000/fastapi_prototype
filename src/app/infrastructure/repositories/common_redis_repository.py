from src.app.infrastructure.extensions.redis_ext.redis_ext import redis_client
from src.app.infrastructure.repositories.base.base_redis_repository import BaseRedisRepository


class CommonRedisRepository(BaseRedisRepository):
    client = redis_client

    @classmethod
    async def is_healthy(cls) -> bool:
        client = cls.get_client()
        result = await client.ping()
        return result
