"""
backend/models/parkinson_schemas.py

Pydantic schemas for Parkinson's Disease Random Forest predictor, SHAP explainability,
feature availability tracking, and API endpoints.

Design principles:
  - Isolated from ADNI schemas.
  - 17 trained features optional to allow missing values.
  - Tracks feature completeness explicitly without fabricating missing inputs.
  - Preserves 34 raw SHAP transformed features as well as top 5 aggregated features.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ParkinsonPredictionRequest(BaseModel):
    AGE_AT_VISIT: Optional[float] = Field(None, description="Age at visit in years")
    EDUCYRS: Optional[float] = Field(None, description="Years of education")
    NP1RTOT: Optional[float] = Field(None, description="MDS-UPDRS Part I total score")
    NP2PTOT: Optional[float] = Field(None, description="MDS-UPDRS Part II total score")
    NP3TOT: Optional[float] = Field(None, description="MDS-UPDRS Part III total score")
    NHY: Optional[float] = Field(None, description="Hoehn and Yahr stage")
    MCATOT: Optional[float] = Field(None, description="Montreal Cognitive Assessment total score")
    GDS_TOTAL: Optional[float] = Field(None, description="Geriatric Depression Scale total score")
    ESS_TOTAL: Optional[float] = Field(None, description="Epworth Sleepiness Scale total score")
    RBD_TOTAL: Optional[float] = Field(None, description="REM Sleep Behavior Disorder questionnaire total score")
    SDMTOTAL: Optional[float] = Field(None, description="Symbol Digit Modalities Test total score")
    DVT_TOTAL_RECALL: Optional[float] = Field(None, description="Benton Judgment / DVT Total Recall score")
    DVT_DELAYED_RECALL: Optional[float] = Field(None, description="Benton Judgment / DVT Delayed Recall score")
    LNS_TOTRAW: Optional[float] = Field(None, description="Letter-Number Sequencing total raw score")
    TMTASEC: Optional[float] = Field(None, description="Trail Making Test A duration in seconds")
    TMTBSEC: Optional[float] = Field(None, description="Trail Making Test B duration in seconds")
    SCOPA_AUT_TOTAL: Optional[float] = Field(None, description="SCOPA-AUT autonomic total score")
    clinical_question: Optional[str] = Field(None, description="Optional clinical question for the LLM agent")


class ParkinsonModelInfo(BaseModel):
    name: str = Field("Random Forest", description="Model algorithm name")
    version: str = Field("1.0", description="Model version")


class FeatureAvailabilityMetadata(BaseModel):
    present_features_count: int = Field(..., description="Number of trained features provided with non-null values")
    missing_features_count: int = Field(..., description="Number of trained features missing/unprovided")
    feature_completeness_ratio: float = Field(..., description="Ratio of present features to total 17 features (0.0 to 1.0)")
    present_features: List[str] = Field(default_factory=list, description="List of feature names provided")
    missing_features: List[str] = Field(default_factory=list, description="List of feature names missing")


class TransformedShapFeature(BaseModel):
    feature: str = Field(..., description="Transformed feature name (original or missing indicator)")
    shap_value: float = Field(..., description="Raw SHAP attribution value for class 1 (Parkinson's Disease)")


class ParkinsonShapFeatureContribution(BaseModel):
    feature: str = Field(..., description="Original clinical feature name")
    feature_value: Optional[Any] = Field(None, description="Input value of the feature (or None if missing)")
    shap_value: float = Field(..., description="Aggregated SHAP attribution value for class 1 (Parkinson's Disease)")
    absolute_importance: float = Field(..., description="Absolute magnitude of aggregated SHAP value")
    direction: str = Field(..., description="Direction: toward_parkinsons_disease or away_from_parkinsons_disease")
    explanation: str = Field(..., description="Non-causal human-readable explanation")


class ParkinsonSHAPExplainability(BaseModel):
    method: str = Field("SHAP TreeExplainer", description="Explainability method used")
    model_type: str = Field("RandomForestClassifier", description="Model architecture")
    base_value: float = Field(..., description="Expected value for class 1 (Parkinson's Disease)")
    raw_transformed_shap: List[TransformedShapFeature] = Field(
        default_factory=list,
        description="Preserved raw SHAP attributions for all 34 transformed features"
    )
    top_features: List[ParkinsonShapFeatureContribution] = Field(
        default_factory=list,
        description="Top 5 human-readable feature contributions aggregated from original + missingness indicator SHAP values"
    )
    aggregation_note: str = Field(
        "Top features represent aggregated human-readable attributions combining original feature and missingness-indicator SHAP values.",
        description="Methodological note explaining feature aggregation"
    )


class ParkinsonPredictionResponse(BaseModel):
    predicted_class: int = Field(..., description="Predicted class index: 0 (Healthy Control) or 1 (Parkinson's Disease)")
    predicted_label: str = Field(..., description="Predicted label: Healthy Control or Parkinson's Disease")
    pd_probability: float = Field(..., description="Probability of Parkinson's Disease")
    healthy_control_probability: float = Field(..., description="Probability of Healthy Control")
    probabilities: Dict[str, float] = Field(..., description="Probabilities for each class")
    model: ParkinsonModelInfo
    feature_values_used: Dict[str, Any] = Field(..., description="Input feature values used")
    feature_availability: FeatureAvailabilityMetadata = Field(..., description="Feature completeness metadata")
    clinical_notice: str = Field(
        "Model explanations describe how the model arrived at its prediction and do not establish causation or provide a clinical diagnosis.",
        description="Clinical disclaimer"
    )
    explainability: Optional[ParkinsonSHAPExplainability] = None
