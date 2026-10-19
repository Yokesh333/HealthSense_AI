"""
tests/test_parkinson.py

Comprehensive test suite for Parkinson's Disease Random Forest predictor, TreeSHAP explainability,
feature availability tracking, exact PDF adapter semantic mapping, multi-agent context routing,
and non-fabrication safety.
"""

import pytest
import asyncio
import numpy as np
from backend.services.parkinson_predictor import ParkinsonPredictor
from backend.models.parkinson_schemas import ParkinsonPredictionRequest
from backend.models.report_schemas import StructuredClinicalProfile, PatientInformation, ClinicalScores
from backend.services.report_adapter import ClinicalProfileAdapter
from backend.agents.orchestrator import Orchestrator
from backend.models.adni_schemas import UnifiedAnalysisRequest, ADNIPredictionRequest


@pytest.fixture(scope="module")
def parkinson_predictor():
    predictor = ParkinsonPredictor()
    predictor.load_model()
    return predictor


def test_1_parkinson_model_loads_successfully(parkinson_predictor):
    """Test 1: Parkinson model artifact, metadata, and SHAP explainer load successfully."""
    assert parkinson_predictor.model is not None
    assert parkinson_predictor.metadata is not None
    assert parkinson_predictor.explainer is not None
    assert len(parkinson_predictor.TRAINED_FEATURES) == 17


def test_2_parkinson_predictor_accepts_valid_input(parkinson_predictor):
    """Test 2: Predictor accepts all 17 valid features."""
    sample = {
        "AGE_AT_VISIT": 68.0,
        "EDUCYRS": 16.0,
        "NP1RTOT": 3.0,
        "NP2PTOT": 5.0,
        "NP3TOT": 18.0,
        "NHY": 2.0,
        "MCATOT": 27.0,
        "GDS_TOTAL": 4.0,
        "ESS_TOTAL": 7.0,
        "RBD_TOTAL": 2.0,
        "SDMTOTAL": 35.0,
        "DVT_TOTAL_RECALL": 45.0,
        "DVT_DELAYED_RECALL": 9.0,
        "LNS_TOTRAW": 10.0,
        "TMTASEC": 32.0,
        "TMTBSEC": 75.0,
        "SCOPA_AUT_TOTAL": 12.0,
    }
    res = parkinson_predictor.predict(sample)
    assert res is not None
    assert "predicted_class" in res
    assert res["predicted_class"] in (0, 1)
    assert res["predicted_label"] in ("Healthy Control", "Parkinson's Disease")


def test_3_parkinson_predictor_binary_prediction(parkinson_predictor):
    """Test 3: Predictor produces binary classification output 0 or 1."""
    res = parkinson_predictor.predict({})
    assert res["predicted_class"] in (0, 1)
    assert res["predicted_label"] in ("Healthy Control", "Parkinson's Disease")


def test_4_probability_values_between_0_and_1(parkinson_predictor):
    """Test 4: Individual probabilities are strictly within [0.0, 1.0]."""
    res = parkinson_predictor.predict({"AGE_AT_VISIT": 70.0, "NHY": 3.0})
    assert 0.0 <= res["pd_probability"] <= 1.0
    assert 0.0 <= res["healthy_control_probability"] <= 1.0
    assert 0.0 <= res["probabilities"]["Healthy Control"] <= 1.0
    assert 0.0 <= res["probabilities"]["Parkinson's Disease"] <= 1.0


def test_5_hc_and_pd_probabilities_sum_to_one(parkinson_predictor):
    """Test 5: Healthy Control + Parkinson's Disease probabilities sum to ~1.0."""
    res = parkinson_predictor.predict({"AGE_AT_VISIT": 65.0, "NP3TOT": 22.0})
    total = res["pd_probability"] + res["healthy_control_probability"]
    assert pytest.approx(total, abs=0.001) == 1.0


def test_6_missing_feature_values_do_not_crash(parkinson_predictor):
    """Test 6: Missing feature values remain missing (NaN) and do not crash predictor."""
    partial_input = {"AGE_AT_VISIT": 62.0}
    res = parkinson_predictor.predict(partial_input)
    assert res is not None
    assert res["feature_availability"]["missing_features_count"] == 16
    assert res["feature_availability"]["present_features_count"] == 1


def test_7_shap_explanation_is_returned(parkinson_predictor):
    """Test 7: SHAP TreeExplainer produces explainability block."""
    res = parkinson_predictor.predict({"NHY": 2.0, "NP3TOT": 15.0})
    assert res["explainability"] is not None
    assert res["explainability"]["method"] == "SHAP TreeExplainer"


def test_8_shap_top_5_list_returned(parkinson_predictor):
    """Test 8: SHAP explanation returns exactly 5 aggregated top features."""
    res = parkinson_predictor.predict({"NHY": 2.0, "NP3TOT": 15.0, "AGE_AT_VISIT": 65.0})
    top = res["explainability"]["top_features"]
    assert len(top) == 5
    for item in top:
        assert "feature" in item
        assert "shap_value" in item
        assert "absolute_importance" in item
        assert "direction" in item
        assert "explanation" in item


def test_9_shap_directions_are_valid(parkinson_predictor):
    """Test 9: SHAP direction strings are valid."""
    res = parkinson_predictor.predict({"NHY": 2.0, "NP3TOT": 25.0})
    top = res["explainability"]["top_features"]
    for item in top:
        assert item["direction"] in ("toward_parkinsons_disease", "away_from_parkinsons_disease")
        assert "contributed" in item["explanation"]
        assert "Parkinson's Disease prediction" in item["explanation"]


def test_10_34_shap_transformed_features_preserved(parkinson_predictor):
    """Test 10: All 34 raw transformed SHAP features are preserved."""
    res = parkinson_predictor.predict({"AGE_AT_VISIT": 60.0})
    raw_shap = res["explainability"]["raw_transformed_shap"]
    assert len(raw_shap) == 34
    # Check transformed names include original 17 features + 17 missingness indicators
    feature_names = [item["feature"] for item in raw_shap]
    assert any("num__AGE_AT_VISIT" in name for name in feature_names)
    assert any("missingindicator__AGE_AT_VISIT" in name for name in feature_names)


def test_11_shap_feature_alignment(parkinson_predictor):
    """Test 11: Top 5 aggregated SHAP features align with absolute magnitude sorting."""
    res = parkinson_predictor.predict({"NHY": 3.0, "NP3TOT": 30.0, "SCOPA_AUT_TOTAL": 18.0})
    top = res["explainability"]["top_features"]
    importances = [f["absolute_importance"] for f in top]
    assert importances == sorted(importances, reverse=True)


def test_12_extremely_incomplete_parkinson_input(parkinson_predictor):
    """Test 12: Predictor safely handles 0 or 1 features provided, returning feature availability metadata."""
    res_empty = parkinson_predictor.predict({})
    assert res_empty["feature_availability"]["present_features_count"] == 0
    assert res_empty["feature_availability"]["missing_features_count"] == 17
    assert res_empty["feature_availability"]["feature_completeness_ratio"] == 0.0

    res_one = parkinson_predictor.predict({"AGE_AT_VISIT": 72.0})
    assert res_one["feature_availability"]["present_features_count"] == 1
    assert res_one["feature_availability"]["missing_features_count"] == 16
    assert res_one["feature_availability"]["feature_completeness_ratio"] == round(1.0 / 17.0, 4)


def test_13_exact_pdf_to_feature_mapping():
    """Test 13: PDF clinical profile maps extracted scores ONLY when semantically exact."""
    profile_data = {
        "disease_context": ["parkinsons"],
        "patient_information": {"age": 68.0, "education": 16.0},
        "clinical_scores": {
            "moca": 26.0,
            "hoehn_yahr": "Stage 2.5",
            "updrs": 35.0,  # Generic UPDRS -> MUST NOT map to NP3TOT
            "other_scores": {
                "MDS_UPDRS_Part_3": 28.0,  # Explicit Part III -> Maps to NP3TOT
                "SCOPA_AUT_TOTAL": 14.0
            }
        }
    }
    prof_obj = StructuredClinicalProfile(**profile_data)
    adapted = ClinicalProfileAdapter.adapt(prof_obj)

    assert adapted.parkinson_data is not None
    p_data = adapted.parkinson_data
    assert p_data.AGE_AT_VISIT == 68.0
    assert p_data.EDUCYRS == 16.0
    assert p_data.MCATOT == 26.0
    assert p_data.NHY == 2.5
    assert p_data.NP3TOT == 28.0  # Mapped from MDS_UPDRS_Part_3
    assert p_data.SCOPA_AUT_TOTAL == 14.0
    # Ensure unmapped features remain None
    assert p_data.NP1RTOT is None
    assert p_data.NP2PTOT is None


def test_14_no_generic_updrs_mapping_to_np3tot():
    """Test 14: Generic UPDRS score is NOT mapped to NP3TOT."""
    profile_data = {
        "disease_context": ["parkinsons"],
        "patient_information": {"age": 70.0},
        "clinical_scores": {
            "updrs": 45.0  # Generic UPDRS
        }
    }
    prof_obj = StructuredClinicalProfile(**profile_data)
    adapted = ClinicalProfileAdapter.adapt(prof_obj)

    assert adapted.parkinson_data is not None
    assert adapted.parkinson_data.NP3TOT is None  # Generic UPDRS must not map to NP3TOT!


def test_15_alzheimer_routing_unchanged(parkinson_predictor):
    """Test 15: Alzheimer's disease_context runs ADNI predictor and does not call Parkinson."""
    from backend.services.adni_predictor import ADNIPredictor
    adni_predictor = ADNIPredictor()
    adni_predictor.load_model()

    orchestrator = Orchestrator(predictor=adni_predictor, parkinson_predictor=parkinson_predictor)
    req = UnifiedAnalysisRequest(
        type="ADNI_ML",
        adni_data=ADNIPredictionRequest(
            AGE=75, EDUCATION=16, CDR=0.5, MMSE=24, SEX="Female", RACE="White", ETHNICITY="Not Hisp/Latino"
        ),
        disease_context=["alzheimers"]
    )
    res = asyncio.run(orchestrator.analyze_unified(req))
    assert "ADNI ML Agent" in res.agents_executed
    assert "Parkinson ML Agent" not in res.agents_executed
    assert res.prediction is not None
    assert res.parkinson_prediction is None


def test_16_parkinson_routing_calls_parkinson_predictor(parkinson_predictor):
    """Test 16: Parkinson's disease_context runs Parkinson predictor and does not call ADNI."""
    from backend.services.adni_predictor import ADNIPredictor
    adni_predictor = ADNIPredictor()
    adni_predictor.load_model()

    orchestrator = Orchestrator(predictor=adni_predictor, parkinson_predictor=parkinson_predictor)
    req = UnifiedAnalysisRequest(
        type="PARKINSON_ML",
        parkinson_data=ParkinsonPredictionRequest(AGE_AT_VISIT=65.0, NHY=2.0),
        disease_context=["parkinsons"]
    )
    res = asyncio.run(orchestrator.analyze_unified(req))
    assert "Parkinson ML Agent" in res.agents_executed
    assert "ADNI ML Agent" not in res.agents_executed
    assert res.parkinson_prediction is not None
    assert res.prediction is None


def test_17_both_routing_keeps_predictions_separate(parkinson_predictor):
    """Test 17: Both disease_context runs both predictors and keeps predictions separate."""
    from backend.services.adni_predictor import ADNIPredictor
    adni_predictor = ADNIPredictor()
    adni_predictor.load_model()

    orchestrator = Orchestrator(predictor=adni_predictor, parkinson_predictor=parkinson_predictor)
    req = UnifiedAnalysisRequest(
        type="CLINICAL_REPORT",
        adni_data=ADNIPredictionRequest(
            AGE=75, EDUCATION=16, CDR=0.5, MMSE=24, SEX="Female", RACE="White", ETHNICITY="Not Hisp/Latino"
        ),
        parkinson_data=ParkinsonPredictionRequest(AGE_AT_VISIT=75.0, NHY=2.0),
        disease_context=["alzheimers", "parkinsons"]
    )
    res = asyncio.run(orchestrator.analyze_unified(req))
    assert "ADNI ML Agent" in res.agents_executed
    assert "Parkinson ML Agent" in res.agents_executed
    assert res.prediction is not None
    assert res.parkinson_prediction is not None
    assert res.prediction.predicted_class in ("CN", "MCI", "AD")
    assert res.parkinson_prediction["predicted_label"] in ("Healthy Control", "Parkinson's Disease")


def test_18_artifact_integrity_verification(parkinson_predictor):
    """
    Test 18: Artifact integrity test verifying the loaded Parkinson pipeline contains:
      - 17 expected input features
      - SimpleImputer with missing indicators
      - RandomForestClassifier
      - n_estimators=500
      - class_weight="balanced"
      - min_samples_leaf=2
    """
    # 1. 17 expected input features
    assert len(parkinson_predictor.TRAINED_FEATURES) == 17
    expected_17 = [
        "AGE_AT_VISIT", "EDUCYRS", "NP1RTOT", "NP2PTOT", "NP3TOT", "NHY",
        "MCATOT", "GDS_TOTAL", "ESS_TOTAL", "RBD_TOTAL", "SDMTOTAL",
        "DVT_TOTAL_RECALL", "DVT_DELAYED_RECALL", "LNS_TOTRAW", "TMTASEC",
        "TMTBSEC", "SCOPA_AUT_TOTAL"
    ]
    assert parkinson_predictor.TRAINED_FEATURES == expected_17

    pipeline = parkinson_predictor.model
    assert pipeline is not None
    assert hasattr(pipeline, "named_steps")

    # 2. SimpleImputer with missing indicators
    imputer = pipeline.named_steps.get("imputer")
    assert imputer is not None
    assert type(imputer).__name__ == "SimpleImputer"
    assert getattr(imputer, "add_indicator", False) is True

    # 3. RandomForestClassifier
    classifier = pipeline.named_steps.get("classifier")
    assert classifier is not None
    assert type(classifier).__name__ == "RandomForestClassifier"

    # 4. n_estimators=500
    assert getattr(classifier, "n_estimators", None) == 500

    # 5. class_weight="balanced"
    assert getattr(classifier, "class_weight", None) == "balanced"

    # 6. min_samples_leaf=2
    assert getattr(classifier, "min_samples_leaf", None) == 2

