import time

from redis.asyncio import Redis


async def is_rate_limited(redis: Redis, key: str, limit: int, window: int) -> bool:
    """Sliding window rate limiter backed by a Redis sorted set.

    Each request is stored as a member scored by its timestamp.
    Members older than `window` seconds are pruned before counting.
    """
    now = time.time()
    window_start = now - window

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)
    results = await pipe.execute()

    count = results[2]
    return count > limit
