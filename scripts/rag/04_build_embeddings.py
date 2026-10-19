"""
scripts/rag/04_build_embeddings.py

Encode all text chunks with sentence-transformers and save embeddings + metadata.

Run from project root:
    python scripts/rag/04_build_embeddings.py
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.embedder import embed_chunks, save_embeddings, MODEL_NAME, EMBEDDING_DIM
from backend.rag.schemas import TextChunk

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

CHUNKS_DIR = PROJECT_ROOT / "data" / "knowledge_base" / "chunks"


def main():
    chunks_file = CHUNKS_DIR / "alzheimer_chunks.json"
    if not chunks_file.exists():
        print(f"ERROR: Chunks not found at {chunks_file}. Run 03_create_chunks.py first.")
        sys.exit(1)

    with open(chunks_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    chunks = [TextChunk(**r) for r in records]
    print(f"Loaded {len(chunks)} chunks.")
    print(f"Embedding model: {MODEL_NAME}")
    print(f"Embedding dimension: {EMBEDDING_DIM}")

    embeddings = embed_chunks(chunks)
    save_embeddings(embeddings, chunks, source_chunk_count=len(chunks))

    print(f"\n{'='*50}")
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Model: {MODEL_NAME}")
    print(f"Dimension: {EMBEDDING_DIM}")
    print(f"Chunks embedded: {len(chunks)}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
