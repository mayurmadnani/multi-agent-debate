"""Configuration management for the debate system."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import os
import yaml


@dataclass
class AgentConfig:
    """Configuration for an individual agent persona."""

    name: str
    instruction: str
    temperature: float
    max_tokens: int
    tools_enabled: bool = False


@dataclass
class ModelConfig:
    """Model backend configuration."""

    backend: str
    model_name: str
    timeout: int = 30
    quantization: Optional[str] = None
    device: str = "auto"


@dataclass
class MemoryConfig:
    """Persistent memory configuration."""

    persist_path: str
    auto_save: bool = True
    max_entries: int = 1000


@dataclass
class OrchestratorConfig:
    """Debate orchestration configuration."""

    default_rounds: int = 3
    enable_summary: bool = True
    random_seed: Optional[int] = None
    max_retries: int = 3
    random_order: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration for the system."""

    level: str = "INFO"
    file: Optional[str] = None
    console: bool = True


@dataclass
class ToolConfig:
    """Configuration for a single tool."""

    enabled: bool = True
    timeout: int = 10
    max_results: int = 5
    cache_results: bool = False


class ConfigManager:
    """Loads and serves configuration objects from YAML files."""

    def __init__(
        self,
        settings_path: str = "configs/settings.yaml",
        personas_path: str = "configs/personas.yaml",
        tools_path: str = "configs/tools.yaml",
        base_path: Optional[str] = None,
    ) -> None:
        self.base_path = Path(base_path or os.getcwd())
        self.settings_path = self.base_path / settings_path
        self.personas_path = self.base_path / personas_path
        self.tools_path = self.base_path / tools_path

        self._settings = self._load_yaml(self.settings_path)
        self._personas = self._load_yaml(self.personas_path)
        self._tools = self._load_yaml(self.tools_path)

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return data

    def get_agent_config(self, key: str) -> AgentConfig:
        data = self._personas.get(key)
        if data is None:
            raise KeyError(f"Agent config '{key}' not found")

        return AgentConfig(
            name=data.get("name", key.title()),
            instruction=data.get("instruction", ""),
            temperature=float(data.get("temperature", 0.8)),
            max_tokens=int(data.get("max_tokens", 256)),
            tools_enabled=bool(data.get("tools_enabled", False)),
        )

    def get_model_config(self) -> ModelConfig:
        model = self._settings.get("model", {})
        return ModelConfig(
            backend=model.get("backend", "ollama"),
            model_name=model.get("model_name", ""),
            timeout=int(model.get("timeout", 60)),
            quantization=model.get("quantization"),
            device=model.get("device", "auto"),
        )

    def get_memory_config(self) -> MemoryConfig:
        memory = self._settings.get("memory", {})
        return MemoryConfig(
            persist_path=memory.get("persist_path", "data/memory.json"),
            auto_save=bool(memory.get("auto_save", True)),
            max_entries=int(memory.get("max_entries", 1000)),
        )

    def get_orchestrator_config(self) -> OrchestratorConfig:
        orch = self._settings.get("orchestrator", {})
        seed = orch.get("random_seed")
        seed_value = int(seed) if seed is not None else None

        return OrchestratorConfig(
            default_rounds=int(orch.get("default_rounds", 1)),
            enable_summary=bool(orch.get("enable_summary", True)),
            random_seed=seed_value,
            max_retries=int(orch.get("max_retries", 2)),
            random_order=bool(orch.get("random_order", True)),
        )

    def get_logging_config(self) -> LoggingConfig:
        logging_cfg = self._settings.get("logging", {})
        return LoggingConfig(
            level=logging_cfg.get("level", "INFO"),
            file=logging_cfg.get("file"),
            console=bool(logging_cfg.get("console", True)),
        )

    def get_tool_config(self, tool_name: str) -> ToolConfig:
        tool_data = self._tools.get(tool_name, {})
        return ToolConfig(
            enabled=bool(tool_data.get("enabled", True)),
            timeout=int(tool_data.get("timeout", 10)),
            max_results=int(tool_data.get("max_results", 5)),
            cache_results=bool(tool_data.get("cache_results", False)),
        )

    def get_all_tool_configs(self) -> Dict[str, ToolConfig]:
        return {name: self.get_tool_config(name) for name in self._tools.keys()}
