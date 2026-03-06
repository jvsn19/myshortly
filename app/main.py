import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.cache import close_redis, init_redis
from app.config import settings
from app.database import Base, engine
from app.models.url import URL  # noqa: F401 — ensures model is registered
from app.routers import redirect, shorten, stats
from app.services.analytics import start_analytics_flush_loop

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    flush_task = asyncio.create_task(
        start_analytics_flush_loop(settings.ANALYTICS_FLUSH_INTERVAL)
    )

    yield

    flush_task.cancel()
    try:
        await flush_task
    except asyncio.CancelledError:
        pass

    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="myshortly",
    description="Production-grade URL shortener",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(shorten.router)
app.include_router(stats.router)
app.include_router(redirect.router)  # catch-all /{code} must be last
