from datetime import datetime

from pydantic import BaseModel


class AsyncUploadResponse(BaseModel):
    document_id: str
    job_id: str
    status: str
    status_url: str


class DocumentStatusResponse(BaseModel):
    id: str
    original_filename: str
    file_extension: str
    file_size: int
    checksum: str
    status: str
    page_count: int | None
    chunk_count: int
    created_at: datetime
    updated_at: datetime
    latest_job_id: str | None = None
    latest_job_status: str | None = None


class IngestionJobResponse(BaseModel):
    id: str
    document_id: str
    status: str
    attempts: int
    error_message: str | None
    chunk_count: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    

class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    source_documents: list[str]  # Metadata from matched docs
