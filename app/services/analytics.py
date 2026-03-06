import asyncio
import logging

from redis.asyncio import Redis
from sqlalchemy import update

from app.database import AsyncSessionLocal
from app.models.url import URL

logger = logging.getLogger(__name__)

CLICK_KEY_PREFIX = "clicks:"


async def increment_click(redis: Redis, code: str) -> None:
    await redis.incr(f"{CLICK_KEY_PREFIX}{code}")


async def flush_clicks_to_db() -> None:
    """Drain Redis click counters into PostgreSQL click_count columns."""
    from app.cache import get_redis

    redis = await get_redis()
    keys = await redis.keys(f"{CLICK_KEY_PREFIX}*")
    if not keys:
        return

    async with AsyncSessionLocal() as db:
        for key in keys:
            code = key.removeprefix(CLICK_KEY_PREFIX)
            count = await redis.getdel(key)
            if count:
                await db.execute(
                    update(URL)
                    .where(URL.code == code)
                    .values(click_count=URL.click_count + int(count))
                )
        await db.commit()


async def start_analytics_flush_loop(interval: int = 60) -> None:
    while True:
        await asyncio.sleep(interval)
        try:
            await flush_clicks_to_db()
        except Exception:
            logger.exception("Analytics flush failed")
