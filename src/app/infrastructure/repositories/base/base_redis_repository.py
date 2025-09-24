import json
from typing import Any

import redis.asyncio as redis

from src.app.infrastructure.extensions.redis_ext.redis_ext import redis_client
from src.app.infrastructure.repositories.base.abstract import AbstractRepository


class BaseRedisRepository(AbstractRepository):
    client: redis.Redis = redis_client

    @classmethod
    def get_client(cls) -> redis.Redis:
        return cls.client

    @classmethod
    async def set(cls, key: str, value: dict, expire_in_seconds: int) -> None:
        client = cls.get_client()
        value_ = json.dumps(value, default=str)
        await client.setex(name=key, value=value_, time=expire_in_seconds)

    @classmethod
    async def get(cls, key: str) -> Any:
        client = cls.get_client()
        value_ = await client.get(name=key)
        if value_:
            return json.loads(value_)
        return None

    @classmethod
    async def delete(cls, keys: list) -> Any:
        client = cls.get_client()
        for key in keys:
            await client.delete(key)
        return None

    @classmethod
    async def exists(cls, key: str) -> bool:
        client = cls.get_client()
        return await client.exists(key)

    @classmethod
    async def flush_db(cls) -> None:
        client = cls.get_client()
        await client.flushdb(asynchronous=True)
