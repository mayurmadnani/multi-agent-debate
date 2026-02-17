"""Summary agent to synthesize debates."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..core.memory import MemoryStore


class SummaryAgent(BaseAgent):
    """Produces a concise summary of the debate."""

    def get_system_prompt(self) -> str:
        return (
            f"{self.instruction}\n"
            "Summarize the discussion clearly, list 2-3 key takeaways, and note any open questions."
        )

    def build_prompt(
        self,
        user_prompt: str,
        history: List[Dict[str, Any]],
        memory: Optional[MemoryStore] = None,
    ) -> str:
        parts = [
            self.get_system_prompt(),
            "",
            "## Original Question:",
            user_prompt,
            "",
            "## Full Conversation:",
            self.format_history(history),
            "",
            f"## Your Response as {self.name}:",
            f"{self.name}:",
        ]
        return "\n".join(parts)
