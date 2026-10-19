"""
tests/test_rag.py

Phase 6 — Biomedical RAG pipeline test suite.

Tests cover:
  1.  RAG schemas validate correctly
  2.  Empty query rejected by schema
  3.  Invalid top_k rejected by schema
  4.  Text cleaner normalises whitespace
  5.  Chunker respects chunk size / overlap / minimum
  6.  Chunk metadata is preserved
  7.  Embedding dimension is 384
  8.  Vector store save/load roundtrip
  9.  Retriever returns descending scores
  10. RAG API /api/rag/retrieve returns correct structure
  11. Only Alzheimer's documents in the index (no Parkinson's)
  12. Existing /health still works
  13. Existing /api/adni/predict still works
  14. Existing /api/agents/analyze still works
"""

import json
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock

from backend.rag.schemas import (
    RAGRequest,
    RAGResponse,
    RawDocument,
    RetrievalResult,
    TextChunk,
)
from backend.rag.text_cleaner import clean_text
from backend.rag.chunker import chunk_document, CHUNK_SIZE, OVERLAP, MIN_CHUNK


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "knowledge_base" / "chunks" / "alzheimer_chunks.json"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "knowledge_base" / "vector_store"

VALID_ADNI_PAYLOAD = {
    "AGE": 72,
    "EDUCATION": 16,
    "ADAS": 12.0,
    "CDR": 0.5,
    "FAQ": 5.0,
    "MMSE": 25.0,
    "MOCA": 21.0,
    "SEX": "Male",
    "RACE": "White",
    "ETHNICITY": "Not Hispanic or Latino",
}


# ---------------------------------------------------------------------------
# Test 1: Schema validation
# ---------------------------------------------------------------------------

def test_rag_schemas_validate():
    """RawDocument, TextChunk, RetrievalResult schemas accept valid data."""
    doc = RawDocument(
        document_id="test_doc",
        source="test.pdf",
        category="Alzheimers/Diagnosis",
        page=1,
        text="Sample biomedical text.",
        disease="alzheimers"
    )
    assert doc.document_id == "test_doc"

    chunk = TextChunk(
        chunk_id="test_chunk",
        document_id="test_doc",
        source="test.pdf",
        category="Alzheimers/Diagnosis",
        page=1,
        text="Sample chunk text.",
        disease="alzheimers"
    )
    assert chunk.chunk_id == "test_chunk"

    result = RetrievalResult(
        chunk_id="test_chunk",
        source="test.pdf",
        category="Alzheimers/Diagnosis",
        page=1,
        score=0.85,
        text="Sample result.",
        disease="alzheimers"
    )
    assert result.score == 0.85


# ---------------------------------------------------------------------------
# Test 2: Empty query rejected
# ---------------------------------------------------------------------------

def test_rag_request_rejects_empty_query():
    """RAGRequest must reject blank or whitespace-only queries."""
    with pytest.raises(Exception):
        RAGRequest(query="", top_k=5)

    with pytest.raises(Exception):
        RAGRequest(query="   ", top_k=5)


# ---------------------------------------------------------------------------
# Test 3: Invalid top_k rejected
# ---------------------------------------------------------------------------

def test_rag_request_rejects_invalid_top_k():
    """RAGRequest must reject top_k < 1 or > 20."""
    with pytest.raises(Exception):
        RAGRequest(query="test query", top_k=0)

    with pytest.raises(Exception):
        RAGRequest(query="test query", top_k=21)


# ---------------------------------------------------------------------------
# Test 4: Text cleaner
# ---------------------------------------------------------------------------

def test_text_cleaner_normalises_whitespace():
    """Text cleaner should collapse excessive whitespace and line breaks."""
    dirty = "Hello    world\n\n\n\n\nThis  is   a  test"
    cleaned = clean_text(dirty)
    assert "    " not in cleaned
    assert "\n\n\n" not in cleaned
    assert "Hello" in cleaned
    assert "world" in cleaned


def test_text_cleaner_preserves_medical_terms():
    """Text cleaner must NOT remove medical terminology."""
    medical = "MMSE score 24/30. CDR 0.5. Amyloid-β42 level: 500 pg/mL."
    cleaned = clean_text(medical)
    assert "MMSE" in cleaned
    assert "CDR" in cleaned
    assert "Amyloid" in cleaned
    assert "500" in cleaned


# ---------------------------------------------------------------------------
# Test 5: Chunker respects size / overlap / minimum
# ---------------------------------------------------------------------------

def test_chunker_respects_chunk_size():
    """Chunks should not exceed CHUNK_SIZE words (except trailing chunks)."""
    # Create a document with 1000 words
    long_text = " ".join([f"word{i}" for i in range(1000)])
    doc = RawDocument(
        document_id="test_long",
        source="test.pdf",
        category="Test",
        page=1,
        text=long_text,
        disease="alzheimers"
    )
    chunks = chunk_document(doc)
    assert len(chunks) > 1, "1000 words should produce multiple chunks"

    for chunk in chunks:
        word_count = len(chunk.text.split())
        assert word_count <= CHUNK_SIZE + 5, (
            f"Chunk has {word_count} words, expected <= {CHUNK_SIZE}"
        )


def test_chunker_skips_short_pages():
    """Pages with fewer than MIN_CHUNK words should produce zero chunks."""
    short_text = "Hello world"
    doc = RawDocument(
        document_id="test_short",
        source="test.pdf",
        category="Test",
        page=1,
        text=short_text,
        disease="alzheimers"
    )
    chunks = chunk_document(doc)
    assert len(chunks) == 0


# ---------------------------------------------------------------------------
# Test 6: Chunk metadata preserved
# ---------------------------------------------------------------------------

def test_chunk_metadata_preserved():
    """Every chunk must retain document_id, source, category, page."""
    text = " ".join([f"word{i}" for i in range(500)])
    doc = RawDocument(
        document_id="meta_test",
        source="meta_test.pdf",
        category="Alzheimers/MRI",
        page=7,
        text=text,
        disease="alzheimers"
    )
    chunks = chunk_document(doc)
    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk.document_id == "meta_test"
        assert chunk.source == "meta_test.pdf"
        assert chunk.category == "Alzheimers/MRI"
        assert chunk.page == 7
        assert chunk.disease == "alzheimers"
        assert chunk.chunk_id.startswith("meta_test_")


# ---------------------------------------------------------------------------
# Test 7: Embedding dimension (checks saved embeddings)
# ---------------------------------------------------------------------------

def test_embedding_dimension_is_384():
    """Saved embeddings must have dimension 384."""
    emb_file = PROJECT_ROOT / "data" / "knowledge_base" / "embeddings" / "embeddings.npy"
    if not emb_file.exists():
        pytest.skip("Embeddings not built yet.")

    embeddings = np.load(str(emb_file))
    assert embeddings.shape[1] == 384, f"Expected dim 384, got {embeddings.shape[1]}"
    assert embeddings.shape[0] > 0, "No embeddings found"


# ---------------------------------------------------------------------------
# Test 8: Vector store save/load roundtrip
# ---------------------------------------------------------------------------

def test_vector_store_save_load():
    """FAISS index should survive a save/load cycle with correct counts."""
    if not (VECTOR_STORE_DIR / "index.faiss").exists():
        pytest.skip("Vector store not built yet.")

    from backend.rag.vector_store import load_index

    index, metadata = load_index()
    assert index.ntotal > 0
    assert index.ntotal == len(metadata)
    assert index.d == 384


# ---------------------------------------------------------------------------
# Test 9: Retriever returns descending scores (via API live test)
# ---------------------------------------------------------------------------

def test_retriever_returns_descending_scores():
    """API retrieval results must be sorted by descending similarity score."""
    if not (VECTOR_STORE_DIR / "index.faiss").exists():
        pytest.skip("Vector store not built yet.")

    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        response = client.post(
            "/api/rag/retrieve",
            json={"query": "Alzheimer's disease diagnosis", "top_k": 5},
        )

    if response.status_code == 503:
        pytest.skip("RAG service not available in test environment.")

    assert response.status_code == 200, response.text
    data = response.json()
    scores = [r["score"] for r in data["results"]]
    assert scores == sorted(scores, reverse=True), "Scores must be descending"


# ---------------------------------------------------------------------------
# Test 10: RAG API returns correct structure
# ---------------------------------------------------------------------------

def test_rag_api_returns_correct_structure():
    """POST /api/rag/retrieve must return the specified response structure."""
    if not (VECTOR_STORE_DIR / "index.faiss").exists():
        pytest.skip("Vector store not built yet.")

    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        response = client.post(
            "/api/rag/retrieve",
            json={"query": "What is Alzheimer's disease?", "top_k": 3},
        )

    if response.status_code == 503:
        pytest.skip("RAG service not available in test environment.")

    assert response.status_code == 200
    data = response.json()

    assert "query" in data
    assert "results" in data
    assert "total_results" in data
    assert "clinical_notice" in data
    assert data["total_results"] == len(data["results"])
    assert data["total_results"] <= 3

    for r in data["results"]:
        assert "chunk_id" in r
        assert "source" in r
        assert "category" in r
        assert "page" in r
        assert "score" in r
        assert "text" in r
        assert isinstance(r["score"], float)
        assert r["score"] > 0


# ---------------------------------------------------------------------------
# Test 11: Only Alzheimer's documents indexed
# ---------------------------------------------------------------------------

def test_disease_metadata_in_index():
    """The vector store metadata must contain both Alzheimer's and Parkinson's documents."""
    if not (VECTOR_STORE_DIR / "metadata.json").exists():
        pytest.skip("Vector store not built yet.")

    with open(VECTOR_STORE_DIR / "metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    diseases = set(entry.get("disease", "") for entry in metadata)
    assert "alzheimers" in diseases, "Alzheimer's documents missing from index"
    assert "parkinsons" in diseases, "Parkinson's documents missing from index"


# ---------------------------------------------------------------------------
# Test 12–14: Existing endpoints still work
# ---------------------------------------------------------------------------

def test_health_still_works():
    """GET /health must still return 200."""
    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_adni_predict_still_works():
    """POST /api/adni/predict must still return valid predictions."""
    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        response = client.post("/api/adni/predict", json=VALID_ADNI_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in {"CN", "MCI", "AD"}


def test_agents_analyze_still_works():
    """POST /api/agents/analyze must still return valid agent response."""
    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": VALID_ADNI_PAYLOAD})
    assert response.status_code == 200
    data = response.json()
    assert data["workflow"] == "ADNI_ML"
    assert data["status"] == "completed"
    assert "ADNI ML Agent" in data["agents_executed"]
