"""Plato agent."""
from __future__ import annotations

from .base import BaseAgent


class PlatoAgent(BaseAgent):
    """Provides theoretical framing and one insightful remark."""

    def get_system_prompt(self) -> str:
        return (
            f"{self.instruction}\n"
            "Offer one insightful comment tying the topic to philosophical theory or frameworks."
        )
