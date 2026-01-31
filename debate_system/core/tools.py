"""Tool implementations with registry support."""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_tool(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a tool function."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        TOOL_REGISTRY[name] = func
        return func

    return decorator


@register_tool("web_search")
def web_search(query: str, max_results: int = 5, timeout: int = 10) -> List[str]:
    """DuckDuckGo Instant Answer API search."""
    cleaned_query = query.strip()
    if not cleaned_query:
        return ["No query provided"]

    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": cleaned_query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        results: List[str] = []

        abstract = data.get("Abstract")
        if abstract:
            results.append(f"Summary: {abstract}")

        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(topic["Text"])

        definition = data.get("Definition")
        if definition:
            results.append(f"Definition: {definition}")

        return results or ["No results found"]
    except requests.Timeout:
        return [f"Search timed out after {timeout} seconds"]
    except Exception as exc:
        logger.warning(f"Web search failed: {exc}")
        return [f"Search error: {exc}"]


@register_tool("calculate")
def calculate(expression: str) -> str:
    """Safely evaluate arithmetic expressions."""
    try:
        allowed = set("0123456789+-*/()% .")
        if not all(ch in allowed for ch in expression):
            return "Error: Invalid characters in expression"

        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as exc:
        logger.warning(f"Calculation failed: {exc}")
        return f"Calculation error: {exc}"


@register_tool("get_current_info")
def get_current_info(info_type: str = "datetime") -> str:
    """Return current date/time information."""
    now = datetime.now()
    choice = info_type.lower()

    if choice == "date":
        return now.strftime("%Y-%m-%d")
    if choice == "time":
        return now.strftime("%H:%M:%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")


def execute_tool(tool_name: str, *args: Any, **kwargs: Any) -> Any:
    """Run a registered tool with error handling."""
    if tool_name not in TOOL_REGISTRY:
        return f"Error: Tool '{tool_name}' not found"

    try:
        return TOOL_REGISTRY[tool_name](*args, **kwargs)
    except Exception as exc:
        logger.error(f"Tool execution error ({tool_name}): {exc}")
        return f"Tool execution error: {exc}"


def list_tools() -> List[str]:
    """Return registered tool names."""
    return list(TOOL_REGISTRY.keys())
