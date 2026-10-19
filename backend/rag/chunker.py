"""
backend/rag/chunker.py

Deterministic word-count-based chunker for the HealthSense AI RAG pipeline.

Configuration:
  CHUNK_SIZE    = 400 words
  OVERLAP       = 80 words
  MIN_CHUNK     = 50 words

Every chunk retains full provenance metadata:
  chunk_id, document_id, source, category, page, text

Chunk IDs are deterministic:
  format: {doc_id}_p{page:04d}_c{chunk_index:04d}

Strategy:
  - Tokenise each page text into words.
  - Slide a window of CHUNK_SIZE words with OVERLAP.
  - Skip chunks shorter than MIN_CHUNK words.
  - A single page can produce multiple chunks.
"""

import logging
from typing import List

from backend.rag.schemas import RawDocument, TextChunk
from backend.rag.text_cleaner import clean_text

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHUNK_SIZE = 400   # words per chunk
OVERLAP = 80       # words of overlap between consecutive chunks
MIN_CHUNK = 50     # minimum words to keep a chunk


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def chunk_document(doc: RawDocument) -> List[TextChunk]:
    """
    Split one RawDocument (one page) into overlapping word-window chunks.

    Args:
        doc: A single extracted page.

    Returns:
        List of TextChunk objects (may be empty if page has < MIN_CHUNK words).
    """
    text = clean_text(doc.text)
    words = text.split()

    if len(words) < MIN_CHUNK:
        return []

    chunks: List[TextChunk] = []
    step = CHUNK_SIZE - OVERLAP
    chunk_index = 0

    start = 0
    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunk_words = words[start:end]

        if len(chunk_words) >= MIN_CHUNK:
            chunk_text = " ".join(chunk_words)
            chunk_id = f"{doc.document_id}_p{doc.page:04d}_c{chunk_index:04d}"
            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    document_id=doc.document_id,
                    disease=doc.disease,
                    source=doc.source,
                    category=doc.category,
                    page=doc.page,
                    text=chunk_text,
                )
            )
            chunk_index += 1

        if end == len(words):
            break

        start += step

    return chunks


def chunk_documents(documents: List[RawDocument]) -> List[TextChunk]:
    """
    Chunk all documents and return a flat list of TextChunk objects.

    Args:
        documents: List of RawDocument objects (one per extracted page).

    Returns:
        Flat list of all TextChunk objects, ordered by document then page.
    """
    all_chunks: List[TextChunk] = []
    skipped_pages = 0

    for doc in documents:
        page_chunks = chunk_document(doc)
        if not page_chunks:
            skipped_pages += 1
        all_chunks.extend(page_chunks)

    logger.info(
        "Chunker: %d chunks created from %d pages (%d pages skipped, < %d words).",
        len(all_chunks),
        len(documents),
        skipped_pages,
        MIN_CHUNK,
    )

    return all_chunks
