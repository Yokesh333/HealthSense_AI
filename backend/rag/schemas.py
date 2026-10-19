"""
backend/rag/schemas.py

Pydantic models for the HealthSense AI biomedical RAG pipeline.

Covers:
  - RawDocument     : output of document_loader (one record per page)
  - TextChunk       : output of chunker (one record per chunk)
  - RetrievalResult : one retrieved chunk with similarity score
  - RAGRequest      : FastAPI request model for POST /api/rag/retrieve
  - RAGResponse     : FastAPI response model
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Pipeline models
# ---------------------------------------------------------------------------

class RawDocument(BaseModel):
    """One page of extracted text from a source PDF."""

    document_id: str = Field(..., description="Deterministic document identifier")
    disease: str = Field(..., description="Disease category (alzheimers or parkinsons)")
    source: str = Field(..., description="Source filename (basename)")
    category: str = Field(..., description="Thematic category, e.g. Alzheimers/Diagnosis")
    page: int = Field(..., description="1-based page number")
    text: str = Field(..., description="Extracted page text (may be empty)")


class TextChunk(BaseModel):
    """One chunk produced by the chunker; retains full provenance metadata."""

    chunk_id: str = Field(..., description="Deterministic chunk identifier")
    document_id: str
    disease: str
    source: str
    category: str
    page: int
    text: str = Field(..., description="Chunk text (≥ min_words words)")


# ---------------------------------------------------------------------------
# Retrieval models
# ---------------------------------------------------------------------------

class RetrievalResult(BaseModel):
    """A single retrieved chunk with its similarity score."""

    chunk_id: str
    disease: str
    source: str
    category: str
    page: int
    score: float = Field(..., description="Cosine similarity score [0, 1]")
    text: str


# ---------------------------------------------------------------------------
# API request / response
# ---------------------------------------------------------------------------

class RAGRequest(BaseModel):
    """Request body for POST /api/rag/retrieve."""

    query: str = Field(..., min_length=1, description="Biomedical query string")
    disease: Optional[str] = Field(None, description="Optional disease filter: 'alzheimers', 'parkinsons', or 'both'")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return (1–20)")

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be blank")
        return v.strip()


class RAGResponse(BaseModel):
    """Response body for POST /api/rag/retrieve."""

    query: str
    results: List[RetrievalResult]
    total_results: int
    clinical_notice: str = (
        "Retrieved biomedical evidence for research purposes; "
        "this is not medical advice."
    )
