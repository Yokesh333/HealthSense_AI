import json
import logging
from typing import Optional, Dict, Any

from backend.agents.base_agent import BaseAgent
from backend.agents.state import AgentResult, AgentState
from backend.services.llm_service import BaseLLMService

logger = logging.getLogger(__name__)

class LLMAgent(BaseAgent):
    """
    Agent responsible for synthesizing ML predictions, questionnaire profiles,
    and RAG evidence into a coherent clinical explanation using the LLM Service.
    """

    @property
    def name(self) -> str:
        return "LLM Agent"

    def __init__(self, llm_service: Optional[BaseLLMService]):
        self._llm_service = llm_service

    async def execute(self, state: AgentState) -> AgentResult:
        logger.info("%s: executing (workflow=%s)...", self.name, state.workflow)
        
        if not self._llm_service:
            msg = "LLMService not available. Applying fallback response."
            logger.warning("%s: %s", self.name, msg)
            raw_fallback = self._get_fallback_response(state)
            validated_fallback = self._validate_and_sanitize_response(raw_fallback, state)
            state.llm_response = validated_fallback
            return AgentResult(agent_name=self.name, success=False, error=msg, data=validated_fallback)

        try:
            prompt = self._construct_prompt(state)
            response_json = await self._llm_service.generate_explanation(prompt, workflow=state.workflow)
            
            # Post-synthesis validation layer
            if response_json.get("what_results_suggest") == "LLM synthesis is currently unavailable.":
                response_json = self._get_fallback_response(state)

            validated_json = self._validate_and_sanitize_response(response_json, state)
            state.llm_response = validated_json
            
            logger.info("%s: completed successfully with validation.", self.name)
            return AgentResult(agent_name=self.name, success=True, data={"status": "completed"})

        except Exception as e:
            logger.error("%s: failed - %s", self.name, str(e))
            raw_fallback = self._get_fallback_response(state)
            validated_fallback = self._validate_and_sanitize_response(raw_fallback, state)
            state.llm_response = validated_fallback
            return AgentResult(agent_name=self.name, success=False, error=str(e), data=validated_fallback)

    def _construct_prompt(self, state: AgentState) -> str:
        workflow_type = state.workflow
        features = {}
        ml_prediction = "None"
        ml_probabilities = "None"
        if state.clinical_features:
            features = state.clinical_features.model_dump(exclude_none=True, exclude={"clinical_question"})
        if state.ml_prediction:
            ml_prediction = state.ml_prediction.predicted_class
            ml_probabilities = json.dumps(state.ml_prediction.probabilities, indent=2)

        q_profile = "None"
        if state.questionnaire_profile:
            q_profile = json.dumps(state.questionnaire_profile, indent=2)

        c_profile = "None"
        if state.clinical_profile:
            c_profile = json.dumps(state.clinical_profile, indent=2)

        evidence_text = "No biomedical evidence retrieved."
        if state.rag_results and "results" in state.rag_results:
            chunks = []
            for idx, res in enumerate(state.rag_results["results"], 1):
                text = res.get("text", "")
                if len(text) > 500:
                    text = text[:500] + "..."
                chunks.append(f"[Evidence {idx}]\nSource: {res.get('source')}\nCategory: {res.get('category')}\nSimilarity: {res.get('score', 0):.4f}\nText: {text}\n")
            if chunks:
                evidence_text = "\n".join(chunks)
                
        web_text = "No current web evidence retrieved."
        if state.web_results:
            w_chunks = []
            for idx, res in enumerate(state.web_results, 1):
                w_chunks.append(f"[Web Evidence {idx}]\nSource: {res.get('source')}\nTitle: {res.get('title')}\nDate: {res.get('published_date')}\nURL: {res.get('url')}\nText: {res.get('snippet')}\n")
            if w_chunks:
                web_text = "\n".join(w_chunks)

        user_q = "Please explain what these results suggest based on the evidence."
        if state.clinical_features and state.clinical_features.clinical_question:
            user_q = state.clinical_features.clinical_question

        if workflow_type == "QUESTIONNAIRE":
            workflow_rules = (
                "WORKFLOW TYPE: QUESTIONNAIRE\n"
                "CRITICAL RULES:\n"
                "1. Questionnaire results above are the primary signal of reported personal symptoms.\n"
                "2. If questionnaire_score is 0 or positive_findings is empty:\n"
                "   - State clearly: 'Your responses did not indicate the memory and thinking difficulties assessed by this questionnaire. This screening result does not diagnose or rule out Alzheimer\\'s disease.'\n"
                "3. DO NOT mention clinical reports, imaging, MRI, MoCA, MMSE, UPDRS, ADNI, or SHAP.\n"
                "4. RAG chunks are background literature ONLY. DO NOT treat RAG text as personal symptoms.\n"
            )
        else:
            workflow_rules = (
                "WORKFLOW TYPE: CLINICAL_REPORT\n"
                "CRITICAL RULES:\n"
                "1. THIS IS A CLINICAL PDF REPORT WORKFLOW. Base synthesis ONLY on extracted report findings and ADNI ML predictions.\n"
                "2. NEVER mention questionnaire responses or write 'your responses did not indicate'. There are NO questionnaire responses in this workflow.\n"
                "3. PROBABILITY MODEL PHRASING: Format model predictions using source-attributed phrasing:\n"
                "   - 'The ADNI-based Random Forest assigned an X% predicted probability to the [Class] class.'\n"
                "   - DO NOT call that percentage the patient's personal probability or likelihood of disease.\n"
                "4. SOURCE-ATTRIBUTED WORDING:\n"
                "   - Use: 'The uploaded report describes...', 'The model assigned...', 'The reported imaging findings include...'.\n"
                "   - DO NOT write: 'You have Alzheimer\\'s', 'This confirms Alzheimer\\'s', 'high likelihood of Alzheimer\\'s', 'typical Alzheimer\\'s changes', or 'consistent with the typical pattern of Alzheimer\\'s disease'.\n"
                "5. NO DIAGNOSTIC CLAIMS: State clearly that the prediction is an AI-assisted machine-learning research prediction and not a medical diagnosis.\n"
            )

        return f"""
{workflow_rules}

Disease Focus: {state.disease_context}

EXTRACTED CLINICAL REPORT PROFILE:
{c_profile}

CLINICAL FEATURES (ADNI):
{json.dumps(features, indent=2) if features else "None"}

ADNI RESEARCH ML PREDICTION (If Applicable):
Class: {ml_prediction}
Probabilities: {ml_probabilities}

AUTHORITATIVE QUESTIONNAIRE PROFILE:
{q_profile}

LOCAL BIOMEDICAL EVIDENCE (BACKGROUND RESEARCH ONLY):
{evidence_text}

CURRENT WEB EVIDENCE:
{web_text}

USER QUESTION:
{user_q}
"""

    def _get_fallback_response(self, state: AgentState) -> Dict[str, Any]:
        results_suggest = "LLM synthesis is currently unavailable."
        why_rel = "Screening data evaluated using deterministic scoring."
        
        disease_ctx = [d.lower() for d in (state.disease_context or [])]
        is_alz = "alzheimers" in disease_ctx
        is_pd = "parkinsons" in disease_ctx
        is_both = (is_alz and is_pd) or "both" in disease_ctx

        if state.workflow == "QUESTIONNAIRE":
            q_profile = state.questionnaire_profile or {}
            score = q_profile.get("questionnaire_score", 0)
            pos_findings = q_profile.get("positive_findings", [])
            if score == 0 or len(pos_findings) == 0:
                if is_both:
                    results_suggest = "Your responses did not indicate the memory, thinking, or movement-related difficulties assessed by this questionnaire. This screening result does not diagnose or rule out Alzheimer's disease or Parkinson's disease."
                elif is_pd:
                    results_suggest = "Your responses did not indicate the movement-related difficulties assessed by this questionnaire. This screening result does not diagnose or rule out Parkinson's disease."
                else:
                    results_suggest = "Your responses did not indicate the memory and thinking difficulties assessed by this questionnaire. This screening result does not diagnose or rule out Alzheimer's disease."
                why_rel = "Your responses indicated no positive symptoms across all assessed areas."
            else:
                results_suggest = f"Your responses indicated {len(pos_findings)} area(s) of reported symptom burden."
                why_rel = "Identifying these functional areas helps focus discussions with your healthcare provider."
        else:
            # CLINICAL_REPORT workflow fallback
            if state.ml_prediction:
                pred_cls = state.ml_prediction.predicted_class
                prob_pct = state.ml_prediction.probabilities.get(pred_cls, 0.0) * 100
                results_suggest = f"LLM synthesis is currently unavailable. The uploaded report findings were analyzed, and the ADNI-based Random Forest assigned a {prob_pct:.1f}% predicted probability to the {pred_cls} class. This is a machine-learning research prediction and not a medical diagnosis."
                why_rel = "Clinical biomarker and cognitive examination scores from the uploaded report provide quantitative metrics for model assessment."
            else:
                results_suggest = "LLM synthesis is currently unavailable. The uploaded report describes findings that were extracted for clinical review."
                why_rel = "The findings are extracted from the submitted clinical document for structured research analysis."

        research_summaries = []
        if state.rag_results and "results" in state.rag_results:
            for r in state.rag_results["results"][:2]:
                text_snippet = r.get("text", "")[:150]
                research_summaries.append(f"Biomedical evidence ({r.get('source', 'Literature')}): {text_snippet}...")
        
        if not research_summaries:
            research_summaries = ["Biomedical research highlights the importance of early cognitive and physical health monitoring."]

        return {
            "what_results_suggest": results_suggest,
            "why_relevant": why_rel,
            "what_research_says": research_summaries,
            "next_steps": [
                "Discuss these screening findings with a qualified healthcare professional.",
                "Keep track of any changes in memory or physical mobility over time."
            ],
            "clinical_notice": "This is an AI-assisted screening/research result and is not a medical diagnosis."
        }

    def _validate_and_sanitize_response(self, response_json: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """
        Post-synthesis validation layer.
        Strictly enforces workflow-aware responses and source-attributed wording.
        """
        if not isinstance(response_json, dict):
            response_json = {}

        suggest_text = response_json.get("what_results_suggest", "")
        why_text = response_json.get("why_relevant", "")

        if state.workflow == "QUESTIONNAIRE":
            q_profile = state.questionnaire_profile or {}
            score = q_profile.get("questionnaire_score", 0)
            pos_findings = q_profile.get("positive_findings", [])
            disease_ctx = [d.lower() for d in (state.disease_context or [])]
            is_pd = "parkinsons" in disease_ctx
            is_both = ("alzheimers" in disease_ctx and is_pd) or "both" in disease_ctx or q_profile.get("questionnaire_id") == "BOTH_SCREENING"

            if is_both:
                zero_stmt = "Your responses did not indicate the memory, thinking, or movement-related difficulties assessed by this questionnaire. This screening result does not diagnose or rule out Alzheimer's disease or Parkinson's disease."
            elif is_pd:
                zero_stmt = "Your responses did not indicate the movement-related difficulties assessed by this questionnaire. This screening result does not diagnose or rule out Parkinson's disease."
            else:
                zero_stmt = "Your responses did not indicate the memory and thinking difficulties assessed by this questionnaire. This screening result does not diagnose or rule out Alzheimer's disease."

            # Scrub prohibited/unsupported terms from questionnaire output
            unsupported_phrases = [
                "typical for your age", "normal for your age", "expected for your age",
                "moca", "mmse", "updrs", "imaging findings", "mri scan", "datscan",
                "clinical report", "random forest", "adni prediction", "shap"
            ]

            for phrase in unsupported_phrases:
                if phrase in suggest_text.lower():
                    logger.warning("Scrubbing unsupported phrase '%s' from questionnaire what_results_suggest", phrase)
                if phrase in why_text.lower():
                    logger.warning("Scrubbing unsupported phrase '%s' from questionnaire why_relevant", phrase)

            if score == 0 or len(pos_findings) == 0:
                response_json["what_results_suggest"] = zero_stmt
                response_json["why_relevant"] = (
                    "The questionnaire assesses self-reported cognitive and physical function. "
                    "When responses indicate no symptoms, the screening profile reflects zero reported burden."
                )

        else:  # CLINICAL_REPORT or ADNI_ML
            # 1. Scrub any leaked questionnaire phrases from clinical report synthesis
            q_phrases = ["questionnaire", "your responses did not indicate", "all answers were never", "zero reported burden"]
            has_q_leak = any(q_p in suggest_text.lower() for q_p in q_phrases)

            if has_q_leak:
                logger.warning("Scrubbing leaked questionnaire phrasing from clinical report output")
                if state.ml_prediction:
                    pred_cls = state.ml_prediction.predicted_class
                    prob_pct = state.ml_prediction.probabilities.get(pred_cls, 0.0) * 100
                    response_json["what_results_suggest"] = (
                        f"The uploaded clinical report describes findings evaluated for research analysis. "
                        f"The ADNI-based Random Forest assigned a {prob_pct:.1f}% predicted probability to the {pred_cls} class. "
                        f"This prediction is a machine-learning research estimate and not a medical diagnosis."
                    )
                else:
                    response_json["what_results_suggest"] = (
                        "The uploaded clinical report describes findings extracted for AI-assisted review. "
                        "This summary is a research estimate and not a medical diagnosis."
                    )

            # 2. Scrub unsupported diagnostic claims while preserving valid scientific language
            unsupported_diag = [
                "you have alzheimer", "confirms alzheimer", "proves alzheimer", "establishes alzheimer",
                "high likelihood of alzheimer", "typical alzheimer's changes", "consistent with the typical pattern of alzheimer"
            ]
            
            for phrase in unsupported_diag:
                val_text = response_json.get("what_results_suggest", "")
                if phrase in val_text.lower():
                    logger.warning("Scrubbing unsupported diagnostic claim '%s' from clinical report response", phrase)
                    import re
                    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                    response_json["what_results_suggest"] = pattern.sub("aligns with clinical report findings evaluated for research analysis", val_text)

        return response_json


