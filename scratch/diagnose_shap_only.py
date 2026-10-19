"""
scratch/diagnose_shap_only.py

SHAP-specific diagnosis: test all scenarios where RF succeeds but SHAP might fail.
"""

import sys
import os
import json
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

SEP = "\n" + "=" * 80 + "\n"


def test_shap_with_features(features_dict, label):
    """Test RF + SHAP with a given feature vector."""
    print(f"{SEP}[{label}] SHAP TEST")
    print(f"  Features: {json.dumps(features_dict, indent=4)}")

    try:
        from backend.services.adni_predictor import ADNIPredictor
        import pandas as pd

        predictor = ADNIPredictor()
        predictor.load_model()

        df = pd.DataFrame({k: [v] for k, v in features_dict.items()})
        print(f"  DataFrame dtypes:")
        for col, dtype in df.dtypes.items():
            print(f"    {col}: {dtype}")

        # RF prediction
        pred_idx = predictor.model.predict(df)[0]
        proba = predictor.model.predict_proba(df)[0]
        class_mapping = {0: "CN", 1: "MCI", 2: "AD"}
        predicted_class = class_mapping.get(int(pred_idx), str(pred_idx))
        print(f"  RF predicted: {predicted_class}")

        # SHAP
        print(f"  SHAP explainer initialized: {predictor.explainer is not None}")
        if predictor.explainer is None:
            print(f"  SHAP SKIPPED -- explainer is None")
            return

        try:
            result = predictor._compute_shap_explanation(df, predicted_class, pred_idx)
            if result:
                print(f"  SHAP SUCCESS -- base_value={result['base_value']}, top_features={len(result['top_features'])}")
                for feat in result["top_features"]:
                    print(f"    {feat['feature']}: {feat['shap_value']:.4f} ({feat['direction']})")
            else:
                print(f"  SHAP returned None (exception caught internally)")
        except Exception as e:
            print(f"  SHAP EXCEPTION: {type(e).__name__}: {e}")
            traceback.print_exc()

    except Exception as e:
        print(f"  TEST FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()


def main():
    print("\n" + "#" * 80)
    print("  SHAP-SPECIFIC DIAGNOSIS")
    print("#" * 80)

    # Test 1: Full features (all present) -- should work
    test_shap_with_features({
        "AGE": 73.0, "EDUCATION": 16.0, "ADAS": 18.0, "CDR": 1.0,
        "FAQ": 12.0, "MMSE": 22.0, "MOCA": 27.0, "SEX": "Male",
        "RACE": "White", "ETHNICITY": "Not Hisp/Latino"
    }, "Full_Features_AD_Profile")

    # Test 2: MMSE present, MOCA/ADAS/FAQ missing (what PDF1 could have if MMSE was extracted)
    test_shap_with_features({
        "AGE": 73.0, "EDUCATION": 12.0, "ADAS": None, "CDR": 0.5,
        "FAQ": None, "MMSE": 22.0, "MOCA": 27.0, "SEX": "Male",
        "RACE": "Caucasian", "ETHNICITY": "Not Hisp/Latino"
    }, "PDF1_Hypothetical_With_MMSE")

    # Test 3: PDF2 type -- age=68, sex=female, MMSE=None (should fail ADNI gate)
    # But simulate what happens if the adapter somehow ran (shouldn't happen)
    test_shap_with_features({
        "AGE": 68.0, "EDUCATION": 12.0, "ADAS": None, "CDR": 0.5,
        "FAQ": None, "MMSE": 24.0, "MOCA": None, "SEX": "Female",
        "RACE": "White", "ETHNICITY": "Not Hisp/Latino"
    }, "PDF2_Hypothetical_With_MMSE")

    # Test 4: Missing MOCA only (most common case)
    test_shap_with_features({
        "AGE": 72.0, "EDUCATION": 16.0, "ADAS": 12.0, "CDR": 0.5,
        "FAQ": 5.0, "MMSE": 25.0, "MOCA": None, "SEX": "Male",
        "RACE": "White", "ETHNICITY": "Not Hisp/Latino"
    }, "Missing_MOCA_Only")

    # Test 5: Many None values (edge case for imputation)
    test_shap_with_features({
        "AGE": 73.0, "EDUCATION": 12.0, "ADAS": None, "CDR": 0.5,
        "FAQ": None, "MMSE": 22.0, "MOCA": None, "SEX": "Male",
        "RACE": "White", "ETHNICITY": "Not Hisp/Latino"
    }, "Multiple_Nones")

    print(f"\n{'#' * 80}")
    print("  SHAP DIAGNOSIS COMPLETE")
    print(f"{'#' * 80}")


if __name__ == "__main__":
    main()
