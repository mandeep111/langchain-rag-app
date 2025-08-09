from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings

def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )
