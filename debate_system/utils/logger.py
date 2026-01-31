"""Logging utilities for the debate system."""
from __future__ import annotations

import logging
from logging import Logger
from typing import Optional
from pathlib import Path

from ..core.config import LoggingConfig


def setup_logging(config: LoggingConfig) -> Logger:
    """Configure root logger based on settings."""
    level = getattr(logging, config.level.upper(), logging.INFO)
    handlers = []

    if config.console:
        handlers.append(logging.StreamHandler())

    if config.file:
        log_path = Path(config.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers or None,
    )

    logger = logging.getLogger("debate_system")
    logger.debug("Logging configured")
    return logger
