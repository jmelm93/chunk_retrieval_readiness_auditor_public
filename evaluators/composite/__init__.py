"""Composite evaluator for orchestrating all evaluations."""

from .evaluator import CompositeEvaluator
from .models import CompositeEvaluationResult

# Backward compatibility alias
ChunkEvaluationResult = CompositeEvaluationResult

__all__ = [
    'CompositeEvaluator',
    'CompositeEvaluationResult',
    'ChunkEvaluationResult'  # Backward compatibility
]