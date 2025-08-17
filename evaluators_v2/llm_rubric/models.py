"""LLM Rubric V2 evaluator models with dimensional scoring and barrier gates."""

from pydantic import BaseModel, Field
from typing import Dict, List, Any
from ..base.models import BaseEvaluationResult


class LLMRubricEval(BaseEvaluationResult):
    """LLM Rubric Quality evaluator result with dimensional scoring.
    
    Extends BaseEvaluationResult with dimensional scores, barrier detection,
    and evidence spans for comprehensive evaluation tracking.
    """
    
    # Dimensional scores (0-100 each)
    standalone: int = Field(
        ge=0, le=100,
        description="Comprehensible without external context (0-100)"
    )
    
    one_idea: int = Field(
        ge=0, le=100,
        description="Single clear focus, no topic drift (0-100)"
    )
    
    structure: int = Field(
        ge=0, le=100,
        description="Scannable with paragraphs/lists/tables/code as needed (0-100)"
    )
    
    right_size: int = Field(
        ge=0, le=100,
        description="Appropriate scope for target token range (0-100)"
    )
    
    # Barrier detection and gates
    gates_triggered: List[str] = Field(
        default_factory=list,
        description="List of barriers that applied score caps (e.g., 'vague_refs', 'wall_of_text')"
    )
    
    evidence_spans: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Dictionary mapping barrier types to evidence text spans"
    )
    
    # Scoring calculation details for auditability
    weighted_score: float = Field(
        description="Raw weighted score before rounding: 0.4*standalone + 0.3*structure + 0.2*one_idea + 0.1*right_size"
    )
    
    def model_post_init(self, __context: Any) -> None:
        """Calculate weighted score and overall score."""
        # Calculate weighted score
        weighted = (
            0.4 * self.standalone +
            0.3 * self.structure + 
            0.2 * self.one_idea +
            0.1 * self.right_size
        )
        object.__setattr__(self, 'weighted_score', weighted)
        
        # Round to get overall score
        rounded_score = round(weighted)
        object.__setattr__(self, 'overall_score', rounded_score)


class LLMRubricMarkdownResult(BaseModel):
    """Simplified result for markdown rendering compatibility."""
    
    evaluator_name: str = Field(default="LLM Rubric Quality")
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


# Barrier gate definitions for reference
BARRIER_GATES = {
    "vague_refs": {
        "affects": "standalone",
        "max_score": 40,
        "description": "Vague references cap standalone score"
    },
    "wall_of_text": {
        "affects": "structure", 
        "max_score": 35,
        "description": "Wall of text caps structure score"
    },
    "topic_confusion": {
        "affects": "one_idea",
        "max_score": 35,
        "description": "Topic confusion caps one_idea score"
    },
    "misleading_headers": {
        "affects": "overall",
        "description": "Misleading headers affect overall narrative (recorded in recommendations)"
    },
    "jargon": {
        "affects": "standalone",
        "penalty_range": (5, 15),
        "description": "Excessive jargon reduces standalone by 5-15 points depending on severity"
    }
}

# Dimension weights for calculation
DIMENSION_WEIGHTS = {
    "standalone": 0.4,
    "structure": 0.3,
    "one_idea": 0.2,
    "right_size": 0.1
}