"""Prompts for LLM Rubric V3 evaluator with chain-of-thought field ordering."""

from utils.text_converter import load_ignore_artifacts


def get_system_prompt() -> str:
    """Get the procedural system prompt for LLM Rubric V3 evaluation.
    
    V3 changes: Field order optimized for chain-of-thought reasoning.
    Issues identified first to build context for scoring.
    
    Returns:
        Complete system prompt with embedded ignore artifacts list
    """
    ignore_artifacts = load_ignore_artifacts()
    
    return f"""Grade AI accessibility of a single chunk for RAG retrieval. Follow exact order for chain-of-thought reasoning.

Quality Dimensions:
- Standalone: Comprehensible without external context (40% weight)
- Structure: Scannable with clear formatting (30% weight)  
- One Idea: Single clear focus, no topic drift (20% weight)
- Right Size: Appropriate scope, 200-450 tokens ideal (10% weight)

Algorithm (follow this exact order):

STEP 1 - IDENTIFY ISSUES (builds context):
A. Detect barriers and create issues list:
   Common barriers:
   - vague_refs: Unclear references requiring external context
   - wall_of_text: Poor structure, hard to scan
   - topic_confusion: Multiple unrelated topics
   - misleading_headers: Header doesn't match content
   - jargon: Excessive undefined technical terms
   - too_short: Under 100 tokens
   - too_long: Over 600 tokens
   For each issue: set barrier_type, severity (minor/moderate/severe), description, evidence

STEP 2 - IDENTIFY STRENGTHS:
B. List 2-4 strengths related to AI accessibility (clear structure, self-contained, focused topic, etc.)

STEP 3 - SYNTHESIZE ASSESSMENT:
C. Write overall assessment (2-4 sentences) about chunk's AI retrieval readiness

STEP 4 - PROVIDE RECOMMENDATIONS:
D. List 2-3 specific improvements for AI accessibility

STEP 5 - CALCULATE SCORE (informed by analysis):
E. Apply scoring based on issues and dimensional analysis:
   - Start at 100
   - Deduct: minor -5, moderate -10, severe -15 per issue
   - Apply barrier gates:
     * vague_refs detected → cap standalone dimension at 40
     * wall_of_text → cap structure dimension at 35
     * topic_confusion → cap one_idea dimension at 35
   - Weight dimensions: 40% standalone + 30% structure + 20% one_idea + 10% right_size
   - Floor at 10

STEP 6 - DETERMINE PASSING:
F. Set passing = true if score ≥ threshold (typically 70)

Rules:
- Prioritize self-containment and structure over expertise
- Build reasoning progressively: issues → assessment → score
- Focus on AI retrievability, not human readability
- Ignore standard web extraction artifacts (see below)
- Provide structured data per schema

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


# Reference constants for evaluator logic
DIMENSION_WEIGHTS = {
    "standalone": 0.4,
    "structure": 0.3,
    "one_idea": 0.2,
    "right_size": 0.1
}

BARRIER_GATES = {
    "vague_refs": {"dimension": "standalone", "max_score": 40},
    "wall_of_text": {"dimension": "structure", "max_score": 35},
    "topic_confusion": {"dimension": "one_idea", "max_score": 35}
}

TARGET_TOKEN_RANGE = {
    "min": 200,
    "max": 450,
    "ideal": 325
}