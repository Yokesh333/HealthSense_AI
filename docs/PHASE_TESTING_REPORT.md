# HealthSense AI - System Testing & Performance Verification Report

**Project:** HealthSense AI  
**Date:** October 5, 2026  
**Environment:** Windows 11 / Python 3.10.9 (venv) / Node.js 20.17.0 / Vite 8.2.2  
**Test Suite Status:** **92 / 92 Passed (100% Pass Rate)**  
**Frontend Build Status:** **SUCCESS (1.06s build time)**

---

## 1. Functional Testing

All functional components were tested using the `pytest` test suite and FastAPI TestClient.

| # | Feature / Subsystem | Test Objective | Status | Expected Result | Actual Result | Execution Time |
|---|---|---|---|---|---|---|
| 1.1 | **FastAPI Health Endpoint** | Verify `/health` service availability | **PASS** | Returns HTTP 200 with `{"status": "healthy"}` | HTTP 200 `{"status": "healthy"}` | <0.001s |
| 1.2 | **ADNI Risk Prediction** | Verify ADNI Random Forest inference | **PASS** | Returns predicted class (CN/MCI/AD) & valid probability distribution | Predicted `AD` (73.98% probability) | 0.030s |
| 1.3 | **Parkinson Risk Prediction** | Verify Parkinson Random Forest inference | **PASS** | Returns predicted label (`Healthy Control` / `Parkinson's Disease`) | Predicted `Healthy Control` (84.2% prob) | 0.159s |
| 1.4 | **SHAP Explainability** | Calculate SHAP feature attributions | **PASS** | Returns sorted list of top feature contributions per prediction | Returned top features (MMSE, CDR, ADAS) | 0.027s |
| 1.5 | **Questionnaire Screening** | Evaluate self-reported symptom questionnaires | **PASS** | Calculates score and returns structured domain breakdown | Generated domain profile for Alzheimer's & Parkinson's | 0.005s |
| 1.6 | **PDF Report Extraction** | PyMuPDF text & Stage-1 LLM extraction | **PASS** | Extracts text and parses into `StructuredClinicalProfile` | Extracted 617 words across 2 pages | 0.420s |
| 1.7 | **Biomedical RAG Retrieval** | FAISS L2 similarity search (384-dim) | **PASS** | Retrieves top-k relevant clinical guideline chunks matching query | Retrieved 5 chunks (`guidelines1.pdf`, score=0.6403) | 0.022s |
| 1.8 | **PubMed Web Intelligence** | Query NCBI E-utilities API | **PASS** | Retrieves recent peer-reviewed articles matching query terms | Retrieved 5 recent PubMed articles | 0.741s |
| 1.9 | **Groq LLM Synthesis** | Executive summary via `openai/gpt-oss-120b` | **PASS** | Generates structured JSON summary matching expected schema | Returned valid JSON executive summary | 2.654s |
| 1.10| **Response Sanitization** | Post-synthesis safety validation | **PASS** | Scrubs unsupported diagnostic claims and questionnaire leaks | Applied soft substitution of unsupported phrases | 0.002s |

---

## 2. Integration Testing

Verification of cross-component interfaces and multi-agent pipeline data flow.

| # | Integration Boundary | Verifications | Status | Expected Output | Actual Output |
|---|---|---|---|---|---|
| 2.1 | **Frontend → FastAPI API** | Endpoint reachability & CORS handling | **PASS** | HTTP 200 response with JSON contract | Successfully connected to API |
| 2.2 | **Report → Extraction → Prediction** | Adapter pipeline transformation | **PASS** | Extracted profile converted to `ADNIClinicalFeatures` | ADNI features successfully constructed |
| 2.3 | **Prediction → SHAP** | Predictor to TreeExplainer bridge | **PASS** | SHAP values computed for predicted class index | SHAP array shape matches feature count |
| 2.4 | **Query → RAG → FAISS** | Embedder to VectorStore interface | **PASS** | Query encoded and searched against 1,558 FAISS vectors | Returned top-5 matching document chunks |
| 2.5 | **Agents → RAG → LLM** | Orchestrator state accumulation | **PASS** | State populated by ADNI Agent, RAG Agent, and LLM Agent | `agents_executed: ["ADNI ML Agent", "RAG Agent", "LLM Agent"]` |
| 2.6 | **LLM → Validation → Frontend** | Final response envelope assembly | **PASS** | Assembled `AgentAnalysisResponse` sent to UI | `explanation` payload delivered to `ExplanationCard.tsx` |

---

## 3. End-to-End Testing

Complete pipeline execution tested using synthetic and de-identified clinical files (`Sample_pdf/HealthSenseAI_Synthetic_Alzheimer_Clinical_Report.pdf`).

### 3.1 Clinical PDF Report Workflow
1. **Upload & Extraction:** 617 words extracted from 2-page synthetic Alzheimer's clinical report.
2. **Stage-1 LLM Structuring:** Parsed age (72), sex (Female), education (16), MMSE (23), MoCA (19), CDR (1.0), ADAS (18), FAQ (10), MRI bilateral hippocampal atrophy.
3. **ADNI ML Prediction:** Assigned **89.8% predicted probability to AD class**.
4. **SHAP Feature Attribution:** MMSE, CDR, ADAS, and Age identified as primary risk drivers.
5. **RAG Knowledge Retrieval:** Retrieved 5 relevant Alzheimer's clinical guideline chunks.
6. **Groq LLM Synthesis:** `openai/gpt-oss-120b` generated a 5-part clinical synthesis (`what_results_suggest`, `why_relevant`, `what_research_says`, `next_steps`, `clinical_notice`).
7. **UI Display:** `ExplanationCard.tsx` rendered the full synthesis cleanly with **Fallback Mode OFF**.

### 3.2 Parkinson Screening & Questionnaire Workflows
- **Parkinson Prediction:** Verified using `AGE_AT_VISIT=68`, `EDUCYRS=16`, `MCATOT=24`, `NHY=2.0`, `NP3TOT=22`. Result: **Healthy Control (84.2% prob)** with SHAP feature ranking (`NP3TOT`, `NHY`).
- **Questionnaire Screening:** Tested Alzheimer's, Parkinson's, and Combined questionnaires. Tested zero-symptom responses (triggers clear non-diagnostic reassurance) and positive symptom responses (triggers domain breakdown and next steps).

---

## 4. Performance Testing

Empirical benchmarks measured over multiple execution runs.

| Subsystem / Operation | Iterations | Min Latency | Max Latency | Average Latency |
|---|---|---|---|---|
| **ADNI Prediction + SHAP** | 5 runs | 0.0242 s | 0.0329 s | **0.0274 s** |
| **Parkinson Prediction + SHAP** | 5 runs | 0.1082 s | 0.3261 s | **0.1616 s** |
| **RAG Vector Search (FAISS)** | 5 runs | 0.0146 s | 0.1598 s | **0.0446 s** |
| **PubMed E-utilities Web Search** | 3 runs | 0.6521 s | 1.8871 s | **1.4604 s** |
| **Groq LLM Synthesis (`gpt-oss-120b`)** | 3 runs | 1.8193 s | 3.3635 s | **2.6540 s** |
| **Full E2E Clinical Report Analysis** | 3 runs | 0.1582 s | 2.9910 s | **1.8143 s** |
| **Frontend Production Build (`vite build`)** | 1 build | N/A | N/A | **1.06 s** |

---

## 5. Negative and Resilience Testing

| Scenario | Input Condition | Expected System Behavior | Measured Result | Status |
|---|---|---|---|---|
| **Corrupted PDF Upload** | Malformed byte stream `b"%PDF-1.4 Corrupt..."` | HTTP 400 Bad Request with clear error message | HTTP 400 (`Failed to read PDF file. The document may be corrupted...`) | **PASS** |
| **Non-PDF Upload** | `test.txt` text/plain file | HTTP 400 Bad Request enforcing `.pdf` constraint | HTTP 400 (`Only PDF files are supported.`) | **PASS** |
| **Empty Request Body** | `{}` sent to `/api/agents/analyze` | HTTP 422 Unprocessable Entity | HTTP 422 | **PASS** |
| **Invalid Field Data Types** | `"AGE": "invalid_string"` | HTTP 422 validation error | HTTP 422 | **PASS** |
| **Missing ADNI Required Fields** | `"AGE": 75.0` (missing MMSE/CDR) | HTTP 422 validation error | HTTP 422 | **PASS** |
| **LLM Rate Limit (HTTP 429)** | Exceeded TPM limit on Groq API | Gracefully catches `RateLimitError` and activates fallback mode | Returned structured fallback summary without server crash | **PASS** |
| **RAG Store Missing** | Querying unindexed disease context | Returns empty evidence list gracefully | Returns 0 chunks, pipeline proceeds | **PASS** |

---

## 6. Regression Testing (LLM Synthesis Pipeline)

Specific regression checks conducted for the LLM synthesis pipeline:

1. **`.env` Path Resolution:** Verified that `backend/config.py` explicitly loads `.env` from `PROJECT_ROOT / ".env"`, preventing `GROQ_API_KEY` loss when uvicorn is launched from arbitrary directories.
2. **Groq API Connectivity:** Tested `GET /api/reports/llm-health` -> Returned HTTP 200 OK `{"status": "connected", "model": "openai/gpt-oss-120b"}`.
3. **Model Selection:** Confirmed active requests use `openai/gpt-oss-120b`.
4. **JSON Response Parsing:** Verified `response_format={"type": "json_object"}` produces valid structured JSON.
5. **Unicode Normalization:** Confirmed non-breaking hyphens (`\u2011`), en-dashes (`\u2013`), em-dashes (`\u2014`), and smart quotes (`\u201c`/`\u201d`/`\u2019`) are normalized to standard ASCII punctuation before JSON decoding.
6. **Response Validation & Sanitization:** Verified soft phrase substitution replaces unsupported phrases without erasing the generated LLM synthesis.
7. **Fallback Mode:** Confirmed that Fallback Mode remains active as a safety net if Groq encounters network failure or HTTP 429 rate limits.

---

## 7. Final Test Summary

- **Backend Pytest Results:** **92 passed out of 92 tests (100% pass rate)**
- **Frontend Build Results:** **1.06s build time (0 errors)**
- **Groq LLM Synthesis:** **OPERATIONAL & CONNECTED (`openai/gpt-oss-120b`)**
- **System Stability:** **STABLE & RESILIENT**
