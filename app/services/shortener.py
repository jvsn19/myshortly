import secrets
import string
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL

ALPHABET = string.ascii_letters + string.digits  # Base62
CODE_LENGTH = 7


def generate_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


async def create_short_url(
    db: AsyncSession,
    original_url: str,
    expires_at: Optional[datetime] = None,
) -> URL:
    for _ in range(5):
        code = generate_code()
        result = await db.execute(select(URL).where(URL.code == code))
        if not result.scalar_one_or_none():
            break
    else:
        raise RuntimeError("Failed to generate a unique code after 5 attempts")

    url = URL(code=code, original_url=original_url, expires_at=expires_at)
    db.add(url)
    await db.commit()
    await db.refresh(url)
    return url


async def get_url_by_code(db: AsyncSession, code: str) -> URL | None:
    result = await db.execute(select(URL).where(URL.code == code))
    return result.scalar_one_or_none()
