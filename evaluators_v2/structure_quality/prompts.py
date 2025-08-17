"""Prompts for Structure Quality V2 evaluator with checklist approach and penalty system."""

from utils.text_converter import load_ignore_artifacts


def get_system_prompt() -> str:
    """Get the procedural system prompt for Structure Quality V2 evaluation.
    
    Returns:
        Complete system prompt with embedded ignore artifacts list
    """
    ignore_artifacts = load_ignore_artifacts()
    
    return f"""Evaluate structural quality of extracted web content for RAG. You cannot restructure HTML; judge content as received.

Checklist (rate each: none/minor/moderate/severe; map → 0/−5/−10/−15; include evidence spans):
- heading: specificity & accuracy
- paragraphs: sizing; avoid walls of text
- lists: used where appropriate
- tables: used where appropriate
- code: properly formatted if present
- flow: intro → body → wrap‑up

Score:
base = 100 − sum(penalties); clamp 0–100
passing = score ≥ cfg.evaluation.thresholds.structure_quality

Ignore standard web artifacts (see below). Output strictly follows schema.

Evaluation Guidelines:

HEADING QUALITY:
- Good: Specific, descriptive, accurately reflects content
- Minor issues: Slightly vague but mostly accurate
- Moderate issues: Generic or somewhat misleading
- Severe issues: Very vague, misleading, or completely inaccurate

PARAGRAPH STRUCTURE:
- Good: Appropriate length (2-5 sentences), clear breaks, logical grouping
- Minor issues: Slightly long paragraphs or minor break issues
- Moderate issues: Some walls of text or poor paragraph breaks
- Severe issues: Massive walls of text, no paragraph structure

LIST USAGE:
- Good: Lists used where appropriate, clear structure, proper formatting
- Minor issues: Minor formatting issues or slight missed opportunities
- Moderate issues: Some missed list opportunities or formatting problems
- Severe issues: Major missed opportunities, poor list structure

TABLE USAGE:
- Good: Tabular data properly formatted, clear headers, appropriate use
- Minor issues: Minor formatting issues or slight missed opportunities
- Moderate issues: Some missed table opportunities or formatting problems
- Severe issues: Major missed opportunities, data poorly presented

CODE FORMATTING:
- Good: Proper code blocks, clear examples, appropriate formatting
- Minor issues: Minor formatting inconsistencies
- Moderate issues: Some code poorly formatted or unclear
- Severe issues: Code examples poorly formatted, unclear, or missing proper blocks

CONTENT FLOW:
- Good: Clear intro → body → wrap-up, logical progression
- Minor issues: Slight flow issues but mostly logical
- Moderate issues: Some organizational problems or abrupt transitions
- Severe issues: Poor organization, confusing flow, major structural problems

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


# For reference: Structural categories and their evaluation criteria
EVALUATION_CRITERIA = {
    "heading": {
        "none": "Heading is specific, descriptive, and accurately reflects content",
        "minor": "Heading is slightly vague but mostly accurate (-5 points)",
        "moderate": "Heading is generic or somewhat misleading (-10 points)", 
        "severe": "Heading is very vague, misleading, or completely inaccurate (-15 points)"
    },
    "paragraphs": {
        "none": "Paragraphs are appropriately sized with clear breaks and logical grouping",
        "minor": "Slightly long paragraphs or minor break issues (-5 points)",
        "moderate": "Some walls of text or poor paragraph breaks (-10 points)",
        "severe": "Massive walls of text, no paragraph structure (-15 points)"
    },
    "lists": {
        "none": "Lists used appropriately with clear structure and proper formatting",
        "minor": "Minor formatting issues or slight missed opportunities (-5 points)",
        "moderate": "Some missed list opportunities or formatting problems (-10 points)",
        "severe": "Major missed opportunities, poor list structure (-15 points)"
    },
    "tables": {
        "none": "Tabular data properly formatted with clear headers where appropriate",
        "minor": "Minor formatting issues or slight missed opportunities (-5 points)",
        "moderate": "Some missed table opportunities or formatting problems (-10 points)",
        "severe": "Major missed opportunities, data poorly presented (-15 points)"
    },
    "code": {
        "none": "Code properly formatted in blocks with clear examples",
        "minor": "Minor formatting inconsistencies (-5 points)",
        "moderate": "Some code poorly formatted or unclear (-10 points)",
        "severe": "Code examples poorly formatted, unclear, or missing proper blocks (-15 points)"
    },
    "flow": {
        "none": "Clear intro → body → wrap-up with logical progression",
        "minor": "Slight flow issues but mostly logical (-5 points)",
        "moderate": "Some organizational problems or abrupt transitions (-10 points)",
        "severe": "Poor organization, confusing flow, major structural problems (-15 points)"
    }
}

# For reference: Point deductions by severity
SEVERITY_POINTS = {
    "none": 0,
    "minor": 5,
    "moderate": 10,
    "severe": 15
}