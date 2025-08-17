"""Prompts for LLM Rubric V2 evaluator with dimensional scoring and procedural gates."""

from utils.text_converter import load_ignore_artifacts


def get_system_prompt() -> str:
    """Get the procedural system prompt for LLM Rubric V2 evaluation.
    
    Returns:
        Complete system prompt with embedded ignore artifacts list
    """
    ignore_artifacts = load_ignore_artifacts()
    
    return f"""You are grading AI accessibility of a single chunk for RAG. Prioritize self‑containment, structure, and focus over expertise.

Dimensions (0–100 each):
- standalone: comprehensible without external context
- one_idea: single clear focus, no topic drift
- structure: scannable (paragraphs/lists/tables/code as needed)
- right_size: appropriate scope (target 200–450 tokens)

Barriers (detect & record evidence spans):
- vague_refs → standalone ≤ 40
- wall_of_text → structure ≤ 35
- topic_confusion → one_idea ≤ 35
- misleading_headers (record but apply via recommendations; affects overall narrative)
- jargon (excessive undefined terms lowers standalone by 5–15 depending on severity)

Scoring:
1) Set initial sub-scores.
2) Apply gates/penalties per barriers.
3) overall = round(0.4*standalone + 0.3*structure + 0.2*one_idea + 0.1*right_size)
4) passing = overall ≥ cfg.evaluation.thresholds.llm_rubric

Output strictly follows the response schema. Ignore standard web artifacts (see below).

{ignore_artifacts}"""


def create_user_prompt(heading: str, text: str) -> str:
    """Create the user prompt for LLM Rubric evaluation.
    
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


# For reference: Dimensional weights used in calculation
DIMENSION_WEIGHTS = {
    "standalone": 0.4,
    "structure": 0.3,
    "one_idea": 0.2,
    "right_size": 0.1
}

# For reference: Barrier gate applications
BARRIER_APPLICATIONS = {
    "vague_refs": {
        "target_dimension": "standalone",
        "max_allowed": 40,
        "trigger": "detected"
    },
    "wall_of_text": {
        "target_dimension": "structure",
        "max_allowed": 35,
        "trigger": "detected"
    },
    "topic_confusion": {
        "target_dimension": "one_idea", 
        "max_allowed": 35,
        "trigger": "detected"
    },
    "misleading_headers": {
        "target_dimension": "recommendations",
        "effect": "narrative_impact",
        "trigger": "detected"
    },
    "jargon": {
        "target_dimension": "standalone",
        "effect": "penalty_range",
        "penalty_min": 5,
        "penalty_max": 15,
        "trigger": "severity_based"
    }
}

# Target token range for right_size scoring
TARGET_TOKEN_RANGE = {
    "min": 200,
    "max": 450,
    "ideal": 325  # Middle of range
}