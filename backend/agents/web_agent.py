import logging
from typing import Optional

from backend.agents.base_agent import BaseAgent
from backend.agents.state import AgentResult, AgentState
from backend.services.web_intelligence_service import BaseWebIntelligenceService

logger = logging.getLogger(__name__)

class WebIntelligenceAgent(BaseAgent):
    """
    Agent responsible for querying external web sources (PubMed)
    when current information is required by the user's clinical question.
    """
    
    @property
    def name(self) -> str:
        return "Web Intelligence Agent"

    def __init__(self, web_service: Optional[BaseWebIntelligenceService]):
        self._web_service = web_service

    async def execute(self, state: AgentState) -> AgentResult:
        logger.info("%s: executing...", self.name)
        
        if not self._web_service:
            msg = "WebIntelligenceService not available, skipping web search."
            logger.warning("%s: %s", self.name, msg)
            state.web_results = []
            return AgentResult(agent_name=self.name, success=False, error=msg, data={"total_results": 0})
            
        try:
            if state.clinical_features and state.clinical_features.clinical_question:
                user_q = state.clinical_features.clinical_question
                query = user_q
                if "alzheimer" not in query.lower() and "dementia" not in query.lower() and "parkinson" not in query.lower():
                    diseases = " ".join(state.disease_context) if state.disease_context else "Alzheimer's"
                    query = f"{diseases} {query}"
            elif state.questionnaire_profile:
                diseases = " ".join(state.disease_context) if state.disease_context else "Alzheimer's Parkinson's"
                query = f"{diseases} screening clinical research updates"
            else:
                query = "Alzheimer's disease recent guidelines"

            logger.info("%s: querying web with: '%s'", self.name, query)
            
            results = await self._web_service.search(query=query)
            
            # Store structured results in state
            state.web_results = results
            
            logger.info("%s: retrieved %d web results.", self.name, len(results))
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={"total_results": len(results)}
            )
            
        except Exception as e:
            logger.error("%s: failed - %s", self.name, str(e))
            state.web_results = []
            return AgentResult(agent_name=self.name, success=False, error=str(e), data={"total_results": 0})
