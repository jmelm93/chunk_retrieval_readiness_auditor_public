"""Prompts for Query-Answer V3 evaluator with chain-of-thought field ordering."""

from utils.text_converter import load_ignore_artifacts


def get_system_prompt() -> str:
    """Get the procedural system prompt for Query-Answer V3 evaluation.
    
    V3 changes: Field order optimized for chain-of-thought reasoning.
    Issues are analyzed first to build context before scoring.
    
    Returns:
        Complete system prompt with embedded ignore artifacts list
    """
    ignore_artifacts = load_ignore_artifacts()
    
    return f"""You are an AI retrieval auditor. Evaluate ONE content chunk for RAG retrievability (not human informativeness).

Objectives (priority order):
1) Detect retrieval barriers and identify issues
2) Ensure self-containment & clarity
3) Ensure header-content alignment
4) Ensure accessibility/readability
5) Consider informativeness last

Chunk types: overview | detail | example | definition | general

Algorithm (follow this exact order for chain-of-thought reasoning):

STEP 1 - IDENTIFY ISSUES (builds context for scoring):
A. Detect barriers and create issues list:
   For each barrier found (vague_refs, misleading_headers, wall_of_text, jargon, topic_confusion, contradictions):
   - Set barrier_type
   - Assign severity: minor | moderate | severe
   - Write clear description
   - Include evidence excerpt (optional, max 100 chars)
   Order issues by severity (severe → moderate → minor)

STEP 2 - IDENTIFY STRENGTHS:
B. List key strengths of the chunk

STEP 3 - SYNTHESIZE ASSESSMENT:
C. Write overall assessment based on issues and strengths found

STEP 4 - PROVIDE RECOMMENDATIONS:
D. List specific, actionable recommendations for improvement

STEP 5 - CALCULATE SCORE (informed by prior analysis):
E. Apply scoring based on issues identified:
   - Start at 80 (good baseline)
   - Deduct: minor -10, moderate -20, severe -30 per issue
   - Apply caps for severe issues:
     * Any severe issue → cap at 40
     * 2+ moderate issues → cap at 60
   - Can earn up to +20 bonus for excellence (no issues + strong points)
   - Final bounds: Max 100, Min 10

STEP 6 - DETERMINE PASSING:
F. Set passing = true if score ≥ threshold (typically 75)

STEP 7 - CHUNK METADATA:
G. Set chunk_type from: overview | detail | example | definition | general
H. List likely_queries this chunk could answer

Rules:
- Barriers dominate scoring; do not compensate with informativeness
- Build reasoning progressively: issues → assessment → score
- Ignore standard web extraction artifacts (see below)
- Provide structured data per schema

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


# Reference constants for evaluator logic
QUALITY_GATE_THRESHOLDS = {
    "multiple_vague_references": 40,
    "misleading_headers": 40,
    "wall_of_text": 35,
    "mixed_unrelated_topics": 40
}

PENALTY_POINTS = {
    "minor": 10,
    "moderate": 20,
    "severe": 30
}

BARRIER_TYPES = [
    "vague_refs",           # Vague cross-references 
    "misleading_headers",   # Header-content misalignment
    "wall_of_text",        # Poor text structure
    "jargon",              # Excessive undefined terminology
    "topic_confusion",     # Mixed unrelated topics
    "contradictions"       # Contradictory information
]