"""
backend/agents/parkinson_agent.py

Parkinson's Disease ML Agent for multi-agent orchestrator pipeline.

Responsibility: Call injected ParkinsonPredictor and store result in shared AgentState.

CRITICAL CONSTRAINTS:
  - Does NOT load joblib artifact directly.
  - Does NOT instantiate a new predictor.
  - Injected from app.state (loaded once at startup).
"""

import logging
from typing import Any, Dict

from backend.agents.base_agent import BaseAgent
from backend.agents.state import (
    AgentResult,
    AgentState,
    ParkinsonMLPredictionResult,
)
from backend.services.parkinson_predictor import ParkinsonPredictor

logger = logging.getLogger(__name__)


class ParkinsonMLAgent(BaseAgent):
    name: str = "Parkinson ML Agent"
    description: str = (
        "Runs the Parkinson's Disease Random Forest classifier to produce a Healthy Control / "
        "Parkinson's Disease prediction with class probabilities and SHAP explanations."
    )

    def __init__(self, predictor: ParkinsonPredictor) -> None:
        self._predictor = predictor

    @property
    def predictor(self) -> ParkinsonPredictor:
        return self._predictor

    async def execute(self, state: AgentState) -> AgentResult:
        logger.info("Parkinson ML Agent: starting prediction.")

        if not state.parkinson_features:
            logger.warning("Parkinson ML Agent: no Parkinson features provided in state.")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="No Parkinson clinical features available in state."
            )

        features: Dict[str, Any] = state.parkinson_features.model_dump()

        try:
            raw: Dict[str, Any] = self._predictor.predict(features)
        except Exception as exc:
            logger.error("Parkinson ML Agent: prediction failed — %s", exc)
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Parkinson ML prediction failed: {str(exc)}"
            )

        ml_result = ParkinsonMLPredictionResult(
            predicted_class=raw["predicted_class"],
            predicted_label=raw["predicted_label"],
            pd_probability=raw["pd_probability"],
            healthy_control_probability=raw["healthy_control_probability"],
            probabilities=raw["probabilities"],
            model_name=raw["model"]["name"],
            model_version=raw["model"]["version"],
            feature_values_used=raw["feature_values_used"],
            feature_availability=raw["feature_availability"],
            clinical_notice=raw["clinical_notice"],
            explainability=raw.get("explainability"),
        )

        # Mutate shared state
        state.parkinson_prediction = ml_result

        logger.info("Parkinson ML Agent: prediction completed — label=%s", ml_result.predicted_label)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "predicted_class": ml_result.predicted_class,
                "predicted_label": ml_result.predicted_label,
                "pd_probability": ml_result.pd_probability,
                "healthy_control_probability": ml_result.healthy_control_probability,
                "probabilities": ml_result.probabilities,
                "model_name": ml_result.model_name,
                "model_version": ml_result.model_version,
                "feature_availability": ml_result.feature_availability,
                "clinical_notice": ml_result.clinical_notice,
            }
        )
