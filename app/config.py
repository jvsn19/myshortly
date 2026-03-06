from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    BASE_URL: str = "http://localhost:8000"
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    ANALYTICS_FLUSH_INTERVAL: int = 60
    CACHE_TTL: int = 3600 # seconds
    model_config = {"env_file": ".env"}


settings = Settings()
