"""
backend/rag/vector_store.py

FAISS vector store for the HealthSense AI biomedical RAG pipeline.

Index type:
    faiss.IndexFlatIP  (inner product)

Because embeddings are L2-normalised by the embedder, inner product = cosine
similarity, which is what we want for semantic search.

Files on disk:
    data/knowledge_base/vector_store/index.faiss   — FAISS binary index
    data/knowledge_base/vector_store/metadata.json — chunk metadata list
                                                     (row i ↔ chunk i)

IMPORTANT: metadata ordering MUST match FAISS vector ordering.
           build_index() and save_index() both take (embeddings, metadata)
           together to enforce this invariant.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VECTOR_STORE_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "knowledge_base"
    / "vector_store"
)

INDEX_FILE = VECTOR_STORE_DIR / "index.faiss"
METADATA_FILE = VECTOR_STORE_DIR / "metadata.json"


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_index(
    embeddings: np.ndarray,
    metadata: List[Dict],
) -> faiss.IndexFlatIP:
    """
    Create a FAISS IndexFlatIP from a normalised embedding matrix.

    Args:
        embeddings: Float32 array, shape (N, dim), L2-normalised.
        metadata:   List of N dicts; metadata[i] corresponds to embeddings[i].

    Returns:
        Populated FAISS index.

    Raises:
        ValueError if embedding count ≠ metadata count.
    """
    if len(embeddings) != len(metadata):
        raise ValueError(
            f"Embedding count ({len(embeddings)}) ≠ metadata count ({len(metadata)})."
        )

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    logger.info(
        "VectorStore: index built — dim=%d, vectors=%d.", dim, index.ntotal
    )
    return index


# ---------------------------------------------------------------------------
# Persist
# ---------------------------------------------------------------------------

def save_index(
    index: faiss.IndexFlatIP,
    metadata: List[Dict],
) -> None:
    """
    Save FAISS index and chunk metadata to disk.

    metadata[i] must correspond to index vector i.
    """
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_FILE))

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    logger.info(
        "VectorStore: saved index (%d vectors) to %s.",
        index.ntotal,
        VECTOR_STORE_DIR,
    )


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_index() -> Tuple[faiss.IndexFlatIP, List[Dict]]:
    """
    Load the FAISS index and metadata from disk.

    Returns:
        (index, metadata_list)

    Raises:
        FileNotFoundError if the vector store has not been built yet.
    """
    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {INDEX_FILE}. "
            "Run scripts/rag/05_build_vector_store.py first."
        )
    if not METADATA_FILE.exists():
        raise FileNotFoundError(
            f"Vector store metadata not found at {METADATA_FILE}. "
            "Run scripts/rag/05_build_vector_store.py first."
        )

    index = faiss.read_index(str(INDEX_FILE))

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    if index.ntotal != len(metadata):
        raise RuntimeError(
            f"FAISS index has {index.ntotal} vectors but metadata has "
            f"{len(metadata)} entries. The index may be corrupted. "
            "Re-run the ingestion pipeline."
        )

    logger.info(
        "VectorStore: loaded index — vectors=%d, dim=%d.",
        index.ntotal,
        index.d,
    )
    return index, metadata


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def query_index(
    index: faiss.IndexFlatIP,
    metadata: List[Dict],
    query_embedding: np.ndarray,
    top_k: int = 5,
    disease: Optional[str] = None,
) -> List[Dict]:
    """
    Search the FAISS index for the top-k nearest neighbours, optionally filtered by disease.
    """
    # For small indexes, we can retrieve all and filter.
    k = index.ntotal
    scores, indices = index.search(query_embedding, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk_meta = dict(metadata[idx])
        
        # Apply disease filter if provided
        if disease and disease != "both" and chunk_meta.get("disease") != disease:
            continue
            
        chunk_meta["score"] = float(score)
        results.append(chunk_meta)
        
        if len(results) >= top_k:
            break

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def vector_store_exists() -> bool:
    """Return True if the vector store files exist on disk."""
    return INDEX_FILE.exists() and METADATA_FILE.exists()
