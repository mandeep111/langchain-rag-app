import pytest
from starlette.datastructures import UploadFile

from app.services.storage import LocalDocumentStorage, UploadTooLargeError


@pytest.mark.asyncio
async def test_storage_computes_checksum_and_writes_file(tmp_path):
    upload = UploadFile(filename="manual.txt", file=__import__("io").BytesIO(b"hello"))
    storage = LocalDocumentStorage(base_path=str(tmp_path), max_size_bytes=1024)

    stored = await storage.save(upload, ".txt")

    assert stored.original_filename == "manual.txt"
    assert stored.file_extension == ".txt"
    assert stored.file_size == 5
    assert len(stored.checksum) == 64
    assert (tmp_path / stored.storage_path.split("/")[-1]).exists()


@pytest.mark.asyncio
async def test_storage_rejects_files_over_limit(tmp_path):
    upload = UploadFile(filename="manual.txt", file=__import__("io").BytesIO(b"hello"))
    storage = LocalDocumentStorage(base_path=str(tmp_path), max_size_bytes=3)

    with pytest.raises(UploadTooLargeError):
        await storage.save(upload, ".txt")
