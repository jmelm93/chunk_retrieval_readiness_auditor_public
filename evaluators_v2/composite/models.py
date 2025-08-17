"""Composite V2 evaluator models with dual feedback storage and enhanced metadata."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Any, Optional
from ..base.models import V2EvaluationMetadata


class CompositeEvaluationResultV2(BaseModel):
    """Enhanced composite evaluation result with V2 features.
    
    This model provides dual output support (markdown + JSON), normalized weights,
    config-driven classification, and comprehensive metadata tracking.
    """
    
    model_config = ConfigDict(extra='forbid')
    
    # Basic identification
    chunk_id: str = Field(
        description="Unique identifier for the evaluated chunk"
    )
    
    chunk_index: int = Field(
        ge=0,
        description="Index of this chunk in the document sequence"
    )
    
    heading: str = Field(
        description="Heading or title of the chunk"
    )
    
    text_preview: str = Field(
        description="Full text content of the chunk (not truncated preview)"
    )
    
    token_count: int = Field(
        ge=0,
        description="Estimated token count for the chunk"
    )
    
    # V2 Enhancement: Dual feedback storage
    feedback_markdown: Dict[str, str] = Field(
        description="Human-readable markdown feedback from each evaluator"
    )
    
    feedback_json: Dict[str, Any] = Field(
        description="Machine-readable structured feedback from each evaluator"
    )
    
    # Scoring with normalized weights
    scores: Dict[str, float] = Field(
        description="Individual evaluator scores (0.0-1.0 scale)"
    )
    
    normalized_weights: Dict[str, float] = Field(
        description="Normalized weights used for scoring (sum = 1.0)"
    )
    
    total_score: float = Field(
        ge=0.0, le=100.0,
        description="Weighted total score (0-100 scale)"
    )
    
    # V2 Enhancement: Config-driven classification
    label: str = Field(
        description="Quality classification based on config thresholds"
    )
    
    passing: bool = Field(
        description="Whether the chunk meets overall quality standards"
    )
    
    # Enhanced metadata
    entities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Entities extracted during evaluation"
    )
    
    metadata: Dict[str, Any] = Field(
        description="Additional metadata about the evaluation process"
    )
    
    # V2 Enhancement: Evaluation audit trail
    evaluation_metadata: Dict[str, V2EvaluationMetadata] = Field(
        description="Detailed metadata from each evaluator"
    )
    
    processing_summary: Dict[str, Any] = Field(
        description="Summary of processing times, retries, and other metrics"
    )


class CompositeResultSummary(BaseModel):
    """Summary statistics for a set of composite evaluation results."""
    
    total_chunks: int = Field(
        ge=0,
        description="Total number of chunks evaluated"
    )
    
    passing_chunks: int = Field(
        ge=0, 
        description="Number of chunks that passed quality thresholds"
    )
    
    average_score: float = Field(
        ge=0.0, le=100.0,
        description="Average score across all chunks"
    )
    
    # Classification counts
    well_optimized: int = Field(
        ge=0,
        description="Count of 'Well Optimized' chunks"
    )
    
    needs_work: int = Field(
        ge=0,
        description="Count of 'Needs Work' chunks"
    )
    
    poorly_optimized: int = Field(
        ge=0,
        description="Count of 'Poorly Optimized' chunks"
    )
    
    # Score distribution
    score_distribution: Dict[str, int] = Field(
        description="Score ranges and their counts"
    )
    
    # Evaluator performance
    evaluator_averages: Dict[str, float] = Field(
        description="Average scores by evaluator"
    )
    
    # Processing metrics
    total_processing_time_ms: int = Field(
        ge=0,
        description="Total processing time across all evaluations"
    )
    
    average_processing_time_ms: float = Field(
        ge=0,
        description="Average processing time per chunk"
    )
    
    retry_statistics: Dict[str, int] = Field(
        description="Retry counts by evaluator"
    )


class ExportFormatV2(BaseModel):
    """V2 export format with both human and machine views."""
    
    summary: CompositeResultSummary = Field(
        description="Overall summary statistics"
    )
    
    chunks: List[CompositeEvaluationResultV2] = Field(
        description="Individual chunk evaluation results"
    )
    
    # V2 Enhancement: Separate human and machine exports
    human_readable: Dict[str, Any] = Field(
        description="Human-readable export with markdown feedback"
    )
    
    machine_readable: Dict[str, Any] = Field(
        description="Machine-readable export with structured data"
    )
    
    # Metadata about the export
    export_metadata: Dict[str, Any] = Field(
        description="Metadata about the export process and configuration"
    )


# Default weight values for reference
DEFAULT_WEIGHTS = {
    "query_answer": 0.25,
    "entity_focus": 0.25,
    "llm_rubric": 0.30,
    "structure_quality": 0.20
}

# Default classification thresholds
DEFAULT_CLASSIFICATION_THRESHOLDS = {
    "well_optimized": 75,
    "needs_work": 60,
    "poorly_optimized": 0
}