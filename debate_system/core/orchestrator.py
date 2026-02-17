"""Coordinates multi-agent debates."""
from __future__ import annotations

import logging
import random
from typing import Dict, List, Optional, Tuple

from ..agents import AristotleAgent, BaseAgent, PlatoAgent, SocratesAgent, SummaryAgent
from ..core.config import ConfigManager, OrchestratorConfig
from ..core.memory import MemoryStore
from ..inference.manager import initialize_model
from ..utils.validators import ensure_non_empty

logger = logging.getLogger(__name__)


class DebateOrchestrator:
    """Runs debates across multiple philosopher agents."""

    def __init__(
        self,
        config_manager: ConfigManager,
        memory_store: Optional[MemoryStore] = None,
        orchestrator_config: Optional[OrchestratorConfig] = None,
    ) -> None:
        self.config_manager = config_manager
        self.memory = memory_store or MemoryStore(
            persist_path=self.config_manager.get_memory_config().persist_path,
            auto_save=self.config_manager.get_memory_config().auto_save,
            max_entries=self.config_manager.get_memory_config().max_entries,
        )
        self.config = orchestrator_config or self.config_manager.get_orchestrator_config()

        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)

        self.agents: Dict[str, BaseAgent] = {}
        self._init_agents()

        # Initialize model backend once
        initialize_model(self.config_manager.get_model_config())

    def _init_agents(self) -> None:
        factory = {
            "socrates": SocratesAgent,
            "plato": PlatoAgent,
            "aristotle": AristotleAgent,
            "summary": SummaryAgent,
        }
        for key, cls in factory.items():
            try:
                cfg = self.config_manager.get_agent_config(key)
                self.agents[key] = cls(cfg)
            except Exception as exc:
                logger.warning(f"Failed to initialize agent '{key}': {exc}")

    def _debate_agents(self) -> List[Tuple[str, BaseAgent]]:
        keys = [k for k in ("socrates", "plato", "aristotle") if k in self.agents]
        return [(k, self.agents[k]) for k in keys]

    def _agent_order(self) -> List[Tuple[str, BaseAgent]]:
        agents = self._debate_agents()
        if self.config.random_order:
            random.shuffle(agents)
        return agents

    def run_debate(self, question: str, rounds: Optional[int] = None, enable_summary: Optional[bool] = None) -> Dict[str, object]:
        gen = self.stream_debate(question, rounds, enable_summary)
        last_result = {}
        for result in gen:
            last_result = result
        return last_result

    def stream_debate(self, question: str, rounds: Optional[int] = None, enable_summary: Optional[bool] = None):
        """Yields intermediate debate results for streaming."""
        question = ensure_non_empty(question, "question")
        rounds = rounds or self.config.default_rounds
        enable_summary = self.config.enable_summary if enable_summary is None else enable_summary

        history: List[Dict[str, object]] = [{"speaker": "User", "content": question}]
        self.memory.add_entry(key="initial_question", value=question, source="user")
        
        yield {
            "question": question,
            "history": history,
            "summary": None,
            "error": None,
            "status": "started"
        }

        for round_idx in range(1, rounds + 1):
            logger.info(f"Round {round_idx}/{rounds}")
            for agent_key, agent in self._agent_order():
                response = self._get_agent_response(agent_key, agent, question, history)
                history.append({
                    "speaker": agent.name,
                    "content": response,
                    "round": round_idx,
                })
                yield {
                    "question": question,
                    "history": history,
                    "summary": None,
                    "error": None,
                    "status": "debating"
                }

        summary_text: Optional[str] = None
        if enable_summary and "summary" in self.agents:
            try:
                summary_text = self.agents["summary"].generate_response(question, history, self.memory)
                history.append({"speaker": "Summary", "content": summary_text})
            except Exception as exc:
                logger.error(f"Summary generation failed: {exc}")

        yield {
            "question": question,
            "history": history,
            "summary": summary_text,
            "error": None,
            "status": "completed"
        }

    def _get_agent_response(
        self,
        agent_key: str,
        agent: BaseAgent,
        question: str,
        history: List[Dict[str, object]],
    ) -> str:
        for attempt in range(self.config.max_retries):
            try:
                return agent.generate_response(question, history, self.memory)
            except Exception as exc:
                logger.warning(f"{agent_key} attempt {attempt + 1} failed: {exc}")
        return f"[Error: {agent_key} failed after {self.config.max_retries} attempts]"

    def format_history(self, history: List[Dict[str, object]]) -> str:
        lines = []
        for entry in history:
            speaker = entry.get("speaker", "Unknown")
            content = str(entry.get("content", "")).strip()
            if content:
                lines.append(f"[{speaker}] {content}")
        return "\n".join(lines)

    def clear_memory(self) -> None:
        self.memory.clear()

    def snapshot_memory(self) -> Dict[str, object]:
        return self.memory.snapshot()


def build_orchestrator(
    config_manager: Optional[ConfigManager] = None,
    base_path: Optional[str] = None,
) -> DebateOrchestrator:
    manager = config_manager or ConfigManager(base_path=base_path or None)
    return DebateOrchestrator(manager)
