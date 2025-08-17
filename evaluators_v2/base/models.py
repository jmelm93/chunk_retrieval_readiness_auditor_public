"""Enhanced base Pydantic models for V2 evaluators."""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ConfigDict


class FormattingOptions(BaseModel):
    """Options for controlling output formatting."""
    
    filter_output: bool = Field(
        default=False,
        description="Whether to limit output to top items for conciseness"
    )
    max_items: int = Field(
        default=3,
        description="Maximum number of items to show in lists when filtering"
    )
    verbosity: str = Field(
        default="normal",
        description="Output verbosity level: concise, normal, or detailed"
    )


class MarkdownFormattable(ABC):
    """Mixin for models that can be formatted as markdown."""
    
    @abstractmethod
    def as_markdown(self, options: Optional[FormattingOptions] = None) -> str:
        """Convert the model to formatted markdown.
        
        Args:
            options: Formatting options for output control
            
        Returns:
            Formatted markdown string
        """
        pass
    
    def as_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        if hasattr(self, 'model_dump'):
            return self.model_dump()
        return {}


class BaseEvaluationResult(BaseModel, MarkdownFormattable):
    """Unified base evaluation result for all V2 evaluators.
    
    This single model replaces the redundant StandardizedEvaluationResult and 
    MachineReadableResult classes, providing both human-readable formatting
    and machine-readable structure in one clean interface.
    """
    
    model_config = ConfigDict(extra='forbid')
    
    evaluator_name: str = Field(
        description="Name of the evaluator that produced this result"
    )
    
    overall_score: int = Field(
        ge=0, le=100,
        description="Overall score from 0-100"
    )
    
    overall_assessment: str = Field(
        description="Clear and concise assessment (2-4 sentences)"
    )
    
    strengths: List[str] = Field(
        description="Key strengths identified by the evaluator"
    )
    
    issues: List[str] = Field(
        description="Key issues identified by the evaluator"
    )
    
    recommendations: List[str] = Field(
        description="Specific actionable recommendations or ['N/A - This section is already well-optimized']"
    )
    
    passing: bool = Field(
        description="Whether evaluation passed the evaluator's threshold"
    )
    
    def as_markdown(self, options: Optional[FormattingOptions] = None) -> str:
        """Generate formatted markdown feedback using standardized format.
        
        Args:
            options: Formatting options for output control
            
        Returns:
            Formatted markdown string with emoji-enhanced structure
        """
        options = options or FormattingOptions()
        lines = []
        
        # Score with pass/fail indicator
        status_emoji = "✅" if self.passing else "❌"
        lines.append("")
        lines.append(f"⭐ **Score:** {self.overall_score}/100 {status_emoji}")
        lines.append("")
        
        # Overall Assessment
        lines.append("📋 **Overall Assessment:**")
        lines.append(self.overall_assessment)
        lines.append("")
        
        # Strengths
        if self.strengths:
            lines.append("✅ **Strengths:**")
            strengths_to_show = self.strengths
            if options.filter_output and len(self.strengths) > options.max_items:
                strengths_to_show = self.strengths[:options.max_items]
                lines.append(f"*Showing top {options.max_items} of {len(self.strengths)} strengths*")
            
            for strength in strengths_to_show:
                lines.append(f"- {strength}")
            lines.append("")
        
        # Issues
        if self.issues:
            lines.append("⚠️ **Issues:**")
            issues_to_show = self.issues
            if options.filter_output and len(self.issues) > options.max_items:
                issues_to_show = self.issues[:options.max_items]
                lines.append(f"*Showing top {options.max_items} of {len(self.issues)} issues*")
            
            for issue in issues_to_show:
                lines.append(f"- {issue}")
            lines.append("")
        
        # Recommendations
        lines.append("🎯 **Recommendations:**")
        recs_to_show = self.recommendations
        if options.filter_output and len(self.recommendations) > options.max_items:
            recs_to_show = self.recommendations[:options.max_items]
            lines.append(f"*Showing top {options.max_items} of {len(self.recommendations)} recommendations*")
        
        for recommendation in recs_to_show:
            lines.append(f"- {recommendation}")
        
        return "\n".join(lines)


class EvidenceSpan(BaseModel):
    """Represents a piece of evidence from the text supporting an evaluation decision.
    
    V2 enhancement: All evaluations must provide evidence spans for auditability.
    """
    
    text: str = Field(
        max_length=100,
        description="Short verbatim excerpt from the chunk (≤15 words typical)"
    )
    
    context: Optional[str] = Field(
        default=None,
        description="Optional context explaining why this span is relevant"
    )
    
    start_char: Optional[int] = Field(
        default=None,
        description="Character offset where this span starts (if available)"
    )
    
    end_char: Optional[int] = Field(
        default=None,
        description="Character offset where this span ends (if available)"
    )


class PenaltyDetail(BaseModel):
    """Represents a specific penalty applied during evaluation.
    
    V2 enhancement: Detailed breakdown of all scoring deductions.
    """
    
    category: str = Field(
        description="Category of the penalty (e.g., 'vague_refs', 'misleading_headers')"
    )
    
    severity: str = Field(
        description="Severity level: 'minor', 'moderate', or 'severe'"
    )
    
    points_deducted: int = Field(
        ge=0,
        description="Number of points deducted for this penalty"
    )
    
    evidence_spans: List[EvidenceSpan] = Field(
        description="Evidence supporting this penalty"
    )
    
    explanation: Optional[str] = Field(
        default=None,
        description="Optional explanation of why this penalty was applied"
    )


class QualityGate(BaseModel):
    """Represents a quality gate that caps the maximum possible score.
    
    V2 enhancement: Track when quality gates are triggered and why.
    """
    
    gate_name: str = Field(
        description="Name of the quality gate (e.g., 'multiple_vague_references')"
    )
    
    max_score: int = Field(
        ge=0, le=100,
        description="Maximum score allowed by this gate"
    )
    
    triggered: bool = Field(
        description="Whether this gate was triggered for this evaluation"
    )
    
    evidence_spans: List[EvidenceSpan] = Field(
        default_factory=list,
        description="Evidence that triggered this gate"
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


# DualOutputResult removed - no longer needed with unified BaseEvaluationResult


# Legacy compatibility mixin removed - evaluators now return BaseEvaluationResult directly