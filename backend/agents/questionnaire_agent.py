import logging
from typing import Dict, Any, List

from backend.agents.base_agent import BaseAgent
from backend.agents.state import AgentState, AgentResult

logger = logging.getLogger(__name__)

# Metadata lookup for question concepts and domains
QUESTION_METADATA: Dict[str, Dict[str, str]] = {
    # Alzheimer's questions
    "ALZ_Q01": {"domain": "recent memory", "concept": "episodic memory impairment"},
    "ALZ_Q02": {"domain": "repeating questions/stories", "concept": "short-term memory deficit"},
    "ALZ_Q03": {"domain": "remembering appointments", "concept": "prospective memory loss"},
    "ALZ_Q04": {"domain": "word finding", "concept": "anomia / language deficit"},
    "ALZ_Q05": {"domain": "familiar places", "concept": "visuospatial disorientation"},
    "ALZ_Q06": {"domain": "planning", "concept": "executive dysfunction"},
    "ALZ_Q07": {"domain": "managing everyday activities", "concept": "impaired daily functioning"},
    "ALZ_Q08": {"domain": "completing tasks", "concept": "apraxia / functional decline"},
    "ALZ_Q09": {"domain": "following conversations", "concept": "receptive language impairment"},
    "ALZ_Q10": {"domain": "independence", "concept": "global functional decline"},
    # Parkinson's questions
    "PD_Q01": {"domain": "tremor", "concept": "resting tremor"},
    "PD_Q02": {"domain": "slowness of movement", "concept": "bradykinesia"},
    "PD_Q03": {"domain": "stiffness", "concept": "muscle rigidity"},
    "PD_Q04": {"domain": "walking changes", "concept": "shuffling gait"},
    "PD_Q05": {"domain": "balance", "concept": "postural instability"},
    "PD_Q06": {"domain": "getting up/turning", "concept": "motor difficulties / freezing"},
    "PD_Q07": {"domain": "handwriting changes", "concept": "micrographia"},
    "PD_Q08": {"domain": "speech/voice changes", "concept": "hypophonia"},
    "PD_Q09": {"domain": "fine motor control", "concept": "loss of fine motor control"},
    "PD_Q10": {"domain": "daily activity changes", "concept": "functional decline"},
}


class QuestionnaireAgent(BaseAgent):
    name = "Questionnaire Agent"
    description = "Validates and summarizes questionnaire responses into a domain profile."

    def __init__(self):
        pass

    async def execute(self, state: AgentState) -> AgentResult:
        logger.info("QuestionnaireAgent: Validating and summarizing questionnaire responses...")
        
        # Enforce workflow isolation: If workflow is not QUESTIONNAIRE, clear questionnaire_profile
        if state.workflow != "QUESTIONNAIRE":
            state.questionnaire_profile = None
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={"status": "skipped", "reason": f"Workflow {state.workflow} is not QUESTIONNAIRE"}
            )

        try:
            if not state.questionnaire_results:
                return AgentResult(
                    agent_name=self.name,
                    success=False,
                    error="No questionnaire data provided."
                )
                
            responses = state.questionnaire_results.get("responses", [])
            q_id = state.questionnaire_results.get("questionnaire_id", "")
            
            # 1. Validate response count based on ID
            expected_count = 10
            if q_id == "BOTH_SCREENING":
                expected_count = 20
                
            if len(responses) != expected_count:
                return AgentResult(
                    agent_name=self.name,
                    success=False,
                    error=f"Expected {expected_count} responses for {q_id}, but got {len(responses)}."
                )
                
            # 2. Build domain profile & deterministic scoring
            # Answers: Never: 0, Rarely: 1, Sometimes: 2, Often: 3
            score_map = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3}
            
            total_score = 0
            max_score = len(responses) * 3
            domain_profile = {}
            concerns = []
            positive_findings = []
            negative_findings = []
            
            for ans in responses:
                q = ans.get("question_id", "")
                ans_str = ans.get("answer", "Never")
                val = score_map.get(ans_str, 0)
                total_score += val
                
                # Grouping by prefix ALZ vs PD
                domain_type = "cognitive" if q.startswith("ALZ") else "movement"
                domain_profile[domain_type] = domain_profile.get(domain_type, 0) + val
                
                meta = QUESTION_METADATA.get(q, {"domain": q, "concept": "reported symptom"})
                finding_desc = f"{q}: {meta['concept']} ({ans_str})"
                
                if val > 0:
                    positive_findings.append(finding_desc)
                else:
                    negative_findings.append(f"{q}: {meta['concept']} (Never)")
                
                if val >= 2:
                    concerns.append(f"Concern noted on {q} ({meta['concept']}: {ans_str})")
            
            # Deterministic symptom burden percentage thresholds
            symptom_ratio = (total_score / max_score) if max_score > 0 else 0.0
            if total_score == 0:
                symptom_burden = "none"
            elif symptom_ratio <= 0.20:
                symptom_burden = "minimal"
            elif symptom_ratio <= 0.45:
                symptom_burden = "mild"
            elif symptom_ratio <= 0.75:
                symptom_burden = "moderate"
            else:
                symptom_burden = "high"

            disease_context = list(state.disease_context) if state.disease_context else []
            if not disease_context:
                if "ALZ" in q_id:
                    disease_context.append("alzheimers")
                if "PD" in q_id or "PARKINSON" in q_id:
                    disease_context.append("parkinsons")
                if "BOTH" in q_id:
                    disease_context = ["alzheimers", "parkinsons"]

            from backend.models.adni_schemas import QuestionnaireProfile, QuestionnaireAnswer
            version = state.questionnaire_results.get("version", "1.0")
            formatted_responses = [
                QuestionnaireAnswer(question_id=r.get("question_id", ""), answer=r.get("answer", ""))
                for r in responses
            ]

            prof_obj = QuestionnaireProfile(
                questionnaire_id=q_id,
                version=version,
                responses=formatted_responses,
                questionnaire_score=total_score,
                questionnaire_max_score=max_score,
                symptom_burden=symptom_burden,
                positive_findings=positive_findings,
                negative_findings=negative_findings,
                disease_context=disease_context
            )
            profile_summary = prof_obj.model_dump()

            state.disease_context = disease_context
            state.questionnaire_profile = profile_summary
            
            logger.info(
                f"QuestionnaireAgent: Processed {len(responses)} responses. "
                f"Score: {total_score}/{max_score} (Burden: {symptom_burden}). Context: {disease_context}"
            )
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=profile_summary
            )
            
        except Exception as e:
            logger.error(f"QuestionnaireAgent error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e)
            )


