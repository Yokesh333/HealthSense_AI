"""
backend/rag/document_loader.py

Deterministic PDF loader for the HealthSense AI biomedical RAG pipeline.

Rules enforced:
  - Both Alzheimer's and Parkinson's documents are ingested.
  - Documents are explicitly tagged with a `disease` field ('alzheimers' or 'parkinsons').
  - Root-level PDFs are explicitly classified by their filenames.
  - Text is extracted page-by-page using PyMuPDF.
  - Empty pages are skipped.
"""

import logging
import re
from pathlib import Path
from typing import List, Tuple

import fitz  # PyMuPDF

from backend.rag.schemas import RawDocument

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RAG_TRAIN_ROOT = Path(__file__).resolve().parent.parent.parent / "RAG_Train"
ALZHEIMER_DIR = RAG_TRAIN_ROOT / "Alzheimer's"
PARKINSON_DIR = RAG_TRAIN_ROOT / "Parkinsons"

ROOT_FILES = {
    "alzheimer's guidelines.pdf": "alzheimers",
    "A guide to thinking changes in parkinsons.pdf": "parkinsons"
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

def _build_document_id(category: str, filename: str) -> str:
    cat_slug = _slugify(category)
    file_slug = _slugify(Path(filename).stem)
    return f"{cat_slug}__{file_slug}"

def _extract_pdf(
    pdf_path: Path,
    document_id: str,
    disease: str,
    category: str,
) -> Tuple[List[RawDocument], int, int]:
    pages: List[RawDocument] = []
    empty_count = 0
    failed_count = 0

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        logger.error("Failed to open PDF %s: %s", pdf_path.name, exc)
        raise RuntimeError(f"Cannot open PDF '{pdf_path.name}': {exc}") from exc

    for page_num in range(len(doc)):
        try:
            page_text = doc[page_num].get_text("text")
        except Exception as exc:
            logger.warning("Failed to extract page %d from %s: %s", page_num + 1, pdf_path.name, exc)
            failed_count += 1
            continue

        if not page_text or not page_text.strip():
            empty_count += 1
            continue

        pages.append(
            RawDocument(
                document_id=document_id,
                disease=disease,
                source=pdf_path.name,
                category=category,
                page=page_num + 1,
                text=page_text,
            )
        )

    doc.close()
    return pages, empty_count, failed_count

# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def discover_pdfs() -> List[Tuple[Path, str, str]]:
    """
    Recursively discover PDFs and assign disease and category.
    Returns: List of (pdf_path, disease, category)
    """
    found: List[Tuple[Path, str, str]] = []

    # 1. Root level explicit files
    for pdf_path in RAG_TRAIN_ROOT.glob("*.pdf"):
        if pdf_path.name in ROOT_FILES:
            disease = ROOT_FILES[pdf_path.name]
            found.append((pdf_path, disease, f"{disease.capitalize()}/General"))
        else:
            logger.warning("Excluded unidentifiable root-level PDF: %s", pdf_path.name)

    # 2. Alzheimer's directory
    if ALZHEIMER_DIR.exists():
        for pdf_path in sorted(ALZHEIMER_DIR.rglob("*.pdf")):
            rel = pdf_path.relative_to(ALZHEIMER_DIR)
            parts = list(rel.parts)
            sub_cat = parts[0] if len(parts) > 1 else "General"
            found.append((pdf_path, "alzheimers", f"Alzheimers/{sub_cat}"))
    else:
        logger.error("Alzheimer's directory not found: %s", ALZHEIMER_DIR)

    # 3. Parkinson's directory
    if PARKINSON_DIR.exists():
        for pdf_path in sorted(PARKINSON_DIR.rglob("*.pdf")):
            rel = pdf_path.relative_to(PARKINSON_DIR)
            parts = list(rel.parts)
            sub_cat = parts[0] if len(parts) > 1 else "General"
            found.append((pdf_path, "parkinsons", f"Parkinsons/{sub_cat}"))
    else:
        logger.error("Parkinson's directory not found: %s", PARKINSON_DIR)

    return found


def load_documents() -> List[RawDocument]:
    pdf_entries = discover_pdfs()
    all_pages: List[RawDocument] = []
    total_empty = 0
    total_failed = 0

    logger.info("DocumentLoader: discovered %d PDFs.", len(pdf_entries))

    for pdf_path, disease, category in pdf_entries:
        doc_id = _build_document_id(category, pdf_path.name)
        logger.info("Loading: %-50s disease=%s category=%s", pdf_path.name, disease, category)

        pages, empty, failed = _extract_pdf(pdf_path, doc_id, disease, category)
        all_pages.extend(pages)
        total_empty += empty
        total_failed += failed

        logger.info("  → %d pages extracted, %d empty skipped, %d failed.", len(pages), empty, failed)

    logger.info("DocumentLoader: total pages=%d, empty=%d, failed=%d.", len(all_pages), total_empty, total_failed)
    return all_pages
