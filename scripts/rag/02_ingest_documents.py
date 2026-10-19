"""
scripts/rag/02_ingest_documents.py

Extract text from all Alzheimer's PDFs and save structured JSON
to data/knowledge_base/raw/.

Run from project root:
    python scripts/rag/02_ingest_documents.py
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.document_loader import load_alzheimer_documents

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

RAW_DIR = PROJECT_ROOT / "data" / "knowledge_base" / "raw"


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Extracting text from Alzheimer's PDFs ...")
    pages = load_alzheimer_documents()

    if not pages:
        print("ERROR: No pages extracted. Check RAG_Train/ directory.")
        sys.exit(1)

    # Serialize
    records = [p.model_dump() for p in pages]
    output_file = RAW_DIR / "alzheimer_raw_pages.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    # Summary
    sources = set(p.source for p in pages)
    categories = set(p.category for p in pages)

    print(f"\n{'='*50}")
    print(f"Documents ingested: {len(sources)}")
    print(f"Categories: {sorted(categories)}")
    print(f"Total pages extracted: {len(pages)}")
    print(f"Output: {output_file}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
