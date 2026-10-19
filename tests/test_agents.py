"""
tests/test_agents.py

Phase 5 — Multi-Agent Foundation test suite.

Tests:
  1. Valid ADNI analysis request → full structured response.
  2. MOCA = null → existing preprocessing handles it; prediction still valid.
  3. Missing required field → HTTP 422.
  4. Orchestrator reuses the existing ADNIPredictor (object-identity check).
  5. Existing /api/adni/predict endpoint remains functional.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
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

VALID_CLASSES = {"CN", "MCI", "AD"}


# ---------------------------------------------------------------------------
# Test 1 — Valid ADNI analysis request
# ---------------------------------------------------------------------------

def test_analyze_valid_complete():
    """
    POST /api/agents/analyze with a fully-specified ADNI payload must return:
      - HTTP 200
      - workflow == "ADNI_ANALYSIS"
      - status == "completed"
      - prediction.class in {CN, MCI, AD}
      - prediction.probabilities contains CN, MCI, AD keys
      - model info present
      - agents_executed contains "ADNI ML Agent"
      - clinical_notice present
    """
    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": VALID_PAYLOAD})

    assert response.status_code == 200, response.text

    data = response.json()

    # Workflow metadata
    assert data["workflow"] == "ADNI_ML"
    assert data["status"] == "completed"

    # Prediction
    assert "prediction" in data
    pred = data["prediction"]
    assert pred["class"] in VALID_CLASSES

    # Probabilities
    assert "probabilities" in pred
    probs = pred["probabilities"]
    assert "CN" in probs
    assert "MCI" in probs
    assert "AD" in probs
    assert abs(sum(probs.values()) - 1.0) < 0.01, "Probabilities must sum to ~1"

    # Model info
    assert "model" in data
    assert "name" in data["model"]
    assert "version" in data["model"]

    # Agents
    assert "agents_executed" in data
    assert "ADNI ML Agent" in data["agents_executed"]

    # Clinical notice
    assert "clinical_notice" in data
    assert data["clinical_notice"]


# ---------------------------------------------------------------------------
# Test 2 — MOCA = null (optional field; handled by existing preprocessing)
# ---------------------------------------------------------------------------

def test_analyze_moca_null():
    """
    MOCA is an optional field with ~58% missingness in the training set.
    The ADNIPredictor's preprocessing must handle None/null without error.
    """
    payload = {**VALID_PAYLOAD, "MOCA": None}

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["status"] == "completed"
    assert data["prediction"]["class"] in VALID_CLASSES


# ---------------------------------------------------------------------------
# Test 3 — Invalid request → HTTP 422
# ---------------------------------------------------------------------------

def test_analyze_missing_required_field():
    """Omitting a required field (AGE) must trigger FastAPI validation → 422."""
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "AGE"}

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})

    assert response.status_code == 422


def test_analyze_invalid_data_type():
    """Sending a string for a numeric field must trigger FastAPI validation → 422."""
    payload = {**VALID_PAYLOAD, "AGE": "not-a-number"}

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Test 4 — Orchestrator reuses the existing ADNIPredictor (object-identity)
# ---------------------------------------------------------------------------

def test_orchestrator_reuses_existing_predictor():
    """
    The ADNIMLAgent must use the SAME ADNIPredictor instance that FastAPI
    loaded at startup (app.state.adni_predictor).

    Verification:
      - We retrieve app.state.adni_predictor after the lifespan starts.
      - We then directly construct an Orchestrator with that instance.
      - We confirm ADNIMLAgent._predictor IS the same object (identity check).

    This guarantees:
      - No second adni_model.joblib load.
      - No model retraining.
      - No duplicate ML logic.
    """
    import asyncio
    from backend.agents.orchestrator import Orchestrator
    from backend.agents.state import ADNIClinicalFeatures

    with TestClient(app) as client:
        # After lifespan startup, app.state.adni_predictor is populated
        app_predictor = app.state.adni_predictor
        assert app_predictor is not None, "ADNIPredictor must be in app.state"

        # Construct orchestrator with the shared predictor
        orchestrator = Orchestrator(predictor=app_predictor)

        # The internal adni agent must hold the SAME predictor instance
        assert orchestrator._adni_agent.predictor is app_predictor, (
            "ADNIMLAgent must hold the same ADNIPredictor instance as app.state "
            "(no second model load allowed)"
        )

        # Also verify end-to-end: run analyze() and check prediction is valid
        from backend.models.adni_schemas import UnifiedAnalysisRequest
        features_dict = VALID_PAYLOAD.copy()
        req = UnifiedAnalysisRequest(type="ADNI_ML", adni_data=features_dict)
        result = asyncio.run(orchestrator.analyze_unified(req))
        assert result.status == "completed"
        assert result.prediction is not None
        assert result.prediction.predicted_class in VALID_CLASSES


# ---------------------------------------------------------------------------
# Test 5 — Existing /api/adni/predict endpoint remains functional
# ---------------------------------------------------------------------------

def test_existing_adni_predict_still_works():
    """
    The Phase 5 changes must not break the existing ADNI prediction endpoint.
    Verify HTTP 200 and valid response shape.
    """
    with TestClient(app) as client:
        response = client.post("/api/adni/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200, response.text

    data = response.json()
    assert "prediction" in data
    assert data["prediction"] in VALID_CLASSES
    assert "probabilities" in data
    assert "CN" in data["probabilities"]
    assert "MCI" in data["probabilities"]
    assert "AD" in data["probabilities"]
    assert "clinical_notice" in data


# ---------------------------------------------------------------------------
# Test 6 — /health endpoint (sanity check)
# ---------------------------------------------------------------------------

def test_health():
    """GET /health must return HTTP 200 and {"status": "healthy"}."""
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# ---------------------------------------------------------------------------
# Phase 7 Tests — LLM and RAG Integration
# ---------------------------------------------------------------------------

from unittest.mock import AsyncMock, patch

def test_analyze_with_llm_mocked():
    """
    Test the full workflow with a mocked LLM service to avoid real Groq API calls.
    """
    payload = {**VALID_PAYLOAD, "clinical_question": "Explain this prediction."}
    
    # Mock LLM service
    mock_llm_response = {
        "what_results_suggest": "Mock summary",
        "why_relevant": "Mock interpretation",
        "what_research_says": ["Mock evidence"],
        "next_steps": ["Mock limitation"],
        "clinical_notice": "Research prototype classification — not a medical diagnosis."
    }
    
    with patch("backend.services.llm_service.GroqLLMService.generate_explanation", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_llm_response
        
        with TestClient(app) as client:
            # We must set GROQ_API_KEY in environment or ensure main.py loads it
            # Actually app.state.llm_service might be None if no API key is present in env.
            # So let's temporarily inject a mocked service into app.state
            from backend.services.llm_service import GroqLLMService
            mock_service = GroqLLMService()
            # we don't want it to fail in init if no key, but GroqLLMService handles no key gracefully.
            app.state.llm_service = mock_service
            
            response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "completed"
    
    # Verify explanation is present
    assert "explanation" in data
    assert data["explanation"]["what_results_suggest"] == "Mock summary"
    
    # Verify RAG Agent and LLM Agent were executed
    assert "ADNI ML Agent" in data["agents_executed"]
    assert "RAG Agent" in data["agents_executed"]
    assert "LLM Agent" in data["agents_executed"]
    
    # Verify RAG results are attached
    assert "evidence" in data
    assert isinstance(data["evidence"], list)

def test_analyze_missing_groq_key_fallback():
    """
    Test that if Groq API key is missing (or LLM service fails), the ML prediction
    and RAG evidence are still returned with a fallback explanation.
    """
    payload = {**VALID_PAYLOAD}
    
    with TestClient(app) as client:
        # Force LLM service to None
        app.state.llm_service = None
        
        response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})
        
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "completed"
    
    assert "explanation" in data
    assert "LLM synthesis is currently unavailable" in data["explanation"]["what_results_suggest"]
    
    # RAG Agent still executed successfully
    assert "RAG Agent" in data["agents_executed"]
    # LLM Agent failed, so it won't be in agents_executed
    assert "LLM Agent" not in data["agents_executed"]
    # Evidence still attached
    assert "evidence" in data

