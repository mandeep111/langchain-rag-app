from app.api import ingest
from app.db.models import DocumentRecord, IngestionJob
from app.services.storage import LocalDocumentStorage


def test_upload_returns_accepted_job_resource(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "enqueue_ingestion_job", lambda job_id: None)
    monkeypatch.setattr(
        ingest,
        "get_document_storage",
        lambda: LocalDocumentStorage(base_path=str(tmp_path), max_size_bytes=1024),
    )

    response = client.post(
        "/documents/upload",
        files={"file": ("manual.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["document_id"]
    assert payload["job_id"]
    assert payload["status"] == "queued"
    assert payload["status_url"].endswith(f"/ingestion-jobs/{payload['job_id']}")

    document = db_session.get(DocumentRecord, payload["document_id"])
    job = db_session.get(IngestionJob, payload["job_id"])
    assert document is not None
    assert document.original_filename == "manual.txt"
    assert document.status == "queued"
    assert job is not None
    assert job.document_id == document.id


def test_upload_rejects_unsupported_file_without_records(client, db_session):
    response = client.post(
        "/documents/upload",
        files={"file": ("manual.exe", b"not allowed", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert db_session.query(DocumentRecord).count() == 0
    assert db_session.query(IngestionJob).count() == 0


def test_document_status_endpoint_returns_latest_job(client, db_session):
    document = DocumentRecord(
        original_filename="manual.txt",
        file_extension=".txt",
        file_size=5,
        checksum="abc123",
        storage_path="/tmp/manual.txt",
        status="queued",
    )
    db_session.add(document)
    db_session.flush()
    job = IngestionJob(document_id=document.id, status="queued")
    db_session.add(job)
    db_session.commit()

    response = client.get(f"/documents/{document.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == document.id
    assert payload["latest_job_id"] == job.id
    assert payload["latest_job_status"] == "queued"


def test_ingestion_job_status_endpoint_returns_safe_shape(client, db_session):
    document = DocumentRecord(
        original_filename="manual.txt",
        file_extension=".txt",
        file_size=5,
        checksum="abc123",
        storage_path="/tmp/manual.txt",
        status="failed",
    )
    db_session.add(document)
    db_session.flush()
    job = IngestionJob(
        document_id=document.id,
        status="failed",
        attempts=1,
        error_message="Document ingestion failed. Check server logs for details.",
    )
    db_session.add(job)
    db_session.commit()

    response = client.get(f"/ingestion-jobs/{job.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == job.id
    assert payload["document_id"] == document.id
    assert payload["status"] == "failed"
    assert payload["chunk_count"] == 0
    assert payload["error_message"] == "Document ingestion failed. Check server logs for details."
