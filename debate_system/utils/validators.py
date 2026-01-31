"""Validation helpers."""
from __future__ import annotations


def ensure_non_empty(text: str, field: str = "value") -> str:
    """Raise if text is empty."""
    if not text or not text.strip():
        raise ValueError(f"{field} cannot be empty")
    return text.strip()


def ensure_positive_int(value: int, field: str) -> int:
    """Raise if value is not a positive integer."""
    if value is None or int(value) <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return int(value)
