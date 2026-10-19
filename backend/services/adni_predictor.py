import os
import json
import logging
import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ADNIPredictor:
    def __init__(self):
        # Resolve project root (assuming this file is in backend/services/)
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.model_path = self.base_dir / "models" / "adni_model.joblib"
        self.metadata_path = self.base_dir / "models" / "model_metadata.json"
        
        self.model = None
        self.metadata = None
        self.explainer = None
        self.feature_names = [
            "AGE", "EDUCATION", "ADAS", "CDR", "FAQ", 
            "MMSE", "MOCA", "SEX", "RACE", "ETHNICITY"
        ]
        
    def load_model(self):
        """Loads the model, metadata artifacts, and initializes the SHAP explainer."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {self.model_path}")
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Model metadata not found at {self.metadata_path}")
            
        try:
            self.model = joblib.load(self.model_path)
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
                
                    # Initialize SHAP TreeExplainer on the classifier step
            try:
                import shap
                classifier = self.model.named_steps["classifier"]
                self.explainer = shap.TreeExplainer(classifier)
                logger.info("ADNIPredictor: SHAP TreeExplainer initialized successfully.")
            except ImportError as e:
                logger.error(
                    "ADNIPredictor: SHAP not installed in this Python environment — "
                    "explainability will be unavailable. Install shap in the active venv: "
                    "pip install shap. Error: %s", e
                )
                self.explainer = None
            except Exception as e:
                logger.warning("ADNIPredictor: Could not initialize SHAP explainer — %s: %s", type(e).__name__, e)
                self.explainer = None
                
        except Exception as e:
            raise RuntimeError(f"Failed to load model artifacts: {str(e)}")

    def _compute_shap_explanation(
        self, df: pd.DataFrame, predicted_class: str, pred_idx: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Computes SHAP feature contributions for the given sample and predicted class.
        This operation is fault-tolerant and non-blocking.
        """
        if self.explainer is None:
            logger.warning(
                "ADNIPredictor: SHAP explainer is not initialized — "
                "explainability will be None. Ensure 'shap' is installed in the "
                "active Python environment used to start the backend."
            )
            return None

        try:
            preprocessor = self.model.named_steps["preprocessor"]
            classifier = self.model.named_steps["classifier"]

            # Preprocess sample
            X_transformed = preprocessor.transform(df)
            
            # Dynamic transformed feature retrieval
            transformed_names = list(preprocessor.get_feature_names_out())
            assert len(transformed_names) == X_transformed.shape[1], (
                f"Feature name count ({len(transformed_names)}) must match "
                f"transformed dimension ({X_transformed.shape[1]})."
            )

            # Robust class index lookup from classifier.classes_
            class_mapping = {0: "CN", 1: "MCI", 2: "AD"}
            classes = list(classifier.classes_)
            
            target_idx = None
            for i, c_val in enumerate(classes):
                try:
                    c_name = class_mapping.get(int(c_val), str(c_val))
                except (ValueError, TypeError):
                    c_name = str(c_val)
                if c_name == predicted_class or str(c_val) == str(pred_idx):
                    target_idx = i
                    break
            
            if target_idx is None:
                target_idx = int(pred_idx) if isinstance(pred_idx, (int, float)) else 0

            # SHAP values calculation
            shap_values_raw = self.explainer.shap_values(X_transformed)

            if isinstance(shap_values_raw, list):
                sample_shap_pred_class = shap_values_raw[target_idx][0]
                base_val = float(self.explainer.expected_value[target_idx])
            elif hasattr(shap_values_raw, "values") and len(shap_values_raw.values.shape) == 3:
                sample_shap_pred_class = shap_values_raw.values[0, :, target_idx]
                base_val = float(shap_values_raw.base_values[0, target_idx])
            elif len(shap_values_raw.shape) == 3:
                sample_shap_pred_class = shap_values_raw[0, :, target_idx]
                base_val = float(self.explainer.expected_value[target_idx])
            else:
                sample_shap_pred_class = shap_values_raw[0]
                base_val = float(self.explainer.expected_value)

            # Feature aggregation mapping to original 10 clinical features
            def get_root_feature(name: str) -> str:
                clean = name.replace("num__", "").replace("cat__", "")
                is_missing = "missingindicator_" in clean
                if is_missing:
                    clean = clean.replace("missingindicator_", "")
                
                for orig in ["AGE", "EDUCATION", "ADAS", "CDR", "FAQ", "MMSE", "MOCA", "SEX", "RACE", "ETHNICITY"]:
                    if clean.startswith(orig):
                        if is_missing:
                            return f"{orig} (missing indicator)"
                        return orig
                return clean

            feature_shap_map: Dict[str, float] = {}
            for t_name, val in zip(transformed_names, sample_shap_pred_class):
                root = get_root_feature(t_name)
                feature_shap_map[root] = feature_shap_map.get(root, 0.0) + float(val)

            # Sort features by absolute SHAP magnitude
            sorted_features = sorted(
                feature_shap_map.items(),
                key=lambda item: abs(item[1]),
                reverse=True
            )

            top_features = []
            for feat_name, val in sorted_features[:5]:
                direction_label = f"toward_{predicted_class}" if val >= 0 else f"away_from_{predicted_class}"
                clean_feat = feat_name.split(" ")[0]
                f_val = df[clean_feat].iloc[0] if (clean_feat in df.columns) else None
                if pd.isna(f_val):
                    f_val = None
                top_features.append({
                    "feature": feat_name,
                    "feature_value": f_val,
                    "shap_value": round(val, 4),
                    "absolute_importance": round(abs(val), 4),
                    "direction": direction_label
                })

            return {
                "method": "SHAP",
                "model_type": "RandomForestClassifier",
                "base_value": round(base_val, 4),
                "top_features": top_features
            }

        except Exception as e:
            logger.error(
                "ADNIPredictor: SHAP calculation failed — %s: %s",
                type(e).__name__, e, exc_info=True
            )
            logger.error(
                "ADNIPredictor: SHAP diagnostics — "
                "shap_version=%s  sklearn_version=%s  model_type=%s  "
                "transformed_shape=%s  predicted_class=%s  pred_idx=%s",
                getattr(__import__('shap'), '__version__', 'N/A'),
                getattr(__import__('sklearn'), '__version__', 'N/A'),
                type(self.model.named_steps.get('classifier', None)).__name__,
                getattr(df, 'shape', 'N/A'),
                predicted_class,
                pred_idx,
            )
            return None

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the prediction pipeline and attaches SHAP explainability.
        
        Args:
            features: Dictionary containing the 10 specific clinical features.
            
        Returns:
            Dictionary with prediction, probabilities, model metadata, clinical notice, and optional explainability.
        """
        if self.model is None or self.metadata is None:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
            
        # Ensure only required features are passed and in the correct order
        try:
            input_data = {feature: [features[feature]] for feature in self.feature_names}
        except KeyError as e:
            raise ValueError(f"Missing required feature: {e}")
            
        # Create DataFrame
        df = pd.DataFrame(input_data)
        
        # Predict
        try:
            pred_idx = self.model.predict(df)[0]
            proba_array = self.model.predict_proba(df)[0]
        except Exception as e:
            raise RuntimeError(f"Model prediction failed: {str(e)}")
            
        # Map prediction index to human-readable class using model.classes_
        class_mapping = {0: "CN", 1: "MCI", 2: "AD"}
        
        # In case the model was trained with string labels directly
        if hasattr(self.model, "classes_"):
            classes = self.model.classes_
            
            try:
                pred_int = int(pred_idx)
                if pred_int in class_mapping:
                    predicted_class = class_mapping[pred_int]
                else:
                    predicted_class = str(pred_idx)
            except (ValueError, TypeError):
                predicted_class = str(pred_idx)
                
            probabilities = {}
            for idx, c_val in enumerate(classes):
                try:
                    c_int = int(c_val)
                    class_name = class_mapping.get(c_int, str(c_val))
                except (ValueError, TypeError):
                    class_name = str(c_val)
                probabilities[class_name] = round(float(proba_array[idx]), 4)
        else:
            # Fallback if classes_ is not available
            predicted_class = class_mapping.get(int(pred_idx), "Unknown")
            probabilities = {
                "CN": round(float(proba_array[0]), 4) if len(proba_array) > 0 else 0.0,
                "MCI": round(float(proba_array[1]), 4) if len(proba_array) > 1 else 0.0,
                "AD": round(float(proba_array[2]), 4) if len(proba_array) > 2 else 0.0,
            }

        # Compute SHAP explanation non-blockingly
        try:
            explainability = self._compute_shap_explanation(df, predicted_class, pred_idx)
        except Exception as exc:
            import traceback
            logger.error(f"ADNIPredictor: SHAP calculation failed non-blockingly — {exc}")
            logger.error(f"SHAP Error Traceback: {traceback.format_exc()}")
            explainability = None
            
        return {
            "prediction": predicted_class,
            "probabilities": probabilities,
            "model": {
                "name": self.metadata.get("model_name", "Unknown"),
                "version": self.metadata.get("model_version", "Unknown")
            },
            "clinical_notice": "Research prototype classification — not a medical diagnosis.",
            "explainability": explainability
        }

