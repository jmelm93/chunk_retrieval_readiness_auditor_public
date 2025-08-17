"""Simplified Entity Focus V3 models - minimal extension of base."""

from typing import List, Literal
from pydantic import BaseModel, Field

from ..base.models import BaseEvaluationResult


class Entity(BaseModel):
    """Simple entity representation."""
    
    text: str = Field(
        description="Entity as it appears in the text"
    )
    
    type: Literal["PRODUCT", "ORG", "PERSON", "CONCEPT", "TECHNOLOGY", "METHOD"] = Field(
        description="Entity type classification"
    )
    
    specificity: Literal["generic", "specific", "proper"] = Field(
        description="Level: generic (broad), specific (concrete), proper (named)"
    )


class EntityFocusResult(BaseEvaluationResult):
    """Entity Focus evaluation result with minimal additional fields.
    
    Extends base with only essential entity-specific fields.
    Scoring logic moved to evaluator.
    """
    
    # Additional fields specific to Entity Focus evaluation  
    primary_entities: List[Entity] = Field(
        description="Main entities extracted from the chunk"
    )
    
    primary_topic: str = Field(
        description="The main topic or subject of the chunk"
    )
    
    entity_coverage: float = Field(
        ge=0.0,
        le=1.0,
        description="Coverage ratio of important entities (0.0-1.0)"
    )
    
    # That's it! No weighted scores, no dimensional breakdowns.
    # The base model already has all we need for output.