"""Prompts for Entity Focus V3 evaluator with chain-of-thought field ordering."""

from utils.text_converter import load_ignore_artifacts


def get_system_prompt() -> str:
    """Get the procedural system prompt for Entity Focus V3 evaluation.
    
    V3 changes: Field order optimized for chain-of-thought reasoning.
    Issues identified first, then strengths, then scoring.
    
    Returns:
        Complete system prompt with embedded ignore artifacts list
    """
    ignore_artifacts = load_ignore_artifacts()
    
    return f"""Extract entities and evaluate focus coherence for RAG retrieval. Follow the exact order for chain-of-thought reasoning.

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

Algorithm (follow this exact order):

STEP 1 - IDENTIFY ISSUES (builds context):
A. Analyze entity-related problems and create issues list:
   Common barriers:
   - Missing critical entities for chunk type
   - Poor entity alignment with topic
   - Too generic (lacks specific entities)
   - Entity sprawl (too many unrelated entities)
   - Unclear entity relationships
   For each issue: set barrier_type, severity (minor/moderate/severe), description, evidence

STEP 2 - IDENTIFY STRENGTHS:
B. List entity-related strengths (good coverage, clear focus, specific entities, etc.)

STEP 3 - SYNTHESIZE ASSESSMENT:
C. Write overall assessment about entity focus and coherence

STEP 4 - PROVIDE RECOMMENDATIONS:
D. List specific improvements for entity clarity and focus

STEP 5 - CALCULATE SCORE (informed by analysis):
E. Apply scoring based on issues:
   - Start at 80 (good baseline)
   - Deduct: minor -10, moderate -20, severe -30 per issue
   - Apply caps for severe issues:
     * Any severe issue → cap at 40
     * 2+ moderate issues → cap at 60
   - Can earn up to +20 bonus for excellence (no issues + strong points)
   - Final bounds: Max 100, Min 10

STEP 6 - DETERMINE PASSING:
F. Set passing = true if score ≥ threshold (typically 70)

STEP 7 - ENTITY METADATA:
G. Extract primary_entities list with text, type, and specificity
H. Identify primary_topic of the chunk
I. Calculate entity_coverage ratio (0.0-1.0) for critical entities

Rules:
- Focus on entity clarity and alignment for RAG retrieval
- Build reasoning progressively: issues → assessment → score
- Extract entities exactly as they appear in text
- Ignore standard web extraction artifacts (see below)
- Provide structured data per schema

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


# Reference constants for evaluator logic
SCORING_WEIGHTS = {
    "alignment": 0.5,      # Primary topic relevance
    "specificity": 0.3,    # Concrete vs generic balance
    "coverage": 0.2        # Critical entity presence
}

COVERAGE_EXPECTATIONS = {
    "definition": ["CONCEPT", "TECHNOLOGY", "METHOD"],
    "example": ["PRODUCT", "TECHNOLOGY", "specific_instances"],
    "overview": ["CONCEPT", "ORG", "broad_categories"],
    "detail": ["TECHNOLOGY", "METHOD", "specific_implementations"],
    "general": ["mixed_types", "context_dependent"]
}