"""Query-Answer V2 evaluator models with structured penalties and evidence tracking."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Any
from ..base.models import EvidenceSpan


class Penalty(BaseModel):
    """Represents a specific penalty applied for AI retrieval barriers."""
    
    barrier: Literal[
        "vague_refs",
        "misleading_headers", 
        "wall_of_text",
        "jargon",
        "topic_confusion",
        "contradictions"
    ] = Field(
        description="Type of AI retrieval barrier detected"
    )
    
    severity: Literal["minor", "moderate", "severe"] = Field(
        description="Severity level of the barrier"
    )
    
    points: int = Field(
        ge=0, le=15,
        description="Points deducted: minor=5, moderate=10, severe=15"
    )
    
    evidence_spans: List[EvidenceSpan] = Field(description="1-3 short verbatim excerpts (≤15 words each) supporting this penalty")


class QueryAnswerEval(BaseModel):
    """Query-Answer Completeness evaluator result.
    
    Standalone model for OpenAI structured outputs compatibility.
    All fields are explicitly required per OpenAI's schema validation.
    """
    
    model_config = ConfigDict(extra='forbid')
    
    # Base evaluator fields (duplicated for standalone compatibility)
    overall_score: int = Field(ge=0, le=100, description="Overall score from 0-100")
    overall_assessment: str = Field(description="Clear and concise assessment (2-4 sentences)")
    strengths: List[str] = Field(description="Key strengths identified by the evaluator")
    issues: List[str] = Field(description="Key issues identified by the evaluator")
    recommendations: List[str] = Field(description="Specific actionable recommendations")
    passing: bool = Field(description="Whether evaluation passed the evaluator's threshold")
    
    # Query-Answer specific fields
    chunk_type: Literal["overview", "detail", "example", "definition", "general"] = Field(description="Classification of the chunk type based on content analysis")
    likely_queries: List[str] = Field(description="3-8 likely user queries this chunk could help answer")
    penalties: List[Penalty] = Field(description="List of AI retrieval barriers detected with evidence")
    penalties_total: int = Field(ge=0, le=90, description="Total penalty points applied (sum of all penalties, capped at 90)")
    quality_caps_applied: List[str] = Field(description="List of quality gates that limited the maximum possible score")
    
    # Scoring breakdown for auditability (no defaults for OpenAI compatibility)
    base_score: int = Field(description="Starting score before penalties (always 100)")
    provisional_score: int = Field(ge=0, le=100, description="Score after applying penalties but before quality caps")
    final_score: int = Field(ge=0, le=100, description="Final score after applying both penalties and quality caps")
    
    def model_post_init(self, __context: Any) -> None:
        """Ensure overall_score matches final_score for consistency."""
        if hasattr(self, 'final_score'):
            object.__setattr__(self, 'overall_score', self.final_score)


class QueryAnswerMarkdownResult(BaseModel):
    """Simplified result for markdown rendering compatibility."""
    
    evaluator_name: str = Field(default="Query-Answer Completeness")
    overall_score: int = Field(ge=0, le=100)
    overall_assessment: str
    strengths: List[str]
    issues: List[str] 
    recommendations: List[str]
    passing: bool
    
    def as_markdown(self, options=None) -> str:
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


# Quality gate definitions for reference
QUALITY_GATES = {
    "multiple_vague_references": {
        "max_score": 60,
        "description": "Multiple vague cross-references detected"
    },
    "misleading_headers": {
        "max_score": 65, 
        "description": "Header-content alignment issues detected"
    },
    "wall_of_text": {
        "max_score": 55,
        "description": "Wall of text structure detected"
    },
    "mixed_unrelated_topics": {
        "max_score": 60,
        "description": "Mixed unrelated topics detected"
    }
}

# Penalty point mapping for reference
PENALTY_POINTS = {
    "minor": 5,
    "moderate": 10, 
    "severe": 15
}