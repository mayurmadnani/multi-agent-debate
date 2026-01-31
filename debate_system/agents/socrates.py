"""Socrates agent."""
from __future__ import annotations

from .base import BaseAgent


class SocratesAgent(BaseAgent):
    """Asks clarifying questions to challenge assumptions."""

    def get_system_prompt(self) -> str:
        return (
            f"{self.instruction}\n"
            "Ask exactly one concise clarifying question that challenges the premise."
        )
