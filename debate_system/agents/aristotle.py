"""Aristotle agent with tool use."""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..core.tools import execute_tool
from ..core.memory import MemoryStore

logger = logging.getLogger(__name__)


class AristotleAgent(BaseAgent):
    """Practical agent that can invoke tools for actionable guidance."""

    _KEYWORDS = [
        "how",
        "plan",
        "steps",
        "action",
        "strategy",
        "research",
        "find",
        "search",
        "calculate",
        "current",
        "information about",
        "tell me about",
        "find out",
        "explain",
    ]

    def get_system_prompt(self) -> str:
        prompt = (
            f"{self.instruction}\n"
            "Provide one practical, actionable recommendation."
            " Do not ask permission to use tools; if you have tool results, use them directly."
        )
        if self.config.tools_enabled:
            prompt += " You may rely on external information you gathered via tools."
        return prompt

    def _should_use_tools(self, question: str, history: List[Dict[str, Any]]) -> bool:
        # Prefer the most recent user turn for intent signals
        recent_user = next(
            (
                turn.get("content", "")
                for turn in reversed(history)
                if str(turn.get("speaker", "")).lower() == "user"
            ),
            question,
        )
        text = str(recent_user).lower()
        math_pattern = r"\d+[\+\-\*\/%]"  # quick math heuristic
        return any(kw in text for kw in self._KEYWORDS) or bool(re.search(math_pattern, text))

    def _detect_tool_needed(self, prompt: str) -> Optional[str]:
        if not getattr(self.config, "tools_enabled", False):
            return None

        text = prompt.lower()

        # Math first to catch explicit expressions
        if re.search(r"\d+[\+\-\*\/%\(\)]\d+", text):
            return "calculate"

        # Web search intents
        if any(
            k in text
            for k in [
                "search",
                "look up",
                "find",
                "google",
                "browse",
                "research",
                "information about",
                "tell me about",
                "find out",
                "explain",
            ]
        ):
            return "web_search"

        # Current info (date / time)
        if any(k in text for k in ["current", "today", "now", "date", "time"]):
            return "get_current_info"

        # Fallback: if numbers present, treat as math; if question words, search
        if any(ch.isdigit() for ch in text):
            return "calculate"
        if any(text.startswith(qw) for qw in ("what", "who", "where", "when", "why", "how")):
            return "web_search"

        return None

    def _extract_question_from_response(self, text: str) -> str:
        sentences = re.split(r"[.!?]+", text)
        questions = [
            s.strip()
            for s in sentences
            if s.strip().lower().startswith(
                ("what", "who", "where", "when", "why", "how", "is", "are", "can")
            )
        ]
        if questions:
            return questions[0]
        return sentences[-1].strip() if sentences else text.strip()

    def generate_response(
        self,
        user_prompt: str,
        history: List[Dict[str, Any]],
        memory: Optional[MemoryStore] = None,
        **generation_kwargs: Any,
    ) -> str:
        if self.config.tools_enabled and self._should_use_tools(user_prompt, history):
            tool = self._detect_tool_needed(user_prompt)
            if tool:
                query = self._extract_question_from_response(user_prompt)

                # Normalize query for specific tools
                if tool == "calculate":
                    expr = re.search(r"[\d\+\-\*\/%\(\)\.\s]+", user_prompt)
                    if expr:
                        query = expr.group().strip()
                elif tool == "get_current_info":
                    if "time" in user_prompt.lower():
                        query = "time"
                    elif "date" in user_prompt.lower() or "today" in user_prompt.lower():
                        query = "date"
                    else:
                        query = "datetime"

                tool_result = execute_tool(tool, query)
                # Normalize list outputs for prompt readability
                if isinstance(tool_result, list):
                    tool_result = "\n".join(str(item) for item in tool_result)
                if memory is not None:
                    memory.add_entry(
                        key=f"tool_{tool}_{len(history)}",
                        value=tool_result,
                        source=self.name,
                    )
                enhanced_prompt = (
                    f"{user_prompt}\n\n[Tool {tool} Result]: {tool_result}\n"
                    "Use this information to craft a practical recommendation."
                )
                return super().generate_response(enhanced_prompt, history, memory, **generation_kwargs)

        response = super().generate_response(user_prompt, history, memory, **generation_kwargs)
        if memory is not None and response:
            memory.add_entry(
                key=f"aristotle_insight_{len(history)}",
                value=response,
                source=self.name,
            )
        return response
