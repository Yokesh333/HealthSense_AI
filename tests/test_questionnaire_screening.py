"""
tests/test_questionnaire_screening.py

Comprehensive test suite verifying deterministic questionnaire scoring,
zero-symptom handling, signal separation (Questionnaire vs ADNI ML),
RAG background isolation, and post-LLM validation.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from backend.main import app

# ---------------------------------------------------------------------------
# Helper function to generate questionnaire payloads
# ---------------------------------------------------------------------------

def make_alz_payload(answer_val: str = "Never"):
    responses = [
        {"question_id": f"ALZ_Q{i:02d}", "answer": answer_val}
        for i in range(1, 11)
    ]
    return {
        "questionnaire_id": "ALZ_SCREENING",
        "version": "1.0",
        "responses": responses
    }

def make_pd_payload(answer_val: str = "Never"):
    responses = [
        {"question_id": f"PD_Q{i:02d}", "answer": answer_val}
        for i in range(1, 11)
    ]
    return {
        "questionnaire_id": "PD_SCREENING",
        "version": "1.0",
        "responses": responses
    }

def make_both_payload(answer_val: str = "Never"):
    responses = [
        {"question_id": f"ALZ_Q{i:02d}", "answer": answer_val}
        for i in range(1, 11)
    ] + [
        {"question_id": f"PD_Q{i:02d}", "answer": answer_val}
        for i in range(1, 11)
    ]
    return {
        "questionnaire_id": "BOTH_SCREENING",
        "version": "1.0",
        "responses": responses
    }


# ---------------------------------------------------------------------------
# 1. Test Alzheimer's 10/10 Never
# ---------------------------------------------------------------------------

def test_alzheimers_all_never():
    """
    10/10 Never for Alzheimer's:
    - score = 0/30, symptom_burden = "none"
    - positive_findings = []
    - explanation matches standard no-symptom statement
    - no "mild Alzheimer's symptoms" or diagnostic claim
    """
    q_data = make_alz_payload("Never")
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": q_data,
        "disease_context": ["alzheimers"]
    }

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "completed"

    q_prof = data["questionnaire_profile"]
    assert q_prof["questionnaire_score"] == 0
    assert q_prof["questionnaire_max_score"] == 30
    assert q_prof["symptom_burden"] == "none"
    assert len(q_prof["positive_findings"]) == 0
    assert len(q_prof["negative_findings"]) == 10

    # Explicitly verify NO clinical report fields are injected into questionnaire_profile
    prohibited_keys = [
        "MoCA", "MMSE", "extracted_scores", "imaging_count", "symptoms_count",
        "imaging_findings", "laboratory_findings", "clinical_impression", "medications"
    ]
    for key in prohibited_keys:
        assert key not in q_prof, f"Key '{key}' should not exist in questionnaire_profile"

    exp = data["explanation"]["what_results_suggest"]
    assert "Your responses did not indicate the memory and thinking difficulties assessed by this questionnaire" in exp
    assert "mild Alzheimer's symptoms" not in exp.lower()
    assert "early Alzheimer's" not in exp.lower()


# ---------------------------------------------------------------------------
# 2. Test Parkinson's 10/10 Never
# ---------------------------------------------------------------------------

def test_parkinsons_all_never():
    """
    10/10 Never for Parkinson's:
    - score = 0/30, symptom_burden = "none"
    - positive_findings = []
    - explanation matches standard no-symptom statement
    - no "mild Parkinson's symptoms" or diagnostic claim
    """
    q_data = make_pd_payload("Never")
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": q_data,
        "disease_context": ["parkinsons"]
    }

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "completed"

    q_prof = data["questionnaire_profile"]
    assert q_prof["questionnaire_score"] == 0
    assert q_prof["questionnaire_max_score"] == 30
    assert q_prof["symptom_burden"] == "none"
    assert len(q_prof["positive_findings"]) == 0
    assert len(q_prof["negative_findings"]) == 10

    exp = data["explanation"]["what_results_suggest"]
    assert "Your responses did not indicate the movement-related difficulties assessed by this questionnaire" in exp
    assert "mild Parkinson's symptoms" not in exp.lower()
    assert "early Parkinson's" not in exp.lower()


# ---------------------------------------------------------------------------
# 3. Test Both Questionnaire 20/20 Never
# ---------------------------------------------------------------------------

def test_both_all_never():
    """
    20/20 Never for Both:
    - score = 0/60, symptom_burden = "none"
    - positive_findings = []
    - explanation matches combined no-symptom statement
    """
    q_data = make_both_payload("Never")
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": q_data,
        "disease_context": ["alzheimers", "parkinsons"]
    }

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "completed"

    q_prof = data["questionnaire_profile"]
    assert q_prof["questionnaire_score"] == 0
    assert q_prof["questionnaire_max_score"] == 60
    assert q_prof["symptom_burden"] == "none"

    exp = data["explanation"]["what_results_suggest"]
    assert "memory, thinking, or movement-related difficulties" in exp


# ---------------------------------------------------------------------------
# 4. Test All Positive Answers (10/10 Often)
# ---------------------------------------------------------------------------

def test_alzheimers_all_positive():
    """
    10/10 Often for Alzheimer's:
    - score = 30/30 (100%), symptom_burden = "high"
    - positive_findings = 10 items
    """
    q_data = make_alz_payload("Often")
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": q_data,
        "disease_context": ["alzheimers"]
    }

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "completed"

    q_prof = data["questionnaire_profile"]
    assert q_prof["questionnaire_score"] == 30
    assert q_prof["questionnaire_max_score"] == 30
    assert q_prof["symptom_burden"] == "high"
    assert len(q_prof["positive_findings"]) == 10
    assert len(q_prof["negative_findings"]) == 0


# ---------------------------------------------------------------------------
# 5. Test Mixed Answers (5 Never, 5 Sometimes)
# ---------------------------------------------------------------------------

def test_parkinsons_mixed_answers():
    """
    5 Never, 5 Sometimes for Parkinson's:
    - score = 10/30 (33.3%), symptom_burden = "mild" (>20% to 45%)
    - positive_findings = 5 items
    """
    responses = [
        {"question_id": f"PD_Q{i:02d}", "answer": "Never" if i <= 5 else "Sometimes"}
        for i in range(1, 11)
    ]
    q_data = {
        "questionnaire_id": "PD_SCREENING",
        "version": "1.0",
        "responses": responses
    }
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": q_data,
        "disease_context": ["parkinsons"]
    }

    with TestClient(app) as client:
        response = client.post("/api/agents/analyze", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "completed"

    q_prof = data["questionnaire_profile"]
    assert q_prof["questionnaire_score"] == 10
    assert q_prof["questionnaire_max_score"] == 30
    assert q_prof["symptom_burden"] == "mild"
    assert len(q_prof["positive_findings"]) == 5
    assert len(q_prof["negative_findings"]) == 5


# ---------------------------------------------------------------------------
# 6. Test RAG Evidence Isolation (LLM trying to claim symptoms from RAG)
# ---------------------------------------------------------------------------

def test_rag_isolation_on_zero_score():
    """
    Even if the LLM generates a response claiming mild symptoms due to RAG chunks,
    the post-LLM validation layer MUST sanitize and override what_results_suggest.
    """
    hallucinated_llm_response = {
        "what_results_suggest": "Based on biomedical literature, your screening suggests mild Alzheimer's symptoms.",
        "why_relevant": "Cognitive changes are described in RAG evidence.",
        "what_research_says": ["Biomedical research chunk summary"],
        "next_steps": ["Consult doctor"],
        "clinical_notice": "Screening notice"
    }

    q_data = make_alz_payload("Never")
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": q_data,
        "disease_context": ["alzheimers"]
    }

    with patch("backend.services.llm_service.GroqLLMService.generate_explanation", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = hallucinated_llm_response

        with TestClient(app) as client:
            from backend.services.llm_service import GroqLLMService
            app.state.llm_service = GroqLLMService()
            response = client.post("/api/agents/analyze", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()

    exp = data["explanation"]["what_results_suggest"]
    assert "Your responses did not indicate the memory and thinking difficulties assessed by this questionnaire" in exp
    assert "mild Alzheimer's symptoms" not in exp


# ---------------------------------------------------------------------------
# 7. Test Signal Separation (Zero Questionnaire + ADNI ML)
# ---------------------------------------------------------------------------

def test_signal_separation_zero_questionnaire_plus_adni():
    """
    When workflow is CLINICAL_REPORT, even if questionnaire_results was attached in error,
    the CLINICAL_REPORT workflow MUST ignore questionnaire_results (setting questionnaire_profile to None)
    and report ADNI ML model prediction without mentioning questionnaire responses.
    """
    from backend.agents.state import AgentState, MLPredictionResult
    from backend.agents.llm_agent import LLMAgent
    from backend.agents.questionnaire_agent import QuestionnaireAgent

    q_data = make_alz_payload("Never")
    state = AgentState(
        workflow="CLINICAL_REPORT",
        disease_context=["alzheimers"],
        questionnaire_results=q_data,
        ml_prediction=MLPredictionResult(
            predicted_class="MCI",
            probabilities={"CN": 0.2, "MCI": 0.7, "AD": 0.1},
            model_name="RandomForestClassifier",
            model_version="1.0",
            clinical_notice="Research model prediction"
        )
    )

    q_agent = QuestionnaireAgent()
    import asyncio
    asyncio.run(q_agent.execute(state))

    assert state.questionnaire_profile is None

    llm_agent = LLMAgent(llm_service=None) # Uses fallback + validation
    asyncio.run(llm_agent.execute(state))

    exp = state.llm_response["what_results_suggest"]
    assert "Your responses did not indicate" not in exp
    assert "ADNI-based Random Forest assigned" in exp
    assert "predicted probability to the" in exp


# ---------------------------------------------------------------------------
# 8. Test Cross-Flow Isolation: PDF -> Questionnaire & Questionnaire -> PDF
# ---------------------------------------------------------------------------

def test_cross_flow_pdf_then_questionnaire():
    """
    Simulate a user performing a PDF report analysis, then starting a new Questionnaire.
    Verify that the API response for the Questionnaire workflow contains ONLY questionnaire data
    and no residual PDF profile.
    """
    with TestClient(app) as client:
        # Step 1: Submit PDF Clinical Report Analysis
        pdf_payload = {
            "type": "CLINICAL_REPORT",
            "clinical_profile": {
                "disease_context": ["alzheimers"],
                "patient_information": {"age": 72, "sex": "Female", "education": 16},
                "clinical_scores": {"moca": 27, "mmse": 28},
                "cognitive_findings": {"details": ["mild memory retrieval decline"]},
                "motor_findings": {"details": []},
                "symptoms": ["short term memory loss"],
                "imaging_findings": [{"modality": "MRI", "finding": "Hippocampal atrophy"}],
                "laboratory_findings": [],
                "medications": [],
                "family_history": [],
                "missing_information": []
            }
        }
        res1 = client.post("/api/agents/analyze", json=pdf_payload)
        assert res1.status_code == 200, res1.text
        data1 = res1.json()
        assert data1["workflow"] == "CLINICAL_REPORT"
        assert data1["questionnaire_profile"] is None  # Report response MUST NOT contain questionnaire_profile

        # Step 2: Submit a Questionnaire (10/10 Never) even if client mistakenly attaches clinical_profile
        q_payload = {
            "type": "QUESTIONNAIRE",
            "questionnaire_data": make_alz_payload("Never"),
            "disease_context": ["alzheimers"],
            "clinical_profile": pdf_payload["clinical_profile"]  # Stale data from previous session
        }
        res2 = client.post("/api/agents/analyze", json=q_payload)
        assert res2.status_code == 200, res2.text
        data2 = res2.json()
        assert data2["workflow"] == "QUESTIONNAIRE"
        
        q_prof = data2["questionnaire_profile"]
        assert q_prof is not None
        assert q_prof["questionnaire_score"] == 0
        assert q_prof["symptom_burden"] == "none"
        
        # Verify no PDF data leaked into questionnaire_profile
        for leaked in ["moca", "MoCA", "mmse", "MMSE", "extracted_scores", "imaging_findings", "imaging_count"]:
            assert leaked not in q_prof


def test_cross_flow_questionnaire_then_pdf():
    """
    Simulate a user completing a Questionnaire, then starting a PDF report analysis.
    Verify that the PDF report API response has questionnaire_profile == None.
    """
    with TestClient(app) as client:
        # Step 1: Submit Questionnaire
        q_payload = {
            "type": "QUESTIONNAIRE",
            "questionnaire_data": make_alz_payload("Often"),
            "disease_context": ["alzheimers"]
        }
        res1 = client.post("/api/agents/analyze", json=q_payload)
        assert res1.status_code == 200, res1.text
        data1 = res1.json()
        assert data1["workflow"] == "QUESTIONNAIRE"
        assert data1["questionnaire_profile"] is not None

        # Step 2: Submit PDF Report Analysis
        pdf_payload = {
            "type": "CLINICAL_REPORT",
            "clinical_profile": {
                "disease_context": ["parkinsons"],
                "patient_information": {"age": 64, "sex": "Male", "education": 14},
                "clinical_scores": {"updrs": 32},
                "cognitive_findings": {"details": []},
                "motor_findings": {"details": ["resting tremor"]},
                "symptoms": ["left hand tremor"],
                "imaging_findings": [],
                "laboratory_findings": [],
                "medications": [],
                "family_history": [],
                "missing_information": []
            },
            "questionnaire_data": make_alz_payload("Often")  # Stale questionnaire data attached
        }
        res2 = client.post("/api/agents/analyze", json=pdf_payload)
        assert res2.status_code == 200, res2.text
        data2 = res2.json()
        assert data2["workflow"] == "CLINICAL_REPORT"
        assert data2["questionnaire_profile"] is None  # Must be None for report workflow

