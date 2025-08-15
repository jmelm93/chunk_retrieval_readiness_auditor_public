"""Pydantic models for LLM Rubric evaluation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..base.models import BaseEvaluationResult, FormattingOptions


class RubricScores(BaseModel):
    """Individual rubric dimension scores."""
    
    model_config = ConfigDict(extra='forbid')
    
    standalone: int = Field(
        ge=0, le=100,
        description="Standalone readability score - chunk understandable without other sections (0-100)"
    )
    one_idea: int = Field(
        ge=0, le=100,
        description="Single topic focus score - maintains coherent focus on one concept (0-100)"
    )
    structure: int = Field(
        ge=0, le=100,
        description="Content structure score - clear heading, intro, organization (0-100)"
    )
    right_size: int = Field(
        ge=0, le=100,
        description="Appropriate size score - not too short or long for retrieval (0-100)"
    )
    
    def average_score(self) -> float:
        """Calculate average across all rubric dimensions."""
        return (self.standalone + self.one_idea + self.structure + self.right_size) / 4


class RubricJustifications(BaseModel):
    """Justifications for each rubric score."""
    
    model_config = ConfigDict(extra='forbid')
    
    standalone: str = Field(
        min_length=10,
        description="1-2 sentence justification for standalone score"
    )
    one_idea: str = Field(
        min_length=10,
        description="1-2 sentence justification for one idea score"
    )
    structure: str = Field(
        min_length=10,
        description="1-2 sentence justification for structure score"
    )
    right_size: str = Field(
        min_length=10,
        description="1-2 sentence justification for right size score"
    )


class ContentFlag(BaseModel):
    """A detected content quality issue."""
    
    model_config = ConfigDict(extra='forbid')
    
    flag_type: str = Field(
        description="Type of issue (e.g., 'vague_references', 'missing_context', 'redundant_content')"
    )
    description: str = Field(
        description="Brief description of the issue"
    )
    severity: str = Field(
        pattern="^(low|medium|high)$",
        description="Severity of the issue: low, medium, or high (always provide one of these values)"
    )


class LLMRubricResult(BaseEvaluationResult):
    """Complete result from LLM Rubric evaluation."""
    
    model_config = ConfigDict(extra='forbid')
    
    # Rubric scores and justifications
    scores: RubricScores = Field(
        description="Individual scores for each rubric dimension"
    )
    justifications: RubricJustifications = Field(
        description="Justifications for each rubric score"
    )
    
    # Content quality indicators
    flags: List[ContentFlag] = Field(
        max_length=5,
        description="Detected content quality issues (provide empty list [] if no issues)"
    )
    
    # Improvement suggestions
    suggested_heading: str = Field(
        min_length=3,
        max_length=50,
        description="Improved heading suggestion (3-8 words ideal)"
    )
    rewrite_lead: str = Field(
        min_length=50,
        max_length=300,
        description="Rewritten introduction paragraph for better clarity"
    )
    recommendations: List[str] = Field(
        min_length=1,
        max_length=3,
        description="1-3 concrete recommendations for improvement"
    )
    
    def as_markdown(self, options: Optional[FormattingOptions] = None) -> str:
        """Generate formatted markdown feedback.
        
        Args:
            options: Formatting options for output control
            
        Returns:
            Formatted markdown string
        """
        options = options or FormattingOptions()
        lines = []
        
        # Overall Assessment
        lines.append("**Assessment:**")
        avg_score = self.scores.average_score()
        if avg_score >= 80:
            lines.append("Excellent chunk quality - well-optimized for AI retrieval")
        elif avg_score >= 60:
            lines.append("Good chunk quality with some areas for improvement")
        else:
            lines.append("Significant improvements needed for effective retrieval")
        
        # Rubric Scores with Explanations
        lines.append("\n**Rubric Scores:**")
        
        lines.append(f"• Standalone Clarity: {self.scores.standalone}/100")
        if options.verbosity != "concise":
            lines.append(f"  → {self.justifications.standalone}")
        
        lines.append(f"• Topic Focus: {self.scores.one_idea}/100")
        if options.verbosity != "concise":
            lines.append(f"  → {self.justifications.one_idea}")
        
        lines.append(f"• Structure Quality: {self.scores.structure}/100")
        if options.verbosity != "concise":
            lines.append(f"  → {self.justifications.structure}")
        
        lines.append(f"• Content Size: {self.scores.right_size}/100")
        if options.verbosity != "concise":
            lines.append(f"  → {self.justifications.right_size}")
        
        # Strengths (if scoring well)
        if avg_score >= 70:
            strengths = self._identify_strengths()
            if strengths:
                self._add_section_if_content(
                    lines, "Strengths",
                    self._format_list_items(strengths[:2] if options.filter_output else strengths, options)
                )
        
        # Issues Found
        if self.flags:
            lines.append("\n**Issues Detected:**")
            
            flags_to_show = self.flags
            if options.filter_output and len(flags_to_show) > 3:
                flags_to_show = flags_to_show[:3]
            
            for flag in flags_to_show:
                severity_marker = "⚠️" if flag.severity == "high" else "•"
                lines.append(f"{severity_marker} {flag.description}")
        
        # Key Recommendations
        if self.recommendations:
            self._add_section_if_content(
                lines, "Key Recommendations",
                [f"{i+1}. {rec}" for i, rec in enumerate(
                    self.recommendations[:3] if options.filter_output else self.recommendations
                )]
            )
        
        # Suggested Improvements (based on low scores)
        low_score_recs = self._generate_improvement_suggestions()
        if low_score_recs and not self.recommendations:
            self._add_section_if_content(
                lines, "Suggested Improvements",
                self._format_list_items(
                    low_score_recs[:2] if options.filter_output else low_score_recs,
                    options
                )
            )
        
        return "\n".join(lines)
    
    def _identify_strengths(self) -> List[str]:
        """Identify strengths based on high-scoring dimensions."""
        strengths = []
        
        if self.scores.standalone >= 80:
            strengths.append("Self-contained and clear without external context")
        if self.scores.one_idea >= 80:
            strengths.append("Maintains strong topical focus")
        if self.scores.structure >= 80:
            strengths.append("Well-structured with clear organization")
        if self.scores.right_size >= 80:
            strengths.append("Optimal length for chunk retrieval")
        
        return strengths
    
    def _generate_improvement_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on low scores."""
        suggestions = []
        
        if self.scores.standalone < 70:
            suggestions.append("Add context to make chunk self-contained")
        if self.scores.one_idea < 70:
            suggestions.append("Focus on a single clear topic or concept")
        if self.scores.structure < 70:
            suggestions.append("Improve formatting and heading structure")
        if self.scores.right_size < 70:
            if self.scores.right_size < 50:
                suggestions.append("Expand content to provide sufficient detail")
            else:
                suggestions.append("Consider splitting into smaller, focused chunks")
        
        return suggestions
    
    def as_json_summary(self) -> Dict[str, Any]:
        """Generate a summary JSON representation.
        
        Returns:
            Dictionary with key metrics and insights
        """
        return {
            "evaluator": self.evaluator_name,
            "score": self.score,
            "passing": self.passing,
            "rubric_scores": {
                "standalone": self.scores.standalone,
                "one_idea": self.scores.one_idea,
                "structure": self.scores.structure,
                "right_size": self.scores.right_size,
                "average": self.scores.average_score()
            },
            "high_severity_flags": sum(1 for f in self.flags if f.severity == "high"),
            "total_flags": len(self.flags),
            "suggested_heading": self.suggested_heading,
            "recommendation_count": len(self.recommendations)
        }