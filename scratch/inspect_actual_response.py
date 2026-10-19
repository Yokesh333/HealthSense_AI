"""
scratch/inspect_actual_response.py
Prints exact JSON from /api/reports/analyze for Alzheimer and Parkinson PDFs.
Shows exactly which keys exist (or don't) in the response.
"""
import json
from fastapi.testclient import TestClient
from backend.main import app

with TestClient(app) as client:
    # --- Alzheimer PDF ---
    print("=" * 70)
    print("ALZHEIMER PDF RESPONSE KEYS")
    print("=" * 70)
    alz_payload = {
        "profile": {
            "disease_context": ["alzheimers"],
            "patient_information": {"age": 73, "sex": "Female", "education": 16},
            "clinical_scores": {"mmse": 22, "moca": 19, "cdr": 1.0, "adas": 15.0, "faq": 8.0},
            "cognitive_findings": {"details": ["Memory impairment"]},
            "motor_findings": {"details": []},
            "symptoms": ["Memory loss"],
            "imaging_findings": [], "laboratory_findings": [],
            "medications": [], "family_history": [], "missing_information": []
        }
    }
    r = client.post("/api/reports/analyze", json=alz_payload)
    print("HTTP Status:", r.status_code)
    data = r.json()
    print("\nTop-level keys:", list(data.keys()))
    print()
    print("prediction:", json.dumps(data.get("prediction"), indent=2))
    print()
    print("explainability key present:", "explainability" in data)
    expl = data.get("explainability")
    print("explainability value:", json.dumps(expl, indent=2) if expl else "NULL / NOT PRESENT")
    print()
    print("parkinson_prediction:", data.get("parkinson_prediction"))
    print("parkinson_explainability:", data.get("parkinson_explainability"))
    print()

    # --- Parkinson PDF ---
    print("=" * 70)
    print("PARKINSON PDF RESPONSE KEYS")
    print("=" * 70)
    pk_payload = {
        "profile": {
            "disease_context": ["parkinsons"],
            "patient_information": {"age": 64, "sex": "Male", "education": 14},
            "clinical_scores": {"moca": 27, "hoehn_yahr": "2", "updrs": 32},
            "cognitive_findings": {"details": []},
            "motor_findings": {"details": ["Parkinson motor findings"]},
            "symptoms": ["resting tremor"],
            "imaging_findings": [], "laboratory_findings": [],
            "medications": [], "family_history": [], "missing_information": []
        }
    }
    r2 = client.post("/api/reports/analyze", json=pk_payload)
    print("HTTP Status:", r2.status_code)
    data2 = r2.json()
    print("\nTop-level keys:", list(data2.keys()))
    print()
    print("prediction:", data2.get("prediction"))
    print()
    print("parkinson_prediction key present:", "parkinson_prediction" in data2)
    pk_pred = data2.get("parkinson_prediction")
    print("parkinson_prediction:", json.dumps(pk_pred, indent=2) if pk_pred else "NULL / NOT PRESENT")
    print()
    print("parkinson_explainability key present:", "parkinson_explainability" in data2)
    pk_expl = data2.get("parkinson_explainability")
    if pk_expl:
        print("parkinson_explainability top-level keys:", list(pk_expl.keys()))
        print("top_features count:", len(pk_expl.get("top_features", [])))
        print("First top feature:", json.dumps(pk_expl["top_features"][0] if pk_expl.get("top_features") else None, indent=2))
    else:
        print("parkinson_explainability: NULL / NOT PRESENT")
