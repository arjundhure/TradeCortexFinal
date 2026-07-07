from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://tradecortex_user:tradecortex123@localhost/tradecortex"
    redis_url: str = "redis://localhost:6379"
    cache_ttl_seconds: int = 60
    secret_key: str = "30ef96fc9c2c4b5550c81313079d701546b6eeb9e0e04000eae02bd914516863"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    app_name: str = "TradeCortex"
    debug: bool = False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
