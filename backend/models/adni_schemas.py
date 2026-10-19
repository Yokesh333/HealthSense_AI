from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ADNIPredictionRequest(BaseModel):
    AGE: float = Field(..., description="Age in years")
    EDUCATION: float = Field(..., description="Years of education")
    ADAS: Optional[float] = Field(None, description="ADAS score")
    CDR: float = Field(..., description="Clinical Dementia Rating")
    FAQ: Optional[float] = Field(None, description="Functional Assessment Questionnaire")
    MMSE: float = Field(..., description="Mini-Mental State Examination")
    MOCA: Optional[float] = Field(None, description="Montreal Cognitive Assessment")
    SEX: str = Field(..., description="Sex (e.g., Male, Female)")
    RACE: str = Field(..., description="Race category")
    ETHNICITY: str = Field(..., description="Ethnicity category")
    clinical_question: Optional[str] = Field(None, description="Optional clinical question for the LLM agent")

class ModelInfo(BaseModel):
    name: str
    version: str

class WebSearchResult(BaseModel):
    title: str
    url: str
    source: str
    domain: str
    published_date: Optional[str] = None
    snippet: str
    trust_indicator: str

class ShapFeatureContribution(BaseModel):
    feature: str = Field(..., description="Original clinical feature name or semantic detail")
    feature_value: Optional[Any] = Field(None, description="Clinical value used for prediction (None if missing/imputed)")
    shap_value: float = Field(..., description="SHAP attribution value for the predicted class")
    absolute_importance: float = Field(..., description="Absolute SHAP magnitude")
    direction: str = Field(..., description="Direction relative to predicted class (toward_X or away_from_X)")

class SHAPExplainability(BaseModel):
    method: str = Field("SHAP", description="Explainability method used")
    model_type: str = Field("RandomForestClassifier", description="Model architecture")
    base_value: float = Field(..., description="Class-specific base/expected value")
    top_features: List[ShapFeatureContribution] = Field(default_factory=list, description="Top contributing features sorted by magnitude")

class ADNIPredictionResponse(BaseModel):
    prediction: str = Field(..., description="Predicted class: CN, MCI, or AD")
    probabilities: Dict[str, float] = Field(..., description="Probabilities for each class")
    model: ModelInfo
    clinical_notice: str = Field(..., description="Clinical disclaimer")
    explainability: Optional[SHAPExplainability] = None

class QuestionnaireAnswer(BaseModel):
    question_id: str
    answer: str

class QuestionnaireResponse(BaseModel):
    questionnaire_id: str
    version: str
    responses: List[QuestionnaireAnswer]

class QuestionnaireProfile(BaseModel):
    questionnaire_id: str
    version: str = "1.0"
    responses: List[QuestionnaireAnswer] = Field(default_factory=list)
    questionnaire_score: int
    questionnaire_max_score: int
    symptom_burden: str
    positive_findings: List[str] = Field(default_factory=list)
    negative_findings: List[str] = Field(default_factory=list)
    disease_context: List[str] = Field(default_factory=list)


from backend.models.parkinson_schemas import ParkinsonPredictionRequest


class UnifiedAnalysisRequest(BaseModel):
    type: str = Field(..., description="ADNI_ML, PARKINSON_ML, QUESTIONNAIRE, or CLINICAL_REPORT")
    adni_data: Optional[ADNIPredictionRequest] = None
    parkinson_data: Optional[ParkinsonPredictionRequest] = None
    questionnaire_data: Optional[QuestionnaireResponse] = None
    clinical_profile: Optional[Dict[str, Any]] = None
    disease_context: Optional[List[str]] = Field(default_factory=list, description="List of active disease contexts")

class FollowUpSection(BaseModel):
    heading: str
    content: str
    key_points: List[str] = Field(default_factory=list)

class FollowUpStructuredData(BaseModel):
    response_type: str = Field("general", description="lifestyle, food, sleep, result_explanation, current_research, or general")
    title: str
    summary: str
    sections: List[FollowUpSection] = Field(default_factory=list)
    evidence_note: Optional[str] = None
    clinical_notice: Optional[str] = None

class FollowUpRequest(BaseModel):
    chat_history: List[Dict[str, str]] = Field(default_factory=list)
    question: str = Field(..., description="User's follow-up question")
    disease_context: List[str] = Field(default_factory=list, description="List of active disease contexts")
    previous_explanation: Optional[Dict[str, Any]] = None
    screening_context: Optional[Dict[str, Any]] = None

class FollowUpResponse(BaseModel):
    answer: str
    response: str
    structured: Optional[FollowUpStructuredData] = None
    rag_evidence: Optional[List[Dict[str, Any]]] = None
    web_evidence: Optional[List[Dict[str, Any]]] = None
