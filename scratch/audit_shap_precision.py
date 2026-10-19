import joblib
import pandas as pd
import shap
import numpy as np

# Load model pipeline
model_pipeline = joblib.load("models/adni_model.joblib")
preprocessor = model_pipeline.named_steps["preprocessor"]
classifier = model_pipeline.named_steps["classifier"]

explainer = shap.TreeExplainer(classifier)

print(f"SHAP version: {shap.__version__}")
print(f"Explainer model output space / feature_perturbation: {explainer.model.model_type if hasattr(explainer, 'model') else 'default'}")
print(f"Base values (expected_value): {explainer.expected_value}")
print(f"Base values sum across all classes: {sum(explainer.expected_value)}")

# Sample payloads
CN_PAYLOAD = {
    "AGE": 65.0, "EDUCATION": 18.0, "ADAS": 3.0, "CDR": 0.0, "FAQ": 0.0,
    "MMSE": 30.0, "MOCA": 29.0, "SEX": "Female", "RACE": "White", "ETHNICITY": "Not Hispanic or Latino"
}

MCI_PAYLOAD = {
    "AGE": 72.0, "EDUCATION": 16.0, "ADAS": 12.0, "CDR": 0.5, "FAQ": 5.0,
    "MMSE": 25.0, "MOCA": 21.0, "SEX": "Male", "RACE": "White", "ETHNICITY": "Not Hispanic or Latino"
}

AD_PAYLOAD = {
    "AGE": 80.0, "EDUCATION": 12.0, "ADAS": 35.0, "CDR": 2.0, "FAQ": 22.0,
    "MMSE": 14.0, "MOCA": 10.0, "SEX": "Male", "RACE": "White", "ETHNICITY": "Not Hispanic or Latino"
}

samples = [("CN", CN_PAYLOAD), ("MCI", MCI_PAYLOAD), ("AD", AD_PAYLOAD)]

for name, payload in samples:
    df = pd.DataFrame({k: [v] for k, v in payload.items()})
    X_transformed = preprocessor.transform(df)
    
    pred_idx = classifier.predict(X_transformed)[0]
    proba = classifier.predict_proba(X_transformed)[0]
    
    # Run SHAP TreeExplainer
    shap_vals = explainer.shap_values(X_transformed)
    
    # Class index lookup
    class_names = ["CN", "MCI", "AD"]
    predicted_class = class_names[pred_idx]
    
    if isinstance(shap_vals, list):
        sample_shap = shap_vals[pred_idx][0]
        base_val = float(explainer.expected_value[pred_idx])
    else:
        sample_shap = shap_vals[0, :, pred_idx]
        base_val = float(explainer.expected_value[pred_idx])
        
    shap_sum_total = base_val + sample_shap.sum()
    model_proba_class = float(proba[pred_idx])
    
    diff = abs(shap_sum_total - model_proba_class)
    
    print(f"\n--- SAMPLE {name} ---")
    print(f"Predicted class: {predicted_class} (index {pred_idx})")
    print(f"Class probabilities from predict_proba: {proba}")
    print(f"Model probability for predicted class ({predicted_class}): {model_proba_class:.10f}")
    print(f"Base value (expected_value[{pred_idx}]): {base_val:.10f}")
    print(f"Sum of SHAP values for class {pred_idx}: {sample_shap.sum():.10f}")
    print(f"base_value + sum(shap_values): {shap_sum_total:.10f}")
    print(f"Exact numerical difference |(base_val + sum_shap) - predict_proba|: {diff:.10e}")
