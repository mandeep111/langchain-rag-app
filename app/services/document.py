# app/services/document.py

import pdfplumber
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings

def extract_text(file_path: str, file_type: str) -> str:
    if file_type == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_type == ".pdf":
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    elif file_type == ".docx":
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file type")

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    return splitter.split_text(text)
