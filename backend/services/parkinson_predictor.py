"""
backend/services/parkinson_predictor.py

Parkinson's Disease Random Forest Predictor Service.

Features & Responsibilities:
  1. Safely loads models/parkinson_model.joblib, metadata, and feature schema.
  2. Accepts inputs for the 17 trained clinical features. Missing features remain missing (np.nan).
  3. Preprocessing (median imputation + missingness indicators) is performed exclusively
     by the saved sklearn pipeline.
  4. Returns binary prediction (0: Healthy Control, 1: Parkinson's Disease), per-class probabilities,
     model metadata, and feature completeness tracking metadata.
  5. Computes TreeSHAP explanations for Class 1 (Parkinson's Disease):
     - Preserves all 34 raw transformed SHAP features (17 features + 17 missingness indicators).
     - Aggregates original feature SHAP value + missingness indicator SHAP value for patient-facing top 5.
     - Uses strictly non-causal phrasing.
"""

import json
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ParkinsonPredictor:
    TRAINED_FEATURES: List[str] = [
        "AGE_AT_VISIT",
        "EDUCYRS",
        "NP1RTOT",
        "NP2PTOT",
        "NP3TOT",
        "NHY",
        "MCATOT",
        "GDS_TOTAL",
        "ESS_TOTAL",
        "RBD_TOTAL",
        "SDMTOTAL",
        "DVT_TOTAL_RECALL",
        "DVT_DELAYED_RECALL",
        "LNS_TOTRAW",
        "TMTASEC",
        "TMTBSEC",
        "SCOPA_AUT_TOTAL",
    ]

    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.model_path = self.base_dir / "models" / "parkinson_model.joblib"
        self.metadata_path = self.base_dir / "models" / "parkinson_model_metadata.json"
        self.schema_path = self.base_dir / "models" / "parkinson_feature_schema.json"

        self.model = None
        self.metadata = None
        self.schema = None
        self.explainer = None

    def load_model(self) -> None:
        """Loads model artifacts and initializes the SHAP TreeExplainer on the classifier step."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Parkinson model artifact not found at {self.model_path}")
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Parkinson metadata not found at {self.metadata_path}")

        try:
            self.model = joblib.load(self.model_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            if self.schema_path.exists():
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    self.schema = json.load(f)

            # Initialize SHAP TreeExplainer on classifier step of pipeline
            try:
                import shap
                classifier = self.model.named_steps["classifier"]
                self.explainer = shap.TreeExplainer(classifier)
                logger.info("ParkinsonPredictor: SHAP TreeExplainer initialized successfully.")
            except ImportError as e:
                logger.error("ParkinsonPredictor: SHAP package not installed — %s", e)
                self.explainer = None
            except Exception as e:
                logger.warning("ParkinsonPredictor: Failed to initialize SHAP explainer — %s", e)
                self.explainer = None

        except Exception as e:
            raise RuntimeError(f"Failed to load Parkinson model artifacts: {str(e)}")

    def _compute_shap_explanation(
        self, df: pd.DataFrame, feature_values_used: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Computes TreeSHAP feature attributions for Class 1 (Parkinson's Disease).
        Preserves all 34 raw transformed SHAP values and computes top 5 aggregated features.
        """
        if self.explainer is None:
            return None

        try:
            imputer = self.model.named_steps["imputer"]
            classifier = self.model.named_steps["classifier"]

            # 1. Transform DataFrame through pipeline's imputer (17 original + 17 missing indicators = 34 columns)
            X_trans = imputer.transform(df)
            num_transformed = X_trans.shape[1]

            # Build names for all 34 transformed features
            transformed_names: List[str] = []
            for feat in self.TRAINED_FEATURES:
                transformed_names.append(f"num__{feat}")
            for feat in self.TRAINED_FEATURES:
                transformed_names.append(f"missingindicator__{feat}")

            # 2. TreeSHAP computation
            shap_raw = self.explainer.shap_values(X_trans)

            # Identify target class 1 (Parkinson's Disease) index in classifier.classes_
            classes = list(getattr(classifier, "classes_", [0, 1]))
            pd_class_idx = 1
            for i, c_val in enumerate(classes):
                if int(c_val) == 1 or str(c_val).lower().startswith("p"):
                    pd_class_idx = i
                    break

            # Extract SHAP array for sample 0 and class 1
            if isinstance(shap_raw, list):
                sample_shap = np.array(shap_raw[pd_class_idx][0])
                base_val = float(self.explainer.expected_value[pd_class_idx])
            elif hasattr(shap_raw, "values") and len(shap_raw.values.shape) == 3:
                sample_shap = shap_raw.values[0, :, pd_class_idx]
                base_val = float(shap_raw.base_values[0, pd_class_idx])
            elif len(shap_raw.shape) == 3:
                sample_shap = shap_raw[0, :, pd_class_idx]
                base_val = float(self.explainer.expected_value[pd_class_idx])
            else:
                sample_shap = np.array(shap_raw[0])
                base_val = float(self.explainer.expected_value[pd_class_idx] if isinstance(self.explainer.expected_value, (list, np.ndarray)) else self.explainer.expected_value)

            # 3. Preserve raw 34 transformed SHAP features
            raw_transformed_shap: List[Dict[str, Any]] = []
            for name, val in zip(transformed_names, sample_shap):
                raw_transformed_shap.append({
                    "feature": name,
                    "shap_value": round(float(val), 4)
                })

            # 4. Aggregate original feature SHAP + missing indicator SHAP per original 17 features
            aggregated_shap: Dict[str, float] = {}
            for i, feat in enumerate(self.TRAINED_FEATURES):
                orig_val = float(sample_shap[i]) if i < len(sample_shap) else 0.0
                miss_val = float(sample_shap[i + 17]) if (i + 17) < len(sample_shap) else 0.0
                aggregated_shap[feat] = orig_val + miss_val

            # Sort features by absolute aggregated magnitude
            sorted_feats = sorted(
                aggregated_shap.items(),
                key=lambda item: abs(item[1]),
                reverse=True
            )

            top_features = []
            for feat_name, shap_val in sorted_feats[:5]:
                is_positive = shap_val >= 0
                dir_str = "toward_parkinsons_disease" if is_positive else "away_from_parkinsons_disease"
                val_raw = feature_values_used.get(feat_name)
                val_display = "Missing" if val_raw is None or (isinstance(val_raw, float) and np.isnan(val_raw)) else str(val_raw)

                # Non-causal explanation phrasing
                contribution_direction = "toward" if is_positive else "away from"
                explanation_str = (
                    f"Feature '{feat_name}' with value {val_display} contributed "
                    f"{contribution_direction} the model's Parkinson's Disease prediction."
                )

                top_features.append({
                    "feature": feat_name,
                    "feature_value": val_raw,
                    "shap_value": round(float(shap_val), 4),
                    "absolute_importance": round(abs(float(shap_val)), 4),
                    "direction": dir_str,
                    "explanation": explanation_str,
                })

            return {
                "method": "SHAP TreeExplainer",
                "model_type": "RandomForestClassifier",
                "base_value": round(base_val, 4),
                "raw_transformed_shap": raw_transformed_shap,
                "top_features": top_features,
                "aggregation_note": (
                    "Top features represent aggregated human-readable attributions combining original "
                    "feature and missingness-indicator SHAP values."
                ),
            }

        except Exception as e:
            logger.error("ParkinsonPredictor: SHAP calculation failed — %s", e, exc_info=True)
            return None

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs prediction pipeline on incoming features dictionary.

        Args:
            features: Dict containing optional Parkinson clinical feature keys.

        Returns:
            Dict containing prediction label, probabilities, model metadata,
            feature availability tracking metadata, SHAP explanation, and notice.
        """
        if self.model is None:
            raise RuntimeError("Parkinson model is not loaded. Call load_model() first.")

        # 1. Feature availability tracking & validation
        present_features: List[str] = []
        missing_features: List[str] = []
        feature_values_used: Dict[str, Any] = {}
        row_dict: Dict[str, List[Any]] = {}

        for feat in self.TRAINED_FEATURES:
            val = features.get(feat)
            # Normalize empty strings or None to NaN
            if val is None or val == "" or (isinstance(val, float) and np.isnan(val)):
                row_dict[feat] = [np.nan]
                feature_values_used[feat] = None
                missing_features.append(feat)
            else:
                try:
                    num_val = float(val)
                    row_dict[feat] = [num_val]
                    feature_values_used[feat] = num_val
                    present_features.append(feat)
                except (ValueError, TypeError):
                    row_dict[feat] = [np.nan]
                    feature_values_used[feat] = None
                    missing_features.append(feat)

        present_count = len(present_features)
        missing_count = len(missing_features)
        completeness_ratio = round(present_count / 17.0, 4)

        feature_availability = {
            "present_features_count": present_count,
            "missing_features_count": missing_count,
            "feature_completeness_ratio": completeness_ratio,
            "present_features": present_features,
            "missing_features": missing_features,
        }

        # 2. Create DataFrame with 17 trained features in exact column order
        df = pd.DataFrame(row_dict)

        # 3. Model Inference via sklearn pipeline
        try:
            pred_class_idx = int(self.model.predict(df)[0])
            proba_arr = self.model.predict_proba(df)[0]
        except Exception as e:
            raise RuntimeError(f"Parkinson model prediction failed: {str(e)}")

        hc_prob = round(float(proba_arr[0]), 4)
        pd_prob = round(float(proba_arr[1]), 4)

        predicted_label = "Parkinson's Disease" if pred_class_idx == 1 else "Healthy Control"

        # 4. Compute TreeSHAP explanation
        explainability = self._compute_shap_explanation(df, feature_values_used)

        return {
            "predicted_class": pred_class_idx,
            "predicted_label": predicted_label,
            "pd_probability": pd_prob,
            "healthy_control_probability": hc_prob,
            "probabilities": {
                "Healthy Control": hc_prob,
                "Parkinson's Disease": pd_prob,
            },
            "model": {
                "name": self.metadata.get("model_name", "Random Forest") if self.metadata else "Random Forest",
                "version": self.metadata.get("model_version", "1.0") if self.metadata else "1.0",
            },
            "feature_values_used": feature_values_used,
            "feature_availability": feature_availability,
            "clinical_notice": (
                "Model explanations describe how the model arrived at its prediction and do not establish "
                "causation or provide a clinical diagnosis."
            ),
            "explainability": explainability,
        }
