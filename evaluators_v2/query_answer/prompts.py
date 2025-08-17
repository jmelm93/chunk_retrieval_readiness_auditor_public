"""Prompts for Query-Answer V2 evaluator with procedural algorithm and shared ignore list."""

from utils.text_converter import load_ignore_artifacts


def get_system_prompt() -> str:
    """Get the procedural system prompt for Query-Answer V2 evaluation.
    
    Returns:
        Complete system prompt with embedded ignore artifacts list
    """
    ignore_artifacts = load_ignore_artifacts()
    
    return f"""You are an AI retrieval auditor. Evaluate ONE content chunk for RAG retrievability (not human informativeness).

Objectives (priority order):
1) Detect retrieval barriers and assign penalties.
2) Ensure self‑containment & clarity.
3) Ensure header–content alignment.
4) Ensure accessibility/readability.
5) Consider informativeness last.

Chunk types: overview | detail | example | definition | general.

Algorithm (follow exactly):
A. Classify chunk_type from the list above.
B. List 3–8 likely user queries this chunk could answer.
C. Detect barriers and assign one severity each:
   - Vague cross-references
   - Misleading headers
   - Wall-of-text
   - Excessive jargon
   - Topic confusion
   - Contradictions
   Severity → penalty points: Minor −5, Moderate −10, Severe −15.
   Include 1–3 short evidence spans per barrier.
D. Compute quality cap (use the highest-severity trigger for each gate):
   - Multiple vague references → MAX 60
   - Misleading headers → MAX 65
   - Wall of text → MAX 55
   - Mixed unrelated topics → MAX 60
E. Score:
   base = 100
   penalties_total = sum of applied penalties (min 0, max 90)
   provisional = max(0, base − penalties_total)
   final_score = min(provisional, lowest_applicable_cap or 100)
F. Passing = final_score ≥ cfg.evaluation.thresholds.query_answer
G. Provide a concise assessment (2–4 sentences), then strengths, issues, and concrete chunk‑level recommendations.

Rules:
- Barriers dominate scoring; do not compensate with informativeness.
- Ignore standard web extraction artifacts (see below).
- Output strictly matches the response schema.

{ignore_artifacts}"""


def create_user_prompt(heading: str, text: str) -> str:
    """Create the minimal user prompt for evaluation.
    
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


# For reference: Quality gate thresholds used in the algorithm
QUALITY_GATE_THRESHOLDS = {
    "multiple_vague_references": 60,
    "misleading_headers": 65,
    "wall_of_text": 55,
    "mixed_unrelated_topics": 60
}

# For reference: Penalty severity mapping
PENALTY_SEVERITY_POINTS = {
    "minor": 5,
    "moderate": 10,
    "severe": 15
}

# For reference: Barrier types that can be detected
BARRIER_TYPES = [
    "vague_refs",           # Vague cross-references 
    "misleading_headers",   # Header-content misalignment
    "wall_of_text",        # Poor text structure
    "jargon",              # Excessive undefined terminology
    "topic_confusion",     # Mixed unrelated topics
    "contradictions"       # Contradictory information
]