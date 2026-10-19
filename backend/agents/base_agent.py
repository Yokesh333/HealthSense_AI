"""
backend/agents/base_agent.py

Abstract base class that every agent in the HealthSense AI multi-agent
system must implement.

Design goals:
  - Minimal interface — name, description, execute().
  - Async execute() so I/O-bound agents (RAG, web) work without blocking.
  - No framework dependencies — plain Python ABC.
"""

from abc import ABC, abstractmethod

from backend.agents.state import AgentResult, AgentState


class BaseAgent(ABC):
    """
    Abstract base for all HealthSense AI agents.

    Subclasses must set `name` and `description` as class-level attributes
    and implement the `execute` coroutine.

    Example future agents that will follow this interface:
      - RAGAgent
      - WebIntelligenceAgent
      - ClinicalSynthesisAgent
      - ImagingAgent
    """

    #: Human-readable agent identifier (used in API responses and logging).
    name: str

    #: Short description of what this agent does.
    description: str

    @abstractmethod
    async def execute(self, state: AgentState) -> AgentResult:
        """
        Execute the agent's task.

        Args:
            state: The shared workflow state.  Agents READ clinical_features
                   and any upstream results they depend on, then WRITE their
                   output into an AgentResult.

        Returns:
            AgentResult with success=True and populated data, or
            success=False and an error message.

        The agent must NEVER raise an unhandled exception to the orchestrator.
        All errors must be caught and returned as AgentResult(success=False).
        """
        ...

    def __repr__(self) -> str:
        return f"<Agent name={self.name!r}>"
