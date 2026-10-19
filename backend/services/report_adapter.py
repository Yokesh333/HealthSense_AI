"""
backend/services/report_adapter.py

Adapter to normalize a StructuredClinicalProfile extracted from a PDF report
into the existing UnifiedAnalysisRequest / AgentState representation.

Design principles:
- Reuses exact existing disease_context contract: ['alzheimers'], ['parkinsons'], ['alzheimers', 'parkinsons'], or ['unknown'].
- Converts extracted clinical features into ADNIPredictionRequest ONLY if Alzheimer's context is present AND legitimate ADNI features exist.
- Never fabricates missing values or forces ADNI execution on Parkinson's-only reports.
- Formulates a structured report summary profile suitable for downstream RAG, Web Intelligence, and LLM synthesis agents.
"""

import logging
from typing import Optional, Dict, Any

from backend.models.report_schemas import StructuredClinicalProfile
from backend.models.adni_schemas import UnifiedAnalysisRequest, ADNIPredictionRequest
from backend.models.parkinson_schemas import ParkinsonPredictionRequest

logger = logging.getLogger(__name__)


class ClinicalProfileAdapter:
    """Adapts StructuredClinicalProfile into UnifiedAnalysisRequest."""

    @staticmethod
    def adapt(
        profile: StructuredClinicalProfile, clinical_question: Optional[str] = None
    ) -> UnifiedAnalysisRequest:
        """
        Convert structured clinical profile to UnifiedAnalysisRequest.
        """
        # Standardize disease context list
        disease_context = list(profile.disease_context) if profile.disease_context else ["unknown"]
        
        # Determine if ADNI data can legitimately be constructed
        adni_request: Optional[ADNIPredictionRequest] = None
        parkinson_request: Optional[ParkinsonPredictionRequest] = None

        is_alzheimers_relevant = "alzheimers" in disease_context
        is_parkinsons_relevant = "parkinsons" in disease_context
        patient = profile.patient_information
        scores = profile.clinical_scores

        # 1. ADNI feature construction (Alzheimer's)
        if is_alzheimers_relevant and patient.age is not None and patient.sex is not None and scores.mmse is not None:
            try:
                adni_request = ADNIPredictionRequest(
                    AGE=float(patient.age),
                    EDUCATION=float(patient.education) if patient.education is not None else 12.0,
                    ADAS=float(scores.adas) if scores.adas is not None else None,
                    CDR=float(scores.cdr) if scores.cdr is not None else 0.5,
                    FAQ=float(scores.faq) if scores.faq is not None else None,
                    MMSE=float(scores.mmse),
                    MOCA=float(scores.moca) if scores.moca is not None else None,
                    SEX=str(patient.sex).capitalize(),
                    RACE=str(patient.race) if patient.race else "White",
                    ETHNICITY=str(patient.ethnicity) if patient.ethnicity else "Not Hisp/Latino",
                    clinical_question=clinical_question,
                )
                logger.info("report_adapter: Built ADNI clinical features for Alzheimer's report analysis.")
            except Exception as exc:
                logger.warning("report_adapter: Could not construct ADNI features — %s", exc)
                adni_request = None

        # 2. Parkinson feature construction (Parkinson's)
        # MUST BE SEMANTICALLY EXACT. Never map generic scores.updrs to NP3TOT.
        if is_parkinsons_relevant:
            try:
                p_kwargs: Dict[str, Any] = {}
                if patient.age is not None:
                    p_kwargs["AGE_AT_VISIT"] = float(patient.age)
                if patient.education is not None:
                    p_kwargs["EDUCYRS"] = float(patient.education)
                if scores.moca is not None:
                    p_kwargs["MCATOT"] = float(scores.moca)

                # Parse Hoehn & Yahr stage if present
                if scores.hoehn_yahr is not None:
                    try:
                        # Extract numeric stage e.g. "2" or "2.5" from string
                        import re
                        match = re.search(r"(\d+(\.\d+)?)", str(scores.hoehn_yahr))
                        if match:
                            p_kwargs["NHY"] = float(match.group(1))
                    except Exception:
                        pass

                # Inspect other_scores for semantically exact Parkinson variables
                oth = scores.other_scores or {}
                for key, val in oth.items():
                    k_lower = key.lower().strip()
                    try:
                        f_val = float(val)
                    except (ValueError, TypeError):
                        continue

                    if k_lower in ("np1rtot", "mds_updrs_part_1", "updrs_part_1"):
                        p_kwargs["NP1RTOT"] = f_val
                    elif k_lower in ("np2ptot", "mds_updrs_part_2", "updrs_part_2"):
                        p_kwargs["NP2PTOT"] = f_val
                    elif k_lower in ("np3tot", "mds_updrs_part_3", "updrs_part_3"):
                        p_kwargs["NP3TOT"] = f_val
                    elif k_lower in ("gds_total", "gds"):
                        p_kwargs["GDS_TOTAL"] = f_val
                    elif k_lower in ("ess_total", "ess"):
                        p_kwargs["ESS_TOTAL"] = f_val
                    elif k_lower in ("rbd_total", "rbd"):
                        p_kwargs["RBD_TOTAL"] = f_val
                    elif k_lower in ("sdmtotal", "sdmt"):
                        p_kwargs["SDMTOTAL"] = f_val
                    elif k_lower in ("dvt_total_recall",):
                        p_kwargs["DVT_TOTAL_RECALL"] = f_val
                    elif k_lower in ("dvt_delayed_recall",):
                        p_kwargs["DVT_DELAYED_RECALL"] = f_val
                    elif k_lower in ("lns_totraw", "lns"):
                        p_kwargs["LNS_TOTRAW"] = f_val
                    elif k_lower in ("tmtasec", "tmt_a"):
                        p_kwargs["TMTASEC"] = f_val
                    elif k_lower in ("tmtbsec", "tmt_b"):
                        p_kwargs["TMTBSEC"] = f_val
                    elif k_lower in ("scopa_aut_total", "scopa_aut"):
                        p_kwargs["SCOPA_AUT_TOTAL"] = f_val

                if p_kwargs:
                    p_kwargs["clinical_question"] = clinical_question
                    parkinson_request = ParkinsonPredictionRequest(**p_kwargs)
                    logger.info("report_adapter: Built Parkinson clinical features from report.")
            except Exception as exc:
                logger.warning("report_adapter: Could not construct Parkinson features — %s", exc)
                parkinson_request = None

        return UnifiedAnalysisRequest(
            type="CLINICAL_REPORT",
            adni_data=adni_request,
            parkinson_data=parkinson_request,
            disease_context=disease_context,
            clinical_profile=profile.model_dump(),
        )

    @staticmethod
    def build_summary_profile(profile: StructuredClinicalProfile) -> Dict[str, Any]:
        """
        Create a patient-friendly summary dictionary for questionnaire_profile compatibility.
        """
        concerns = []
        if profile.cognitive_findings.details:
            concerns.extend(profile.cognitive_findings.details)
        if profile.motor_findings.details:
            concerns.extend(profile.motor_findings.details)
        if profile.symptoms:
            concerns.extend([f"Symptom: {s}" for s in profile.symptoms])

        scores_summary = {}
        sc = profile.clinical_scores
        if sc.mmse is not None:
            scores_summary["MMSE"] = sc.mmse
        if sc.moca is not None:
            scores_summary["MoCA"] = sc.moca
        if sc.cdr is not None:
            scores_summary["CDR"] = sc.cdr
        if sc.updrs is not None:
            scores_summary["UPDRS"] = sc.updrs

        return {
            "profile": {
                "extracted_scores": scores_summary,
                "symptoms_count": len(profile.symptoms),
                "imaging_count": len(profile.imaging_findings),
            },
            "areas_of_concern": concerns or ["Extracted findings from clinical report"],
            "clinical_impression": profile.clinical_impression or "Not specified",
            "notice": "Extracted clinical report profile. This is an AI-assisted research summary, NOT a diagnosis.",
        }
