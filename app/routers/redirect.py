import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.config import settings
from app.database import get_db
from app.services.analytics import increment_click
from app.services.shortener import get_url_by_code

router = APIRouter()

CACHE_TTL = settings.CACHE_TTL


@router.get("/{code}")
async def redirect(
    code: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    cached = await redis.get(f"url:{code}")
    if cached:
        data: dict = json.loads(cached)
        if data.get("expires_at"):
            expires_at = datetime.fromisoformat(data["expires_at"])
            if expires_at < datetime.now(timezone.utc):
                raise HTTPException(status_code=410, detail="URL has expired")
        await increment_click(redis, code)
        return RedirectResponse(url=data["original_url"], status_code=302)

    url = await get_url_by_code(db, code)

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    if url.expires_at and url.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="URL has expired")

    ttl = CACHE_TTL

    if url.expires_at:
        remaining = (url.expires_at - datetime.now(timezone.utc)).total_seconds()
        ttl = min(CACHE_TTL, max(1, int(remaining)))

    cache_data = {
        "original_url": url.original_url,
        "expires_at": url.expires_at.isoformat() if url.expires_at else None,
    }
    await redis.setex(f"url:{code}", ttl, json.dumps(cache_data))

    await increment_click(redis, code)
    return RedirectResponse(url=url.original_url, status_code=302)
