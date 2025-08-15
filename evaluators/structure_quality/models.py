"""Pydantic models for AI-driven Structure Quality evaluation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..base.models import BaseEvaluationResult, FormattingOptions


class StructuralElement(BaseModel):
    """Analysis of a specific structural element in the chunk."""
    
    model_config = ConfigDict(extra='forbid')
    
    element_type: str = Field(
        description="Type of structural element (heading, list, table, paragraph, code_block, etc.)"
    )
    effectiveness_score: int = Field(
        ge=0, le=100,
        description="How effectively this element is used (0-100)"
    )
    assessment: str = Field(
        min_length=10,
        description="Assessment of how this element contributes to or detracts from chunk quality"
    )
    
    
class HeadingQuality(BaseModel):
    """Detailed assessment of heading quality."""
    
    model_config = ConfigDict(extra='forbid')
    
    clarity_score: int = Field(
        ge=0, le=100,
        description="How clear and descriptive the heading is (0-100)"
    )
    accuracy_score: int = Field(
        ge=0, le=100,
        description="How accurately the heading describes the content (0-100)"
    )
    specificity_score: int = Field(
        ge=0, le=100,
        description="How specific vs generic the heading is (0-100)"
    )
    improved_heading: str = Field(
        min_length=3,
        max_length=100,
        description="Suggested improved heading if current one needs work"
    )
    issues: List[str] = Field(
        max_length=3,
        description="Specific issues with the current heading (provide empty list [] if none)"
    )


class ReadabilitySignals(BaseModel):
    """Signals affecting chunk readability and scanability."""
    
    model_config = ConfigDict(extra='forbid')
    
    has_clear_intro: bool = Field(
        description="Whether chunk has a clear introductory context"
    )
    logical_flow: bool = Field(
        description="Whether content follows a logical progression"
    )
    appropriate_formatting: bool = Field(
        description="Whether formatting choices match content needs"
    )
    scanability_score: int = Field(
        ge=0, le=100,
        description="How easy it is to quickly scan and extract information (0-100)"
    )
    information_density: str = Field(
        pattern="^(too_sparse|appropriate|too_dense)$",
        description="Assessment of information density: too_sparse, appropriate, or too_dense"
    )


class StructuralIssue(BaseModel):
    """A specific structural issue affecting chunk quality."""
    
    model_config = ConfigDict(extra='forbid')
    
    issue_type: str = Field(
        description="Type of issue (e.g., 'wall_of_text', 'poor_hierarchy', 'missing_structure', 'inconsistent_formatting')"
    )
    description: str = Field(
        min_length=10,
        description="Description of the structural issue"
    )
    impact: str = Field(
        pattern="^(low|medium|high)$",
        description="Impact on chunk retrieval quality: low, medium, or high"
    )
    suggestion: str = Field(
        min_length=10,
        description="Specific suggestion to fix this issue"
    )


class StructureQualityResult(BaseEvaluationResult):
    """Complete result from AI-driven Structure Quality evaluation."""
    
    model_config = ConfigDict(extra='forbid')
    
    # Core structure analysis
    structural_elements: List[StructuralElement] = Field(
        max_length=5,
        description="Analysis of key structural elements in the chunk"
    )
    
    heading_quality: HeadingQuality = Field(
        description="Detailed heading quality assessment"
    )
    
    readability_signals: ReadabilitySignals = Field(
        description="Readability and scanability assessment"
    )
    
    # Quality metrics
    overall_structure_score: int = Field(
        ge=0, le=100,
        description="Overall structure quality score (0-100)"
    )
    
    formatting_effectiveness: int = Field(
        ge=0, le=100,
        description="How effectively formatting supports content comprehension (0-100)"
    )
    
    retrieval_friendliness: int = Field(
        ge=0, le=100,
        description="How well-structured for AI chunk retrieval (0-100)"
    )
    
    # Issues and recommendations
    structural_issues: List[StructuralIssue] = Field(
        max_length=3,
        description="Major structural issues found (provide empty list [] if none)"
    )
    
    strengths: List[str] = Field(
        max_length=3,
        description="Structural strengths (provide empty list [] if none)"
    )
    
    recommendations: List[str] = Field(
        min_length=1,
        max_length=3,
        description="Specific recommendations for improving structure"
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
        
        # Assessment
        lines.append("**Assessment:**")
        lines.append(self.explanation)
        
        # Structural Analysis
        lines.append("\n**Structural Analysis:**")
        
        # Heading Quality
        avg_heading_score = (
            self.heading_quality.clarity_score + 
            self.heading_quality.accuracy_score + 
            self.heading_quality.specificity_score
        ) / 3
        lines.append(f"• Heading Quality: {int(avg_heading_score)}/100")
        if self.heading_quality.issues:
            lines.append(f"  Issues: {', '.join(self.heading_quality.issues[:2])}")
        
        # Readability
        lines.append(f"• Scanability: {self.readability_signals.scanability_score}/100")
        lines.append(f"• Information Density: {self.readability_signals.information_density.replace('_', ' ').title()}")
        
        readability_checks = []
        if self.readability_signals.has_clear_intro:
            readability_checks.append("✓ Clear intro")
        else:
            readability_checks.append("✗ Missing intro")
        if self.readability_signals.logical_flow:
            readability_checks.append("✓ Logical flow")
        else:
            readability_checks.append("✗ Poor flow")
        if self.readability_signals.appropriate_formatting:
            readability_checks.append("✓ Good formatting")
        else:
            readability_checks.append("✗ Formatting issues")
        
        lines.append(f"• {', '.join(readability_checks)}")
        
        # Structural Elements
        if self.structural_elements:
            lines.append("\n**Key Structural Elements:**")
            elements_to_show = self.structural_elements
            if options.filter_output and len(elements_to_show) > 3:
                elements_to_show = elements_to_show[:3]
            
            for element in elements_to_show:
                effectiveness_indicator = "✓" if element.effectiveness_score >= 70 else "⚠️" if element.effectiveness_score >= 50 else "✗"
                lines.append(f"{effectiveness_indicator} {element.element_type.replace('_', ' ').title()}: {element.effectiveness_score}/100")
                if options.verbosity != "concise":
                    lines.append(f"  → {element.assessment}")
        
        # Strengths
        if self.strengths and self.score >= 60:
            self._add_section_if_content(
                lines, "Strengths",
                self._format_list_items(self.strengths[:2] if options.filter_output else self.strengths, options)
            )
        
        # Structural Issues
        if self.structural_issues:
            lines.append("\n**Structural Issues:**")
            
            issues_to_show = self.structural_issues
            if options.filter_output and len(issues_to_show) > 2:
                issues_to_show = issues_to_show[:2]
            
            for issue in issues_to_show:
                severity_marker = "⚠️" if issue.impact == "high" else "•"
                lines.append(f"{severity_marker} {issue.description}")
                if options.verbosity != "concise":
                    lines.append(f"  → Fix: {issue.suggestion}")
        
        # Improved Heading Suggestion
        if avg_heading_score < 70 and self.heading_quality.improved_heading:
            lines.append(f"\n**Suggested Heading:** {self.heading_quality.improved_heading}")
        
        # Optimization Suggestions
        if self.recommendations:
            self._add_section_if_content(
                lines, "Optimization Suggestions",
                self._format_list_items(
                    self.recommendations[:2] if options.filter_output else self.recommendations,
                    options
                )
            )
        
        return "\n".join(lines)
    
    def as_json_summary(self) -> Dict[str, Any]:
        """Generate a summary JSON representation.
        
        Returns:
            Dictionary with key metrics and insights
        """
        avg_heading_score = (
            self.heading_quality.clarity_score + 
            self.heading_quality.accuracy_score + 
            self.heading_quality.specificity_score
        ) / 3
        
        return {
            "evaluator": self.evaluator_name,
            "score": self.score,
            "passing": self.passing,
            "overall_structure_score": self.overall_structure_score,
            "formatting_effectiveness": self.formatting_effectiveness,
            "retrieval_friendliness": self.retrieval_friendliness,
            "heading_quality": int(avg_heading_score),
            "scanability_score": self.readability_signals.scanability_score,
            "has_clear_intro": self.readability_signals.has_clear_intro,
            "logical_flow": self.readability_signals.logical_flow,
            "information_density": self.readability_signals.information_density,
            "structural_element_count": len(self.structural_elements),
            "issue_count": len(self.structural_issues),
            "high_impact_issues": sum(1 for i in self.structural_issues if i.impact == "high")
        }