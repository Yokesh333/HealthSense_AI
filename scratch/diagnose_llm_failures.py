"""
scratch/diagnose_llm_failures.py

Targeted LLM failure diagnosis for PDF1 (LLM synthesis fallback)
and PDF2 (Stage-1 extraction failure).
"""

import sys
import os
import json
import time
import asyncio
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

SEP = "\n" + "=" * 80 + "\n"

PDF1 = os.path.join(os.path.dirname(__file__), "..", "Sample_pdf", "alzheimer.pdf")
PDF2 = os.path.join(os.path.dirname(__file__), "..", "Sample_pdf", "alzheimer_2.pdf")


async def test_stage1_llm_extraction(pdf_path, label):
    """Directly call extract_clinical_variables and capture exact exception."""
    print(f"{SEP}[{label}] TESTING STAGE-1 LLM EXTRACTION DIRECTLY")

    import fitz
    from backend.services.llm_service import GroqLLMService
    from backend.services.pdf_service import PDFExtractionService

    with open(pdf_path, "rb") as f:
        content = f.read()

    pdf_svc = PDFExtractionService()
    extracted_text, pages = pdf_svc.validate_and_extract(content, os.path.basename(pdf_path))
    print(f"  Extracted text length: {len(extracted_text)}")
    print(f"  First 200 chars: {extracted_text[:200]!r}")

    llm = GroqLLMService()
    print(f"  Calling extract_clinical_variables with {len(extracted_text)} chars...")
    t0 = time.time()
    try:
        result = await llm.extract_clinical_variables(extracted_text)
        elapsed = time.time() - t0
        print(f"  SUCCESS in {elapsed:.2f}s")
        print(f"  disease_context: {result.get('disease_context')}")
        pat = result.get("patient_information", {})
        scores = result.get("clinical_scores", {})
        print(f"  patient: age={pat.get('age')}, sex={pat.get('sex')}, education={pat.get('education')}")
        print(f"  scores: MMSE={scores.get('mmse')}, MoCA={scores.get('moca')}, CDR={scores.get('cdr')}")
        return result
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  FAILED in {elapsed:.2f}s")
        print(f"  Exception type: {type(e).__name__}")
        print(f"  Exception detail: {e}")
        traceback.print_exc()
        return None


async def test_stage2_llm_synthesis(profile, label):
    """Directly call generate_explanation and capture exact exception."""
    print(f"{SEP}[{label}] TESTING STAGE-2 LLM SYNTHESIS DIRECTLY")

    from backend.services.llm_service import GroqLLMService
    from backend.agents.state import AgentState, ADNIClinicalFeatures

    llm = GroqLLMService()

    # Build a minimal state that represents what PDF1 would produce
    # (Alzheimer context, no ADNI features, has RAG-style content)
    state = AgentState(
        workflow="CLINICAL_REPORT",
        disease_context=profile.get("disease_context", ["unknown"]),
        clinical_profile=profile,
        ml_prediction=None,
        rag_results=None,
    )

    # Build the prompt as LLMAgent would
    from backend.agents.llm_agent import LLMAgent
    agent = LLMAgent(llm_service=llm)
    prompt = agent._construct_prompt(state)
    print(f"  Prompt length: {len(prompt)} chars")
    print(f"  Prompt excerpt: {prompt[:300]!r}")

    print(f"  Calling generate_explanation...")
    t0 = time.time()
    try:
        result = await llm.generate_explanation(prompt, workflow="CLINICAL_REPORT")
        elapsed = time.time() - t0
        print(f"  Response in {elapsed:.2f}s")
        suggest = result.get("what_results_suggest", "")
        print(f"  what_results_suggest: {suggest[:300]!r}")

        if "LLM synthesis is currently unavailable" in suggest:
            print(f"  *** FALLBACK DETECTED -- this is the fallback response from _fallback_response()")
        else:
            print(f"  SUCCESS -- real LLM response received")
        return result
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  FAILED in {elapsed:.2f}s")
        print(f"  Exception type: {type(e).__name__}")
        print(f"  Exception detail: {e}")
        traceback.print_exc()
        return None


async def main():
    print("\n" + "#" * 80)
    print("  LLM FAILURE DIAGNOSIS")
    print("#" * 80)

    from backend.config import GROQ_API_KEY, GROQ_MODEL
    print(f"\nGROQ_API_KEY: {'SET (len=' + str(len(GROQ_API_KEY)) + ')' if GROQ_API_KEY else 'MISSING'}")
    print(f"GROQ_MODEL: {GROQ_MODEL!r}")

    # === PDF1: Diagnose Stage-1 LLM extraction (succeeded) and Stage-2 LLM synthesis (fell back) ===
    print(f"\n{'#' * 80}")
    print("  PDF1 (alzheimer.pdf) -- Stage-1 LLM extraction diagnosis")
    print(f"{'#' * 80}")

    # PDF1 Stage-1 extraction already succeeded in the earlier diagnostic,
    # so we know the profile. Now diagnose why Stage-2 synthesis falls back.
    # Reconstruct the profile from what we know:
    pdf1_profile = {
        "disease_context": ["alzheimers"],
        "patient_information": {"age": 73.0, "sex": "male", "education": None, "race": None, "ethnicity": None},
        "clinical_scores": {"mmse": None, "moca": 27.0, "cdr": None, "adas": None, "faq": None, "updrs": None, "hoehn_yahr": None, "other_scores": {}},
        "cognitive_findings": {"memory_impairment": True, "executive_dysfunction": None, "language_deficits": None, "details": []},
        "motor_findings": {"resting_tremor": None, "bradykinesia": None, "rigidity": None, "gait_postural_instability": None, "details": []},
        "symptoms": [],
        "duration": None,
        "imaging_findings": [],
        "laboratory_findings": [],
        "medications": [],
        "family_history": [],
        "clinical_impression": "prodromal Alzheimer's disease (A+/T+/N+)",
        "source_pages": {},
        "missing_information": ["mmse", "cdr", "adas", "faq"]
    }

    print(f"\n  ** STAGE-2 LLM Synthesis for PDF1 (profile without ADNI prediction) **")
    await test_stage2_llm_synthesis(pdf1_profile, "PDF1_SYNTHESIS")

    # === PDF2: Diagnose Stage-1 LLM extraction (failed) ===
    print(f"\n{'#' * 80}")
    print("  PDF2 (alzheimer_2.pdf) -- Stage-1 LLM extraction diagnosis")
    print(f"{'#' * 80}")
    pdf2_result = await test_stage1_llm_extraction(PDF2, "PDF2_EXTRACT")

    if pdf2_result:
        print(f"\n  ** STAGE-2 LLM Synthesis for PDF2 **")
        await test_stage2_llm_synthesis(pdf2_result, "PDF2_SYNTHESIS")


if __name__ == "__main__":
    asyncio.run(main())
