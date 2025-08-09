from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

def create_limiter():
    """
    Create a Limiter instance.
    If REDIS_URL is provided, slowapi (via limits) will use Redis for storage.
    For local/simple use, the default in-memory storage will be used.
    """
    if settings.REDIS_URL:
        # storage URI format: "redis://localhost:6379"
        storage_uri = settings.REDIS_URL
        limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri, default_limits=[settings.DEFAULT_RATE_LIMIT])
    else:
        limiter = Limiter(key_func=get_remote_address, default_limits=[settings.DEFAULT_RATE_LIMIT])
    return limiter
