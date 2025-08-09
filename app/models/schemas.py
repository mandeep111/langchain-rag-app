from pydantic import BaseModel

class UploadResponse(BaseModel):
    message: str
    num_chunks: int
