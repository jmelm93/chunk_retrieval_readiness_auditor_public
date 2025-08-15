"""Pydantic models for AI-driven Entity Focus evaluation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..base.models import BaseEvaluationResult, FormattingOptions


class ExtractedEntity(BaseModel):
    """An entity extracted from the chunk text by the AI evaluator."""
    
    model_config = ConfigDict(extra='forbid')
    
    name: str = Field(
        min_length=1,
        description="The entity name as it appears in the text"
    )
    entity_type: str = Field(
        description="Type of entity (e.g., PRODUCT, ORGANIZATION, PERSON, CONCEPT, TECHNOLOGY, METHOD)"
    )
    salience: float = Field(
        ge=0.0, le=1.0,
        description="Estimated importance/prominence in the chunk (0.0-1.0)"
    )
    is_concrete: bool = Field(
        description="Whether this is a specific, concrete entity vs abstract/generic"
    )


class EntityRelevance(BaseModel):
    """Evaluation of an individual entity's relevance and contribution."""
    
    model_config = ConfigDict(extra='forbid')
    
    entity_name: str = Field(
        min_length=1,
        description="Name of the entity being evaluated"
    )
    entity_type: str = Field(
        description="Type of entity (PERSON, ORGANIZATION, CONCEPT, PRODUCT, etc.)"
    )
    relevance_score: int = Field(
        ge=0, le=100,
        description="How relevant this entity is to the chunk's main topic (0-100)"
    )
    contribution: str = Field(
        min_length=10,
        description="How this entity contributes to the chunk's value"
    )
    is_concrete: bool = Field(
        description="Whether this is a concrete, specific entity vs generic reference"
    )


class EntityCoherence(BaseModel):
    """Overall assessment of entity-topic alignment and coherence."""
    
    model_config = ConfigDict(extra='forbid')
    
    primary_topic: str = Field(
        min_length=3,
        description="The primary topic/concept this chunk focuses on"
    )
    topic_alignment_score: int = Field(
        ge=0, le=100,
        description="How well entities align with and support the primary topic (0-100)"
    )
    entity_density: str = Field(
        pattern="^(sparse|appropriate|dense)$",
        description="Entity density assessment: sparse, appropriate, or dense"
    )
    diversity_assessment: str = Field(
        min_length=20,
        description="Whether entity diversity helps or hinders chunk focus"
    )


class MissingEntity(BaseModel):
    """An entity that should be present but is missing."""
    
    model_config = ConfigDict(extra='forbid')
    
    entity_description: str = Field(
        min_length=5,
        description="Description of the missing entity"
    )
    why_important: str = Field(
        min_length=10,
        description="Why this entity would strengthen the chunk"
    )
    impact_score: int = Field(
        ge=1, le=10,
        description="Impact of this missing entity (1-10, where 10 is critical)"
    )


class EntityQualityIssue(BaseModel):
    """A specific issue with entity usage in the chunk."""
    
    model_config = ConfigDict(extra='forbid')
    
    issue_type: str = Field(
        description="Type of issue (e.g., 'too_generic', 'irrelevant', 'overused', 'underspecified')"
    )
    description: str = Field(
        min_length=10,
        description="Description of the issue"
    )
    affected_entities: List[str] = Field(
        max_length=3,
        description="Entities affected by this issue (provide empty list [] if general issue)"
    )


class EntityFocusResult(BaseEvaluationResult):
    """Complete result from AI-driven Entity Focus evaluation."""
    
    model_config = ConfigDict(extra='forbid')
    
    # Extracted entities (NEW - AI extracts these itself)
    extracted_entities: List[ExtractedEntity] = Field(
        min_length=0,
        max_length=10,
        description="Entities extracted from the chunk by the AI evaluator"
    )
    
    # Core entity analysis
    entity_relevance_evaluations: List[EntityRelevance] = Field(
        min_length=1,
        max_length=5,
        description="Relevance evaluation for top entities in the chunk"
    )
    
    entity_coherence: EntityCoherence = Field(
        description="Overall entity-topic coherence assessment"
    )
    
    # Quality metrics
    overall_focus_score: int = Field(
        ge=0, le=100,
        description="Overall entity focus quality score (0-100)"
    )
    
    concrete_entity_ratio: float = Field(
        ge=0.0, le=1.0,
        description="Ratio of concrete/specific entities vs generic references"
    )
    
    heading_entity_alignment: bool = Field(
        description="Whether key entities align with the chunk heading"
    )
    
    # Missing and issues
    missing_entities: List[MissingEntity] = Field(
        max_length=3,
        description="Critical entities that are missing (provide empty list [] if none)"
    )
    
    quality_issues: List[EntityQualityIssue] = Field(
        max_length=3,
        description="Issues with entity usage (provide empty list [] if none)"
    )
    
    # Strengths and recommendations
    strengths: List[str] = Field(
        max_length=3,
        description="Strengths in entity usage (provide empty list [] if none)"
    )
    
    recommendations: List[str] = Field(
        min_length=1,
        max_length=3,
        description="Specific recommendations for improving entity focus"
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
        
        # Entity Analysis
        lines.append("\n**Entity Analysis:**")
        lines.append(f"• Primary Topic: {self.entity_coherence.primary_topic}")
        lines.append(f"• Topic Alignment: {self.entity_coherence.topic_alignment_score}/100")
        lines.append(f"• Entity Density: {self.entity_coherence.entity_density.title()}")
        lines.append(f"• Concrete Entity Ratio: {int(self.concrete_entity_ratio * 100)}%")
        
        # Show extracted entities first (NEW)
        if self.extracted_entities:
            lines.append("\n**Extracted Entities:**")
            concrete_count = sum(1 for e in self.extracted_entities if e.is_concrete)
            total_count = len(self.extracted_entities)
            lines.append(f"Found {total_count} entities ({concrete_count} concrete, {total_count - concrete_count} generic)")
            
            if options.verbosity != "concise" and self.extracted_entities:
                # Show a few examples
                for entity in self.extracted_entities[:5]:
                    marker = "✓" if entity.is_concrete else "○"
                    lines.append(f"  {marker} {entity.name} ({entity.entity_type})")
        
        # Top Entities
        if self.entity_relevance_evaluations:
            lines.append("\n**Top Entities by Relevance:**")
            
            entities_to_show = self.entity_relevance_evaluations
            if options.filter_output and len(entities_to_show) > 3:
                entities_to_show = entities_to_show[:3]
            
            for i, entity in enumerate(entities_to_show, 1):
                concrete_marker = "✓" if entity.is_concrete else "○"
                lines.append(f"{i}. \"{entity.entity_name}\" ({entity.entity_type}) {concrete_marker} - {entity.relevance_score}% relevance")
                if options.verbosity != "concise":
                    lines.append(f"   → {entity.contribution}")
        
        # Entity Coherence Details
        if options.verbosity != "concise":
            lines.append("\n**Entity Diversity:**")
            lines.append(self.entity_coherence.diversity_assessment)
        
        # Strengths
        if self.strengths and self.score >= 60:
            self._add_section_if_content(
                lines, "Strengths",
                self._format_list_items(self.strengths[:2] if options.filter_output else self.strengths, options)
            )
        
        # Quality Issues
        if self.quality_issues:
            lines.append("\n**Entity Usage Issues:**")
            
            issues_to_show = self.quality_issues
            if options.filter_output and len(issues_to_show) > 2:
                issues_to_show = issues_to_show[:2]
            
            for issue in issues_to_show:
                lines.append(f"• {issue.description}")
                if issue.affected_entities:
                    lines.append(f"  Affects: {', '.join(issue.affected_entities)}")
        
        # Missing Entities
        if self.missing_entities:
            lines.append("\n**Missing Critical Entities:**")
            
            missing_to_show = self.missing_entities
            if options.filter_output and len(missing_to_show) > 2:
                missing_to_show = missing_to_show[:2]
            
            for missing in missing_to_show:
                impact_marker = "⚠️" if missing.impact_score >= 7 else "•"
                lines.append(f"{impact_marker} {missing.entity_description}")
                if options.verbosity != "concise":
                    lines.append(f"  → {missing.why_important}")
        
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
        return {
            "evaluator": self.evaluator_name,
            "score": self.score,
            "passing": self.passing,
            "primary_topic": self.entity_coherence.primary_topic,
            "topic_alignment_score": self.entity_coherence.topic_alignment_score,
            "overall_focus_score": self.overall_focus_score,
            "concrete_entity_ratio": round(self.concrete_entity_ratio, 2),
            "heading_alignment": self.heading_entity_alignment,
            "entity_count": len(self.entity_relevance_evaluations),
            "missing_count": len(self.missing_entities),
            "issue_count": len(self.quality_issues),
            "entity_density": self.entity_coherence.entity_density
        }