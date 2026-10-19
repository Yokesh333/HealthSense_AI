"""
backend/rag/service.py

RAGService — the single component that the FastAPI application interacts with.

Responsibilities:
  1. Load the sentence-transformers model ONCE at startup.
  2. Load the FAISS index and metadata ONCE at startup.
  3. Expose a retrieve(query, top_k) method.

The FastAPI lifespan handler calls RAGService() once and stores the instance
in app.state.rag_service. Subsequent requests reuse the same object.

The service is also designed to be usable by the Multi-Agent orchestrator
in a future phase (the Orchestrator can receive it via dependency injection,
just like the ADNIPredictor).
"""

import logging
from typing import List

from backend.rag import vector_store as vs
from backend.rag.retriever import Retriever
from backend.rag.schemas import RetrievalResult

logger = logging.getLogger(__name__)


class RAGService:
    """
    Singleton service for biomedical semantic retrieval.

    Usage:
        service = RAGService()   # loads models + index
        results = service.retrieve("What is Alzheimer's disease?", top_k=5)
    """

    def __init__(self) -> None:
        logger.info("RAGService: initialising ...")

        # ------------------------------------------------------------------
        # Load FAISS index + metadata
        # ------------------------------------------------------------------
        logger.info("RAGService: loading FAISS index ...")
        index, metadata = vs.load_index()
        self._index = index
        self._metadata = metadata
        logger.info(
            "RAGService: index loaded — %d vectors, dim=%d.",
            index.ntotal,
            index.d,
        )

        # ------------------------------------------------------------------
        # Load embedding model (sentence-transformers)
        # ------------------------------------------------------------------
        logger.info("RAGService: loading embedding model ...")
        import os
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        from sentence_transformers import SentenceTransformer
        from backend.rag.embedder import MODEL_NAME
        self._model = SentenceTransformer(MODEL_NAME)
        logger.info("RAGService: embedding model loaded.")

        # ------------------------------------------------------------------
        # Build retriever
        # ------------------------------------------------------------------
        self._retriever = Retriever(
            index=self._index,
            metadata=self._metadata,
            embedding_model=self._model,
        )

        logger.info(
            "RAGService: ready — %d indexed chunks.", index.ntotal
        )

    def retrieve(self, query: str, top_k: int = 5, disease: str = None) -> List[RetrievalResult]:
        """
        Perform semantic retrieval against the biomedical knowledge base.

        Args:
            query:   Biomedical query string.
            top_k:   Number of results (1–20).
            disease: Optional disease filter ('alzheimers', 'parkinsons', or 'both').

        Returns:
            List of RetrievalResult objects sorted by descending similarity.

        Raises:
            ValueError:   for blank query or invalid top_k.
            RuntimeError: if the underlying service is unavailable.
        """
        return self._retriever.retrieve(query=query, top_k=top_k, disease=disease)

    @property
    def num_chunks(self) -> int:
        """Total number of indexed chunks."""
        return self._index.ntotal
