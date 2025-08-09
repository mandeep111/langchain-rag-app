import os
from fastapi import FastAPI
from app.api import ingest, query
from app.core.config import settings

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI(
    title="LangChain RAG API",
    description="Upload documents and query them using LLM",
    version="1.0.0"
)

app.include_router(ingest.router)
app.include_router(query.router)

@app.get("/")
def root():
    return {"message": "RAG API is running!"}
