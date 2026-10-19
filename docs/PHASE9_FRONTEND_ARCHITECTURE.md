# Phase 9: Frontend Architecture

## Overview
Phase 9 introduces the primary user interface for HealthSense AI, designed as a modern research dashboard. The frontend is built as a single-page application (SPA) using React, Vite, and TypeScript. It interfaces directly with the FastAPI backend orchestrator.

## Technology Stack
- **Framework:** React 18
- **Build Tool:** Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS (Utility-first CSS framework)
- **HTTP Client:** Axios
- **Icons:** Lucide React

## Architecture Diagram

```mermaid
flowchart TD
    subgraph Frontend [React Application]
        App[App.tsx\nState & Layout]
        Form[ClinicalInputForm.tsx]
        
        subgraph Dashboard
            Pred[PredictionCard.tsx]
            Prob[ProbabilityChart.tsx]
            Work[AgentWorkflow.tsx]
            Exp[ExplanationCard.tsx]
            WebEv[WebEvidenceList.tsx]
            RAGEv[EvidenceList.tsx]
        end
        
        API_Service[services/api.ts]
    end
    
    subgraph Backend [FastAPI Application]
        Orchestrator[POST /api/agents/analyze]
    end
    
    Form -->|1. Submit Clinical Data| App
    App -->|2. analyzePatient()| API_Service
    API_Service -->|3. HTTP POST| Orchestrator
    Orchestrator -->|4. AgentAnalysisResponse| API_Service
    API_Service -->|5. Return Data| App
    App -->|6. Render state| Dashboard
```

## Key Components

### 1. `ClinicalInputForm`
A carefully validated form matching the ADNI baseline feature set exactly. It handles the specific requirement that `MOCA` must be nullable by converting empty strings to `null` before transmission.

### 2. `AgentWorkflow`
Dynamically visualizes the multi-agent pipeline based strictly on the `agents_executed` array returned by the backend. This visually reinforces the adaptive routing behavior of the Orchestrator (e.g., dynamically showing the Web Intelligence Agent when requested).

### 3. Evidence Lists (`EvidenceList`, `WebEvidenceList`)
Distinct components for rendering purely local RAG (Alzheimer's FAISS index) evidence versus external PubMed Web evidence. Web evidence includes external secure URLs (`target="_blank" rel="noopener noreferrer"`).

### 4. `ExplanationCard`
Renders the LLM-generated structured explanation. Identifies and gracefully labels fallback states if the backend LLM service is unavailable, ensuring the dashboard remains fully functional.

## Security and Configuration
- **API Base URL:** Configured via the `VITE_API_BASE_URL` environment variable, avoiding hardcoded origins.
- **CORS:** FastAPI is configured to allow `http://localhost:5173` strictly for local development.
- **Secrets:** No API keys (e.g., Groq, NCBI) or model files are exposed to the frontend.
- **Clinical Data:** The frontend does not persist clinical features locally (no `localStorage` or `sessionStorage` usage for patient data).
