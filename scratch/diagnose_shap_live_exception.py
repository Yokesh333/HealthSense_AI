"""
scratch/diagnose_shap_live_exception.py

Capture the exact SHAP exception from the RUNNING backend's predictor instance.
We do this by patching the predictor's SHAP method via the TestClient.
"""

import sys
import os
import json
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

SEP = "\n" + "=" * 80 + "\n"

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
}


def main():
    print("\n" + "#" * 80)
    print("  SHAP LIVE EXCEPTION CAPTURE (via TestClient)")
    print("#" * 80)

    from fastapi.testclient import TestClient
    from backend.main import app
    import pandas as pd

    print(f"{SEP}Using TestClient to get actual predictor instance at runtime")

    with TestClient(app) as client:
        predictor = app.state.adni_predictor

        print(f"  Predictor loaded: {predictor is not None}")
        print(f"  Model: {predictor.model is not None}")
        print(f"  Explainer: {predictor.explainer}")
        print(f"  Explainer type: {type(predictor.explainer)}")

        if predictor.explainer is None:
            print(f"  SHAP explainer is None -- it failed to initialize at startup!")
            print(f"  Check backend startup logs for: 'ADNIPredictor: Could not initialize SHAP explainer'")
            return

        # Now test SHAP directly on the running predictor
        print(f"\n  Attempting SHAP with the runtime predictor instance...")
        df = pd.DataFrame({k: [v] for k, v in SYNTHETIC_FEATURES.items()})

        preprocessor = predictor.model.named_steps["preprocessor"]
        classifier = predictor.model.named_steps["classifier"]

        print(f"  preprocessor type: {type(preprocessor)}")
        print(f"  classifier type: {type(classifier)}")

        try:
            X_transformed = preprocessor.transform(df)
            print(f"  X_transformed shape: {X_transformed.shape}")
        except Exception as e:
            print(f"  preprocessor.transform FAILED: {type(e).__name__}: {e}")
            traceback.print_exc()
            return

        try:
            pred_idx = predictor.model.predict(df)[0]
            class_mapping = {0: "CN", 1: "MCI", 2: "AD"}
            predicted_class = class_mapping.get(int(pred_idx), str(pred_idx))
            print(f"  RF predicted: {predicted_class}")
        except Exception as e:
            print(f"  RF predict FAILED: {type(e).__name__}: {e}")
            traceback.print_exc()
            return

        print(f"\n  Calling explainer.shap_values(X_transformed)...")
        try:
            shap_values_raw = predictor.explainer.shap_values(X_transformed)
            print(f"  shap_values type: {type(shap_values_raw).__name__}")
            if isinstance(shap_values_raw, list):
                print(f"  list len={len(shap_values_raw)}, each shape: {[s.shape for s in shap_values_raw]}")
            else:
                print(f"  array shape: {shap_values_raw.shape}")
            print(f"  SHAP VALUES COMPUTED SUCCESSFULLY on the runtime predictor!")
        except Exception as e:
            print(f"  SHAP shap_values() FAILED: {type(e).__name__}: {e}")
            traceback.print_exc()
            return

        # Also check get_feature_names_out
        print(f"\n  Calling preprocessor.get_feature_names_out()...")
        try:
            names = list(preprocessor.get_feature_names_out())
            print(f"  Feature names ({len(names)}): {names}")
        except Exception as e:
            print(f"  get_feature_names_out FAILED: {type(e).__name__}: {e}")
            traceback.print_exc()

        # Now call full _compute_shap_explanation with try-except unmasked
        print(f"\n  Calling predictor._compute_shap_explanation directly...")
        try:
            result = predictor._compute_shap_explanation(df, predicted_class, pred_idx)
            if result:
                print(f"  SUCCESS: {json.dumps({k: str(v) for k, v in result.items() if k != 'top_features'}, indent=2)}")
            else:
                print(f"  Returned None (inner exception caught)")
        except Exception as e:
            print(f"  EXCEPTION: {type(e).__name__}: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
