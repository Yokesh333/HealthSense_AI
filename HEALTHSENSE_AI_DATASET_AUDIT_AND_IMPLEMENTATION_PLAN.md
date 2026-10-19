# HEALTHSENSE AI: DATASET AUDIT AND IMPLEMENTATION PLAN

## 1. Executive Summary
An exhaustive read-only audit of the `HealthSense AI` datasets was conducted. The project folder contains over 15,000 files, including high-quality longitudinal clinical, imaging, and cognitive datasets from ADNI and PPMI. Unstructured datasets like MRI scans and voice recordings are also present. The data strongly supports predictive modeling for Alzheimer’s disease (via ADNI) and Parkinson’s disease (via PPMI) using structured tabular data. A 16-phase implementation plan has been designed to transition this raw data into a multi-agent clinical decision support system.

## 2. Current Project Status
- **Phase 1 Completed**: Folder structure, virtual environment, FastAPI backend, environment files, requirements, and Git repository are established.
- **Audit Phase**: Data has been profiled without modification. No models have been trained.

## 3. Dataset Inventory
- **Total Files**: 15,105
- **ADNI**: 22 CSV files (Cognitive, Medical History, Subject Demographics, Imaging derived).
- **PPMI**: 37 CSV files (Motor/Non-motor, Enrollment, Family History, Demographics, Imaging derived).
- **Imaging**: 13,638 files (e.g., `Augmented Alzheimer MRI 4-Classes Dataset`, `.nii`, `.dcm`, `.jpg`).
- **Voice Data**: 1,134 `.wav` files (Parkinson's/Healthy).

## 4. ADNI Detailed Audit
- **Files**: Include `ADAS`, `CDR`, `FAQ`, `MMSE`, `MOCA`, `REGISTRY`, `INITHEALTH`, etc.
- **Size & Shape**: Datasets range from ~121 rows (`NEUROPATH`) to ~29,000 rows (`REGISTRY`).
- **Target**: `REGISTRY` contains `PTSTATUS` and `RGSTATUS`. `NEUROPATH` contains detailed pathology. 
- **Features**: Highly detailed cognitive scores, demographic data, and MRI volumetric measures.

## 5. PPMI Detailed Audit
- **Files**: `Primary_Research_Diagnosis`, `PD_Diagnosis_History`, `MDS-UPDRS` (Parts I-IV), Non-motor assessments (MoCA, Sleep, Geriatric Depression).
- **Size & Shape**: Datasets range from ~363 rows (`Grey_Matter_Volume`) to ~38,000 rows (`MDS-UPDRS_Part_III`).
- **Target**: `Primary_Research_Diagnosis` contains `PRIMDIAG` (Primary Diagnosis). `Participant_Status` contains `ENROLL_STATUS`.
- **Features**: Tremor, rigidity, bradykinesia scores, behavioral metrics, and MRI structural data.

## 6. Other Dataset Audit
- **MRI/Imaging (Augmented Alzheimer)**: Contains JPEG images sorted into classes (e.g., MildDemented). Cannot be trivially linked to ADNI subject metadata.
- **Voice Dataset**: Parkinson's telemonitoring voice `.wav` files. Cannot be directly linked to PPMI subjects due to lack of shared IDs.

## 7. File/Folder Relationships
- **ADNI**: Linked by `PTID` or `RID` across all tables.
- **PPMI**: Linked by `PATNO` across all tables.

## 8. Subject/Patient Identifier Analysis
- **ADNI**: Primary subject identifiers are `PTID` and `RID`.
- **PPMI**: Primary subject identifier is `PATNO`. 
- **Timepoints**: ADNI uses `VISCODE` / `VISCODE2`. PPMI uses `EVENT_ID`.

## 9. Target/Label Analysis
- **ADNI**: `PTSTATUS` (Patient Status) is the likely target for AD vs. MCI vs. CN.
- **PPMI**: `PRIMDIAG` (Primary Diagnosis) or `APPRDX` (Apparent Diagnosis) is the target for PD vs. Control.

## 10. Missing Data Analysis
- Longitudinal data naturally contains missing values when subjects miss follow-up visits or certain tests are only administered at baseline. `MDS-UPDRS` and `ADAS` show expected attrition.

## 11. Duplicate Analysis
- Rows are not strict duplicates; they represent distinct longitudinal visits (e.g., a subject appears multiple times but with different `VISCODE` or `EVENT_ID`). 

## 12. Longitudinal Data Analysis
- Both ADNI and PPMI are highly longitudinal. A single patient (`PATNO`/`PTID`) has a baseline visit (`EVENT_ID` = 1, or `VISCODE` = 'bl') and subsequent follow-ups (e.g., Month 12, Month 24).

## 13. Data Leakage Risks
- **CRITICAL RISK**: Randomly splitting rows into train/test will cause the same subject to appear in both sets, leading to severe data leakage. 
- **Mitigation**: Perform a **GroupKFold** or strict **Subject-Level Split**. Ensure all longitudinal records for a single `PATNO`/`PTID` remain in exactly one fold (train, val, or test).

## 14. Recommended Dataset Selection
- **PRIMARY**: ADNI (Structured tabular CSVs) & PPMI (Structured tabular CSVs). These contain the rich clinical history and diagnostic targets needed for the predictive agents.
- **SECONDARY**: ADNI & PPMI MRI derived measurements (e.g., `UASPMVBM`, `FS7_ASEG_VOL`). 
- **NOT RECOMMENDED**: Augmented Alzheimer MRI JPGs and Voice Datasets. (Complexity overhead is too high, and they cannot be reliably joined to the rich clinical tabular data. Including them violates the constraint of avoiding unnecessary complexity).

## 15. Recommended ML Tasks
- **AD Task**: Predict Alzheimer's status (Cognitively Normal [CN] vs. Mild Cognitive Impairment [MCI] vs. Alzheimer's Disease [AD]) based on ADNI baseline and 1-year clinical/cognitive data.
- **PD Task**: Predict Parkinson's Disease (PD vs. Healthy Control) based on PPMI MDS-UPDRS, cognitive, and demographic data.

## 16. Recommended Features
- **ADNI**: Age, Sex, Education, MMSE, MoCA, ADAS, CDR, FAQ, and MRI Volumetrics.
- **PPMI**: Age, Sex, MDS-UPDRS (Parts I-III), MoCA, Sleep scores, and Tremor/Rigidity clinical observations.

## 17. Recommended Preprocessing
1. **Join**: Merge tables on Subject ID + Visit ID.
2. **Filter**: Select baseline visit for basic models, or aggregate for temporal models.
3. **Impute**: Use median/mode imputation or iterative imputation for clinical scores. 
4. **Encode**: One-hot encode categorical features (Sex, Race).

## 18. Recommended ML Models
- Tree-based models (XGBoost, LightGBM, Random Forest) are highly recommended. They handle missing data well, don't require extensive scaling, and offer high explainability (feature importance/SHAP values) which is critical for clinical decision support.

## 19. RAG Data Strategy
- **Current Datasets**: Do NOT use clinical CSVs for RAG. 
- **Future Strategy**: Ingest public medical guidelines, neurology textbooks, recent PubMed abstracts on AD and PD, and treatment protocols into a Vector DB.

## 20. Web Intelligence Strategy
- Use tools like Tavily or Serper API to query live clinical trials, new drug approvals (e.g., Leqembi), or recent research dynamically.

## 21. Proposed HealthSense AI Architecture
- **Frontend**: React/Next.js interface for physicians.
- **Backend**: FastAPI.
- **ML Layer**: Pre-trained XGBoost models exposed via internal endpoints.
- **LLM/RAG Layer**: LangChain/LlamaIndex orchestration. 

## 22. Multi-Agent Architecture
1. **Clinical/Patient Agent**: Synthesizes the patient's raw EHR/clinical input into a structured narrative.
2. **Prediction Agent**: Formats data, calls the ML models (ADNI/PPMI), and extracts SHAP explanations.
3. **Biomedical RAG Agent**: Queries the vector database for established medical guidelines related to the patient's presentation.
4. **Web Intelligence Agent**: Searches the web for recent clinical trials or drug interactions.
5. **Reasoning/Decision Agent**: Receives inputs from all above agents, resolves conflicts, and generates a cohesive differential diagnosis.
6. **Response Agent**: Formats the final output for the clinician.

## 23. Complete Phase-by-Phase Implementation Plan
1. **Phase 1**: Project Foundation (Completed).
2. **Phase 2**: Dataset Audit (Completed).
3. **Phase 3**: Dataset Preparation & Merging (Join ADNI/PPMI tables, perform subject-level splits).
4. **Phase 4**: ML Modeling (Train XGBoost models for AD and PD, extract SHAP explainers).
5. **Phase 5**: RAG Pipeline Setup (Set up Vector DB, ingest medical guidelines).
6. **Phase 6**: Agent Implementation (Develop individual LangChain agents).
7. **Phase 7**: Multi-Agent Orchestration (Implement LangGraph or custom orchestrator).
8. **Phase 8**: FastAPI Integration (Expose agents and ML predictions via REST API).
9. **Phase 9**: Frontend Development (Build clinician dashboard).
10. **Phase 10**: System Integration & Testing (End-to-end evaluation).
11. **Phase 11**: Deployment (Dockerization, Cloud hosting).

## 24. Testing Strategy
- **Unit Tests**: Pytest for data preprocessing pipelines and API endpoints.
- **Integration Tests**: Ensure agents communicate without data loss.

## 25. Evaluation Strategy
- **ML**: ROC-AUC, F1-Score, and Calibration curves to measure clinical reliability.
- **RAG**: Answer Faithfulness (does the answer match the retrieved documents?) and Context Precision.
- **LLM/Agents**: Compare [LLM Only] vs [LLM + RAG] vs [Full Multi-Agent] using a golden set of 50 synthetic patient profiles to measure hallucination rates and clinical safety.

## 26. Deployment Strategy
- **Local/Open-Source**: Provide Docker-compose to run FastAPI, Postgres (pgvector), and a local LLM (e.g., Llama-3 via Ollama) for strict privacy.
- **Cloud**: AWS/GCP with Groq/OpenAI APIs abstracted behind a central `LLMService` interface allowing hot-swapping of providers.

## 27. Risks and Mitigations
- **Data Leakage**: Mitigated by strict subject-level splitting.
- **Hallucinations**: Mitigated by forcing the Reasoning Agent to cite sources from the RAG Agent.
- **Complexity**: Mitigated by dropping raw image/voice datasets and focusing on tabular data.

## 28. Questions/Decisions Requiring Confirmation
- Do you agree with dropping the Image and Voice datasets to focus on high-fidelity tabular predictive modeling?
- Should we use SQLite/ChromaDB for local development, or immediately set up Postgres/pgvector?

## 29. Final Recommended Implementation Order
1. Data Preprocessing (Phase 3)
2. ML Modeling (Phase 4)
3. RAG/Agent setup (Phases 5-7)
4. API & Frontend (Phases 8-9)

---

## CONCISE SUMMARY

CURRENT STATUS:
Phase 1 completed. Dataset audit finished. Datasets contain 15k+ files, with highly valuable longitudinal structured data in ADNI and PPMI.

NEXT PHASE:
Phase 3 - Dataset Preparation & Merging (Subject-level splitting and joining tables).

PRIMARY DATASETS:
ADNI structured CSVs (Cognitive, Medical, Demographics).
PPMI structured CSVs (UPDRS, Demographics, Diagnoses).

SECONDARY DATASETS:
ADNI/PPMI derived imaging volumetrics (CSV format).

DATASETS TO KEEP FOR FUTURE:
Augmented Alzheimer MRI images, Voice Dataset, PPMI raw MRI/DICOMs.

DATASETS NOT RECOMMENDED:
Using raw images or voice files in the core initial multi-agent architecture (adds unnecessary complexity without direct ID linkages to clinical data).

FIRST IMPLEMENTATION TASK:
Write Python scripts to cleanly merge ADNI cognitive/demographic tables on `PTID`/`VISCODE` and PPMI tables on `PATNO`/`EVENT_ID`, generating a single flattened baseline dataset for each disease.
