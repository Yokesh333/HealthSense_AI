"""
scratch/diagnose_live_adni_direct.py

Test ADNI prediction directly against /api/adni/predict to check if SHAP works
on the live backend (same model instance loaded at startup).
"""

import sys
import os
import json
import time
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND = "http://127.0.0.1:8000"
SEP = "\n" + "=" * 80 + "\n"

# Synthetic PDF's ADNI features
SYNTHETIC_ADNI = {
    "AGE": 72.0,
    "EDUCATION": 16.0,
    "ADAS": 18.0,
    "CDR": 1.0,
    "FAQ": 10.0,
    "MMSE": 23.0,
    "MOCA": 19.0,
    "SEX": "Female",
    "RACE": "White",
    "ETHNICITY": "Not Hisp/Latino"
}

def test_direct_predict(payload, label):
    """Test /api/adni/predict directly - uses the same shared predictor as /api/reports/analyze."""
    print(f"{SEP}[{label}] /api/adni/predict (direct)")
    t0 = time.time()
    resp = requests.post(f"{BACKEND}/api/adni/predict", json=payload, timeout=30)
    elapsed = time.time() - t0
    print(f"  Status: {resp.status_code} | {elapsed:.2f}s")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  prediction: {data.get('prediction')}")
        print(f"  probabilities: {data.get('probabilities')}")
        expl = data.get("explainability")
        if expl:
            print(f"  SHAP: SUCCESS -- base_value={expl.get('base_value')}")
            for feat in expl.get("top_features", []):
                print(f"    {feat['feature']}: {feat['shap_value']:.4f} ({feat['direction']})")
        else:
            print(f"  SHAP: None returned (SHAP failed silently)")
        return data
    else:
        print(f"  FAILED: {resp.text[:500]}")
        return None


def test_agents_analyze(payload, label):
    """Test /api/agents/analyze with ADNI_ML type - also uses shared predictor."""
    print(f"{SEP}[{label}] /api/agents/analyze (ADNI_ML)")
    t0 = time.time()
    resp = requests.post(
        f"{BACKEND}/api/agents/analyze",
        json={"type": "ADNI_ML", "adni_data": payload},
        timeout=60
    )
    elapsed = time.time() - t0
    print(f"  Status: {resp.status_code} | {elapsed:.2f}s")
    if resp.status_code == 200:
        data = resp.json()
        pred = data.get("prediction")
        if pred:
            print(f"  predicted_class: {pred.get('class') or pred.get('predicted_class')}")
        expl = data.get("explainability")
        if expl:
            print(f"  SHAP: SUCCESS -- base_value={expl.get('base_value')}")
        else:
            print(f"  SHAP: None returned")
        return data
    else:
        print(f"  FAILED: {resp.text[:500]}")
        return None


def test_reports_analyze(profile, label):
    """Test /api/reports/analyze - what the frontend uses after PDF extraction."""
    print(f"{SEP}[{label}] /api/reports/analyze (CLINICAL_REPORT)")
    t0 = time.time()
    resp = requests.post(
        f"{BACKEND}/api/reports/analyze",
        json={"profile": profile, "clinical_question": "What does this suggest?"},
        timeout=60
    )
    elapsed = time.time() - t0
    print(f"  Status: {resp.status_code} | {elapsed:.2f}s")
    if resp.status_code == 200:
        data = resp.json()
        pred = data.get("prediction", {})
        if pred:
            print(f"  prediction: {json.dumps(pred, indent=2)}")
        expl = data.get("explainability")
        if expl:
            print(f"  SHAP: SUCCESS -- base_value={expl.get('base_value')}")
            for feat in expl.get("top_features", []):
                print(f"    {feat['feature']}: {feat['shap_value']:.4f} ({feat['direction']})")
        else:
            print(f"  SHAP: None returned")
        print(f"  agents_executed: {data.get('agents_executed')}")
        print(f"  errors: {data.get('errors')}")
        return data
    else:
        print(f"  FAILED: {resp.text[:500]}")
        return None


# Full profile from Synthetic PDF
SYNTHETIC_PROFILE = {
    "disease_context": ["alzheimers"],
    "patient_information": {"age": 72.0, "sex": "Female", "education": 16.0, "race": None, "ethnicity": None},
    "clinical_scores": {
        "mmse": 23.0, "moca": 19.0, "cdr": 1.0, "adas": 18.0, "faq": 10.0,
        "updrs": None, "hoehn_yahr": None, "other_scores": {}
    },
    "cognitive_findings": {"memory_impairment": True, "executive_dysfunction": True, "language_deficits": True, "details": []},
    "motor_findings": {"resting_tremor": None, "bradykinesia": None, "rigidity": None, "gait_postural_instability": None, "details": []},
    "symptoms": ["short-term memory loss"],
    "duration": "2 years",
    "imaging_findings": [],
    "laboratory_findings": [],
    "medications": [],
    "family_history": [],
    "clinical_impression": "Progressive amnestic cognitive impairment, Alzheimer-type",
    "source_pages": {},
    "missing_information": ["race", "ethnicity"]
}


def main():
    print("\n" + "#" * 80)
    print("  LIVE ADNI SHAP DIAGNOSIS")
    print("#" * 80)

    # Test 1: Direct /api/adni/predict - should use same shared model
    test_direct_predict(SYNTHETIC_ADNI, "SYNTHETIC_DIRECT_PREDICT")

    # Test 2: /api/agents/analyze with ADNI_ML type
    test_agents_analyze(SYNTHETIC_ADNI, "SYNTHETIC_AGENTS_ANALYZE")

    # Test 3: /api/reports/analyze - what frontend uses
    test_reports_analyze(SYNTHETIC_PROFILE, "SYNTHETIC_REPORTS_ANALYZE")


if __name__ == "__main__":
    main()
