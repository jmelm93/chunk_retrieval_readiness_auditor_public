"""Entity Focus V2 evaluator models with entity extraction and alignment scoring."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Any


class Entity(BaseModel):
    """Represents an extracted entity with type and specificity information."""
    
    text: str = Field(description="Surface form of the entity as it appears in the text")
    type: Literal["PRODUCT", "ORG", "PERSON", "CONCEPT", "TECHNOLOGY", "METHOD"] = Field(description="Categorization of the entity type")
    specificity: Literal["generic", "specific", "proper"] = Field(description="Level of specificity: generic (broad terms), specific (concrete instances), proper (named entities)")


class EntityFocusEval(BaseModel):
    """Entity Focus & Coherence evaluator result.
    
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
    
    # Entity Focus specific fields
    primary_topic: str = Field(description="The main topic or subject matter of the chunk")
    entities: List[Entity] = Field(description="List of extracted entities with types and specificity")
    
    # Dimensional scores (0-100 each)
    alignment: int = Field(ge=0, le=100, description="How well entities align with the primary topic (0-100)")
    specificity_score: int = Field(ge=0, le=100, description="Balance of concrete vs generic entities (0-100)")
    coverage: int = Field(ge=0, le=100, description="Presence of critical entities for the chunk type (0-100)")
    missing_critical_entities: List[str] = Field(description="List of entity types or specific entities that should be present but are missing")
    
    # Scoring calculation details for auditability
    weighted_score: float = Field(description="Raw weighted score: 0.5*alignment + 0.3*specificity + 0.2*coverage")
    
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