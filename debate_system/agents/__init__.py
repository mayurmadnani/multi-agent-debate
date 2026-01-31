"""Agent implementations for the debate system."""

from .base import BaseAgent
from .socrates import SocratesAgent
from .plato import PlatoAgent
from .aristotle import AristotleAgent
from .summary import SummaryAgent

__all__ = [
	"BaseAgent",
	"SocratesAgent",
	"PlatoAgent",
	"AristotleAgent",
	"SummaryAgent",
]
