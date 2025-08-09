import os
from typing import List
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from app.core.embedding import get_embedding_model

# Path to persist the vector DB
CHROMA_PATH = "chroma_db"

def get_vector_store():
    embedding = get_embedding_model()
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding)

def add_documents_to_vector_store(chunks: List[str], metadata: dict):
    embedding = get_embedding_model()

    documents = [
        Document(page_content=chunk, metadata={**metadata, "chunk_index": i})
        for i, chunk in enumerate(chunks)
    ]

    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding)
    vectorstore.add_documents(documents)
    vectorstore.persist()
