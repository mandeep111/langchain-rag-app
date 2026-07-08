import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


@dataclass(frozen=True)
class StoredDocument:
    original_filename: str
    file_extension: str
    file_size: int
    checksum: str
    storage_path: str


class UploadTooLargeError(ValueError):
    pass


class LocalDocumentStorage:
    def __init__(self, base_path: str | None = None, max_size_bytes: int | None = None):
        self.base_path = Path(base_path or settings.DOCUMENT_STORAGE_PATH)
        self.max_size_bytes = max_size_bytes or settings.MAX_UPLOAD_SIZE_BYTES

    async def save(self, file: UploadFile, file_extension: str) -> StoredDocument:
        self.base_path.mkdir(parents=True, exist_ok=True)

        original_filename = os.path.basename(file.filename or f"upload{file_extension}")
        temp_path = self.base_path / f"{uuid.uuid4()}.tmp"
        digest = hashlib.sha256()
        file_size = 0

        with temp_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > self.max_size_bytes:
                    temp_path.unlink(missing_ok=True)
                    raise UploadTooLargeError("Uploaded file exceeds the configured size limit")
                digest.update(chunk)
                destination.write(chunk)

        checksum = digest.hexdigest()
        final_path = self.base_path / f"{uuid.uuid4()}{file_extension}"
        temp_path.replace(final_path)

        return StoredDocument(
            original_filename=original_filename,
            file_extension=file_extension,
            file_size=file_size,
            checksum=checksum,
            storage_path=str(final_path),
        )


def get_document_storage() -> LocalDocumentStorage:
    return LocalDocumentStorage()
