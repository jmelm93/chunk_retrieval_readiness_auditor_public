"""Pydantic models for Composite evaluation results."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from ..base.models import FormattingOptions


class CompositeEvaluationResult(BaseModel):
    """Complete evaluation result combining all evaluators."""
    
    model_config = ConfigDict(extra='forbid')
    
    # Chunk identification
    chunk_id: str = Field(
        description="Unique identifier for the chunk"
    )
    chunk_index: int = Field(
        ge=0,
        description="Index of chunk in document"
    )
    heading: str = Field(
        default="",
        description="Chunk heading"
    )
    text_preview: str = Field(
        description="Full chunk text (not truncated)"
    )
    token_count: int = Field(
        ge=0,
        description="Token count for the chunk"
    )
    
    # Individual evaluator scores
    scores: Dict[str, float] = Field(
        description="Individual scores from each evaluator (normalized 0-1)"
    )
    
    # Composite metrics
    total_score: float = Field(
        ge=0.0, le=100.0,
        description="Weighted total score (0-100)"
    )
    label: str = Field(
        description="Quality label (Well Optimized, Needs Work, Poorly Optimized)"
    )
    passing: bool = Field(
        description="Whether chunk meets minimum quality threshold"
    )
    
    # Detailed feedback from each evaluator
    feedback: Dict[str, str] = Field(
        description="Markdown-formatted feedback from each evaluator"
    )
    
    # Entity metadata
    entities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Entities detected in the chunk"
    )
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata and insights"
    )
    
    def as_markdown(self, options: Optional[FormattingOptions] = None) -> str:
        """Generate comprehensive markdown report for this chunk.
        
        Args:
            options: Formatting options
            
        Returns:
            Formatted markdown string
        """
        options = options or FormattingOptions()
        lines = []
        
        # Header
        lines.append(f"## Chunk {self.chunk_index + 1}: {self.heading or 'Untitled'}")
        lines.append("")
        
        # Overall Score
        lines.append(f"**Overall Score:** {self.total_score:.1f}/100 - {self.label}")
        lines.append(f"**Status:** {'✅ Passing' if self.passing else '❌ Failing'}")
        lines.append(f"**Token Count:** {self.token_count}")
        lines.append("")
        
        # Individual Scores
        lines.append("### Evaluator Scores")
        for evaluator, score in self.scores.items():
            score_pct = score * 100
            evaluator_name = evaluator.replace('_', ' ').title()
            emoji = "✅" if score >= 0.6 else "⚠️" if score >= 0.4 else "❌"
            lines.append(f"- {emoji} **{evaluator_name}:** {score_pct:.1f}%")
        lines.append("")
        
        # Detailed Feedback
        lines.append("### Detailed Feedback")
        for evaluator, feedback in self.feedback.items():
            if feedback:
                lines.append(f"\n#### {evaluator.replace('_', ' ').title()}")
                lines.append(feedback)
        
        # Full Content (if verbosity is detailed)
        if options.verbosity == "detailed":
            lines.append("\n### Full Content")
            lines.append("```")
            lines.append(self.text_preview)
            lines.append("```")
        
        return "\n".join(lines)
    
    def as_json_summary(self) -> Dict[str, Any]:
        """Generate JSON summary of evaluation.
        
        Returns:
            Dictionary with key metrics
        """
        return {
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "heading": self.heading,
            "total_score": self.total_score,
            "label": self.label,
            "passing": self.passing,
            "token_count": self.token_count,
            "scores": self.scores,
            "entity_count": len(self.entities),
            "top_issue": self._identify_top_issue(),
            "top_strength": self._identify_top_strength()
        }
    
    def _identify_top_issue(self) -> Optional[str]:
        """Identify the lowest-scoring evaluator as top issue."""
        if not self.scores:
            return None
        
        min_evaluator = min(self.scores.items(), key=lambda x: x[1])
        if min_evaluator[1] < 0.6:
            return f"{min_evaluator[0].replace('_', ' ').title()} ({min_evaluator[1]*100:.0f}%)"
        return None
    
    def _identify_top_strength(self) -> Optional[str]:
        """Identify the highest-scoring evaluator as top strength."""
        if not self.scores:
            return None
        
        max_evaluator = max(self.scores.items(), key=lambda x: x[1])
        if max_evaluator[1] >= 0.7:
            return f"{max_evaluator[0].replace('_', ' ').title()} ({max_evaluator[1]*100:.0f}%)"
        return None