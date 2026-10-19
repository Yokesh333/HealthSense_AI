"""
backend/api/agents.py

FastAPI router for the multi-agent analysis endpoint.

Route: POST /api/agents/analyze

The router:
  1. Accepts the same ADNIPredictionRequest used by /api/adni/predict.
  2. Pulls the shared ADNIPredictor from app.state (loaded once at startup).
  3. Constructs an Orchestrator with that predictor instance.
  4. Runs the orchestrator workflow.
  5. Returns an AgentAnalysisResponse.

Error handling:
  - Predictor not loaded → HTTP 503
  - Workflow failure → HTTP 500 with sanitised message (no stack traces,
    no filesystem paths, no patient data)
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from backend.agents.orchestrator import Orchestrator
from backend.agents.state import ADNIClinicalFeatures, AgentAnalysisResponse
from backend.models.adni_schemas import UnifiedAnalysisRequest, FollowUpRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AgentAnalysisResponse)
async def analyze(request: Request, data: UnifiedAnalysisRequest) -> AgentAnalysisResponse:
    """
    Run the multi-agent ADNI analysis workflow or Questionnaire workflow.
    """
    predictor = getattr(request.app.state, "adni_predictor", None)
    parkinson_predictor = getattr(request.app.state, "parkinson_predictor", None)

    if predictor is None and parkinson_predictor is None:
        raise HTTPException(status_code=503, detail="No ML predictors available.")

    rag_service = getattr(request.app.state, "rag_service", None)
    web_service = getattr(request.app.state, "web_service", None)
    llm_service = getattr(request.app.state, "llm_service", None)

    orchestrator = Orchestrator(
        predictor=predictor,
        parkinson_predictor=parkinson_predictor,
        rag_service=rag_service,
        web_service=web_service,
        llm_service=llm_service
    )

    try:
        result: AgentAnalysisResponse = await orchestrator.analyze_unified(data)
    except Exception as exc:
        logger.error("agents/analyze: unexpected orchestrator error — %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Multi-agent workflow encountered an unexpected error. Check server logs.",
        )

    if result.status == "failed":
        logger.error("agents/analyze: workflow failed — %s", result.errors)
        raise HTTPException(status_code=500, detail=f"Workflow failed: {'; '.join(result.errors)}")

    return result


@router.post("/followup")
async def followup(request: Request, data: FollowUpRequest):
    """
    Handle conversational follow-up with structured, patient-friendly response.
    Uses LLM, RAG and Web services.
    """
    llm_service = getattr(request.app.state, "llm_service", None)
    rag_service = getattr(request.app.state, "rag_service", None)
    web_service = getattr(request.app.state, "web_service", None)

    if not llm_service:
        raise HTTPException(status_code=503, detail="LLM service is not available.")

    # 1. Build screening & disease context
    context_blocks = []
    
    if data.disease_context:
        context_blocks.append(f"Active Disease Context: {', '.join(data.disease_context)}")
        
    if data.screening_context:
        try:
            import json
            context_blocks.append(f"Patient Screening Context:\n{json.dumps(data.screening_context, indent=2)}")
        except Exception:
            pass
    elif data.previous_explanation:
        try:
            import json
            context_blocks.append(f"Previous Explanation:\n{json.dumps(data.previous_explanation, indent=2)}")
        except Exception:
            pass

    # 2. Gather context from RAG based on disease_context
    rag_results = []
    web_results = []

    disease_filter = "both"
    if data.disease_context and len(data.disease_context) == 1:
        disease_filter = data.disease_context[0]

    if rag_service:
        try:
            rag_results = rag_service.retrieve(query=data.question, top_k=3, disease=disease_filter)
            if rag_results:
                context_blocks.append("Biomedical Knowledge Base Evidence:\n" + "\n".join(r.text for r in rag_results))
        except Exception as e:
            logger.error("agents/followup RAG error: %s", e)

    # 3. Gather context from Web for latest/current queries
    if web_service:
        try:
            web_results = await web_service.search(data.question)
            if web_results:
                context_blocks.append("Web/PubMed Evidence:\n" + "\n".join(r.get("snippet", "") for r in web_results))
        except Exception as e:
            logger.error("agents/followup Web error: %s", e)

    # Determine authoritative workflow type
    workflow = None
    if data.screening_context and isinstance(data.screening_context, dict):
        workflow = data.screening_context.get("workflow")
    
    if not workflow:
        if data.screening_context and data.screening_context.get("questionnaire_profile"):
            workflow = "QUESTIONNAIRE"
        else:
            workflow = "CLINICAL_REPORT"

    prompt = f"AUTHORITATIVE WORKFLOW TYPE: {workflow}\nPatient Question: {data.question}\n\n" + "\n\n".join(context_blocks)
    raw_response = await llm_service.generate_followup_response(
        prompt=prompt, 
        chat_history=data.chat_history,
        workflow=workflow
    )
    
    structured_data = None
    answer_text = ""

    if isinstance(raw_response, dict):
        structured_data = raw_response
        parts = []
        if structured_data.get("title"):
            parts.append(structured_data["title"])
        if structured_data.get("summary"):
            parts.append(structured_data["summary"])
        for sec in structured_data.get("sections", []):
            sec_text = f"{sec.get('heading', '')}\n{sec.get('content', '')}".strip()
            if sec.get("key_points"):
                sec_text += "\n" + "\n".join(f"• {kp}" for kp in sec["key_points"])
            parts.append(sec_text)
        if structured_data.get("clinical_notice"):
            parts.append(structured_data["clinical_notice"])
        answer_text = "\n\n".join(parts)
    else:
        answer_text = str(raw_response)

    formatted_rag = [
        {
            "text": r.text,
            "source": r.source,
            "page": r.page,
            "score": r.score,
            "category": r.category,
            "disease_context": r.disease
        }
        for r in rag_results
    ]

    return {
        "answer": answer_text,
        "response": answer_text,
        "structured": structured_data,
        "rag_evidence": formatted_rag,
        "web_evidence": web_results
    }
