"""Base classes for evaluators v2."""

from .models import (
    BaseEvaluationResult,
    BaseMetrics,
    MarkdownFormattable,
    FormattingOptions
)
from .base_evaluator import BaseStructuredEvaluator

__all__ = [
    'BaseEvaluationResult',
    'BaseMetrics',
    'MarkdownFormattable',
    'FormattingOptions',
    'BaseStructuredEvaluator'
]