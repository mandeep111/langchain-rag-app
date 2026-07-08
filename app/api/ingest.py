import os
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.queue import enqueue_ingestion_job
from app.db.models import DocumentRecord, IngestionJob
from app.db.session import get_db
from app.models.schemas import AsyncUploadResponse, DocumentStatusResponse
from app.services.storage import UploadTooLargeError, get_document_storage


router = APIRouter(prefix="/documents", tags=["Documents"])

SUPPORTED_EXTENSIONS = [".txt", ".pdf", ".docx"]


@router.post("/upload", response_model=AsyncUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    storage = get_document_storage()

    try:
        stored_document = await storage.save(file, ext)
    except UploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    document = DocumentRecord(
        original_filename=stored_document.original_filename,
        file_extension=stored_document.file_extension,
        file_size=stored_document.file_size,
        checksum=stored_document.checksum,
        storage_path=stored_document.storage_path,
        status="queued",
    )
    db.add(document)
    db.flush()

    ingestion_job = IngestionJob(document_id=document.id, status="queued")
    db.add(ingestion_job)
    db.commit()

    try:
        enqueue_ingestion_job(ingestion_job.id)
    except Exception as exc:
        ingestion_job.status = "failed"
        ingestion_job.error_message = "Failed to enqueue ingestion job."
        document.status = "failed"
        db.commit()
        raise HTTPException(status_code=503, detail="Failed to enqueue ingestion job") from exc

    return AsyncUploadResponse(
        document_id=document.id,
        job_id=ingestion_job.id,
        status=ingestion_job.status,
        status_url=str(request.url_for("get_ingestion_job", job_id=ingestion_job.id)),
    )


@router.get("/{document_id}", response_model=DocumentStatusResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(DocumentRecord, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    latest_job = db.scalars(
        select(IngestionJob)
        .where(IngestionJob.document_id == document.id)
        .order_by(IngestionJob.created_at.desc())
        .limit(1)
    ).first()

    return DocumentStatusResponse(
        id=document.id,
        original_filename=document.original_filename,
        file_extension=document.file_extension,
        file_size=document.file_size,
        checksum=document.checksum,
        status=document.status,
        page_count=document.page_count,
        chunk_count=document.chunk_count,
        created_at=document.created_at,
        updated_at=document.updated_at,
        latest_job_id=latest_job.id if latest_job else None,
        latest_job_status=latest_job.status if latest_job else None,
    )
