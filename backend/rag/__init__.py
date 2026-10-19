"""
backend/rag/__init__.py

Public exports for the RAG package.
"""

from backend.rag.schemas import (
    RAGRequest,
    RAGResponse,
    RawDocument,
    RetrievalResult,
    TextChunk,
)
from backend.rag.service import RAGService

__all__ = [
    "RAGService",
    "RawDocument",
    "TextChunk",
    "RetrievalResult",
    "RAGRequest",
    "RAGResponse",
]
