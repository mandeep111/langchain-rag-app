from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import IngestionJob
from app.db.session import get_db
from app.models.schemas import IngestionJobResponse

router = APIRouter(prefix="/ingestion-jobs", tags=["Ingestion Jobs"])


@router.get("/{job_id}", response_model=IngestionJobResponse, name="get_ingestion_job")
def get_ingestion_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(IngestionJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Ingestion job not found")

    return IngestionJobResponse(
        id=job.id,
        document_id=job.document_id,
        status=job.status,
        attempts=job.attempts,
        error_message=job.error_message,
        chunk_count=job.document.chunk_count,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
