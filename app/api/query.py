from fastapi import APIRouter, HTTPException, Security, Request
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_chain import get_rag_chain
from app.core.security import get_api_key

router = APIRouter(prefix="/query", tags=["Query"])

QUERY_LIMIT = "60/minute"

@router.post("/", response_model=QueryResponse)
async def query_documents(
    request: Request,  # get request for limiter
    query_request: QueryRequest,
    api_key: str = Security(get_api_key)
):
    limiter = request.app.state.limiter
    # Apply rate limiting programmatically
    await limiter.limit(1)(lambda req: None)(request)  # This raises 429 if limit exceeded

    try:
        rag_chain = get_rag_chain()
        result = rag_chain.invoke({"query": query_request.question})

        source_docs = result.get("source_documents", [])
        sources = list({doc.metadata.get("source") for doc in source_docs})

        return QueryResponse(
            question=query_request.question,
            answer=result["result"],
            source_documents=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
