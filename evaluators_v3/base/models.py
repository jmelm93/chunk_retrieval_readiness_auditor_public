"""Simplified base models for V3 evaluators with chain-of-thought field ordering."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class Issue(BaseModel):
    """Represents a single issue/barrier found during evaluation."""
    
    barrier_type: str = Field(
        description="Type of barrier detected (e.g., 'vague_refs', 'wall_of_text')"
    )
    
    severity: Literal["minor", "moderate", "severe"] = Field(
        description="Severity level affecting score deduction"
    )
    
    description: str = Field(
        description="Human-readable explanation of the issue"
    )
    
    evidence: Optional[str] = Field(
        default=None,
        description="Optional text excerpt supporting this issue (max 100 chars)"
    )


class BaseEvaluationResult(BaseModel):
    """Base result for all V3 evaluators with chain-of-thought field ordering.
    
    Field order optimized for AI reasoning:
    1. Analysis fields first (issues, strengths) - builds context
    2. Synthesis fields second (assessment, recommendations) - uses context  
    3. Scoring fields last (score, passing) - informed by analysis
    
    This ordering helps the AI build up reasoning before making final judgments.
    """
    
    model_config = ConfigDict(extra='forbid')
    
    # 1. ANALYSIS PHASE - Identify specific issues and strengths
    issues: List[Issue] = Field(
        description="List of issues/barriers found, ordered by severity"
    )
    
    strengths: List[str] = Field(
        description="Key strengths identified in the chunk (2-4 items)"
    )
    
    # 2. SYNTHESIS PHASE - Synthesize findings into assessment
    assessment: str = Field(
        description="Overall assessment summarizing the evaluation (1-4 sentences)"
    )
    
    recommendations: List[str] = Field(
        description="Specific actionable improvements. If no changes are required, notate 'N/A - Chunk is optimal' (do not force recommendations)"
    )
    
    # 3. SCORING PHASE - Final scoring based on analysis
    score: int = Field(
        ge=0, 
        le=100,
        description="Final score from 0-100 based on issues found"
    )
    
    passing: bool = Field(
        description="Whether the chunk passes the quality threshold"
    )
    
    def to_markdown(self) -> str:
        """Generate markdown representation for human consumption."""
        lines = []
        
        # Score and status
        status_emoji = "✅" if self.passing else "❌"
        lines.append(f"⭐ **Score:** {self.score}/100 {status_emoji}")
        lines.append("")
        
        # Assessment
        lines.append("📋 **Assessment:**")
        lines.append(self.assessment)
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
                severity_marker = "🔴" if issue.severity == "severe" else "🟡" if issue.severity == "moderate" else "⚪"
                lines.append(f"- {severity_marker} {issue.description}")
                if issue.evidence:
                    lines.append(f"  > \"{issue.evidence}\"")
            lines.append("")
        
        # Recommendations
        if self.recommendations:
            lines.append("🎯 **Recommendations:**")
            for rec in self.recommendations:
                lines.append(f"- {rec}")
        
        return "\n".join(lines)
    
    def calculate_penalty_score(self) -> int:
        """Calculate score based on issues found.
        
        This is a helper method evaluators can use or override.
        Returns the score after applying penalties for issues.
        """
        score = 100  # Start at 100
        
        # Apply penalties based on severity
        for issue in self.issues:
            if issue.severity == "minor":
                score -= 5
            elif issue.severity == "moderate":
                score -= 10
            elif issue.severity == "severe":
                score -= 15
        
        # Floor at 10 to avoid completely zeroing out
        return max(10, score)