"""
tests/test_xai_shap.py

Comprehensive test suite verifying ADNI Random Forest SHAP Explainability (XAI):
- CN, MCI, AD predictions and class-specific SHAP attributions
- Predicted-class index lookup
- Dynamic feature retrieval & root feature aggregation
- Missing MOCA handling
- Top-5 ordering by absolute magnitude & direction labels
- Base value consistency check
- Prediction & probability invariance
- Non-blocking SHAP failure behavior
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.adni_predictor import ADNIPredictor

# Sample test inputs for different target profiles
MCI_PAYLOAD = {
    "AGE": 72.0,
    "EDUCATION": 16.0,
    "ADAS": 12.0,
    "CDR": 0.5,
    "FAQ": 5.0,
    "MMSE": 25.0,
    "MOCA": 21.0,
    "SEX": "Male",
    "RACE": "White",
    "ETHNICITY": "Not Hispanic or Latino",
}

CN_PAYLOAD = {
    "AGE": 65.0,
    "EDUCATION": 18.0,
    "ADAS": 3.0,
    "CDR": 0.0,
    "FAQ": 0.0,
    "MMSE": 30.0,
    "MOCA": 29.0,
    "SEX": "Female",
    "RACE": "White",
    "ETHNICITY": "Not Hispanic or Latino",
}

AD_PAYLOAD = {
    "AGE": 80.0,
    "EDUCATION": 12.0,
    "ADAS": 35.0,
    "CDR": 2.0,
    "FAQ": 22.0,
    "MMSE": 14.0,
    "MOCA": 10.0,
    "SEX": "Male",
    "RACE": "White",
    "ETHNICITY": "Not Hispanic or Latino",
}


# ---------------------------------------------------------------------------
# 1. Test MCI prediction SHAP
# ---------------------------------------------------------------------------

def test_shap_mci_prediction():
    """Verify SHAP explainability structure and top features for an MCI prediction."""
    with TestClient(app) as client:
        res = client.post("/api/adni/predict", json=MCI_PAYLOAD)

    assert res.status_code == 200, res.text
    data = res.json()
    assert data["prediction"] == "MCI"
    assert "explainability" in data
    exp = data["explainability"]

    assert exp is not None
    assert exp["method"] == "SHAP"
    assert exp["model_type"] == "RandomForestClassifier"
    assert isinstance(exp["base_value"], float)
    assert len(exp["top_features"]) <= 5

    # Check top-5 ordering (absolute importance descending)
    importances = [f["absolute_importance"] for f in exp["top_features"]]
    assert importances == sorted(importances, reverse=True)

    # Check direction format
    for feat in exp["top_features"]:
        assert feat["direction"] in ("toward_MCI", "away_from_MCI")


# ---------------------------------------------------------------------------
# 2. Test CN prediction SHAP
# ---------------------------------------------------------------------------

def test_shap_cn_prediction():
    """Verify SHAP explainability structure for a Cognitively Normal (CN) prediction."""
    with TestClient(app) as client:
        res = client.post("/api/adni/predict", json=CN_PAYLOAD)

    assert res.status_code == 200, res.text
    data = res.json()
    assert data["prediction"] == "CN"
    exp = data["explainability"]

    assert exp is not None
    assert exp["method"] == "SHAP"
    for feat in exp["top_features"]:
        assert feat["direction"] in ("toward_CN", "away_from_CN")


# ---------------------------------------------------------------------------
# 3. Test AD prediction SHAP
# ---------------------------------------------------------------------------

def test_shap_ad_prediction():
    """Verify SHAP explainability structure for an Alzheimer's Disease (AD) prediction."""
    with TestClient(app) as client:
        res = client.post("/api/adni/predict", json=AD_PAYLOAD)

    assert res.status_code == 200, res.text
    data = res.json()
    assert data["prediction"] == "AD"
    exp = data["explainability"]

    assert exp is not None
    assert exp["method"] == "SHAP"
    for feat in exp["top_features"]:
        assert feat["direction"] in ("toward_AD", "away_from_AD")


# ---------------------------------------------------------------------------
# 4. Test Missing MOCA handling
# ---------------------------------------------------------------------------

def test_shap_missing_moca():
    """Verify prediction and SHAP explainability succeed cleanly when MOCA is None."""
    payload = {**MCI_PAYLOAD, "MOCA": None}
    with TestClient(app) as client:
        res = client.post("/api/adni/predict", json=payload)

    assert res.status_code == 200, res.text
    data = res.json()
    assert data["prediction"] == "MCI"
    exp = data["explainability"]

    assert exp is not None
    # Feature list should use original clinical feature names and preserve missing indicator label
    feature_names = [f["feature"] for f in exp["top_features"]]
    for f in feature_names:
        assert not f.startswith("num__")
        assert not f.startswith("cat__")


# ---------------------------------------------------------------------------
# 5. Test Model Prediction & Probability Invariance
# ---------------------------------------------------------------------------

def test_model_invariance_with_and_without_shap():
    """
    Verify that prediction and class probabilities are strictly identical
    whether SHAP is computed or set to None.
    """
    predictor = ADNIPredictor()
    predictor.load_model()

    # Normal run with SHAP
    res_shap = predictor.predict(MCI_PAYLOAD)

    # Run with SHAP disabled
    predictor.explainer = None
    res_no_shap = predictor.predict(MCI_PAYLOAD)

    assert res_shap["prediction"] == res_no_shap["prediction"]
    assert res_shap["probabilities"] == res_no_shap["probabilities"]
    assert res_shap["model"] == res_no_shap["model"]
    assert res_shap["clinical_notice"] == res_no_shap["clinical_notice"]
    assert res_no_shap["explainability"] is None


# ---------------------------------------------------------------------------
# 6. Test Fault Tolerance (SHAP failure does not break prediction)
# ---------------------------------------------------------------------------

def test_shap_failure_non_blocking():
    """
    If SHAP TreeExplainer raises an exception, predict() must still return 200
    with valid prediction and probabilities, setting explainability=None.
    """
    with TestClient(app) as client:
        predictor = app.state.adni_predictor
        with patch.object(predictor, "_compute_shap_explanation", side_effect=Exception("Simulated SHAP error")):
            res = client.post("/api/adni/predict", json=MCI_PAYLOAD)

    assert res.status_code == 200, res.text
    data = res.json()
    assert data["prediction"] in ("CN", "MCI", "AD")
    assert "probabilities" in data
    assert data["explainability"] is None


# ---------------------------------------------------------------------------
# 7. Test SHAP Base Value Mathematical Consistency
# ---------------------------------------------------------------------------

def test_shap_mathematical_consistency():
    """
    Verify that SHAP output is directly in probability space and math matches predict_proba:
    base_value + sum(selected_class_shap_values) == predict_proba within tight 1e-5 tolerance.
    Tested across CN, MCI, and AD sample inputs.
    """
    import shap
    import pandas as pd

    predictor = ADNIPredictor()
    predictor.load_model()

    preprocessor = predictor.model.named_steps["preprocessor"]
    classifier = predictor.model.named_steps["classifier"]
    explainer = shap.TreeExplainer(classifier)

    samples = [("CN", CN_PAYLOAD), ("MCI", MCI_PAYLOAD), ("AD", AD_PAYLOAD)]

    for name, payload in samples:
        df = pd.DataFrame({k: [v] for k, v in payload.items()})
        X_transformed = preprocessor.transform(df)
        pred_idx = classifier.predict(X_transformed)[0]
        pred_proba = classifier.predict_proba(X_transformed)[0, pred_idx]

        shap_vals = explainer.shap_values(X_transformed)

        if isinstance(shap_vals, list):
            sample_shap = shap_vals[pred_idx][0]
            base_val = float(explainer.expected_value[pred_idx])
        else:
            sample_shap = shap_vals[0, :, pred_idx]
            base_val = float(explainer.expected_value[pred_idx])

        shap_sum = base_val + sample_shap.sum()
        diff = abs(shap_sum - pred_proba)

        # Assert tight probability space tolerance < 1e-5
        assert diff < 1e-5, f"Sample {name}: SHAP sum ({shap_sum}) differs from predict_proba ({pred_proba}) by {diff}"


# ---------------------------------------------------------------------------
# 8. Test Agent Orchestrator Forwarding
# ---------------------------------------------------------------------------

def test_orchestrator_forwards_explainability():
    """Verify POST /api/agents/analyze includes explainability when running ADNI_ML."""
    with TestClient(app) as client:
        res = client.post("/api/agents/analyze", json={"type": "ADNI_ML", "adni_data": MCI_PAYLOAD})

    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "completed"
    assert "explainability" in data
    assert data["explainability"]["method"] == "SHAP"
