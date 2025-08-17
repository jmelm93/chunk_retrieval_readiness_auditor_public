"""Essential base Pydantic models for V2 evaluators."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class EvidenceSpan(BaseModel):
    """Represents a piece of evidence from the text supporting an evaluation decision.
    
    V2 enhancement: All evaluations must provide evidence spans for auditability.
    """
    
    barrier_type: str = Field(
        description="Type of barrier this evidence supports (e.g., 'vague_refs')"
    )

    text: str = Field(
        max_length=100,
        description="Short verbatim excerpt from the chunk (≤15 words typical)"
    )
    
    context: Optional[str] = Field(
        description="Optional context explaining why this span is relevant"
    )
    
    start_char: Optional[int] = Field(
        description="Character offset where this span starts (if available)"
    )
    
    end_char: Optional[int] = Field(
        description="Character offset where this span ends (if available)"
    )



class V2EvaluationMetadata(BaseModel):
    """Metadata for V2 evaluations providing audit trail and context."""
    
    model_config = ConfigDict(extra='forbid')
    
    model_used: str = Field(
        description="OpenAI model used for this evaluation"
    )
    
    chunk_char_count: int = Field(
        ge=0,
        description="Character count of the evaluated chunk"
    )
    
    chunk_word_count: int = Field(
        ge=0,
        description="Word count of the evaluated chunk"
    )
    
    was_truncated: bool = Field(
        description="Whether the chunk text was truncated before evaluation"
    )
    
    processing_time_ms: Optional[int] = Field(
        default=None,
        description="Time taken for evaluation in milliseconds"
    )
    
    retry_count: int = Field(
        default=0,
        description="Number of retries needed for successful evaluation"
    )
    
    config_threshold: float = Field(
        description="Passing threshold used for this evaluation"
    )
