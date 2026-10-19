"""
scripts/rag/03_create_chunks.py

Read raw extracted pages and produce overlapping text chunks.

Run from project root:
    python scripts/rag/03_create_chunks.py
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.chunker import chunk_documents, CHUNK_SIZE, OVERLAP, MIN_CHUNK
from backend.rag.schemas import RawDocument

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

RAW_DIR = PROJECT_ROOT / "data" / "knowledge_base" / "raw"
CHUNKS_DIR = PROJECT_ROOT / "data" / "knowledge_base" / "chunks"


def main():
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    raw_file = RAW_DIR / "alzheimer_raw_pages.json"
    if not raw_file.exists():
        print(f"ERROR: Raw pages not found at {raw_file}. Run 02_ingest_documents.py first.")
        sys.exit(1)

    with open(raw_file, "r", encoding="utf-8") as f:
        raw_records = json.load(f)

    pages = [RawDocument(**r) for r in raw_records]
    print(f"Loaded {len(pages)} raw pages.")

    chunks = chunk_documents(pages)

    if not chunks:
        print("ERROR: No chunks created.")
        sys.exit(1)

    records = [c.model_dump() for c in chunks]
    output_file = CHUNKS_DIR / "alzheimer_chunks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    # Summary
    sources = set(c.source for c in chunks)
    categories = set(c.category for c in chunks)

    print(f"\n{'='*50}")
    print(f"Chunking config: size={CHUNK_SIZE}, overlap={OVERLAP}, min={MIN_CHUNK}")
    print(f"Source documents: {len(sources)}")
    print(f"Categories: {sorted(categories)}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Output: {output_file}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
