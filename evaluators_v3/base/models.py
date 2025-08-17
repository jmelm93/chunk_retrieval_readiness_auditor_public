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


class Recommendation(BaseModel):
    """Structured recommendation for chunk optimization."""
    
    action: str = Field(
        description="Specific action to improve chunk (e.g., 'Add citation for the 95% recovery claim')"
    )
    
    category: Literal[
        "citation_needed",      # Add sources for claims
        "definition_needed",     # Define vague terms
        "structure_improvement", # Fix formatting/organization  
        "clarity_enhancement",   # Remove vague references
        "entity_enrichment",     # Add specific entities
        "context_bridge",        # Add contextual setup
        "frontload_content"      # Move key info to beginning
    ] = Field(
        description="Category of improvement for grouping similar fixes"
    )
    
    impact: Literal["critical", "high", "medium", "low"] = Field(
        description="Expected impact on AI retrievability (critical=fixes severe barriers, high=major improvement, medium=noticeable help, low=minor enhancement)"
    )
    
    confidence: Literal["certain", "likely", "possible"] = Field(
        description="Confidence this fix will improve retrieval (certain=clear barrier, likely=probable improvement, possible=may help)"
    )
    
    example: Optional[str] = Field(
        default=None,
        description="Optional example of how to implement (e.g., 'Add: according to Smith et al. 2023')"
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
    
    recommendations: List[Recommendation] = Field(
        description="Prioritized improvements ordered by impact (critical→high→medium). Only include medium+ impact items. Empty list if chunk is optimal - do not force recommendations."
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
        
        # Recommendations (grouped by impact)
        if self.recommendations:
            lines.append("🎯 **Recommendations:**")
            
            # Group recommendations by impact level
            critical_recs = [r for r in self.recommendations if r.impact == "critical"]
            high_recs = [r for r in self.recommendations if r.impact == "high"]
            medium_recs = [r for r in self.recommendations if r.impact == "medium"]
            
            # Category icons
            category_icons = {
                "citation_needed": "📝",
                "definition_needed": "🔤",
                "structure_improvement": "📋",
                "clarity_enhancement": "🔍",
                "entity_enrichment": "🏷️",
                "context_bridge": "🔗",
                "frontload_content": "⬆️"
            }
            
            # Display by impact level
            if critical_recs:
                lines.append("")
                lines.append("**🔴 Critical Impact** (Must Fix):")
                for rec in critical_recs:
                    icon = category_icons.get(rec.category, "•")
                    lines.append(f"- {icon} {rec.action}")
                    if rec.example:
                        lines.append(f"  → Example: {rec.example}")
            
            if high_recs:
                lines.append("")
                lines.append("**🟠 High Impact**:")
                for rec in high_recs:
                    icon = category_icons.get(rec.category, "•")
                    lines.append(f"- {icon} {rec.action}")
                    if rec.example:
                        lines.append(f"  → Example: {rec.example}")
            
            if medium_recs:
                lines.append("")
                lines.append("**🟡 Medium Impact**:")
                for rec in medium_recs:
                    icon = category_icons.get(rec.category, "•")
                    lines.append(f"- {icon} {rec.action}")
                    if rec.example:
                        lines.append(f"  → Example: {rec.example}")
        
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