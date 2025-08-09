from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from app.services.vector_store import get_vector_store
from app.core.config import settings

def get_rag_chain():
    vector_store = get_vector_store()
    
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    llm = ChatOpenAI(
        temperature=0.2,
        model_name="gpt-3.5-turbo",
        openai_api_key=settings.OPENAI_API_KEY
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain


