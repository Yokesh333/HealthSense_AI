"""
scripts/rag/05_build_vector_store.py

Build FAISS IndexFlatIP from pre-computed embeddings and save to disk.

Run from project root:
    python scripts/rag/05_build_vector_store.py
"""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.embedder import load_embeddings
from backend.rag.vector_store import build_index, save_index

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    print("Loading embeddings ...")
    embeddings, metadata = load_embeddings()
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Metadata entries: {len(metadata)}")

    print("Building FAISS index (IndexFlatIP) ...")
    index = build_index(embeddings, metadata)

    print("Saving FAISS index ...")
    save_index(index, metadata)

    print(f"\n{'='*50}")
    print(f"FAISS index built successfully")
    print(f"Index type: IndexFlatIP")
    print(f"Vectors: {index.ntotal}")
    print(f"Dimension: {index.d}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
