import pytest

from app.db.models import DocumentRecord, IngestionJob
from app.services import ingestion


def test_worker_processes_txt_document(db_session, tmp_path, monkeypatch):
    source = tmp_path / "manual.txt"
    source.write_text("First section.\n\nSecond section.", encoding="utf-8")
    captured = {}
    monkeypatch.setattr(
        ingestion,
        "add_documents_to_vector_store",
        lambda chunks, metadata: captured.update({"chunks": chunks, "metadata": metadata}),
    )

    document = DocumentRecord(
        original_filename="manual.txt",
        file_extension=".txt",
        file_size=source.stat().st_size,
        checksum="abc123",
        storage_path=str(source),
        status="queued",
    )
    db_session.add(document)
    db_session.flush()
    job = IngestionJob(document_id=document.id, status="queued")
    db_session.add(job)
    db_session.commit()

    ingestion._process_ingestion_job(db_session, job.id)

    db_session.refresh(document)
    db_session.refresh(job)
    assert document.status == "completed"
    assert document.chunk_count >= 1
    assert job.status == "completed"
    assert job.attempts == 1
    assert captured["metadata"]["document_id"] == document.id
    assert captured["metadata"]["ingestion_job_id"] == job.id


def test_worker_marks_failures_with_safe_error(db_session, tmp_path, monkeypatch):
    source = tmp_path / "manual.txt"
    source.write_text("content", encoding="utf-8")
    monkeypatch.setattr(ingestion, "extract_text", lambda path, ext: "")

    document = DocumentRecord(
        original_filename="manual.txt",
        file_extension=".txt",
        file_size=source.stat().st_size,
        checksum="abc123",
        storage_path=str(source),
        status="queued",
    )
    db_session.add(document)
    db_session.flush()
    job = IngestionJob(document_id=document.id, status="queued")
    db_session.add(job)
    db_session.commit()

    with pytest.raises(ValueError):
        ingestion._process_ingestion_job(db_session, job.id)

    db_session.refresh(document)
    db_session.refresh(job)
    assert document.status == "failed"
    assert job.status == "failed"
    assert job.error_message == ingestion.SAFE_FAILURE_MESSAGE
