import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.rate_limiter import create_limiter
from app.api import ingest, query

# Create limiter and FastAPI app
limiter = Limiter(key_func=get_remote_address)


os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI(
    title="LangChain RAG API",
    description="Upload documents and query them using LLM",
    version="1.0.0"
)

# CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# SlowAPI middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Register routers
app.include_router(ingest.router)
app.include_router(query.router)

@app.get("/")
def root():
    return {"message": "RAG API is running!"}

# Rate limit (429) handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."}
    )
