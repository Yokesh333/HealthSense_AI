import joblib
import pandas as pd
import shap
import numpy as np

model_pipeline = joblib.load("models/adni_model.joblib")
preprocessor = model_pipeline.named_steps["preprocessor"]
classifier = model_pipeline.named_steps["classifier"]
explainer = shap.TreeExplainer(classifier)

sample_data = {
    "AGE": [72.0],
    "EDUCATION": [16.0],
    "ADAS": [12.0],
    "CDR": [0.5],
    "FAQ": [5.0],
    "MMSE": [25.0],
    "MOCA": [None],
    "SEX": ["Male"],
    "RACE": ["White"],
    "ETHNICITY": ["Not Hispanic or Latino"]
}
df = pd.DataFrame(sample_data)
X_transformed = preprocessor.transform(df)

pred_idx = classifier.predict(X_transformed)[0]
class_names = ["CN", "MCI", "AD"]
predicted_class = class_names[pred_idx]

shap_matrix = explainer.shap_values(X_transformed)
if isinstance(shap_matrix, list):
    sample_shap_pred_class = shap_matrix[pred_idx][0]
    base_val = float(explainer.expected_value[pred_idx])
else:
    sample_shap_pred_class = shap_matrix[0, :, pred_idx]
    base_val = float(explainer.expected_value[pred_idx])

transformed_names = preprocessor.get_feature_names_out()

def get_root_feature(name: str) -> str:
    clean = name.replace("num__", "").replace("cat__", "")
    if "missingindicator_" in clean:
        clean = clean.replace("missingindicator_", "")
    for orig in ["AGE", "EDUCATION", "ADAS", "CDR", "FAQ", "MMSE", "MOCA", "SEX", "RACE", "ETHNICITY"]:
        if clean.startswith(orig):
            return orig
    return clean

feature_shap_map = {}
for name, val in zip(transformed_names, sample_shap_pred_class):
    root = get_root_feature(name)
    feature_shap_map[root] = feature_shap_map.get(root, 0.0) + float(val)

sorted_features = sorted(
    feature_shap_map.items(),
    key=lambda item: abs(item[1]),
    reverse=True
)

top_features = []
for feat, val in sorted_features[:5]:
    direction = f"toward_{predicted_class}" if val >= 0 else f"away_from_{predicted_class}"
    top_features.append({
        "feature": feat,
        "shap_value": round(val, 4),
        "absolute_importance": round(abs(val), 4),
        "direction": direction
    })

explainability = {
    "method": "SHAP",
    "model_type": "RandomForestClassifier",
    "base_value": round(base_val, 4),
    "top_features": top_features
}

import json
print(json.dumps(explainability, indent=2))
