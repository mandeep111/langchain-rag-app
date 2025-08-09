import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Security, Request
from fastapi.responses import JSONResponse
from app.models.schemas import UploadResponse
from app.services.document import extract_text, chunk_text
from app.services.vector_store import add_documents_to_vector_store
from app.core.config import settings
from app.core.security import get_api_key

router = APIRouter(prefix="/documents", tags=["Document Ingestion"])

SUPPORTED_EXTENSIONS = [".txt", ".pdf", ".docx"]

UPLOAD_LIMIT = "10/hour"

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    request: Request,  # get request for limiter
    file: UploadFile = File(...),
    api_key: str = Security(get_api_key)
):
    limiter = request.app.state.limiter
    # Apply rate limiting programmatically
    await limiter.limit(UPLOAD_LIMIT)(lambda req: None)(request)  # Raises 429 if limit exceeded

    ext = os.path.splitext(file.filename)[1]
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_id = str(uuid.uuid4())
    temp_path = f"/tmp/{file_id}{ext}"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        text = extract_text(temp_path, ext)
        if not text.strip():
            raise ValueError("No text extracted from the file.")

        chunks = chunk_text(text)

        metadata = {"source": file.filename, "type": ext}
        add_documents_to_vector_store(chunks, metadata)

        return UploadResponse(message="Document processed and stored", num_chunks=len(chunks))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
