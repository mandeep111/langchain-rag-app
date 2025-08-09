from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title="LangChain RAG API",
    description="Upload documents and query them using LLM",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "RAG API is running!"}
