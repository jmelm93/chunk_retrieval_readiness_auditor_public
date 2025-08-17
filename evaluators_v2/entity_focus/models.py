"""Entity Focus V2 evaluator models with entity extraction and alignment scoring."""

from pydantic import BaseModel, Field
from typing import List, Literal, Any
from ..base.models import BaseEvaluationResult


class Entity(BaseModel):
    """Represents an extracted entity with type and position information."""
    
    text: str = Field(
        description="Surface form of the entity as it appears in the text"
    )
    
    type: Literal[
        "PRODUCT",
        "ORG", 
        "PERSON",
        "CONCEPT",
        "TECHNOLOGY",
        "METHOD"
    ] = Field(
        description="Categorization of the entity type"
    )
    
    start: int = Field(
        ge=0,
        description="Character offset where the entity starts in the text"
    )
    
    end: int = Field(
        ge=0,
        description="Character offset where the entity ends in the text"
    )
    
    specificity: Literal["generic", "specific", "proper"] = Field(
        description="Level of specificity: generic (broad terms), specific (concrete instances), proper (named entities)"
    )


class EntityFocusEval(BaseEvaluationResult):
    """Machine-readable result for Entity Focus & Coherence evaluator.
    
    This model captures entity extraction and focus analysis with 
    dimensional scoring and missing entity detection.
    """
    
    primary_topic: str = Field(
        description="The main topic or subject matter of the chunk"
    )
    
    entities: List[Entity] = Field(
        description="List of extracted entities with types, positions, and specificity"
    )
    
    # Dimensional scores (0-100 each)
    alignment: int = Field(
        ge=0, le=100,
        description="How well entities align with the primary topic (0-100)"
    )
    
    specificity_score: int = Field(
        ge=0, le=100,
        description="Balance of concrete vs generic entities (0-100)"
    )
    
    coverage: int = Field(
        ge=0, le=100,
        description="Presence of critical entities for the chunk type (0-100)"
    )
    
    missing_critical_entities: List[str] = Field(
        description="List of entity types or specific entities that should be present but are missing"
    )
    
    # Scoring calculation details for auditability
    weighted_score: float = Field(
        description="Raw weighted score: 0.5*alignment + 0.3*specificity + 0.2*coverage"
    )
    
    # Override overall_score to be calculated field
    overall_score: int = Field(
        ge=0, le=100,
        description="Final score: round(weighted_score)"
    )
    
    def model_post_init(self, __context: Any) -> None:
        """Calculate weighted score and overall score."""
        # Calculate weighted score
        weighted = (
            0.5 * self.alignment +
            0.3 * self.specificity_score +
            0.2 * self.coverage
        )
        object.__setattr__(self, 'weighted_score', weighted)
        
        # Round to get overall score
        rounded_score = round(weighted)
        object.__setattr__(self, 'overall_score', rounded_score)


class EntityFocusMarkdownResult(BaseModel):
    """Simplified result for markdown rendering compatibility."""
    
    evaluator_name: str = Field(default="Entity Focus & Coherence")
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


# Entity type definitions for reference
ENTITY_TYPES = {
    "PRODUCT": "Software products, tools, services, applications",
    "ORG": "Organizations, companies, institutions",
    "PERSON": "People, authors, developers, researchers",
    "CONCEPT": "Abstract concepts, principles, ideas",
    "TECHNOLOGY": "Technologies, frameworks, languages, protocols", 
    "METHOD": "Methods, processes, techniques, approaches"
}

# Specificity levels for reference
SPECIFICITY_LEVELS = {
    "generic": "Broad, general terms (e.g., 'database', 'software')",
    "specific": "Concrete instances (e.g., 'relational database', 'web application')",
    "proper": "Named entities (e.g., 'PostgreSQL', 'React.js')"
}

# Dimension weights for calculation
DIMENSION_WEIGHTS = {
    "alignment": 0.5,
    "specificity": 0.3,
    "coverage": 0.2
}