"""Core components for orchestration, config, memory, and tools."""

from .config import (
	AgentConfig,
	ConfigManager,
	LoggingConfig,
	MemoryConfig,
	ModelConfig,
	OrchestratorConfig,
	ToolConfig,
)
from .memory import MemoryStore, MemoryEntry
from .tools import execute_tool, list_tools

def __getattr__(name):
    if name in {"DebateOrchestrator", "build_orchestrator"}:
        from .orchestrator import DebateOrchestrator, build_orchestrator
        return DebateOrchestrator if name == "DebateOrchestrator" else build_orchestrator
    raise AttributeError

__all__ = [
	"AgentConfig",
	"ConfigManager",
	"LoggingConfig",
	"MemoryConfig",
	"ModelConfig",
	"OrchestratorConfig",
	"ToolConfig",
	"MemoryStore",
	"MemoryEntry",
	"execute_tool",
	"list_tools",
	"DebateOrchestrator",
	"build_orchestrator",
]
