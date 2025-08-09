from fastapi import APIRouter, HTTPException, Security, Request
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_chain import get_rag_chain
from app.core.security import get_api_key
from app.utils.logger import logger


router = APIRouter(prefix="/query", tags=["Query"])

QUERY_LIMIT = "60/minute"

@router.post("/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):

    try:
        logger.info(f"Received query request: {query_request.question}", extra={"request_id": getattr(request.state, "request_id", "-")})
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
        logger.error(f"Query failed: {str(e)}", extra={"request_id": getattr(request.state, "request_id", "-")})
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        rag_chain = get_rag_chain()
        result = rag_chain.invoke({"query": query_request.question})

        source_docs = result.get("source_documents", [])
        sources = list({doc.metadata.get("source") for doc in source_docs})

        return QueryResponse(
            question=request.question,
            answer=result["result"],
            source_documents=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")