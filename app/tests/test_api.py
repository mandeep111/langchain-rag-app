from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_document_upload_and_query():
    # Upload document
    files = {"file": ("test.txt", b"This is a test RAG document")}
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 200

    # Query the document
    payload = {"query": "What is this document about?"}
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    assert "test" in response.json()["answer"].lower()
