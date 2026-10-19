"""
backend/rag/retriever.py

Semantic retrieval layer for the HealthSense AI biomedical RAG pipeline.

Responsibilities:
  - Accept a query string.
  - Generate a query embedding using the same model used during ingestion.
  - Search the FAISS index.
  - Return ranked RetrievalResult objects.

Error handling:
  - Empty / blank query → ValueError.
  - top_k out of range → ValueError.
  - Vector store unavailable → RuntimeError (caller handles as HTTP 503).
"""

import logging
from typing import List, Optional

import numpy as np

from backend.rag import vector_store as vs
from backend.rag.schemas import RetrievalResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TOP_K = 5
MAX_TOP_K = 20


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class Retriever:
    """
    Semantic retriever backed by a FAISS index and sentence-transformers.

    Intended to be instantiated once and reused (e.g. stored in app.state).
    """

    def __init__(self, index, metadata: list, embedding_model) -> None:
        """
        Args:
            index:           Loaded FAISS IndexFlatIP.
            metadata:        Metadata list aligned with index vectors.
            embedding_model: SentenceTransformer model instance.
        """
        self._index = index
        self._metadata = metadata
        self._model = embedding_model

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        disease: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """
        Run semantic similarity search.

        Args:
            query:   Biomedical query string (must not be blank).
            top_k:   Number of results (1–20).
            disease: Optional disease filter ('alzheimers', 'parkinsons', or 'both').

        Returns:
            List of RetrievalResult sorted by descending score.

        Raises:
            ValueError: for blank query or invalid top_k.
            RuntimeError: if the index is unavailable.
        """
        # ------------------------------------------------------------------
        # Input validation
        # ------------------------------------------------------------------
        query = query.strip()
        if not query:
            raise ValueError("Query must not be empty or blank.")

        if not (1 <= top_k <= MAX_TOP_K):
            raise ValueError(
                f"top_k must be between 1 and {MAX_TOP_K}. Got {top_k}."
            )

        # ------------------------------------------------------------------
        # Embed query
        # ------------------------------------------------------------------
        logger.info("Retriever: encoding query (len=%d chars).", len(query))
        query_embedding = self._model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype(np.float32)  # shape: (1, dim)

        # ------------------------------------------------------------------
        # FAISS search
        # ------------------------------------------------------------------
        raw_results = vs.query_index(
            self._index,
            self._metadata,
            query_embedding,
            top_k=top_k,
            disease=disease,
        )

        # ------------------------------------------------------------------
        # Map to RetrievalResult
        # ------------------------------------------------------------------
        results = [
            RetrievalResult(
                chunk_id=r["chunk_id"],
                disease=r["disease"],
                source=r["source"],
                category=r["category"],
                page=r["page"],
                score=round(r["score"], 6),
                text=r["text"],
            )
            for r in raw_results
        ]

        logger.info(
            "Retriever: query completed — %d results returned.", len(results)
        )
        return results
