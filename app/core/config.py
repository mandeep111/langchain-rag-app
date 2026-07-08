import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)  # Let local .env win over stale shell values.


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    DATABASE_URL: str = "postgresql+psycopg://rag:rag@localhost:5432/rag_app"
    REDIS_URL: str = "redis://localhost:6379/0"
    DOCUMENT_STORAGE_PATH: str = "./storage/documents"
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
