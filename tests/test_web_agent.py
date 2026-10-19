import pytest
from unittest.mock import AsyncMock, patch
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

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_analyze_with_web_agent_routing():
    """
    If clinical_question contains current-info keywords (e.g., 'latest'), 
    the WebIntelligenceAgent must be included in the workflow.
    """
    payload = {**VALID_PAYLOAD, "clinical_question": "What are the latest treatments?"}
    
    mock_web_results = [{
        "title": "Mock Latest Treatment",
        "url": "https://pubmed.ncbi.nlm.nih.gov/12345/",
        "source": "Mock Journal",
        "domain": "pubmed.ncbi.nlm.nih.gov",
        "published_date": "2026-01-01",
        "snippet": "Mock snippet.",
        "trust_indicator": "PubMed/NIH Authority"
    }]
    
    mock_llm_response = {
        "what_results_suggest": "Mock summary",
        "why_relevant": "Mock interp",
        "what_research_says": [],
        "next_steps": [],
        "clinical_notice": "Research prototype classification — not a medical diagnosis."
    }

    with patch("backend.services.web_intelligence_service.PubMedWebIntelligenceService.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_web_results
        with patch("backend.services.llm_service.GroqLLMService.generate_explanation", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response
            
            with TestClient(app) as client:
                # Mock the LLM service to avoid API errors if key is missing
                from backend.services.llm_service import GroqLLMService
                app.state.llm_service = GroqLLMService()
                
                response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})
                
    assert response.status_code == 200
    data = response.json()
    
    # Verify routing included Web Intelligence Agent
    assert "Web Intelligence Agent" in data["agents_executed"]
    assert "ADNI ML Agent" in data["agents_executed"]
    assert "RAG Agent" in data["agents_executed"]
    assert "LLM Agent" in data["agents_executed"]
    
    # Verify web evidence is attached
    assert "web_evidence" in data
    assert len(data["web_evidence"]) == 1
    assert data["web_evidence"][0]["title"] == "Mock Latest Treatment"


def test_analyze_without_web_agent_routing():
    """
    If clinical_question does not contain keywords, the WebIntelligenceAgent
    should NOT be executed.
    """
    payload = {**VALID_PAYLOAD, "clinical_question": "Explain this prediction."}
    
    mock_llm_response = {
        "what_results_suggest": "Mock summary",
        "why_relevant": "Mock interp",
        "what_research_says": [],
        "next_steps": [],
        "clinical_notice": "Research prototype classification — not a medical diagnosis."
    }

    with patch("backend.services.llm_service.GroqLLMService.generate_explanation", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_llm_response
        
        with TestClient(app) as client:
            from backend.services.llm_service import GroqLLMService
            app.state.llm_service = GroqLLMService()
            
            response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})
            
    assert response.status_code == 200
    data = response.json()
    
    # Verify routing skipped Web Intelligence Agent
    assert "Web Intelligence Agent" not in data["agents_executed"]
    assert "ADNI ML Agent" in data["agents_executed"]
    
    # Verify web evidence is empty
    assert "web_evidence" in data
    assert len(data["web_evidence"]) == 0


def test_analyze_no_question_skips_web():
    """
    If there is no clinical_question, WebIntelligenceAgent should be skipped.
    """
    payload = {**VALID_PAYLOAD}
    
    with TestClient(app) as client:
        # Disable LLM service to use fallback and avoid mocking it
        app.state.llm_service = None
        
        response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})
        
    assert response.status_code == 200
    data = response.json()
    
    assert "Web Intelligence Agent" not in data["agents_executed"]
    assert len(data["web_evidence"]) == 0


def test_analyze_web_timeout_fallback():
    """
    If the WebIntelligenceService raises an exception (e.g., timeout), 
    the Orchestrator must still succeed using ML and RAG.
    """
    payload = {**VALID_PAYLOAD, "clinical_question": "What are the latest treatments?"}
    
    with patch("backend.services.web_intelligence_service.PubMedWebIntelligenceService.search", new_callable=AsyncMock) as mock_search:
        import httpx
        mock_search.side_effect = httpx.TimeoutException("Mock timeout")
        
        with TestClient(app) as client:
            app.state.llm_service = None
            response = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": payload})
            
    assert response.status_code == 200
    data = response.json()
    
    # The Web Agent failed, so it won't appear in agents_executed
    assert "Web Intelligence Agent" not in data["agents_executed"]
    assert "ADNI ML Agent" in data["agents_executed"]
    
    # Web evidence should be empty due to failure
    assert data["web_evidence"] == []
    
    # The workflow as a whole should still be completed
    assert data["status"] == "completed"
    assert "prediction" in data
