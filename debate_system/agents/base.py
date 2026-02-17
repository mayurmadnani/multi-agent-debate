"""Base agent definitions."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..core.config import AgentConfig
from ..core.memory import MemoryStore
from ..inference.manager import generate_text

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for philosopher agents."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.name = config.name
        self.instruction = config.instruction
        logger.debug(f"Initialized agent: {self.name}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Persona-specific system prompt."""

    def format_history(self, history: List[Dict[str, Any]]) -> str:
        if not history:
            return "(No prior conversation)"

        lines = []
        for turn in history:
            speaker = turn.get("speaker") or turn.get("agent") or "Unknown"
            content = turn.get("content") or turn.get("response") or ""
            content = str(content).strip()
            if content:
                lines.append(f"[{speaker}] {content}")
        return "\n".join(lines) if lines else "(No prior conversation)"

    def format_memory(self, memory: Optional[MemoryStore], limit: int = 5) -> str:
        if memory is None:
            return "(No memory available)"
        return memory.format_for_prompt(limit)

    def build_prompt(
        self,
        user_prompt: str,
        history: List[Dict[str, Any]],
        memory: Optional[MemoryStore] = None,
    ) -> str:
        parts = [
            self.get_system_prompt(),
            "",
            "## Conversation History:",
            self.format_history(history),
        ]

        if memory:
            parts.extend([
                "",
                "## Relevant Context:",
                self.format_memory(memory),
            ])

        parts.extend([
            "",
            "## Current Question:",
            user_prompt,
            "",
            f"## Your Response as {self.name}:",
            f"{self.name}:",
        ])

        return "\n".join(parts)

    def extract_response(self, raw_output: str) -> str:
        """Extract the agent's core response from raw model output."""
        response = raw_output.strip()
        
        # Remove common speaker prefixes
        prefixes = [f"{self.name}:", f"[{self.name}]"]
        for prefix in prefixes:
            if response.lower().startswith(prefix.lower()):
                response = response[len(prefix):].strip()
                break

        # Return the response, preserving newlines
        return response.strip()

    def generate_response(
        self,
        user_prompt: str,
        history: List[Dict[str, Any]],
        memory: Optional[MemoryStore] = None,
        **generation_kwargs: Any,
    ) -> str:
        prompt = self.build_prompt(user_prompt, history, memory)
        params = {
            "temperature": self.config.temperature,
            "max_new_tokens": self.config.max_tokens,
        }
        params.update(generation_kwargs)

        logger.debug(f"{self.name} generating with params: {params}")
        raw = generate_text(prompt, **params)
        response = self.extract_response(raw)
        logger.info(f"{self.name} responded:\n{response}")
        return response
