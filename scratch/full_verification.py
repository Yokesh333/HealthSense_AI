"""
scratch/full_verification.py

Comprehensive End-to-End Verification Script for HealthSense AI.
Executes verification across Phase 2 through Phase 18 via FastAPI TestClient.
"""

import os
import json
import joblib
from fastapi.testclient import TestClient
from backend.main import app

def run_full_verification():
    results = {}
    print("============================================================")
    print("HEALTHSENSE AI — AUTOMATED END-TO-END VERIFICATION SUITE")
    print("============================================================")

    with TestClient(app) as client:

        # -------------------------------------------------------------------
        # Phase 2: Backend Startup & Route Verification
        # -------------------------------------------------------------------
        print("\n--- PHASE 2: Route & Health Verification ---")
        res_health = client.get("/health")
        assert res_health.status_code == 200, res_health.text
        assert res_health.json()["status"] == "healthy"
        print("[PASS] GET /health -> healthy")

        res_openapi = client.get("/openapi.json")
        assert res_openapi.status_code == 200, res_openapi.text
        routes = res_openapi.json()["paths"]
        
        expected_routes = [
            "/api/adni/predict",
            "/api/parkinson/predict",
            "/api/agents/analyze",
            "/api/agents/followup",
            "/api/rag/retrieve",
            "/api/questionnaire/{type_}",
            "/api/reports/extract",
            "/api/reports/analyze",
            "/health"
        ]
        
        for r in expected_routes:
            assert r in routes, f"Missing route: {r}"
            print(f"[PASS] Verified route registration: {r}")

        # -------------------------------------------------------------------
        # Phase 3: Alzheimer Direct ML Test
        # -------------------------------------------------------------------
        print("\n--- PHASE 3: Alzheimer Direct ML Test ---")
        adni_payload = {
            "AGE": 72.0,
            "EDUCATION": 16.0,
            "ADAS": 12.0,
            "CDR": 0.5,
            "FAQ": 5.0,
            "MMSE": 25.0,
            "MOCA": 21.0,
            "SEX": "Male",
            "RACE": "White",
            "ETHNICITY": "Not Hispanic or Latino"
        }
        res_adni = client.post("/api/adni/predict", json=adni_payload)
        assert res_adni.status_code == 200, res_adni.text
        adni_data = res_adni.json()
        assert adni_data["prediction"] in ("CN", "MCI", "AD")
        prob_sum = sum(adni_data["probabilities"].values())
        assert abs(prob_sum - 1.0) < 0.01
        assert "model" in adni_data
        print(f"[PASS] ADNI Prediction: {adni_data['prediction']}, Probabilities: {adni_data['probabilities']}")

        # -------------------------------------------------------------------
        # Phase 4 & 5: Parkinson Direct ML Test & SHAP Verification
        # -------------------------------------------------------------------
        print("\n--- PHASE 4 & 5: Parkinson Direct ML & SHAP Verification ---")
        pk_payload = {
            "AGE_AT_VISIT": 64.0,
            "EDUCYRS": 14.0,
            "NP1RTOT": 10.0,
            "NP2PTOT": 8.0,
            "NP3TOT": 32.0,
            "NHY": 2.0,
            "MCATOT": 27.0,
            "GDS_TOTAL": 5.0,
            "ESS_TOTAL": 7.0,
            "RBD_TOTAL": 4.0,
            "SDMTOTAL": 42.0,
            "DVT_TOTAL_RECALL": 20.0,
            "DVT_DELAYED_RECALL": 7.0,
            "LNS_TOTRAW": 10.0,
            "TMTASEC": 45.0,
            "TMTBSEC": 95.0,
            "SCOPA_AUT_TOTAL": 12.0
        }
        res_pk = client.post("/api/parkinson/predict", json=pk_payload)
        assert res_pk.status_code == 200, res_pk.text
        pk_data = res_pk.json()
        assert pk_data["predicted_class"] in (0, 1)
        assert pk_data["predicted_label"] in ("Healthy Control", "Parkinson's Disease")
        pk_prob_sum = pk_data["pd_probability"] + pk_data["healthy_control_probability"]
        assert abs(pk_prob_sum - 1.0) < 0.01
        
        # Feature availability
        fa = pk_data["feature_availability"]
        assert fa["present_features_count"] == 17
        assert fa["missing_features_count"] == 0
        assert fa["feature_completeness_ratio"] == 1.0

        # SHAP 34 transformed features & Top 5 aggregation
        expl = pk_data["explainability"]
        assert expl["method"] == "SHAP TreeExplainer"
        assert len(expl["raw_transformed_shap"]) == 34
        assert len(expl["top_features"]) == 5
        
        for item in expl["top_features"]:
            assert item["feature"] in pk_payload
            assert "contributed" in item["explanation"]
            assert "Parkinson's Disease prediction" in item["explanation"]

        print(f"[PASS] Parkinson Prediction: {pk_data['predicted_label']} (PD Prob: {pk_data['pd_probability']})")
        print(f"[PASS] Verified 34 raw SHAP features & 5 aggregated top features. Top feature 1: {expl['top_features'][0]['feature']}")

        # -------------------------------------------------------------------
        # Phase 6: Model Artifact Integrity Verification
        # -------------------------------------------------------------------
        print("\n--- PHASE 6: Model Artifact Integrity Verification ---")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, "models")
        
        manifest_path = os.path.join(models_dir, "MODEL_MANIFEST.json")
        pk_meta_path = os.path.join(models_dir, "parkinson_model_metadata.json")
        pk_model_path = os.path.join(models_dir, "parkinson_model.joblib")

        assert os.path.exists(manifest_path)
        assert os.path.exists(pk_meta_path)
        assert os.path.exists(pk_model_path)

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["model"]["algorithm"] == "Random Forest"
        assert manifest["model"]["n_estimators"] == 500
        assert manifest["model"]["class_weight"] == "balanced"
        assert len(manifest["features"]) == 17

        loaded_pk_model = joblib.load(pk_model_path)
        clf = loaded_pk_model.named_steps["classifier"]
        assert clf.n_estimators == 500
        assert clf.class_weight == "balanced"
        assert clf.min_samples_leaf == 2
        assert clf.random_state == 42
        print("[PASS] Verified Parkinson model artifact parameters: 500 trees, balanced weights, leaf=2, seed=42.")

        # -------------------------------------------------------------------
        # Phase 7 & 8: Missing Features & Invalid Inputs Tests
        # -------------------------------------------------------------------
        print("\n--- PHASE 7 & 8: Missing Features & Invalid Inputs ---")
        # Partial input
        res_partial = client.post("/api/parkinson/predict", json={"AGE_AT_VISIT": 65.0, "NHY": 2.0})
        assert res_partial.status_code == 200
        p_data = res_partial.json()
        assert p_data["feature_availability"]["present_features_count"] == 2
        assert p_data["feature_availability"]["missing_features_count"] == 15

        # Empty input
        res_empty = client.post("/api/parkinson/predict", json={})
        assert res_empty.status_code == 200
        e_data = res_empty.json()
        assert e_data["feature_availability"]["present_features_count"] == 0

        # String invalid numerical input rejected by Pydantic schema validation (HTTP 422)
        res_invalid = client.post("/api/parkinson/predict", json={"AGE_AT_VISIT": "invalid_number"})
        assert res_invalid.status_code == 422, "Pydantic schema must reject invalid non-numeric string with 422"

        print("[PASS] Missing & invalid inputs handled safely via Pydantic validation & pipeline imputation.")

        # -------------------------------------------------------------------
        # Phase 9 & 10: Multi-Agent Disease Routing Verification
        # -------------------------------------------------------------------
        print("\n--- PHASE 9 & 10: Multi-Agent Disease Routing ---")
        # A. Alzheimer's only
        res_alz_only = client.post("/api/agents/analyze", json={
            "type": "ADNI_ML",
            "adni_data": adni_payload,
            "disease_context": ["alzheimers"]
        })
        assert res_alz_only.status_code == 200
        d_alz = res_alz_only.json()
        assert "ADNI ML Agent" in d_alz["agents_executed"]
        assert "Parkinson ML Agent" not in d_alz["agents_executed"]
        assert d_alz["prediction"] is not None
        assert d_alz["parkinson_prediction"] is None
        print("[PASS] Routing: Alzheimer's context executed ADNI ML Agent ONLY.")

        # B. Parkinson's only
        res_pk_only = client.post("/api/agents/analyze", json={
            "type": "PARKINSON_ML",
            "parkinson_data": pk_payload,
            "disease_context": ["parkinsons"]
        })
        assert res_pk_only.status_code == 200
        d_pk = res_pk_only.json()
        assert "Parkinson ML Agent" in d_pk["agents_executed"]
        assert "ADNI ML Agent" not in d_pk["agents_executed"]
        assert d_pk["parkinson_prediction"] is not None
        assert d_pk["prediction"] is None
        print("[PASS] Routing: Parkinson's context executed Parkinson ML Agent ONLY.")

        # C. Both
        res_both = client.post("/api/agents/analyze", json={
            "type": "CLINICAL_REPORT",
            "adni_data": adni_payload,
            "parkinson_data": pk_payload,
            "disease_context": ["alzheimers", "parkinsons"]
        })
        assert res_both.status_code == 200
        d_both = res_both.json()
        assert "ADNI ML Agent" in d_both["agents_executed"]
        assert "Parkinson ML Agent" in d_both["agents_executed"]
        assert d_both["prediction"] is not None
        assert d_both["parkinson_prediction"] is not None
        print("[PASS] Routing: Both context executed BOTH predictors independently.")

        # -------------------------------------------------------------------
        # Phase 11: RAG Retrieval Verification
        # -------------------------------------------------------------------
        print("\n--- PHASE 11: RAG Retrieval Verification ---")
        res_rag_alz = client.post("/api/rag/retrieve", json={
            "query": "amyloid plaque memory impairment",
            "top_k": 3,
            "disease": "alzheimers"
        })
        assert res_rag_alz.status_code == 200
        chunks_alz = res_rag_alz.json()["results"]
        assert len(chunks_alz) > 0
        for c in chunks_alz:
            assert c["disease"] in ("alzheimers", "both")
        print(f"[PASS] RAG Alzheimer filtered query returned {len(chunks_alz)} Alzheimer-specific chunks.")

        res_rag_pk = client.post("/api/rag/retrieve", json={
            "query": "alpha synuclein bradykinesia resting tremor",
            "top_k": 3,
            "disease": "parkinsons"
        })
        assert res_rag_pk.status_code == 200
        chunks_pk = res_rag_pk.json()["results"]
        assert len(chunks_pk) > 0
        for c in chunks_pk:
            assert c["disease"] in ("parkinsons", "both")
        print(f"[PASS] RAG Parkinson filtered query returned {len(chunks_pk)} Parkinson-specific chunks.")

        # -------------------------------------------------------------------
        # Phase 13: Questionnaire Endpoints Verification
        # -------------------------------------------------------------------
        print("\n--- PHASE 13: Questionnaire Endpoints Verification ---")
        res_q_alz = client.get("/api/questionnaire/alzheimers")
        assert res_q_alz.status_code == 200
        assert len(res_q_alz.json()["questions"]) == 10

        res_q_pk = client.get("/api/questionnaire/parkinsons")
        assert res_q_pk.status_code == 200
        assert len(res_q_pk.json()["questions"]) == 10

        res_q_both = client.get("/api/questionnaire/both")
        assert res_q_both.status_code == 200
        assert res_q_both.json()["total_questions"] == 20

        print("[PASS] Verified Questionnaire endpoints: Alzheimer (10 Qs), Parkinson (10 Qs), Both (20 Qs).")

        # -------------------------------------------------------------------
        # Phase 14-17: PDF Extraction & Parkinson Exact Semantic Mapping
        # -------------------------------------------------------------------
        print("\n--- PHASE 14-17: PDF Semantic Mapping Verification ---")
        pdf_test_payload = {
            "type": "CLINICAL_REPORT",
            "clinical_profile": {
                "disease_context": ["parkinsons"],
                "patient_information": {"age": 66, "education": 16},
                "clinical_scores": {
                    "moca": 26,
                    "hoehn_yahr": "Stage 2.0",
                    "updrs": 34, # Generic UPDRS -> MUST NOT map to NP3TOT
                    "other_scores": {
                        "MDS_UPDRS_Part_3": 28, # Explicit Part III -> Maps to NP3TOT
                        "SCOPA_AUT_TOTAL": 15
                    }
                }
            }
        }
        res_pdf = client.post("/api/agents/analyze", json=pdf_test_payload)
        assert res_pdf.status_code == 200
        d_pdf = res_pdf.json()
        used_feats = d_pdf["parkinson_prediction"]["feature_values_used"]
        assert used_feats["AGE_AT_VISIT"] == 66.0
        assert used_feats["EDUCYRS"] == 16.0
        assert used_feats["MCATOT"] == 26.0
        assert used_feats["NHY"] == 2.0
        assert used_feats["NP3TOT"] == 28.0
        assert used_feats["SCOPA_AUT_TOTAL"] == 15.0
        assert used_feats["NP1RTOT"] is None
        print("[PASS] Verified exact PDF semantic mapping. Generic 'UPDRS' was NOT mapped to NP3TOT.")

        # -------------------------------------------------------------------
        # Phase 18: Follow-up Chat Verification
        # -------------------------------------------------------------------
        print("\n--- PHASE 18: Follow-up Chat Verification ---")
        res_followup = client.post("/api/agents/followup", json={
            "question": "What lifestyle modifications help manage motor fluctuations in Parkinson's Disease?",
            "disease_context": ["parkinsons"],
            "screening_context": {"workflow": "CLINICAL_REPORT"}
        })
        assert res_followup.status_code == 200
        d_fol = res_followup.json()
        assert "answer" in d_fol
        assert d_fol["answer"] != ""
        print("[PASS] Verified POST /api/agents/followup response.")

        print("\n============================================================")
        print("ALL PHASES 2 THROUGH 18 VERIFIED SUCCESSFULLY WITH 0 FAILURES")
        print("============================================================")

if __name__ == "__main__":
    run_full_verification()
