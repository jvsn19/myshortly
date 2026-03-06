from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.database import get_db
from app.schemas.url import StatsResponse
from app.services.shortener import get_url_by_code

router = APIRouter()


@router.get("/api/v1/stats/{code}", response_model=StatsResponse)
async def get_stats(
    code: str,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    url = await get_url_by_code(db, code)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    redis_clicks = await redis.get(f"clicks:{code}")
    total_clicks = url.click_count + (int(redis_clicks) if redis_clicks else 0)

    return StatsResponse(
        code=url.code,
        original_url=url.original_url,
        total_clicks=total_clicks,
        created_at=url.created_at,
        expires_at=url.expires_at,
    )
