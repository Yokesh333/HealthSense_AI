"""
tests/test_workflow_synthesis_matrix.py

Comprehensive test suite verifying the Workflow-Aware LLM Synthesis Test Matrix (A through J):
A. Alzheimer Questionnaire - all Never
B. Alzheimer Questionnaire - mixed responses
C. Alzheimer Clinical PDF
D. Parkinson Clinical PDF
E. Both disease workflow
F. Clinical PDF -> questionnaire
G. Questionnaire -> clinical PDF
H. Clinical PDF follow-up: "What does my result mean?"
I. Questionnaire follow-up: "What does my result mean?"
J. Clinical PDF follow-up: latest treatment/research
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

# ---------------------------------------------------------------------------
# Helper payload generators
# ---------------------------------------------------------------------------

def make_alz_questionnaire(answer: str = "Never"):
    return {
        "questionnaire_id": "ALZ_SCREENING",
        "version": "1.0",
        "responses": [
            {"question_id": f"ALZ_Q{i:02d}", "answer": answer}
            for i in range(1, 11)
        ]
    }

def make_pd_questionnaire(answer: str = "Never"):
    return {
        "questionnaire_id": "PD_SCREENING",
        "version": "1.0",
        "responses": [
            {"question_id": f"PD_Q{i:02d}", "answer": answer}
            for i in range(1, 11)
        ]
    }

def make_alz_clinical_profile():
    return {
        "disease_context": ["alzheimers"],
        "patient_information": {"age": 74, "sex": "Male", "education": 16},
        "clinical_scores": {"moca": 18, "mmse": 21, "cdr": 1.0},
        "cognitive_findings": {"details": ["Moderate short-term memory impairment", "Word-finding difficulty"]},
        "motor_findings": {"details": []},
        "symptoms": ["Memory loss", "Spatial disorientation"],
        "imaging_findings": [{"modality": "MRI", "finding": "Bilateral hippocampal atrophy"}],
        "laboratory_findings": [],
        "medications": [],
        "family_history": [],
        "missing_information": []
    }

def make_pd_clinical_profile():
    return {
        "disease_context": ["parkinsons"],
        "patient_information": {"age": 68, "sex": "Female", "education": 14},
        "clinical_scores": {"updrs": 28, "hoehn_yahr": 2.0},
        "cognitive_findings": {"details": []},
        "motor_findings": {"details": ["Right-hand resting tremor", "Bradykinesia", "Rigidity"]},
        "symptoms": ["Resting tremor", "Slow movement"],
        "imaging_findings": [{"modality": "DaTSCAN", "finding": "Reduced dopamine transporter uptake"}],
        "laboratory_findings": [],
        "medications": [],
        "family_history": [],
        "missing_information": []
    }

# ---------------------------------------------------------------------------
# Test A: Alzheimer Questionnaire - all Never
# ---------------------------------------------------------------------------
def test_matrix_a_alzheimer_questionnaire_all_never():
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": make_alz_questionnaire("Never"),
        "disease_context": ["alzheimers"]
    }
    with TestClient(app) as client:
        res = client.post("/api/agents/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["workflow"] == "QUESTIONNAIRE"
    q_prof = data["questionnaire_profile"]
    assert q_prof is not None
    assert q_prof["questionnaire_score"] == 0
    assert q_prof["symptom_burden"] == "none"

    # SHAP explainability MUST be null for QUESTIONNAIRE
    assert data["explainability"] is None

    # Isolation check: NO mention of report, MRI, imaging, ADNI, RF, SHAP, MoCA, MMSE
    suggest_text = str(data["explanation"]["what_results_suggest"]) + " " + str(data["explanation"].get("why_relevant", ""))
    for forbidden in ["clinical report", "MRI", "imaging", "ADNI", "Random Forest", "SHAP", "MoCA", "MMSE"]:
        assert forbidden.lower() not in suggest_text.lower(), f"Forbidden phrase '{forbidden}' found in questionnaire explanation"

# ---------------------------------------------------------------------------
# Test B: Alzheimer Questionnaire - mixed responses
# ---------------------------------------------------------------------------
def test_matrix_b_alzheimer_questionnaire_mixed_responses():
    q_data = make_alz_questionnaire("Never")
    # Set 5 to Sometimes
    for i in range(5):
        q_data["responses"][i]["answer"] = "Sometimes"

    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": q_data,
        "disease_context": ["alzheimers"]
    }
    with TestClient(app) as client:
        res = client.post("/api/agents/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["workflow"] == "QUESTIONNAIRE"
    q_prof = data["questionnaire_profile"]
    assert q_prof["questionnaire_score"] == 10
    assert q_prof["symptom_burden"] == "mild"
    assert len(q_prof["positive_findings"]) == 5
    assert data["explainability"] is None

# ---------------------------------------------------------------------------
# Test C: Alzheimer Clinical PDF
# ---------------------------------------------------------------------------
def test_matrix_c_alzheimer_clinical_pdf():
    payload = {
        "type": "CLINICAL_REPORT",
        "clinical_profile": make_alz_clinical_profile(),
        "disease_context": ["alzheimers"]
    }
    with TestClient(app) as client:
        res = client.post("/api/agents/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["workflow"] == "CLINICAL_REPORT"
    assert data["questionnaire_profile"] is None  # MUST be null for CLINICAL_REPORT

    # End-to-end SHAP verification
    expl = data["explainability"]
    assert expl is not None, "Explainability must not be null for Alzheimer Clinical Report"
    assert expl["method"] == "SHAP"
    top_features = expl["top_features"]
    assert isinstance(top_features, list) and len(top_features) > 0
    first_feat = top_features[0]
    assert "feature_name" in first_feat or "feature" in first_feat or "display_name" in first_feat

    # Language verification
    exp_text = str(data["explanation"]["what_results_suggest"]).replace("\u2011", "-").lower()
    assert "adni-based random forest assigned" in exp_text
    assert "% predicted probability to the" in exp_text

    # Prohibited phrases check
    prohibited_claims = [
        "your questionnaire responses",
        "you have alzheimer",
        "confirms alzheimer",
        "proves alzheimer",
        "high likelihood of alzheimer",
        "typical alzheimer",
        "consistent with the typical pattern"
    ]
    for claim in prohibited_claims:
        assert claim not in exp_text.lower(), f"Prohibited claim '{claim}' found in clinical report explanation"

# ---------------------------------------------------------------------------
# Test D: Parkinson Clinical PDF
# ---------------------------------------------------------------------------
def test_matrix_d_parkinson_clinical_pdf():
    payload = {
        "type": "CLINICAL_REPORT",
        "clinical_profile": make_pd_clinical_profile(),
        "disease_context": ["parkinsons"]
    }
    with TestClient(app) as client:
        res = client.post("/api/agents/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["workflow"] == "CLINICAL_REPORT"
    assert data["questionnaire_profile"] is None

    # ADNI/SHAP skipped for Parkinson's
    assert data["explainability"] is None

    exp_text = str(data["explanation"])
    assert "your questionnaire responses" not in exp_text.lower()
    assert "ADNI" not in exp_text

# ---------------------------------------------------------------------------
# Test E: Both disease workflow
# ---------------------------------------------------------------------------
def test_matrix_e_both_disease_workflow():
    responses = make_alz_questionnaire("Never")["responses"] + make_pd_questionnaire("Never")["responses"]
    q_data = {
        "questionnaire_id": "BOTH_SCREENING",
        "version": "1.0",
        "responses": responses
    }
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": q_data,
        "disease_context": ["alzheimers", "parkinsons"]
    }
    with TestClient(app) as client:
        res = client.post("/api/agents/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["workflow"] == "QUESTIONNAIRE"
    assert data["questionnaire_profile"]["questionnaire_score"] == 0
    assert data["questionnaire_profile"]["questionnaire_max_score"] == 60
    assert data["explainability"] is None

# ---------------------------------------------------------------------------
# Test F: Clinical PDF -> questionnaire cross-flow
# ---------------------------------------------------------------------------
def test_matrix_f_clinical_pdf_to_questionnaire():
    payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": make_alz_questionnaire("Never"),
        "disease_context": ["alzheimers"],
        "clinical_profile": make_alz_clinical_profile()  # Stale client data
    }
    with TestClient(app) as client:
        res = client.post("/api/agents/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["workflow"] == "QUESTIONNAIRE"
    q_prof = data["questionnaire_profile"]
    assert q_prof is not None
    assert q_prof["questionnaire_score"] == 0
    assert data["explainability"] is None

    # Leaked profile check
    for leaked in ["moca", "mmse", "imaging_findings"]:
        assert leaked not in q_prof

# ---------------------------------------------------------------------------
# Test G: Questionnaire -> clinical PDF cross-flow
# ---------------------------------------------------------------------------
def test_matrix_g_questionnaire_to_clinical_pdf():
    payload = {
        "type": "CLINICAL_REPORT",
        "clinical_profile": make_alz_clinical_profile(),
        "disease_context": ["alzheimers"],
        "questionnaire_data": make_alz_questionnaire("Often")  # Stale client data
    }
    with TestClient(app) as client:
        res = client.post("/api/agents/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["workflow"] == "CLINICAL_REPORT"
    assert data["questionnaire_profile"] is None  # MUST be null
    assert data["explainability"] is not None

# ---------------------------------------------------------------------------
# Test H: Clinical PDF follow-up: "What does my result mean?"
# ---------------------------------------------------------------------------
def test_matrix_h_clinical_pdf_followup_what_does_result_mean():
    # Obtain initial report analysis
    initial_payload = {
        "type": "CLINICAL_REPORT",
        "clinical_profile": make_alz_clinical_profile(),
        "disease_context": ["alzheimers"]
    }
    with TestClient(app) as client:
        init_res = client.post("/api/agents/analyze", json=initial_payload).json()

        followup_payload = {
            "question": "What does my result mean?",
            "screening_context": {
                "workflow": init_res["workflow"],
                "disease_context": init_res["disease_context"],
                "clinical_profile": initial_payload["clinical_profile"],
                "questionnaire_profile": init_res["questionnaire_profile"],
                "ml_prediction": init_res.get("prediction") or init_res.get("ml_prediction"),
                "explanation": init_res["explanation"]
            }
        }
        res = client.post("/api/agents/followup", json=followup_payload)

    assert res.status_code == 200, res.text
    answer = res.json()["answer"]

    # Must NOT contain questionnaire phrases
    forbidden_phrases = [
        "your questionnaire responses",
        "your responses did not indicate",
        "all answers were never",
        "zero reported burden"
    ]
    for phrase in forbidden_phrases:
        assert phrase not in answer.lower(), f"Forbidden questionnaire phrase '{phrase}' found in clinical report follow-up"

# ---------------------------------------------------------------------------
# Test I: Questionnaire follow-up: "What does my result mean?"
# ---------------------------------------------------------------------------
def test_matrix_i_questionnaire_followup_what_does_result_mean():
    initial_payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": make_alz_questionnaire("Never"),
        "disease_context": ["alzheimers"]
    }
    with TestClient(app) as client:
        init_res = client.post("/api/agents/analyze", json=initial_payload).json()

        followup_payload = {
            "question": "What does my result mean?",
            "screening_context": {
                "workflow": init_res["workflow"],
                "disease_context": init_res["disease_context"],
                "questionnaire_profile": init_res["questionnaire_profile"],
                "explanation": init_res["explanation"]
            }
        }
        res = client.post("/api/agents/followup", json=followup_payload)

    assert res.status_code == 200, res.text
    answer = res.json()["answer"]

    # Must NOT contain clinical report terms
    forbidden_terms = [
        "clinical report",
        "mri",
        "imaging",
        "adni prediction",
        "random forest",
        "shap",
        "moca",
        "mmse"
    ]
    for term in forbidden_terms:
        assert term not in answer.lower(), f"Forbidden clinical term '{term}' found in questionnaire follow-up"

# ---------------------------------------------------------------------------
# Test J: Clinical PDF follow-up: latest treatment/research
# ---------------------------------------------------------------------------
def test_matrix_j_clinical_pdf_followup_latest_research():
    initial_payload = {
        "type": "CLINICAL_REPORT",
        "clinical_profile": make_alz_clinical_profile(),
        "disease_context": ["alzheimers"]
    }
    with TestClient(app) as client:
        init_res = client.post("/api/agents/analyze", json=initial_payload).json()

        followup_payload = {
            "question": "What are the latest treatment options and research findings for these results?",
            "screening_context": {
                "workflow": init_res["workflow"],
                "disease_context": init_res["disease_context"],
                "clinical_profile": initial_payload["clinical_profile"],
                "ml_prediction": init_res.get("prediction") or init_res.get("ml_prediction"),
                "explanation": init_res["explanation"]
            }
        }
        res = client.post("/api/agents/followup", json=followup_payload)

    assert res.status_code == 200, res.text
    data = res.json()
    assert "answer" in data and len(data["answer"]) > 0
    # Must NOT contain questionnaire phrases
    assert "your questionnaire responses" not in data["answer"].lower()
