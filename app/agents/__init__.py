"""
Agent Registry for n8n Desktop Bots Suite.
Provides access to all 9 specialized engineering agents.
"""

from typing import Dict, Optional
from app.agents.base import BaseAgent
from app.agents.coding_assistant import CodingAssistantAgent
from app.agents.rag_bot import RagBotAgent
from app.agents.system_design import SystemDesignAgent
from app.agents.high_thinking import HighThinkingAgent
from app.agents.testing_bot import TestingBotAgent
from app.agents.advanced_rag import AdvancedRagAgent
from app.agents.cloud_deployment import CloudDeploymentAgent
from app.agents.ml_pipeline import MlPipelineAgent
from app.agents.n8n_manager import N8nManagerAgent

# Registry of singleton instances
AGENT_REGISTRY: Dict[str, BaseAgent] = {
    "coding-assistant": CodingAssistantAgent(),
    "rag-bot": RagBotAgent(),
    "system-design": SystemDesignAgent(),
    "high-thinking": HighThinkingAgent(),
    "testing-bot": TestingBotAgent(),
    "advanced-rag": AdvancedRagAgent(),
    "cloud-deployment": CloudDeploymentAgent(),
    "ml-pipeline": MlPipelineAgent(),
    "n8n-manager": N8nManagerAgent(),
}


def get_agent(bot_id: str) -> Optional[BaseAgent]:
    """Retrieves an agent by its unique identifier."""
    return AGENT_REGISTRY.get(bot_id)
