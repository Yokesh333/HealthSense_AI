"""
backend/agents/adni_agent.py

ADNI ML Agent — the Phase 5 production agent.

Responsibility: Call the EXISTING ADNIPredictor and store the result in the
shared AgentState.

CRITICAL CONSTRAINTS:
  - This agent does NOT load adni_model.joblib.
  - This agent does NOT contain any ML/preprocessing logic.
  - This agent does NOT instantiate a new ADNIPredictor.
  - The ADNIPredictor instance is injected at construction time.
  - The single shared predictor comes from FastAPI app.state (loaded once
    at startup in backend/main.py).
"""

import logging
from typing import Any, Dict

from backend.agents.base_agent import BaseAgent
from backend.agents.state import (
    AgentResult,
    AgentState,
    MLPredictionResult,
)
from backend.services.adni_predictor import ADNIPredictor

logger = logging.getLogger(__name__)


class ADNIMLAgent(BaseAgent):
    """
    Wraps the existing ADNIPredictor Random Forest classifier.

    The predictor instance is injected by the Orchestrator so that the model
    is loaded exactly once (during FastAPI startup) and reused for every
    request.
    """

    name: str = "ADNI ML Agent"
    description: str = (
        "Runs the ADNI Random Forest classifier to produce a CN / MCI / AD "
        "prediction with class probabilities."
    )

    def __init__(self, predictor: ADNIPredictor) -> None:
        """
        Args:
            predictor: The shared ADNIPredictor instance from app.state.
                       Must already have load_model() called.
        """
        self._predictor = predictor

    @property
    def predictor(self) -> ADNIPredictor:
        """Expose the injected predictor for identity checks in tests."""
        return self._predictor

    async def execute(self, state: AgentState) -> AgentResult:
        """
        Run the ADNI ML prediction.

        Reads:  state.clinical_features
        Writes: state.ml_prediction  (via the returned AgentResult.data)

        Returns:
            AgentResult with the ML prediction, or an error result if
            prediction fails.
        """
        logger.info("ADNI ML Agent: starting prediction.")

        # Convert Pydantic model → plain dict for the predictor
        features: Dict[str, Any] = state.clinical_features.model_dump()

        try:
            raw: Dict[str, Any] = self._predictor.predict(features)
        except Exception as exc:
            logger.error("ADNI ML Agent: prediction failed — %s", exc)
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="ADNI ML prediction failed. Internal error logged.",
            )

        # Unpack the predictor's standard return dict
        # Guard: explainability may be None (SHAP unavailable) or a valid SHAP dict.
        # If for any reason it is an unexpected type/dict, Pydantic will reject it—
        # catch that here and fall back to None rather than crashing the agent.
        raw_explainability = raw.get("explainability")
        if raw_explainability is not None and not isinstance(raw_explainability, dict):
            # Already a Pydantic model (shouldn’t happen, but be safe)
            raw_explainability = None
        elif isinstance(raw_explainability, dict) and "error" in raw_explainability:
            logger.error(
                "ADNI ML Agent: SHAP returned an error dict — discarding. "
                "Error: %s", raw_explainability.get("error")
            )
            raw_explainability = None

        try:
            ml_result = MLPredictionResult(
                predicted_class=raw["prediction"],
                probabilities=raw["probabilities"],
                model_name=raw["model"]["name"],
                model_version=raw["model"]["version"],
                clinical_notice=raw["clinical_notice"],
                explainability=raw_explainability,
            )
        except Exception as exc:
            logger.error(
                "ADNI ML Agent: MLPredictionResult construction failed — %s: %s "
                "(explainability will be None)", type(exc).__name__, exc
            )
            ml_result = MLPredictionResult(
                predicted_class=raw["prediction"],
                probabilities=raw["probabilities"],
                model_name=raw["model"]["name"],
                model_version=raw["model"]["version"],
                clinical_notice=raw["clinical_notice"],
                explainability=None,
            )

        # Mutate shared state so the orchestrator can read it
        state.ml_prediction = ml_result

        logger.info(
            "ADNI ML Agent: prediction completed — class=%s",
            ml_result.predicted_class,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "predicted_class": ml_result.predicted_class,
                "probabilities": ml_result.probabilities,
                "model_name": ml_result.model_name,
                "model_version": ml_result.model_version,
                "clinical_notice": ml_result.clinical_notice,
            },
        )
