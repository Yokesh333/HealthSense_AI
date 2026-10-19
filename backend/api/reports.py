"""
backend/api/reports.py

FastAPI router for clinical report upload, Stage-1 extraction, and unified analysis.

Routes:
  - POST /api/reports/extract: Upload PDF, validate & extract text via PyMuPDF, perform Stage-1 Groq extraction -> StructuredClinicalProfile.
  - POST /api/reports/analyze: Accept StructuredClinicalProfile, adapt into UnifiedAnalysisRequest, invoke Orchestrator IN-MEMORY -> AgentAnalysisResponse.
"""

import logging
from typing import Optional, Dict, Any

from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from pydantic import BaseModel

from backend.services.pdf_service import PDFExtractionService, PDFExtractionError
from backend.models.report_schemas import StructuredClinicalProfile
from backend.services.report_adapter import ClinicalProfileAdapter
from backend.agents.orchestrator import Orchestrator
from backend.agents.state import AgentAnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Reports"])
pdf_service = PDFExtractionService()


class ReportAnalyzeRequest(BaseModel):
    profile: StructuredClinicalProfile
    clinical_question: Optional[str] = None


@router.post("/extract", response_model=StructuredClinicalProfile)
async def extract_report(request: Request, file: UploadFile = File(...)) -> StructuredClinicalProfile:
    """
    Extract text from a PDF report and structure clinical variables using Stage-1 Groq LLM extraction.
    Strictly accepts PDF. Enforces 10 MB and 20 page limits. Detects image-only / scanned PDFs.
    """
    filename = file.filename or "report.pdf"
    if file.content_type != "application/pdf" and not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content_bytes = await file.read()
    except Exception as e:
        logger.error("reports/extract: Failed reading uploaded file — %s", e)
        raise HTTPException(status_code=400, detail="Failed to read uploaded file.")
    finally:
        await file.close()

    # 1. Text extraction & PDF validation
    try:
        extracted_text, _ = pdf_service.validate_and_extract(content_bytes, filename=filename)
    except PDFExtractionError as exc:
        logger.warning("reports/extract: PDF extraction error — %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("reports/extract: Unexpected PDF extraction failure — %s", exc)
        raise HTTPException(status_code=400, detail="Failed to process PDF report.")

    # 2. Stage-1 LLM Extraction
    llm_service = getattr(request.app.state, "llm_service", None)
    if not llm_service:
        # Fallback if LLM service is not configured (e.g. key missing in dev)
        logger.warning("reports/extract: LLM service missing. Returning basic profile.")
        return StructuredClinicalProfile(
            disease_context=["unknown"],
            clinical_impression="Groq LLM service is not configured.",
            missing_information=["Stage-1 LLM extraction unavailable."]
        )

    try:
        extracted_dict = await llm_service.extract_clinical_variables(extracted_text)
        profile = StructuredClinicalProfile(**extracted_dict)
        return profile
    except Exception as exc:
        logger.error("reports/extract: Stage-1 extraction failed — %s", exc)
        return StructuredClinicalProfile(
            disease_context=["unknown"],
            clinical_impression="Stage-1 extraction service encountered a temporary error.",
            missing_information=["Automated structured extraction incomplete. Please retry."]
        )


@router.post("/analyze", response_model=AgentAnalysisResponse)
async def analyze_report(request: Request, body: ReportAnalyzeRequest) -> AgentAnalysisResponse:
    """
    Execute the existing unified multi-agent orchestrator directly IN-MEMORY for an extracted report.
    """
    predictor = getattr(request.app.state, "adni_predictor", None)
    parkinson_predictor = getattr(request.app.state, "parkinson_predictor", None)
    rag_service = getattr(request.app.state, "rag_service", None)
    web_service = getattr(request.app.state, "web_service", None)
    llm_service = getattr(request.app.state, "llm_service", None)

    if predictor is None and parkinson_predictor is None:
        raise HTTPException(status_code=503, detail="No ML predictors available.")

    # 1. Adapt StructuredClinicalProfile -> UnifiedAnalysisRequest
    unified_request = ClinicalProfileAdapter.adapt(body.profile, clinical_question=body.clinical_question)

    # 2. Invoke Orchestrator directly in-memory
    orchestrator = Orchestrator(
        predictor=predictor,
        parkinson_predictor=parkinson_predictor,
        rag_service=rag_service,
        web_service=web_service,
        llm_service=llm_service
    )

    try:
        result: AgentAnalysisResponse = await orchestrator.analyze_unified(unified_request)
        return result
    except Exception as exc:
        logger.error("reports/analyze: In-memory orchestrator error — %s", exc)
        raise HTTPException(status_code=500, detail="Report analysis failed due to an internal error.")


@router.get("/llm-health")
async def llm_health_check(request: Request) -> Dict[str, Any]:
    """
    Service-level health check for Groq LLM connectivity.
    """
    llm_service = getattr(request.app.state, "llm_service", None)
    if not llm_service:
        return {"status": "unavailable", "reason": "LLM service is not initialized on app.state."}
    
    if hasattr(llm_service, "check_connection"):
        return await llm_service.check_connection()
    return {"status": "available"}

