"""Base Pydantic models for all evaluators."""

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




# class ScoreBreakdownItem(BaseModel):
#     """Individual score breakdown item."""
    
#     model_config = ConfigDict(extra='forbid')
    
#     score: int = Field(
#         ge=0, le=100,
#         description="Score for this dimension (0-100)"
#     )
#     explanation: str = Field(
#         description="Brief explanation of this score"
#     )


class StandardizedEvaluationResult(BaseModel, MarkdownFormattable):
    """Standardized evaluation result format for all evaluators."""
    
    model_config = ConfigDict(extra='forbid')
    
    evaluator_name: str = Field(
        description="Name of the evaluator that produced this result"
    )
    
    overall_score: int = Field(
        ge=0, le=100,
        description="Overall score from 0-100"
    )
    
    overall_assessment: str = Field(
        description="Clear and concise assessment - whatever length needed for clarity"
    )
    
    # score_breakdown: Optional[Dict[str, ScoreBreakdownItem]] = Field(
    #     default=None,
    #     description="Optional breakdown of sub-scores with explanations"
    # )
    
    strengths: List[str] = Field(
        description="Key strengths - AI determines appropriate number"
    )
    
    issues: List[str] = Field(
        description="Key issues - AI determines appropriate number"
    )
    
    recommendations: List[str] = Field(
        description="List of specific recommendations or ['N/A - This section is already well-optimized']"
    )
    
    passing: bool = Field(
        description="Whether evaluation passed minimum threshold"
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
        
        # Score
        lines.append(f"**Score:** {self.overall_score}/100")
        lines.append("")
        
        # # Breakdown (if available)
        # if self.score_breakdown:
        #     lines.append("**Breakdown:**")
        #     for dimension, breakdown in self.score_breakdown.items():
        #         lines.append(f"• {dimension}: {breakdown.score}/100 - {breakdown.explanation}")
        #     lines.append("")
        
        # Score Reasoning
        lines.append("**Score Reasoning:**")
        lines.append("")
        
        # Overall Assessment
        lines.append("📋 **Overall Assessment:**")
        lines.append(self.overall_assessment)
        lines.append("")
        
        # Strengths
        if self.strengths:
            lines.append("✅ **Strengths:**")
            for strength in self.strengths:
                lines.append(f"- {strength}")
            lines.append("")
        
        # Issues
        if self.issues:
            lines.append("⚠️ **Issues:**")
            for issue in self.issues:
                lines.append(f"- {issue}")
            lines.append("")
        
        # Recommendations
        lines.append("🎯 **Recommendations:**")
        for recommendation in self.recommendations:
            lines.append(f"- {recommendation}")
        
        return "\n".join(lines)