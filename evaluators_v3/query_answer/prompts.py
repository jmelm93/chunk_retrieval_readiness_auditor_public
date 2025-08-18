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
     * Minor: Small imperfections that don't block retrieval (slight vagueness, minor formatting issues)
     * Moderate: Noticeable problems but content still usable (some unclear refs, structural issues)
     * Severe: Significant barriers to retrieval (major confusion, contradictions, misleading content)
   - Write clear description
   - Include evidence excerpt (optional, max 100 chars)
   Order issues by severity (severe → moderate → minor)
   
   CALIBRATION GUIDE:
   - Excellent content (85-100): 0-1 minor issues max. Technical complexity ≠ confusion
   - Good content (70-85): 1-2 minor issues, maybe 1 moderate
   - Medium content (50-70): 2-3 issues total, mix of minor/moderate
   - Poor content (30-50): Multiple moderate issues or 1+ severe
   - Very poor (10-30): Multiple severe issues or many moderate issues
   Note: Be appropriately strict with obviously weak content, lenient with strong content

STEP 2 - IDENTIFY STRENGTHS:
B. List key strengths of the chunk

STEP 3 - SYNTHESIZE ASSESSMENT:
C. Write overall assessment based on issues and strengths found

STEP 4 - PROVIDE RECOMMENDATIONS:
D. For each improvement needed, create a structured recommendation. Order output by impact. Exclude low impact unless chunk scores >80

STEP 5 - CALCULATE SCORE (informed by prior analysis):
E. Apply scoring based on issues identified:
   - Start at 95 (excellent baseline)
   - Deduct: minor -5, moderate -10, severe -20 per issue
   - Apply caps:
     * Any severe issue → cap at 65
     * 3+ moderate issues → cap at 75
   - Perfect content: Score = 100 if no issues
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
    "multiple_vague_references": 50,
    "misleading_headers": 50,
    "wall_of_text": 45,
    "mixed_unrelated_topics": 50
}

PENALTY_POINTS = {
    "minor": 5,
    "moderate": 10,
    "severe": 20
}

BARRIER_TYPES = [
    "vague_refs",           # Vague cross-references 
    "misleading_headers",   # Header-content misalignment
    "wall_of_text",        # Poor text structure
    "jargon",              # Excessive undefined terminology
    "topic_confusion",     # Mixed unrelated topics
    "contradictions"       # Contradictory information
]