from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    url: HttpUrl
    expires_at: Optional[datetime] = None


class ShortenResponse(BaseModel):
    short_url: str
    code: str
    expires_at: Optional[datetime] = None


class StatsResponse(BaseModel):
    code: str
    original_url: str
    total_clicks: int
    created_at: datetime
    expires_at: Optional[datetime] = None
