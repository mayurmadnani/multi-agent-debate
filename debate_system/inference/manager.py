"""Model manager singleton and helper functions."""
from __future__ import annotations

import logging
from typing import Optional, Protocol

from ..core.config import ModelConfig
from .backends import OllamaBackend, TransformersBackend

logger = logging.getLogger(__name__)


class ModelBackend(Protocol):
    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        ...


class ModelManager:
    """Singleton manager for model backends."""

    _instance: Optional["ModelManager"] = None

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.backend: Optional[ModelBackend] = None
        self.config: Optional[ModelConfig] = None
        self._initialized = True

    def initialize(self, config: ModelConfig) -> None:
        self.config = config
        backend_name = config.backend.lower()

        if backend_name == "ollama":
            self.backend = OllamaBackend(config)
        elif backend_name == "transformers":
            self.backend = TransformersBackend(config)
        else:
            raise ValueError(f"Unsupported backend: {config.backend}")

        logger.info(f"Initialized model backend: {backend_name}")

    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not self.backend:
            raise RuntimeError("Model backend not initialized")
        return self.backend.generate(prompt, temperature, max_tokens)


def get_model_manager() -> ModelManager:
    return ModelManager()


def initialize_model(config: ModelConfig) -> None:
    manager = get_model_manager()
    manager.initialize(config)


def generate_text(prompt: str, temperature: float = 0.8, max_new_tokens: int = 256) -> str:
    manager = get_model_manager()
    return manager.generate(prompt, temperature, max_new_tokens)
