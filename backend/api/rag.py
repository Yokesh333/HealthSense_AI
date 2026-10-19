"""
backend/api/rag.py

FastAPI router for the biomedical RAG retrieval endpoint.

Route:  POST /api/rag/retrieve

This endpoint performs RETRIEVAL ONLY.
No LLM answer generation occurs here or anywhere else in Phase 6.

Error handling:
  - RAGService not available → HTTP 503
  - Blank query / invalid top_k → HTTP 422 (Pydantic validation)
  - Retrieval failure → HTTP 500 with sanitised message
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from backend.rag.schemas import RAGRequest, RAGResponse, RetrievalResult

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/retrieve", response_model=RAGResponse)
async def retrieve(request: Request, body: RAGRequest) -> RAGResponse:
    """
    Retrieve the most relevant biomedical chunks for a given query.

    Accepts a free-text biomedical query and returns the top-k most
    semantically similar chunks from the Alzheimer's knowledge base.

    This endpoint does NOT generate an answer. It returns source text
    excerpts with similarity scores and full provenance metadata.
    """
    # ------------------------------------------------------------------
    # Get shared RAGService from app.state
    # ------------------------------------------------------------------
    rag_service = getattr(request.app.state, "rag_service", None)

    if rag_service is None:
        logger.error("rag/retrieve: RAGService not found in app.state.")
        raise HTTPException(
            status_code=503,
            detail=(
                "RAG service is unavailable. The knowledge base may not have "
                "been built yet. Run the ingestion pipeline first."
            ),
        )

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------
    logger.info(
        "rag/retrieve: query=%r, top_k=%d", body.query[:80], body.top_k
    )

    try:
        results = rag_service.retrieve(query=body.query, top_k=body.top_k)
    except ValueError as exc:
        # Validation errors (blank query, invalid top_k)
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("rag/retrieve: unexpected error — %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Retrieval failed. Check server logs.",
        )

    # ------------------------------------------------------------------
    # Build response
    # ------------------------------------------------------------------
    return RAGResponse(
        query=body.query,
        results=results,
        total_results=len(results),
    )
