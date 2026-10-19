"""
scratch/diagnose_shap_exception.py

Capture the exact exception that causes SHAP to return None in the live API flow
for the Synthetic Alzheimer PDF.

The live API shows: RF ran, probabilities returned, but SHAP=None.
Yet direct in-process SHAP works fine.

The difference: the live backend uses the model loaded at startup.
We need to simulate EXACTLY what the orchestrator does when it runs ADNI ML Agent.
"""

import sys
import os
import json
import time
import traceback
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(name)s | %(message)s")

SEP = "\n" + "=" * 80 + "\n"

# The exact feature vector that the Synthetic PDF produces
SYNTHETIC_FEATURES = {
    "AGE": 72.0,
    "EDUCATION": 16.0,
    "ADAS": 18.0,
    "CDR": 1.0,
    "FAQ": 10.0,
    "MMSE": 23.0,
    "MOCA": 19.0,
    "SEX": "Female",
    "RACE": "White",
    "ETHNICITY": "Not Hisp/Latino",
    "clinical_question": "What does this suggest?"
}


def test_predict_with_logging(features, label):
    """Call predictor.predict() with full exception logging enabled."""
    print(f"{SEP}[{label}] PREDICT WITH FULL LOGGING")

    from backend.services.adni_predictor import ADNIPredictor
    import pandas as pd

    predictor = ADNIPredictor()
    predictor.load_model()

    print(f"  Explainer initialized: {predictor.explainer is not None}")

    # Patch _compute_shap_explanation to log exact exception
    original_compute = predictor._compute_shap_explanation

    def patched_compute(df, predicted_class, pred_idx):
        print(f"  _compute_shap_explanation called: predicted_class={predicted_class}, pred_idx={pred_idx}")
        print(f"  df dtypes: {dict(df.dtypes)}")
        print(f"  df values: {df.to_dict()}")
        try:
            result = original_compute(df, predicted_class, pred_idx)
            print(f"  _compute_shap_explanation returned: {result is not None}")
            return result
        except Exception as e:
            print(f"  _compute_shap_explanation EXCEPTION: {type(e).__name__}: {e}")
            traceback.print_exc()
            raise

    predictor._compute_shap_explanation = patched_compute

    # Call predict() exactly as ADNIMLAgent does
    features_clean = {k: v for k, v in features.items()}
    print(f"\n  Features passed to predict(): {json.dumps({k: v for k, v in features_clean.items() if k != 'clinical_question'}, indent=4)}")

    result = predictor.predict(features_clean)
    print(f"\n  predict() returned:")
    print(f"    prediction: {result['prediction']}")
    print(f"    probabilities: {result['probabilities']}")
    print(f"    explainability: {result['explainability']}")

    return result


def test_shap_manually(features_for_rf, label):
    """
    Manually execute each step of _compute_shap_explanation with verbose logging.
    """
    print(f"{SEP}[{label}] MANUAL SHAP STEP-BY-STEP")

    from backend.services.adni_predictor import ADNIPredictor
    import pandas as pd
    import numpy as np

    predictor = ADNIPredictor()
    predictor.load_model()

    if predictor.explainer is None:
        print("  explainer is None -- SHAP will return None immediately")
        return

    # Build dataframe same way predict() does
    feature_names = ["AGE", "EDUCATION", "ADAS", "CDR", "FAQ", "MMSE", "MOCA", "SEX", "RACE", "ETHNICITY"]
    input_data = {feat: [features_for_rf[feat]] for feat in feature_names}
    df = pd.DataFrame(input_data)

    print(f"  Input DataFrame:")
    for col in df.columns:
        val = df[col].iloc[0]
        print(f"    {col}: {val!r} (type={type(val).__name__}, dtype={df[col].dtype})")

    preprocessor = predictor.model.named_steps["preprocessor"]
    classifier = predictor.model.named_steps["classifier"]

    print(f"\n  Step 1: preprocessor.transform(df)")
    try:
        X_transformed = preprocessor.transform(df)
        print(f"    X_transformed shape: {X_transformed.shape}")
        print(f"    X_transformed dtype: {X_transformed.dtype}")
        print(f"    X_transformed values: {X_transformed}")
    except Exception as e:
        print(f"    FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    print(f"\n  Step 2: preprocessor.get_feature_names_out()")
    try:
        transformed_names = list(preprocessor.get_feature_names_out())
        print(f"    Feature names ({len(transformed_names)}): {transformed_names}")
    except Exception as e:
        print(f"    FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    print(f"\n  Step 3: predictor.model.predict(df)")
    try:
        pred_idx = predictor.model.predict(df)[0]
        proba = predictor.model.predict_proba(df)[0]
        class_mapping = {0: "CN", 1: "MCI", 2: "AD"}
        predicted_class = class_mapping.get(int(pred_idx), str(pred_idx))
        print(f"    pred_idx: {pred_idx} -> {predicted_class}")
        print(f"    probabilities: {dict(zip([class_mapping.get(int(c), str(c)) for c in classifier.classes_], proba.round(4)))}")
    except Exception as e:
        print(f"    FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    print(f"\n  Step 4: explainer.shap_values(X_transformed)")
    try:
        shap_values_raw = predictor.explainer.shap_values(X_transformed)
        print(f"    shap_values type: {type(shap_values_raw).__name__}")
        if isinstance(shap_values_raw, list):
            print(f"    list length: {len(shap_values_raw)}, each shape: {[s.shape for s in shap_values_raw]}")
            target_idx = int(pred_idx)
            sample_shap = shap_values_raw[target_idx][0]
            base_val = float(predictor.explainer.expected_value[target_idx])
        elif hasattr(shap_values_raw, "values"):
            print(f"    Explanation object, values shape: {shap_values_raw.values.shape}")
            target_idx = int(pred_idx)
            sample_shap = shap_values_raw.values[0, :, target_idx]
            base_val = float(shap_values_raw.base_values[0, target_idx])
        else:
            print(f"    numpy array shape: {shap_values_raw.shape}")
            if len(shap_values_raw.shape) == 3:
                target_idx = int(pred_idx)
                sample_shap = shap_values_raw[0, :, target_idx]
                base_val = float(predictor.explainer.expected_value[target_idx])
            else:
                sample_shap = shap_values_raw[0]
                base_val = float(predictor.explainer.expected_value)

        print(f"    target_idx: {target_idx}")
        print(f"    base_val: {base_val}")
        print(f"    sample_shap sum: {float(sample_shap.sum()):.6f}")
        print(f"    base + shap_sum: {base_val + float(sample_shap.sum()):.6f}")
        print(f"    expected predict_proba[{predicted_class}]: {float(proba[int(pred_idx)]):.6f}")
        print(f"    SHAP COMPUTED SUCCESSFULLY")
    except Exception as e:
        print(f"    SHAP VALUES FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    print(f"\n  Step 5: Assert len(transformed_names) == X_transformed.shape[1]")
    print(f"    {len(transformed_names)} == {X_transformed.shape[1]}: {len(transformed_names) == X_transformed.shape[1]}")


def main():
    print("\n" + "#" * 80)
    print("  SHAP EXCEPTION CAPTURE DIAGNOSTIC")
    print("#" * 80)

    # Test 1: Full predict() flow with patched exception logging
    test_predict_with_logging(SYNTHETIC_FEATURES, "SYNTHETIC_PREDICT_FLOW")

    # Test 2: Step-by-step SHAP
    test_shap_manually(SYNTHETIC_FEATURES, "SYNTHETIC_SHAP_MANUAL")


if __name__ == "__main__":
    main()
