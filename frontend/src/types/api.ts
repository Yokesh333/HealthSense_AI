export interface ClinicalFeatures {
  AGE?: number | null;
  EDUCATION?: number | null;
  ADAS?: number | null;
  CDR?: number | null;
  FAQ?: number | null;
  MMSE?: number | null;
  MOCA?: number | null;
  SEX?: string | null;
  RACE?: string | null;
  ETHNICITY?: string | null;
  clinical_question?: string | null;
}

export interface PatientInformation {
  age?: number | null;
  sex?: string | null;
  education?: number | null;
  race?: string | null;
  ethnicity?: string | null;
}

export interface ClinicalScores {
  mmse?: number | null;
  moca?: number | null;
  cdr?: number | null;
  adas?: number | null;
  faq?: number | null;
  updrs?: number | null;
  hoehn_yahr?: string | null;
  other_scores?: Record<string, any>;
}

export interface CognitiveFindings {
  memory_impairment?: boolean | null;
  executive_dysfunction?: boolean | null;
  language_deficits?: boolean | null;
  details?: string[];
}

export interface MotorFindings {
  resting_tremor?: boolean | null;
  bradykinesia?: boolean | null;
  rigidity?: boolean | null;
  gait_postural_instability?: boolean | null;
  details?: string[];
}

export interface ImagingFinding {
  modality: string;
  finding: string;
  source_page?: number | null;
}

export interface StructuredClinicalProfile {
  disease_context: string[];
  patient_information: PatientInformation;
  clinical_scores: ClinicalScores;
  cognitive_findings: CognitiveFindings;
  motor_findings: MotorFindings;
  symptoms: string[];
  duration?: string | null;
  imaging_findings: ImagingFinding[];
  laboratory_findings: string[];
  medications: string[];
  family_history: string[];
  clinical_impression?: string | null;
  source_pages?: Record<string, number[]>;
  missing_information: string[];
}

export interface MLPrediction {
  class: "CN" | "MCI" | "AD";        // actual JSON key from backend (PredictionSummary alias)
  predicted_class?: "CN" | "MCI" | "AD"; // alias for backward compat (undefined in real responses)
  probabilities: {
    CN: number;
    MCI: number;
    AD: number;
  };
  explainability?: SHAPExplainability;
}

export interface RAGChunk {
  text: string;
  source: string;
  page: number;
  score: number;
  category?: string;
  disease_context?: string;
  disease?: string;
}

export interface WebSearchResult {
  title: string;
  url: string;
  source: string;
  domain: string;
  published_date: string;
  snippet: string;
  trust_indicator: string;
}

export interface LLMExplanation {
  what_results_suggest: string;
  why_relevant: string;
  what_research_says: string[];
  next_steps: string[];
  clinical_notice: string;
}

export interface ShapFeatureContribution {
  feature: string;
  feature_value?: any;
  shap_value: number;
  absolute_importance: number;
  direction: string;
}

export interface SHAPExplainability {
  method: string;
  model_type: string;
  base_value: number;
  top_features: ShapFeatureContribution[];
}

export interface ParkinsonShapFeatureContribution {
  feature: string;
  feature_value?: any;
  shap_value: number;
  absolute_importance: number;
  direction: string;
  explanation: string;
}

export interface TransformedShapFeature {
  feature: string;
  shap_value: number;
}

export interface ParkinsonSHAPExplainability {
  method: string;
  model_type: string;
  base_value: number;
  raw_transformed_shap?: TransformedShapFeature[];
  top_features: ParkinsonShapFeatureContribution[];
  aggregation_note?: string;
}

export interface FeatureAvailabilityMetadata {
  present_features_count: number;
  missing_features_count: number;
  feature_completeness_ratio: number;
  present_features: string[];
  missing_features: string[];
}

export interface ParkinsonPrediction {
  predicted_class: number;
  predicted_label: string;
  pd_probability: number;
  healthy_control_probability: number;
  probabilities: {
    "Healthy Control": number;
    "Parkinson's Disease": number;
  };
  model_name: string;
  model_version: string;
  feature_values_used?: Record<string, any>;
  feature_availability?: FeatureAvailabilityMetadata;
  clinical_notice?: string;
  explainability?: ParkinsonSHAPExplainability;
}

export interface AgentAnalysisResponse {
  workflow: string;
  status: "completed" | "failed";
  disease_context?: string[];
  prediction?: MLPrediction;
  parkinson_prediction?: ParkinsonPrediction;
  parkinson_explainability?: ParkinsonSHAPExplainability;
  questionnaire_profile?: any;
  model?: {
    name: string;
    version: string;
  };
  agents_executed: string[];
  explanation: LLMExplanation;
  evidence: RAGChunk[];
  web_evidence: WebSearchResult[];
  clinical_notice: string;
  explainability?: SHAPExplainability;
  errors: string[];
}

export type ScreeningType = "alzheimers" | "parkinsons" | "both";

export interface QuestionnaireItem {
  id: string;
  domain: string;
  question: string;
  options: { label: string; value: number }[];
}

export interface QuestionnaireAnswer {
  question_id: string;
  answer: string;
}

export interface QuestionnaireResponse {
  questionnaire_id: string;
  version: string;
  responses: QuestionnaireAnswer[];
}

export interface QuestionnaireData {
  questionnaire_id: string;
  version: string;
  items: QuestionnaireItem[];
  disease_context: string[];
}

export interface UnifiedAnalysisRequest {
  type: "ADNI_ML" | "QUESTIONNAIRE" | "CLINICAL_REPORT";
  adni_data?: ClinicalFeatures;
  questionnaire_data?: QuestionnaireResponse;
  clinical_profile?: StructuredClinicalProfile | Record<string, any>;
  disease_context?: string[];
}

export interface FollowUpSection {
  heading: string;
  content: string;
  key_points?: string[];
}

export interface FollowUpStructuredResponse {
  response_type?: "lifestyle" | "food" | "sleep" | "result_explanation" | "current_research" | "general";
  title?: string;
  summary?: string;
  sections?: FollowUpSection[];
  evidence_note?: string;
  clinical_notice?: string;
}

export interface FollowUpRequest {
  question: string;
  disease_context?: string[];
  previous_explanation?: LLMExplanation;
  screening_context?: any;
}

export interface FollowUpResponse {
  answer: string;
  response?: string;
  structured?: FollowUpStructuredResponse;
  web_evidence?: WebSearchResult[];
  rag_evidence?: RAGChunk[];
}
