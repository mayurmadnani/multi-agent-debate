"""Model backend implementations."""
from __future__ import annotations

import logging
from typing import Any

import requests
from transformers import pipeline
import torch

from ..core.config import ModelConfig

logger = logging.getLogger(__name__)


class OllamaBackend:
    """Ollama local inference backend."""

    def __init__(self, config: ModelConfig):
        self.model_name = config.model_name
        self.base_url = "http://localhost:11434"
        self.timeout = config.timeout

    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")


class TransformersBackend:
    """HuggingFace Transformers backend with optional quantization."""

    def __init__(self, config: ModelConfig):
        self.model_name = config.model_name
        self.device = self._resolve_device(config.device)
        self.quantization = config.quantization
        self._pipeline = None

    def _resolve_device(self, device: str) -> int:
        if device == "auto":
            return 0 if torch.cuda.is_available() else -1
        try:
            return int(device)
        except ValueError:
            return -1

    def _lazy_init(self) -> None:
        if self._pipeline:
            return

        kwargs: dict[str, Any] = {}
        if self.quantization == "8bit":
            kwargs["load_in_8bit"] = True
        elif self.quantization == "4bit":
            kwargs["load_in_4bit"] = True

        self._pipeline = pipeline(
            task="text-generation",
            model=self.model_name,
            device=self.device,
            **kwargs,
        )

    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        self._lazy_init()
        assert self._pipeline is not None

        result = self._pipeline(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
        )[0]["generated_text"]

        if result.startswith(prompt):
            return result[len(prompt):].strip()
        return result.strip()
