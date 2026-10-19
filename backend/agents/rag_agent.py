import logging
from typing import Optional

from backend.agents.base_agent import BaseAgent
from backend.agents.state import AgentResult, AgentState
from backend.rag.service import RAGService
from backend.config import RAG_TOP_K

logger = logging.getLogger(__name__)

class RAGAgent(BaseAgent):
    """
    Agent responsible for querying the Biomedical RAG system based on the
    user's clinical question or the ML prediction result.
    """
    
    @property
    def name(self) -> str:
        return "RAG Agent"

    def __init__(self, rag_service: Optional[RAGService]):
        self._rag_service = rag_service

    async def execute(self, state: AgentState) -> AgentResult:
        logger.info("%s: executing...", self.name)
        
        if not self._rag_service:
            msg = "RAGService not available, skipping retrieval."
            logger.warning("%s: %s", self.name, msg)
            return AgentResult(agent_name=self.name, success=False, error=msg)
            
        try:
            # Build query base
            if state.clinical_features and state.clinical_features.clinical_question:
                base_query = state.clinical_features.clinical_question
            elif state.clinical_profile:
                cp = state.clinical_profile
                findings = []
                if cp.get("symptoms"):
                    findings.extend(cp["symptoms"])
                if cp.get("clinical_impression"):
                    findings.append(cp["clinical_impression"])
                if cp.get("cognitive_findings", {}).get("details"):
                    findings.extend(cp["cognitive_findings"]["details"])
                if cp.get("motor_findings", {}).get("details"):
                    findings.extend(cp["motor_findings"]["details"])
                
                query_terms = " ".join(findings[:5])
                base_query = f"clinical findings pathology evidence {query_terms}".strip()
            elif state.questionnaire_profile:
                concerns = " ".join(state.questionnaire_profile.get("areas_of_concern", []))
                base_query = f"screening assessment clinical characteristics {concerns}".strip()
            elif state.ml_prediction:
                ml_class = state.ml_prediction.predicted_class
                base_query = f"clinical diagnosis cognitive assessment {ml_class} dementia"
            else:
                base_query = "clinical characteristics and evidence"

            retrieval_response = []
            
            if len(state.disease_context) > 1:
                # Query each disease separately to maintain distinct evidence retrieval and disease attribution
                per_disease_k = max(2, RAG_TOP_K // len(state.disease_context))
                for dis in state.disease_context:
                    dis_query = f"{dis} {base_query}".strip()
                    logger.info("%s: querying RAG for disease=%s with: '%s' (top_k=%d)", self.name, dis, dis_query, per_disease_k)
                    res = self._rag_service.retrieve(query=dis_query, top_k=per_disease_k, disease=dis)
                    retrieval_response.extend(res)
            elif len(state.disease_context) == 1:
                dis = state.disease_context[0]
                dis_query = f"{dis} {base_query}".strip()
                logger.info("%s: querying RAG for disease=%s with: '%s' (top_k=%d)", self.name, dis, dis_query, RAG_TOP_K)
                retrieval_response = self._rag_service.retrieve(query=dis_query, top_k=RAG_TOP_K, disease=dis)
            else:
                logger.info("%s: querying RAG with default query: '%s' (top_k=%d)", self.name, base_query, RAG_TOP_K)
                retrieval_response = self._rag_service.retrieve(query=base_query, top_k=RAG_TOP_K)

            # Store full results in state
            state.rag_results = {"results": [r.model_dump() for r in retrieval_response]}
            
            logger.info("%s: retrieved %d chunks.", self.name, len(retrieval_response))
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={"total_results": len(retrieval_response)}
            )
            
        except Exception as e:
            logger.error("%s: failed - %s", self.name, str(e))
            return AgentResult(agent_name=self.name, success=False, error=str(e))
