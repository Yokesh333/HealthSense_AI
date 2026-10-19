"""
backend/agents/orchestrator.py

Orchestrator / Supervisor for the HealthSense AI multi-agent system.

Multi-disease routing design:
  - Disease context 'alzheimers': Runs ADNIMLAgent only.
  - Disease context 'parkinsons': Runs ParkinsonMLAgent only.
  - Disease context 'both' or ['alzheimers', 'parkinsons']: Runs both predictors if valid inputs exist, keeping predictions separate.
"""

import logging
from typing import List, Optional

from backend.agents.adni_agent import ADNIMLAgent
from backend.agents.parkinson_agent import ParkinsonMLAgent
from backend.agents.rag_agent import RAGAgent
from backend.agents.web_agent import WebIntelligenceAgent
from backend.agents.llm_agent import LLMAgent
from backend.agents.base_agent import BaseAgent
from backend.rag.service import RAGService
from backend.services.web_intelligence_service import BaseWebIntelligenceService
from backend.services.llm_service import BaseLLMService
from backend.agents.state import (
    ADNIClinicalFeatures,
    ParkinsonClinicalFeatures,
    AgentAnalysisResponse,
    AgentState,
    ModelInfo,
    PredictionSummary,
)
from backend.services.adni_predictor import ADNIPredictor
from backend.services.parkinson_predictor import ParkinsonPredictor

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Supervisor that coordinates agent execution for multi-disease analysis requests.
    """

    WORKFLOW_NAME = "UNIFIED_ANALYSIS"

    def __init__(
        self, 
        predictor: ADNIPredictor,
        parkinson_predictor: Optional[ParkinsonPredictor] = None,
        rag_service: Optional[RAGService] = None,
        web_service: Optional[BaseWebIntelligenceService] = None,
        llm_service: Optional[BaseLLMService] = None
    ) -> None:
        """
        Args:
            predictor: Shared ADNIPredictor from app.state.adni_predictor.
            parkinson_predictor: Shared ParkinsonPredictor from app.state.parkinson_predictor.
            rag_service: Optional RAGService from app.state.
            web_service: Optional BaseWebIntelligenceService from app.state.
            llm_service: Optional LLMService from app.state.
        """
        self._predictor = predictor
        self._parkinson_predictor = parkinson_predictor
        self._rag_service = rag_service
        self._web_service = web_service
        self._llm_service = llm_service

        # Instantiate agents
        self._adni_agent = ADNIMLAgent(predictor=self._predictor)
        self._parkinson_agent = ParkinsonMLAgent(predictor=self._parkinson_predictor) if self._parkinson_predictor else None
        self._rag_agent = RAGAgent(rag_service=self._rag_service)
        self._web_agent = WebIntelligenceAgent(web_service=self._web_service)
        self._llm_agent = LLMAgent(llm_service=self._llm_service)

    # ------------------------------------------------------------------
    # Routing hook
    # ------------------------------------------------------------------

    def _select_agents(self, state: AgentState) -> List[BaseAgent]:
        """
        Determine which agents to run for an ADNI_ML or PARKINSON_ML or CLINICAL_REPORT workflow.
        """
        agents: List[BaseAgent] = []

        # Check disease_context or input features available
        run_adni = False
        run_parkinson = False

        if state.workflow == "ADNI_ML":
            run_adni = True
        elif state.workflow == "PARKINSON_ML":
            run_parkinson = True
        elif state.workflow == "CLINICAL_REPORT":
            ctx = [d.lower() for d in state.disease_context]
            if "alzheimers" in ctx or "both" in ctx:
                if state.clinical_features is not None:
                    run_adni = True
            if "parkinsons" in ctx or "both" in ctx:
                if state.parkinson_features is not None:
                    run_parkinson = True
            if not ctx or ctx == ["unknown"]:
                if state.clinical_features is not None:
                    run_adni = True
                if state.parkinson_features is not None:
                    run_parkinson = True

        if run_adni:
            agents.append(self._adni_agent)
        if run_parkinson and self._parkinson_agent:
            agents.append(self._parkinson_agent)

        agents.append(self._rag_agent)

        # Check for web keywords
        needs_web = False
        question_text = ""
        if state.clinical_features and state.clinical_features.clinical_question:
            question_text = state.clinical_features.clinical_question
        elif state.parkinson_features and state.parkinson_features.clinical_question:
            question_text = state.parkinson_features.clinical_question

        if question_text:
            q_lower = question_text.lower()
            keywords = [
                "latest", "recent", "current", "update", "updated", 
                "new", "newest", "2026", "treatment", "treatments", 
                "fda", "approval", "approved", "news", "recent studies", 
                "new research", "clinical trials", "trial", "guideline", "guidelines"
            ]
            if any(kw in q_lower for kw in keywords):
                needs_web = True
                logger.info("Orchestrator: Routing to WebIntelligenceAgent due to keywords.")

        if needs_web:
            agents.append(self._web_agent)

        agents.append(self._llm_agent)
        return agents

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def analyze_unified(
        self, data: 'UnifiedAnalysisRequest'
    ) -> AgentAnalysisResponse:
        """
        Execute the multi-agent workflow based on the request type and disease context.
        """
        logger.info("Orchestrator: unified workflow started (type=%s).", data.type)

        workflow_type = data.type

        clinical_features = None
        parkinson_features = None
        clinical_profile = None
        questionnaire_results = None
        questionnaire_profile = None

        if workflow_type == "QUESTIONNAIRE":
            # Strictly isolate: Questionnaire workflow contains ONLY questionnaire data
            questionnaire_results = data.questionnaire_data.model_dump() if data.questionnaire_data else None
        elif workflow_type in ("CLINICAL_REPORT", "ADNI_ML", "PARKINSON_ML"):
            clinical_profile = getattr(data, "clinical_profile", None)

            if getattr(data, "adni_data", None):
                try:
                    clinical_features = ADNIClinicalFeatures(**data.adni_data.model_dump())
                except Exception as exc:
                    logger.debug("Orchestrator: Invalid adni_data passed: %s", exc)

            if getattr(data, "parkinson_data", None):
                try:
                    parkinson_features = ParkinsonClinicalFeatures(**data.parkinson_data.model_dump())
                except Exception as exc:
                    logger.debug("Orchestrator: Invalid parkinson_data passed: %s", exc)

            if clinical_profile:
                try:
                    from backend.models.report_schemas import StructuredClinicalProfile
                    from backend.services.report_adapter import ClinicalProfileAdapter
                    prof_obj = StructuredClinicalProfile(**clinical_profile)
                    adapted = ClinicalProfileAdapter.adapt(prof_obj)

                    if adapted.adni_data and not clinical_features:
                        clinical_features = ADNIClinicalFeatures(**adapted.adni_data.model_dump())
                    if adapted.parkinson_data and not parkinson_features:
                        parkinson_features = ParkinsonClinicalFeatures(**adapted.parkinson_data.model_dump())
                except Exception as exc:
                    logger.debug("Orchestrator: Could not auto-adapt clinical_profile: %s", exc)

        state = AgentState(
            workflow=workflow_type,
            disease_context=getattr(data, "disease_context", []) or [],
            clinical_features=clinical_features,
            parkinson_features=parkinson_features,
            questionnaire_results=questionnaire_results,
            questionnaire_profile=questionnaire_profile,
            clinical_profile=clinical_profile,
        )

        import time
        workflow_start = time.time()
        logger.info(f"[ANALYZE] Request received (type={workflow_type})")

        agents: List[BaseAgent] = []
        if workflow_type in ("ADNI_ML", "PARKINSON_ML", "CLINICAL_REPORT"):
            agents = self._select_agents(state)
        elif workflow_type == "QUESTIONNAIRE":
            from backend.agents.questionnaire_agent import QuestionnaireAgent
            agents = [QuestionnaireAgent(), self._rag_agent, self._llm_agent]
        else:
            state.errors.append(f"Unknown workflow type: {workflow_type}")
            return AgentAnalysisResponse(
                workflow=workflow_type,
                status="failed",
                agents_executed=[],
                errors=state.errors,
            )

        agent_names = [a.name for a in agents]
        logger.info("Orchestrator: agents selected — %s", agent_names)

        # ------------------------------------------------------------------
        # Agent execution
        # ------------------------------------------------------------------
        for agent in agents:
            agent_start = time.time()
            logger.info("Orchestrator: executing agent=%r", agent.name)
            result = await agent.execute(state)
            agent_dur = time.time() - agent_start
            logger.info(f"[ANALYZE] {agent.name}: {agent_dur:.3f}s")
            state.agent_results.append(result)

            if not result.success:
                error_msg = result.error or "Agent failed with an unknown error."
                state.errors.append(f"{agent.name}: {error_msg}")
                logger.error("Orchestrator: agent=%r failed — %s", agent.name, error_msg)

                if agent.name in ("ADNI ML Agent", "Parkinson ML Agent"):
                    # Log error but continue pipeline so RAG / LLM can run
                    logger.warning("Orchestrator: continuing workflow despite ML Agent failure.")
                    continue
                else:
                    logger.warning("Orchestrator: continuing workflow despite %r failure.", agent.name)
                    continue

            logger.info("Orchestrator: agent=%r completed successfully.", agent.name)

        logger.info(f"[ANALYZE] Total analysis duration: {time.time() - workflow_start:.3f}s")

        # ------------------------------------------------------------------
        # Response assembly
        # ------------------------------------------------------------------
        agents_executed = [r.agent_name for r in state.agent_results if r.success]

        prediction_summary = None
        model_info = None
        explainability = None
        clinical_notice = "This is an AI-assisted screening/research result and is not a medical diagnosis."

        if state.ml_prediction:
            ml = state.ml_prediction
            prediction_summary = PredictionSummary(**{"class": ml.predicted_class, "probabilities": ml.probabilities})
            model_info = ModelInfo(name=ml.model_name, version=ml.model_version)
            explainability = ml.explainability
            clinical_notice = ml.clinical_notice

        parkinson_pred_dict = None
        parkinson_expl_obj = None

        if state.parkinson_prediction:
            pk = state.parkinson_prediction
            parkinson_pred_dict = {
                "predicted_class": pk.predicted_class,
                "predicted_label": pk.predicted_label,
                "pd_probability": pk.pd_probability,
                "healthy_control_probability": pk.healthy_control_probability,
                "probabilities": pk.probabilities,
                "model_name": pk.model_name,
                "model_version": pk.model_version,
                "feature_values_used": pk.feature_values_used,
                "feature_availability": pk.feature_availability.model_dump(),
                "clinical_notice": pk.clinical_notice,
            }
            parkinson_expl_obj = pk.explainability
            if not clinical_notice or clinical_notice == "This is an AI-assisted screening/research result and is not a medical diagnosis.":
                clinical_notice = pk.clinical_notice

        evidence = state.rag_results.get("results", []) if state.rag_results else []
        web_evidence = state.web_results if state.web_results else []
        explanation = state.llm_response or {}

        return AgentAnalysisResponse(
            workflow=workflow_type,
            status="completed",
            disease_context=state.disease_context,
            prediction=prediction_summary,
            model=model_info,
            parkinson_prediction=parkinson_pred_dict,
            parkinson_explainability=parkinson_expl_obj,
            questionnaire_profile=state.questionnaire_profile if workflow_type == "QUESTIONNAIRE" else None,
            explanation=explanation,
            evidence=evidence,
            web_evidence=web_evidence,
            agents_executed=agents_executed,
            clinical_notice=clinical_notice,
            explainability=explainability,
        )
