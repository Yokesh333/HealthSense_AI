"""
backend/models/report_schemas.py

Pydantic schemas representing the Stage-1 extracted Structured Clinical Profile.

Design principles:
- Explicit typed sub-models for patient info, clinical scores, findings, imaging.
- All fields Optional or with default empty factories to prevent false inferences.
- Never fabricates missing numerical values or clinical status.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PatientInformation(BaseModel):
    """Demographic and basic patient information explicitly found in report."""
    age: Optional[float] = Field(None, description="Age in years if stated")
    sex: Optional[str] = Field(None, description="Sex if stated (e.g. Male, Female)")
    education: Optional[float] = Field(None, description="Years of education if stated")
    race: Optional[str] = Field(None, description="Race category if stated")
    ethnicity: Optional[str] = Field(None, description="Ethnicity category if stated")


class ClinicalScores(BaseModel):
    """Explicitly reported objective clinical examination scores."""
    mmse: Optional[float] = Field(None, description="Mini-Mental State Examination score")
    moca: Optional[float] = Field(None, description="Montreal Cognitive Assessment score")
    cdr: Optional[float] = Field(None, description="Clinical Dementia Rating score")
    adas: Optional[float] = Field(None, description="ADAS-Cog score")
    faq: Optional[float] = Field(None, description="Functional Assessment Questionnaire score")
    updrs: Optional[float] = Field(None, description="Unified Parkinson's Disease Rating Scale score")
    hoehn_yahr: Optional[str] = Field(None, description="Hoehn & Yahr stage if stated")
    other_scores: Dict[str, Any] = Field(default_factory=dict, description="Other explicit numerical scores")


class CognitiveFindings(BaseModel):
    """Cognitive impairment findings explicitly reported."""
    memory_impairment: Optional[bool] = Field(None, description="Memory impairment reported")
    executive_dysfunction: Optional[bool] = Field(None, description="Executive dysfunction reported")
    language_deficits: Optional[bool] = Field(None, description="Language deficits reported")
    details: List[str] = Field(default_factory=list, description="Descriptive cognitive findings")


class MotorFindings(BaseModel):
    """Motor / neurological findings explicitly reported."""
    resting_tremor: Optional[bool] = Field(None, description="Resting tremor reported")
    bradykinesia: Optional[bool] = Field(None, description="Bradykinesia / slowness reported")
    rigidity: Optional[bool] = Field(None, description="Rigidity / stiffness reported")
    gait_postural_instability: Optional[bool] = Field(None, description="Gait / postural instability reported")
    details: List[str] = Field(default_factory=list, description="Descriptive motor findings")


class ImagingFinding(BaseModel):
    """Explicit imaging report findings (MRI, CT, DaTSCAN, PET)."""
    modality: str = Field(..., description="Imaging modality e.g. MRI, DaTSCAN")
    finding: str = Field(..., description="Key radiological finding")
    source_page: Optional[int] = Field(None, description="Page number where reported")


class StructuredClinicalProfile(BaseModel):
    """
    Top-level structured clinical report extracted by Stage-1 LLM.
    """
    disease_context: List[str] = Field(
        default_factory=list,
        description="List of detected disease contexts: ['alzheimers'], ['parkinsons'], ['alzheimers', 'parkinsons'], or ['unknown']"
    )
    patient_information: PatientInformation = Field(default_factory=PatientInformation)
    clinical_scores: ClinicalScores = Field(default_factory=ClinicalScores)
    cognitive_findings: CognitiveFindings = Field(default_factory=CognitiveFindings)
    motor_findings: MotorFindings = Field(default_factory=MotorFindings)
    symptoms: List[str] = Field(default_factory=list, description="Explicit symptoms reported")
    duration: Optional[str] = Field(None, description="Duration of symptoms if stated")
    imaging_findings: List[ImagingFinding] = Field(default_factory=list, description="Imaging findings")
    laboratory_findings: List[str] = Field(default_factory=list, description="Lab / biomarker findings")
    medications: List[str] = Field(default_factory=list, description="Current medications")
    family_history: List[str] = Field(default_factory=list, description="Family medical history")
    clinical_impression: Optional[str] = Field(None, description="Diagnosing physician impression or conclusion")
    source_pages: Dict[str, Any] = Field(default_factory=dict, description="Page mapping for key sections")
    missing_information: List[str] = Field(default_factory=list, description="Key unstated clinical variables")
