"""Structure Quality V2 evaluator models with structural issue tracking and penalty system."""

from pydantic import BaseModel, Field
from typing import List, Literal, Any
from ..base.models import BaseEvaluationResult


class StructuralIssue(BaseModel):
    """Represents a specific structural issue found in the content."""
    
    kind: Literal[
        "heading",
        "paragraphs", 
        "lists",
        "tables",
        "code",
        "flow"
    ] = Field(
        description="Category of structural issue"
    )
    
    severity: Literal["minor", "moderate", "severe"] = Field(
        description="Severity level of the issue"
    )
    
    points: int = Field(
        ge=0, le=15,
        description="Points deducted: minor=5, moderate=10, severe=15"
    )
    
    evidence_spans: List[str] = Field(
        description="Specific examples of the structural issue from the content"
    )


class StructureEval(BaseEvaluationResult):
    """Machine-readable result for Structure Quality evaluator.
    
    This model captures structural analysis with issue tracking,
    penalty calculation, and evidence spans for auditability.
    """
    
    issues: List[StructuralIssue] = Field(
        description="List of structural issues detected with evidence"
    )
    
    # Scoring calculation details for auditability
    base_score: int = Field(
        default=100,
        description="Starting score before penalties (always 100)"
    )
    
    total_penalties: int = Field(
        ge=0,
        description="Total penalty points applied (sum of all issue penalties)"
    )
    
    # Override overall_score to be calculated field
    overall_score: int = Field(
        ge=0, le=100,
        description="Final score: max(0, base_score - total_penalties)"
    )
    
    def model_post_init(self, __context: Any) -> None:
        """Calculate total penalties and overall score."""
        # Calculate total penalties
        total_penalties = sum(issue.points for issue in self.issues)
        object.__setattr__(self, 'total_penalties', total_penalties)
        
        # Calculate final score (base - penalties, clamped 0-100)
        final_score = max(0, min(100, self.base_score - total_penalties))
        object.__setattr__(self, 'overall_score', final_score)


class StructureMarkdownResult(BaseModel):
    """Simplified result for markdown rendering compatibility."""
    
    evaluator_name: str = Field(default="Structure Quality")
    overall_score: int = Field(ge=0, le=100)
    overall_assessment: str
    strengths: List[str]
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
        
        # Recommendations
        lines.append("🎯 **Recommendations:**")
        for recommendation in self.recommendations:
            lines.append(f"- {recommendation}")
        
        return "\n".join(lines)


# Structural categories for reference
STRUCTURAL_CATEGORIES = {
    "heading": {
        "description": "Heading specificity and accuracy",
        "good_indicators": ["descriptive", "specific", "accurate"],
        "issues": ["vague", "misleading", "generic", "missing"]
    },
    "paragraphs": {
        "description": "Paragraph sizing and readability",
        "good_indicators": ["appropriate length", "clear breaks", "logical grouping"],
        "issues": ["walls of text", "too short", "poor breaks"]
    },
    "lists": {
        "description": "Use of lists where appropriate",
        "good_indicators": ["proper enumeration", "clear structure", "appropriate use"],
        "issues": ["missed opportunities", "poor formatting", "unclear structure"]
    },
    "tables": {
        "description": "Use of tables where appropriate",
        "good_indicators": ["tabular data properly formatted", "clear headers", "readable"],
        "issues": ["missed table opportunities", "poor formatting", "unclear structure"]
    },
    "code": {
        "description": "Code formatting and presentation",
        "good_indicators": ["proper code blocks", "syntax highlighting", "clear examples"],
        "issues": ["poor code formatting", "missing code blocks", "unclear examples"]
    },
    "flow": {
        "description": "Overall content flow and organization",
        "good_indicators": ["intro → body → wrap-up", "logical progression", "clear structure"],
        "issues": ["poor organization", "abrupt transitions", "missing flow"]
    }
}

# Penalty severity mapping
PENALTY_SEVERITY = {
    "minor": 5,
    "moderate": 10,
    "severe": 15
}