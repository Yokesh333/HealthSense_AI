"""
backend/agents/state.py

Typed Pydantic models representing the shared state that flows through the
multi-agent orchestration pipeline.

Design principles:
  - All fields are explicitly typed — no uncontrolled dicts.
  - Optional fields are used where future agents will populate data.
  - Single source of truth for the workflow state shape.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.models.adni_schemas import ModelInfo, WebSearchResult, SHAPExplainability
from backend.models.parkinson_schemas import (
    ParkinsonPredictionRequest,
    ParkinsonSHAPExplainability,
    FeatureAvailabilityMetadata,
)


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

class ADNIClinicalFeatures(BaseModel):
    """Validated ADNI clinical features passed into the workflow."""

    AGE: float
    EDUCATION: float
    ADAS: Optional[float] = None
    CDR: float
    FAQ: Optional[float] = None
    MMSE: float
    MOCA: Optional[float] = None
    SEX: str
    RACE: str
    ETHNICITY: str
    clinical_question: Optional[str] = None


class ParkinsonClinicalFeatures(ParkinsonPredictionRequest):
    """Validated Parkinson clinical features passed into the workflow."""
    pass


# ---------------------------------------------------------------------------
# ML prediction results
# ---------------------------------------------------------------------------

class MLPredictionResult(BaseModel):
    """Structured output from the ADNI ML prediction step."""

    predicted_class: str = Field(..., description="Predicted class: CN, MCI, or AD")
    probabilities: Dict[str, float] = Field(
        ..., description="Per-class probabilities"
    )
    model_name: str
    model_version: str
    clinical_notice: str
    explainability: Optional[SHAPExplainability] = None


class ParkinsonMLPredictionResult(BaseModel):
    """Structured output from the Parkinson ML prediction step."""

    predicted_class: int = Field(..., description="Predicted class index: 0 or 1")
    predicted_label: str = Field(..., description="Predicted label: Healthy Control or Parkinson's Disease")
    pd_probability: float = Field(..., description="Probability of Parkinson's Disease")
    healthy_control_probability: float = Field(..., description="Probability of Healthy Control")
    probabilities: Dict[str, float] = Field(..., description="Probabilities for each class")
    model_name: str
    model_version: str
    feature_values_used: Dict[str, Any]
    feature_availability: FeatureAvailabilityMetadata
    clinical_notice: str
    explainability: Optional[ParkinsonSHAPExplainability] = None


# ---------------------------------------------------------------------------
# Per-agent execution record
# ---------------------------------------------------------------------------

class AgentResult(BaseModel):
    """Record of a single agent's execution within the workflow."""

    agent_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None   # Agent-specific structured output
    error: Optional[str] = None             # Error message if success=False


# ---------------------------------------------------------------------------
# Workflow state — the envelope passed between orchestrator and agents
# ---------------------------------------------------------------------------

class AgentState(BaseModel):
    """
    Top-level workflow state.

    The orchestrator initialises this, passes it to each agent, and agents
    populate their section before returning an AgentResult.
    """

    workflow: str = "ADNI_ANALYSIS"
    disease_context: List[str] = Field(default_factory=list)
    chat_history: List[Dict[str, str]] = Field(default_factory=list)
    clinical_features: Optional[ADNIClinicalFeatures] = None
    parkinson_features: Optional[ParkinsonClinicalFeatures] = None
    questionnaire_results: Optional[Dict[str, Any]] = None
    questionnaire_profile: Optional[Dict[str, Any]] = None
    clinical_profile: Optional[Dict[str, Any]] = None

    # Results populated by agents
    agent_results: List[AgentResult] = Field(default_factory=list)
    ml_prediction: Optional[MLPredictionResult] = None
    parkinson_prediction: Optional[ParkinsonMLPredictionResult] = None

    # Future & Synthesis agent slots
    rag_results: Optional[Dict[str, Any]] = None
    web_intelligence_results: Optional[Dict[str, Any]] = None
    clinical_synthesis: Optional[Dict[str, Any]] = None
    
    # LLM
    llm_response: Optional[Dict[str, Any]] = None
    final_explanation: Optional[Dict[str, Any]] = None
    
    # Web
    web_results: Optional[List[Dict[str, Any]]] = None

    # Diagnostics
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Final API response
# ---------------------------------------------------------------------------

class PredictionSummary(BaseModel):
    """Prediction class and per-class probabilities for the API response."""

    predicted_class: str = Field(..., alias="class")
    probabilities: Dict[str, float]

    model_config = {"populate_by_name": True}


class ModelInfo(BaseModel):
    name: str
    version: str


class AgentAnalysisResponse(BaseModel):
    """
    Structured response returned by POST /api/agents/analyze.
    """

    workflow: str
    status: str                              # "completed" | "failed"
    disease_context: List[str] = Field(default_factory=list)
    prediction: Optional[PredictionSummary] = None
    model: Optional[ModelInfo] = None
    parkinson_prediction: Optional[Dict[str, Any]] = None
    parkinson_explainability: Optional[ParkinsonSHAPExplainability] = None
    questionnaire_profile: Optional[Dict[str, Any]] = None
    explanation: Optional[Dict[str, Any]] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    web_evidence: List[WebSearchResult] = Field(default_factory=list)
    agents_executed: List[str]
    clinical_notice: Optional[str] = None
    explainability: Optional[SHAPExplainability] = None
    errors: List[str] = Field(default_factory=list)
