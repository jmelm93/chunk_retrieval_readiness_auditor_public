"""Prompts for Structure Quality V3 evaluator with chain-of-thought field ordering."""

from utils.text_converter import load_ignore_artifacts


def get_system_prompt() -> str:
    """Get the procedural system prompt for Structure Quality V3 evaluation.
    
    V3 changes: Field order optimized for chain-of-thought reasoning.
    Issues identified first to build context for scoring.
    
    Returns:
        Complete system prompt with embedded ignore artifacts list
    """
    ignore_artifacts = load_ignore_artifacts()
    
    return f"""Evaluate structural quality of extracted web content for RAG. You cannot restructure HTML; judge content as received.

Structural Elements to Evaluate:
- Heading: Specificity and accuracy
- Paragraphs: Appropriate sizing, avoid walls of text
- Lists: Used where appropriate for enumeration
- Tables: Used for tabular data presentation
- Code: Properly formatted if present
- Flow: Logical intro → body → wrap-up progression

Algorithm (follow this exact order):

STEP 1 - IDENTIFY ISSUES (builds context):
A. Check each structural element and create issues list:
   For each problem found:
   - Set barrier_type (e.g., "poor_heading", "wall_of_text", "missing_lists", "poor_flow")
   - Assign severity: minor | moderate | severe
   - Write clear description of the structural problem
   - Include evidence excerpt showing the issue
   Order issues by severity (severe → moderate → minor)

STEP 2 - IDENTIFY STRENGTHS:
B. List 2-4 structural strengths (clear headings, good formatting, logical flow, etc.)

STEP 3 - SYNTHESIZE ASSESSMENT:
C. Write overall assessment (2-4 sentences) about structural quality for RAG

STEP 4 - PROVIDE RECOMMENDATIONS:
D. List 2-3 specific structural improvements

STEP 5 - CALCULATE SCORE (informed by analysis):
E. Apply scoring based on structural issues:
   - Start at 100
   - Deduct: minor -5, moderate -10, severe -15 per issue
   - Floor at 10

STEP 6 - DETERMINE PASSING:
F. Set passing = true if score ≥ threshold (typically 70)

Structural Issue Guidelines:

HEADING QUALITY:
- Minor: Slightly vague but mostly accurate
- Moderate: Generic or somewhat misleading
- Severe: Very vague, misleading, or completely inaccurate

PARAGRAPH STRUCTURE:
- Minor: Slightly long paragraphs or minor break issues
- Moderate: Some walls of text or poor paragraph breaks
- Severe: Massive walls of text, no paragraph structure

LIST USAGE:
- Minor: Minor formatting issues or slight missed opportunities
- Moderate: Some missed list opportunities or formatting problems
- Severe: Major missed opportunities, poor list structure

TABLE USAGE:
- Minor: Minor formatting issues or slight missed opportunities
- Moderate: Some missed table opportunities or formatting problems
- Severe: Major missed opportunities, data poorly presented

CODE FORMATTING:
- Minor: Minor formatting inconsistencies
- Moderate: Some code poorly formatted or unclear
- Severe: Code examples poorly formatted, unclear, or missing proper blocks

CONTENT FLOW:
- Minor: Slight flow issues but mostly logical
- Moderate: Some organizational problems or abrupt transitions
- Severe: Poor organization, confusing flow, major structural problems

Rules:
- Judge structure as received (cannot restructure HTML)
- Build reasoning progressively: issues → assessment → score
- Focus on structural quality for AI retrieval
- Ignore standard web extraction artifacts (see below)
- Provide structured data per schema

{ignore_artifacts}"""


def create_user_prompt(heading: str, text_or_html: str) -> str:
    """Create the user prompt for Structure Quality evaluation.
    
    Args:
        heading: Chunk heading or "[No heading]"
        text_or_html: Chunk content (may include HTML for structure analysis)
        
    Returns:
        Formatted user prompt
    """
    heading_display = heading if heading and heading.strip() else "[No heading]"
    
    return f"""HEADING: {heading_display}

CONTENT:
{text_or_html}"""


# Reference constants for evaluator logic
STRUCTURAL_CATEGORIES = [
    "heading",
    "paragraphs",
    "lists",
    "tables", 
    "code",
    "flow"
]

SEVERITY_POINTS = {
    "minor": 5,
    "moderate": 10,
    "severe": 15
}