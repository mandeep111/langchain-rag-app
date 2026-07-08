import logging

from sqlalchemy.orm import Session

from app.db.models import DocumentRecord, IngestionJob, utc_now
from app.db.session import SessionLocal
from app.services.document import chunk_text, extract_text
from app.services.vector_store import add_documents_to_vector_store

logger = logging.getLogger(__name__)

SAFE_FAILURE_MESSAGE = "Document ingestion failed. Check server logs for details."


def process_ingestion_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        _process_ingestion_job(db, job_id)
    finally:
        db.close()


def _process_ingestion_job(db: Session, job_id: str) -> None:
    job = db.get(IngestionJob, job_id)
    if job is None:
        logger.error("Ingestion job %s was not found", job_id)
        return

    document = db.get(DocumentRecord, job.document_id)
    if document is None:
        logger.error("Document %s for ingestion job %s was not found", job.document_id, job_id)
        return

    if job.status == "completed":
        logger.info("Ingestion job %s is already completed; skipping", job_id)
        return

    try:
        now = utc_now()
        job.status = "processing"
        job.attempts += 1
        job.started_at = job.started_at or now
        job.error_message = None
        document.status = "processing"
        db.commit()

        text = extract_text(document.storage_path, document.file_extension)
        if not text.strip():
            raise ValueError("No text extracted from the file.")

        chunks = chunk_text(text)
        metadata = {
            "source": document.original_filename,
            "type": document.file_extension,
            "document_id": document.id,
            "ingestion_job_id": job.id,
        }
        add_documents_to_vector_store(chunks, metadata)

        completed_at = utc_now()
        document.status = "completed"
        document.chunk_count = len(chunks)
        job.status = "completed"
        job.completed_at = completed_at
        job.error_message = None
        db.commit()
    except Exception:
        logger.exception("Ingestion job %s failed", job_id)
        db.rollback()
        failed_job = db.get(IngestionJob, job_id)
        failed_document = db.get(DocumentRecord, job.document_id)
        if failed_job is not None:
            failed_job.status = "failed"
            failed_job.error_message = SAFE_FAILURE_MESSAGE
            failed_job.completed_at = utc_now()
        if failed_document is not None:
            failed_document.status = "failed"
        db.commit()
        raise
