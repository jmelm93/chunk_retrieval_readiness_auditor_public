"""Simplified Query-Answer V3 models - minimal extension of base."""

from typing import List, Literal
from pydantic import Field

from ..base.models import BaseEvaluationResult


class QueryAnswerResult(BaseEvaluationResult):
    """Query-Answer evaluation result with minimal additional fields.
    
    Extends base with only essential query-answer specific fields.
    All scoring logic moved to evaluator - model just holds data.
    """
    
    # Additional fields specific to Query-Answer evaluation
    chunk_type: Literal["overview", "detail", "example", "definition", "general"] = Field(
        description="Classification of the chunk type based on content analysis"
    )
    
    likely_queries: List[str] = Field(
        description="3-8 likely user queries this chunk could help answer"
    )
    
    # That's it! No duplicate scores, no calculated fields, no complexity.
    # The base model already has:
    # - issues (with barriers as Issue objects)
    # - strengths
    # - assessment
    # - recommendations  
    # - score
    # - passing