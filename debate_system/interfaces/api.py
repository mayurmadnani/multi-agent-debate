"""Programmatic API for the debate system."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core import build_orchestrator, ConfigManager
from ..utils.logger import setup_logging


class DebateAPI:
    """Convenient wrapper for running debates programmatically."""

    def __init__(
        self,
        settings_path: str = "configs/settings.yaml",
        personas_path: str = "configs/personas.yaml",
        tools_path: str = "configs/tools.yaml",
    ) -> None:
        self.config_manager = ConfigManager(
            settings_path=settings_path,
            personas_path=personas_path,
            tools_path=tools_path,
        )
        setup_logging(self.config_manager.get_logging_config())
        self.orchestrator = build_orchestrator(config_manager=self.config_manager)

    def ask(self, question: str, rounds: Optional[int] = None, enable_summary: Optional[bool] = None) -> Dict[str, Any]:
        return self.orchestrator.run_debate(question, rounds=rounds, enable_summary=enable_summary)

    def get_memory(self, key: str) -> Optional[Any]:
        return self.orchestrator.memory.get_entry(key)

    def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        entries = self.orchestrator.memory.search(query, limit)
        return [entry.to_dict() for entry in entries]

    def clear_memory(self) -> None:
        self.orchestrator.memory.clear()


__all__ = ["DebateAPI"]
