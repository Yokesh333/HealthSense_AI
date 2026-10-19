# Phase 7 — LLM-Enhanced Multi-Agent Biomedical Analysis

Phase 7 of HealthSense AI introduces an LLM (Language Model) agent that works alongside the existing Machine Learning and RAG components to provide an evidence-grounded clinical explanation. 

## Architecture Diagram

```mermaid
graph TD
    User([User]) --> |"POST /api/agents/analyze"| FastAPI[FastAPI App]
    FastAPI --> |"ADNIClinicalFeatures"| Orchestrator[Multi-Agent Orchestrator]
    
    subgraph "Dependency Injection Layer (Loaded once at startup)"
        Predictor[ADNIPredictor (Random Forest)]
        RAG[RAGService (FAISS + Embeddings)]
        LLM[LLMService (Groq)]
    end
    
    Predictor -.-> Orchestrator
    RAG -.-> Orchestrator
    LLM -.-> Orchestrator

    subgraph "Execution Pipeline (Deterministic Order)"
        Orchestrator --> |"1. Execute"| ADNI_Agent[ADNI ML Agent]
        ADNI_Agent --> |"Uses"| Predictor
        Predictor --> |"CN / MCI / AD"| ADNI_Agent
        ADNI_Agent --> |"Populates state.ml_prediction"| Orchestrator
        
        Orchestrator --> |"2. Execute"| RAG_Agent[RAG Agent]
        RAG_Agent --> |"Uses"| RAG
        RAG --> |"Top-K Biomedical Chunks"| RAG_Agent
        RAG_Agent --> |"Populates state.rag_results"| Orchestrator
        
        Orchestrator --> |"3. Execute"| LLM_Agent[LLM Agent]
        LLM_Agent --> |"Uses"| LLM
        LLM --> |"JSON Explanation"| LLM_Agent
        LLM_Agent --> |"Populates state.llm_response"| Orchestrator
    end
    
    Orchestrator --> |"AgentAnalysisResponse"| FastAPI
    FastAPI --> User
```

## Data Flow & Responsibilities

1. **User Request**: The user submits clinical features (e.g., AGE, MMSE, ADAS) and an optional `clinical_question`.
2. **FastAPI**: Validates the input payload and passes it, along with the injected services (`app.state.adni_predictor`, `app.state.rag_service`, `app.state.llm_service`), to the Orchestrator.
3. **Orchestrator**: Executes a deterministic workflow consisting of three specialized agents in order.
4. **ADNI ML Agent**: 
   - Uses the pre-loaded Random Forest model to predict CN, MCI, or AD.
   - Outputs the classification probabilities.
   - **Crucially: The LLM does NOT make this classification. It is authoritative.**
5. **RAG Agent**: 
   - Takes the `clinical_question` (or generates a deterministic query based on the ML prediction if no question was provided).
   - Retrieves relevant evidence from the FAISS Biomedical Knowledge Base.
6. **LLM Agent**:
   - Compiles a strict prompt comprising the user's clinical features, the authoritative ML prediction, and the retrieved chunks of biomedical text.
   - Calls the Groq API to synthesize this information into a structured JSON explanation.
7. **Final Assembly**: The Orchestrator collects the outputs and returns an `AgentAnalysisResponse` that neatly separates the prediction, the explanation, and the raw evidence.

## Dependency Injection and Singleton Loading

A key optimization in this architecture is that heavy resources are loaded exactly once during the `FastAPI` startup lifespan:

- The Random Forest model (`joblib`)
- The FAISS index (`IndexFlatIP`)
- The Sentence-Transformers model (`all-MiniLM-L6-v2`)
- The Groq client connection pool

By extracting these from `app.state` and injecting them into the Orchestrator per request, we ensure fast request times without re-incurring startup penalties, and we avoid memory leaks or excessive resource consumption.
