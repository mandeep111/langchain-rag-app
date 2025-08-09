import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api import ingest, query
from app.core.middleware import RequestLoggingMiddleware  # Assuming custom middleware
from app.core.exceptions import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

# Disable Huggingface tokenizer parallelism to avoid deadlocks
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize rate limiter with client IP as key
limiter = Limiter(key_func=get_remote_address)

def create_app() -> FastAPI:
    app = FastAPI(
        title="LangChain RAG API",
        description="Upload documents and query them using LLM",
        version="1.0.0"
    )

    # CORS setup if configured
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add custom request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Add SlowAPI rate limiting middleware
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # Register routers
    app.include_router(ingest.router)
    app.include_router(query.router)

    # Exception handlers
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    app.add_exception_handler(
        RequestValidationError := __import__("fastapi.exceptions", fromlist=["RequestValidationError"]).RequestValidationError,
        validation_exception_handler
    )

    # Root health check endpoint
    @app.get("/")
    async def root():
        return {"message": "RAG API is running!"}

    return app


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."}
    )


app = create_app()
