import redis.asyncio as redis

from app.config import settings

_redis_client: redis.Redis | None = None


async def init_redis() -> None:
    global _redis_client
    _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis() -> None:
    if _redis_client:
        await _redis_client.aclose()


async def get_redis() -> redis.Redis:
    return _redis_client
