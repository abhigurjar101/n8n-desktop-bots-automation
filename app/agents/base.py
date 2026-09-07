"""
Base Agent Interface for n8n Desktop Bots Suite.
Provides standard execution contract, metadata, and fallback helpers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAgent(ABC):
    """Abstract base class for all 9 specialized engineering bots."""

    def __init__(self, bot_id: str, name: str, emoji: str, category: str):
        self.bot_id = bot_id
        self.name = name
        self.emoji = emoji
        self.category = category

    @abstractmethod
    async def execute(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent task and return a structured dictionary."""
        pass

    def format_markdown(self, title: str, sections: Dict[str, str]) -> str:
        """Helper to format structured markdown outputs."""
        lines = [f"## {self.emoji} {title}\n"]
        for heading, body in sections.items():
            lines.append(f"### {heading}\n{body}\n")
        return "\n".join(lines)
