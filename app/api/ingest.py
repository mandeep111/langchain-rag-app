import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse
from app.services.document import extract_text, chunk_text
from app.services.vector_store import add_documents_to_vector_store


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

        # ✅ Store in vector DB
        metadata = {
            "source": file.filename,
            "type": ext
        }
        add_documents_to_vector_store(chunks, metadata)

        return UploadResponse(message="Document processed and stored", num_chunks=len(chunks))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        os.remove(temp_path)
