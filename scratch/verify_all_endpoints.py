"""
scratch/verify_all_endpoints.py

Live API test script using FastAPI TestClient to verify:
1. POST /api/parkinson/predict
2. Alzheimer's-only routing via POST /api/agents/analyze
3. Parkinson-only routing via POST /api/agents/analyze
4. Both routing via POST /api/agents/analyze
5. SHAP output structure & preservation of 34 raw features
6. PDF semantic mapping
7. Questionnaire non-fabrication
"""

from fastapi.testclient import TestClient
from backend.main import app

with TestClient(app) as client:
    print("--- 1. Testing POST /api/parkinson/predict ---")
    p_payload = {
        "AGE_AT_VISIT": 67.0,
        "EDUCYRS": 16.0,
        "NHY": 2.0,
        "NP3TOT": 24.0,
        "MCATOT": 26.0,
        "SCOPA_AUT_TOTAL": 14.0,
    }
    resp = client.post("/api/parkinson/predict", json=p_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    print("Prediction Result:", data["predicted_label"], f"(PD Prob: {data['pd_probability']})")
    print("Feature Availability:", data["feature_availability"])
    assert data["feature_availability"]["present_features_count"] == 6
    assert data["feature_availability"]["missing_features_count"] == 11
    assert len(data["explainability"]["raw_transformed_shap"]) == 34
    assert len(data["explainability"]["top_features"]) == 5
    print("Top SHAP Feature 1:", data["explainability"]["top_features"][0])
    print("PASSED 1\n")

    print("--- 2. Testing Alzheimer's-Only Routing ---")
    alz_req = {
        "type": "ADNI_ML",
        "adni_data": {
            "AGE": 72, "EDUCATION": 16, "ADAS": 12.0, "CDR": 0.5, "FAQ": 5.0,
            "MMSE": 25.0, "MOCA": 21.0, "SEX": "Male", "RACE": "White", "ETHNICITY": "Not Hispanic or Latino"
        },
        "disease_context": ["alzheimers"]
    }
    resp = client.post("/api/agents/analyze", json=alz_req)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    print("Executed Agents:", data["agents_executed"])
    assert "ADNI ML Agent" in data["agents_executed"]
    assert "Parkinson ML Agent" not in data["agents_executed"]
    assert data["prediction"] is not None
    assert data["parkinson_prediction"] is None
    print("PASSED 2\n")

    print("--- 3. Testing Parkinson-Only Routing ---")
    pd_req = {
        "type": "PARKINSON_ML",
        "parkinson_data": p_payload,
        "disease_context": ["parkinsons"]
    }
    resp = client.post("/api/agents/analyze", json=pd_req)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    print("Executed Agents:", data["agents_executed"])
    assert "Parkinson ML Agent" in data["agents_executed"]
    assert "ADNI ML Agent" not in data["agents_executed"]
    assert data["parkinson_prediction"] is not None
    assert data["prediction"] is None
    print("PASSED 3\n")

    print("--- 4. Testing Both Routing ---")
    both_req = {
        "type": "CLINICAL_REPORT",
        "adni_data": alz_req["adni_data"],
        "parkinson_data": p_payload,
        "disease_context": ["alzheimers", "parkinsons"]
    }
    resp = client.post("/api/agents/analyze", json=both_req)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    print("Executed Agents:", data["agents_executed"])
    assert "ADNI ML Agent" in data["agents_executed"]
    assert "Parkinson ML Agent" in data["agents_executed"]
    assert data["prediction"] is not None
    assert data["parkinson_prediction"] is not None
    print("ADNI Prediction:", data["prediction"]["class"])
    print("Parkinson Prediction:", data["parkinson_prediction"]["predicted_label"])
    print("PASSED 4\n")

    print("--- 5. Testing PDF Semantic Mapping Safety ---")
    pdf_payload = {
        "type": "CLINICAL_REPORT",
        "clinical_profile": {
            "disease_context": ["parkinsons"],
            "patient_information": {"age": 69, "education": 14},
            "clinical_scores": {
                "moca": 25,
                "hoehn_yahr": "Stage 2.0",
                "updrs": 30, # Generic UPDRS -> Must not map to NP3TOT!
                "other_scores": {
                    "MDS_UPDRS_Part_3": 22
                }
            }
        }
    }
    resp = client.post("/api/agents/analyze", json=pdf_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    pk_pred = data["parkinson_prediction"]
    assert pk_pred["feature_values_used"]["AGE_AT_VISIT"] == 69.0
    assert pk_pred["feature_values_used"]["MCATOT"] == 25.0
    assert pk_pred["feature_values_used"]["NHY"] == 2.0
    assert pk_pred["feature_values_used"]["NP3TOT"] == 22.0
    assert pk_pred["feature_values_used"]["NP1RTOT"] is None
    print("PDF Mapping Validated. Generic UPDRS was NOT mapped to NP3TOT!")
    print("PASSED 5\n")

    print("--- 6. Testing Questionnaire Non-Fabrication ---")
    q_payload = {
        "type": "QUESTIONNAIRE",
        "questionnaire_data": {
            "questionnaire_id": "PARKINSON_SCREENING",
            "version": "1.0",
            "responses": [
                {"question_id": "PD_Q01", "answer": "Often"},
                {"question_id": "PD_Q02", "answer": "Sometimes"},
                {"question_id": "PD_Q03", "answer": "Rarely"},
                {"question_id": "PD_Q04", "answer": "Never"},
                {"question_id": "PD_Q05", "answer": "Never"},
                {"question_id": "PD_Q06", "answer": "Never"},
                {"question_id": "PD_Q07", "answer": "Never"},
                {"question_id": "PD_Q08", "answer": "Never"},
                {"question_id": "PD_Q09", "answer": "Never"},
                {"question_id": "PD_Q10", "answer": "Never"}
            ]
        },
        "disease_context": ["parkinsons"]
    }
    resp = client.post("/api/agents/analyze", json=q_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["workflow"] == "QUESTIONNAIRE"
    assert data["questionnaire_profile"] is not None
    assert data["parkinson_prediction"] is None
    print("Questionnaire Non-Fabrication Validated. No ML prediction forced from questionnaire!")
    print("PASSED 6\n")

    print("--- 7. Testing POST /api/reports/analyze for Parkinson PDF ---")
    report_payload = {
        "profile": {
            "disease_context": ["parkinsons"],
            "patient_information": {"age": 64, "sex": "Male", "education": 14},
            "clinical_scores": {
                "moca": 27,
                "hoehn_yahr": "2",
                "updrs": 32,
            },
            "cognitive_findings": {"details": []},
            "motor_findings": {"details": ["Parkinson motor findings"]},
            "symptoms": ["resting tremor"],
            "imaging_findings": [],
            "laboratory_findings": [],
            "medications": [],
            "family_history": [],
            "missing_information": []
        }
    }
    resp = client.post("/api/reports/analyze", json=report_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    print("Executed Agents:", data["agents_executed"])
    assert "Parkinson ML Agent" in data["agents_executed"]
    assert data["parkinson_prediction"] is not None
    assert data["parkinson_explainability"] is not None
    assert len(data["parkinson_explainability"]["top_features"]) == 5
    print("Parkinson Prediction:", data["parkinson_prediction"]["predicted_label"])
    print("Top SHAP Feature:", data["parkinson_explainability"]["top_features"][0]["feature"])
    print("PASSED 7\n")

    print("--- 8. Testing POST /api/reports/analyze for Alzheimer PDF ---")
    alz_report_payload = {
        "profile": {
            "disease_context": ["alzheimers"],
            "patient_information": {"age": 73, "sex": "Female", "education": 16},
            "clinical_scores": {
                "mmse": 22,
                "moca": 19,
                "cdr": 1.0,
                "adas": 15.0,
                "faq": 8.0
            },
            "cognitive_findings": {"details": ["Memory impairment", "Executive dysfunction"]},
            "motor_findings": {"details": []},
            "symptoms": ["Memory loss", "Confusion"],
            "imaging_findings": [],
            "laboratory_findings": [],
            "medications": [],
            "family_history": [],
            "missing_information": []
        }
    }
    resp = client.post("/api/reports/analyze", json=alz_report_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    print("Executed Agents:", data["agents_executed"])
    assert "ADNI ML Agent" in data["agents_executed"]
    assert "Parkinson ML Agent" not in data["agents_executed"]
    assert data["prediction"] is not None
    assert data["explainability"] is not None
    assert data["parkinson_prediction"] is None
    assert data["parkinson_explainability"] is None
    assert len(data["explainability"]["top_features"]) <= 5
    print("Alzheimer Prediction Class:", data["prediction"]["class"])
    print("Top Alzheimer SHAP Feature:", data["explainability"]["top_features"][0]["feature"], "Value:", data["explainability"]["top_features"][0].get("feature_value"))
    print("Disease Isolation Verified: Parkinson SHAP did not appear for Alzheimer PDF.")
    print("PASSED 8\n")

    print("=== ALL EMPIRICAL CHECKS PASSED SUCCESSFULLY ===")
