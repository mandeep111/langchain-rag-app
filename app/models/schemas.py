from pydantic import BaseModel

class UploadResponse(BaseModel):
    message: str
    num_chunks: int
    
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    source_documents: list[str]  # Metadata from matched docs
