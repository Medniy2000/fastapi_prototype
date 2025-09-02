import redis.asyncio as redis

from src.app.config.settings import settings

redis_client = redis.from_url(settings.REDIS_URL)
