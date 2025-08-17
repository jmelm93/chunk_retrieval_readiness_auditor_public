"""Essential base Pydantic models for V2 evaluators."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, List


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



class MarkdownResult(BaseModel):
    """Simplified result for markdown rendering compatibility."""
    
    overall_score: int = Field(ge=0, le=100)
    overall_assessment: str
    strengths: List[str]
    issues: List[str] 
    recommendations: List[str]
    passing: bool
    
    def as_markdown(self) -> str:
        """Generate markdown feedback for human consumption."""
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