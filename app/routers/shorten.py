from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.config import settings
from app.database import get_db
from app.schemas.url import ShortenRequest, ShortenResponse
from app.services.rate_limiter import is_rate_limited
from app.services.shortener import create_short_url

router = APIRouter()


@router.post("/api/v1/shorten", response_model=ShortenResponse)
async def shorten_url(
    request: Request,
    body: ShortenRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    client_ip = request.client.host
    if await is_rate_limited(
        redis,
        f"rate:{client_ip}",
        settings.RATE_LIMIT_REQUESTS,
        settings.RATE_LIMIT_WINDOW,
    ):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    url = await create_short_url(db, str(body.url), body.expires_at)

    return ShortenResponse(
        short_url=f"{settings.BASE_URL}/{url.code}",
        code=url.code,
        expires_at=url.expires_at,
    )
