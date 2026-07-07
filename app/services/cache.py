import json
import redis
from app.config import get_settings

settings = get_settings()

_client = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def cache_get(key: str):
    try:
        raw = get_redis().get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def cache_set(key: str, value, ttl: int = None):
    try:
        ttl = ttl or settings.cache_ttl_seconds
        get_redis().setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def cache_delete(key: str):
    try:
        get_redis().delete(key)
    except Exception:
        pass


def stock_cache_key(symbol: str, period: str = "3mo") -> str:
    return f"stock:{symbol.upper()}:{period}" 
