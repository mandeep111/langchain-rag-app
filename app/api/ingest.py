# app/api/ingest.py

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UploadResponse
from app.services.document import extract_text, chunk_text

router = APIRouter(prefix="/documents", tags=["Document Ingestion"])

SUPPORTED_EXTENSIONS = [".txt", ".pdf", ".docx"]

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save temporarily
    file_id = str(uuid.uuid4())
    temp_path = f"/tmp/{file_id}{ext}"
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        text = extract_text(temp_path, ext)
        if not text.strip():
            raise ValueError("No text extracted from the file.")

        chunks = chunk_text(text)
        num_chunks = len(chunks)

        return UploadResponse(message="Document processed and chunked", num_chunks=num_chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        os.remove(temp_path)
