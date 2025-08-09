from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_chain import get_rag_chain

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        rag_chain = get_rag_chain()
        result = rag_chain(request.question)

        source_docs = result.get("source_documents", [])
        sources = list({doc.metadata.get("source") for doc in source_docs})

        return QueryResponse(
            question=request.question,
            answer=result["result"],
            source_documents=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
