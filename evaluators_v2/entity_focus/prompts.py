"""Prompts for Entity Focus V2 evaluator with entity extraction and focus analysis."""

from utils.text_converter import load_ignore_artifacts


def get_system_prompt() -> str:
    """Get the procedural system prompt for Entity Focus V2 evaluation.
    
    Returns:
        Complete system prompt with embedded ignore artifacts list
    """
    ignore_artifacts = load_ignore_artifacts()
    
    return f"""Extract entities and evaluate focus for RAG. Use the schema. Keep extraction faithful to surface forms.

Tasks:
1) Extract entities with type, offsets, and specificity (generic/specific/proper).
2) Identify primary topic.
3) Score (0–100): alignment (on‑topic entities), specificity (concrete vs generic), coverage (critical entities present for the chunk type).
4) overall = round(0.5*alignment + 0.3*specificity + 0.2*coverage)
5) passing = overall ≥ cfg.evaluation.thresholds.entity_focus

Entity Types:
- PRODUCT: Software products, tools, services, applications
- ORG: Organizations, companies, institutions  
- PERSON: People, authors, developers, researchers
- CONCEPT: Abstract concepts, principles, ideas
- TECHNOLOGY: Technologies, frameworks, languages, protocols
- METHOD: Methods, processes, techniques, approaches

Specificity Levels:
- generic: Broad terms (e.g., "database", "software")
- specific: Concrete instances (e.g., "relational database", "web application")  
- proper: Named entities (e.g., "PostgreSQL", "React.js")

Scoring Guidelines:
- Alignment (50%): How well entities relate to the primary topic
- Specificity (30%): Balance of concrete vs generic terms
- Coverage (20%): Presence of entities critical for the chunk type

Ignore standard web artifacts (see below). Output strictly matches schema.

{ignore_artifacts}"""


def create_user_prompt(heading: str, text: str) -> str:
    """Create the user prompt for Entity Focus evaluation.
    
    Args:
        heading: Chunk heading or "[No heading]"
        text: Chunk text content
        
    Returns:
        Formatted user prompt
    """
    heading_display = heading if heading and heading.strip() else "[No heading]"
    
    return f"""HEADING: {heading_display}

CONTENT:
{text}"""


# For reference: Entity extraction guidelines
EXTRACTION_GUIDELINES = {
    "surface_form_faithful": "Extract entities exactly as they appear in text",
    "position_accurate": "Provide exact character start/end positions",
    "type_appropriate": "Choose the most specific applicable type",
    "specificity_correct": "Assess generic/specific/proper accurately"
}

# For reference: Scoring weights
SCORING_WEIGHTS = {
    "alignment": 0.5,      # Primary topic relevance
    "specificity": 0.3,    # Concrete vs generic balance
    "coverage": 0.2        # Critical entity presence
}

# For reference: Coverage expectations by chunk type
COVERAGE_EXPECTATIONS = {
    "definition": ["CONCEPT", "TECHNOLOGY", "METHOD"],
    "example": ["PRODUCT", "TECHNOLOGY", "specific_instances"],
    "overview": ["CONCEPT", "ORG", "broad_categories"],
    "detail": ["TECHNOLOGY", "METHOD", "specific_implementations"],
    "general": ["mixed_types", "context_dependent"]
}