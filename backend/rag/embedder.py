"""
backend/rag/embedder.py

Sentence-transformers embedding service for the HealthSense AI RAG pipeline.

Model:
    sentence-transformers/all-MiniLM-L6-v2
    Dimension: 384
    Normalisation: L2 (so FAISS inner-product = cosine similarity)

Behaviour:
  - Load model once; do not reload between requests.
  - Encode in batches of BATCH_SIZE.
  - Save embeddings as .npy + metadata as JSON.
  - Load returns (embeddings_array, metadata_list).
  - Do not regenerate if embeddings already exist (checked via manifest).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from backend.rag.schemas import TextChunk

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
BATCH_SIZE = 64

EMBEDDINGS_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "knowledge_base"
    / "embeddings"
)

EMBEDDINGS_FILE = EMBEDDINGS_DIR / "embeddings.npy"
METADATA_FILE = EMBEDDINGS_DIR / "metadata.json"
MANIFEST_FILE = EMBEDDINGS_DIR / "manifest.json"


# ---------------------------------------------------------------------------
# Module-level model cache (lazy; loaded on first use)
# ---------------------------------------------------------------------------

_model = None


def _get_model():
    """Return the cached sentence-transformer model, loading it if needed."""
    global _model
    if _model is None:
        logger.info("Embedder: loading model '%s' ...", MODEL_NAME)
        from sentence_transformers import SentenceTransformer  # noqa: F401
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedder: model loaded (dim=%d).", EMBEDDING_DIM)
    return _model


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def embed_chunks(chunks: List[TextChunk]) -> np.ndarray:
    """
    Encode a list of TextChunks and return a normalised embedding matrix.

    Args:
        chunks: TextChunk objects whose .text will be encoded.

    Returns:
        Float32 numpy array of shape (len(chunks), EMBEDDING_DIM),
        L2-normalised (cosine similarity ≡ inner product).
    """
    model = _get_model()
    texts = [c.text for c in chunks]
    logger.info(
        "Embedder: encoding %d chunks in batches of %d ...",
        len(texts),
        BATCH_SIZE,
    )
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,   # L2 normalise → cosine via dot product
        show_progress_bar=True,
    )
    logger.info("Embedder: encoding complete, shape=%s.", embeddings.shape)
    return embeddings.astype(np.float32)


def save_embeddings(
    embeddings: np.ndarray,
    chunks: List[TextChunk],
    source_chunk_count: Optional[int] = None,
) -> None:
    """
    Persist embeddings and chunk metadata to disk.

    Files written:
      embeddings/embeddings.npy   — raw float32 matrix
      embeddings/metadata.json    — list of chunk dicts (row i ↔ chunk i)
      embeddings/manifest.json    — model info + creation timestamp
    """
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    np.save(str(EMBEDDINGS_FILE), embeddings)

    # Metadata list: row i corresponds to chunk i
    metadata = [c.model_dump() for c in chunks]
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    manifest: Dict = {
        "model_name": MODEL_NAME,
        "embedding_dim": EMBEDDING_DIM,
        "num_chunks": len(chunks),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "source_chunk_count": source_chunk_count or len(chunks),
    }
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info(
        "Embedder: saved %d embeddings to %s.", len(chunks), EMBEDDINGS_DIR
    )


def load_embeddings() -> Tuple[np.ndarray, List[Dict]]:
    """
    Load persisted embeddings and metadata from disk.

    Returns:
        (embeddings, metadata_list) where embeddings[i] corresponds to
        metadata_list[i].

    Raises:
        FileNotFoundError if embeddings have not been built yet.
    """
    if not EMBEDDINGS_FILE.exists() or not METADATA_FILE.exists():
        raise FileNotFoundError(
            f"Embeddings not found at {EMBEDDINGS_DIR}. "
            "Run scripts/rag/04_build_embeddings.py first."
        )

    embeddings = np.load(str(EMBEDDINGS_FILE)).astype(np.float32)
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    logger.info(
        "Embedder: loaded embeddings shape=%s, metadata=%d entries.",
        embeddings.shape,
        len(metadata),
    )
    return embeddings, metadata


def embeddings_exist() -> bool:
    """Return True if pre-built embeddings are available on disk."""
    return EMBEDDINGS_FILE.exists() and METADATA_FILE.exists()
