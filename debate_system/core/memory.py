"""Persistent memory store with search and metadata."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Single memory entry with metadata."""

    key: str
    value: Any
    timestamp: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(**data)


class MemoryStore:
    """Persistent key-value memory with search capabilities."""

    def __init__(self, persist_path: Optional[str] = None, auto_save: bool = True, max_entries: int = 1000) -> None:
        self.persist_path = Path(persist_path) if persist_path else None
        self.auto_save = auto_save
        self.max_entries = max_entries
        self.entries: Dict[str, MemoryEntry] = {}

        if self.persist_path:
            self._load()

    def add_entry(self, key: str, value: Any, source: str = "system") -> None:
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=datetime.now().isoformat(),
            source=source,
        )
        self.entries[key] = entry

        if len(self.entries) > self.max_entries:
            # Drop oldest entry when exceeding capacity
            oldest_key = sorted(self.entries.values(), key=lambda e: e.timestamp)[0].key
            self.entries.pop(oldest_key, None)

        if self.auto_save:
            self._save()

    def get_entry(self, key: str) -> Optional[Any]:
        entry = self.entries.get(key)
        return entry.value if entry else None

    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        query_lower = query.lower()
        results = [
            entry
            for entry in self.entries.values()
            if query_lower in entry.key.lower() or query_lower in str(entry.value).lower()
        ]
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    def get_recent(self, n: int = 5) -> List[MemoryEntry]:
        return sorted(self.entries.values(), key=lambda e: e.timestamp, reverse=True)[:n]

    def format_for_prompt(self, limit: int = 5) -> str:
        recent = self.get_recent(limit)
        if not recent:
            return "No relevant memory."

        lines = ["Recent relevant context:"]
        for entry in recent:
            lines.append(f"- {entry.key}: {entry.value} (from {entry.source})")
        return "\n".join(lines)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "entries": [e.to_dict() for e in self.entries.values()],
            "count": len(self.entries),
            "persist_path": str(self.persist_path) if self.persist_path else None,
        }

    def clear(self) -> None:
        self.entries.clear()
        if self.auto_save:
            self._save()

    def _save(self) -> None:
        if not self.persist_path:
            return
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            data = {k: v.to_dict() for k, v in self.entries.items()}
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as exc:
            logger.error(f"Failed to save memory: {exc}")

    def _load(self) -> None:
        if not self.persist_path or not self.persist_path.exists():
            return
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.entries = {k: MemoryEntry.from_dict(v) for k, v in data.items()}
        except Exception as exc:
            logger.error(f"Failed to load memory: {exc}")
            self.entries = {}

    def __len__(self) -> int:
        return len(self.entries)
