import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
    DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "60/minute")
    REDIS_URL = os.getenv("REDIS_URL", "")
    API_KEYS = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]


settings = Settings()
