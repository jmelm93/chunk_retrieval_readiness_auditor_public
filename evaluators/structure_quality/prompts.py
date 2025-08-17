"""Prompts for Structure Quality evaluation."""

from typing import Optional

# Configuration constants
MIN_HEADING_WORDS = 3
MAX_HEADING_WORDS = 10


# System prompt for structure quality evaluation
SYSTEM_PROMPT = """You are an expert at evaluating content structure for AI retrieval systems.

Your evaluation should:
1. Assess heading quality and accuracy
2. Evaluate structural element effectiveness
3. Judge readability and scanability
4. Identify structural issues and their impact
5. Provide actionable improvement suggestions

Be thorough but fair. Focus on structural aspects that affect AI chunk retrieval.
Remember that perfect HTML/Markdown isn't required - focus on whether the structure aids or hinders comprehension."""


def create_evaluation_prompt(chunk_text: str,
                            chunk_heading: str,
                            html_content: Optional[str] = None,
                            min_heading_words: int = 3,
                            max_heading_words: int = 10) -> str:
    """Create the evaluation prompt for structure quality assessment.
    
    Args:
        chunk_text: Plain text version of the chunk
        chunk_heading: The chunk's heading
        html_content: Optional HTML/formatted version
        min_heading_words: Minimum recommended heading words
        max_heading_words: Maximum recommended heading words
        
    Returns:
        Formatted prompt for evaluation
    """
    # Use HTML content if available, otherwise plain text
    content_to_analyze = html_content if html_content else chunk_text
    
    prompt = f"""You are evaluating the structural quality of a content chunk for AI retrieval systems.

CONTEXT:
- This chunk will be retrieved by AI systems to answer user queries
- Good structure aids both AI comprehension and information extraction
- Structure should enhance, not hinder, the content's value
- Consider this is web content that may have extraction artifacts

CHUNK HEADING: {chunk_heading if chunk_heading else "No heading provided"}

CHUNK CONTENT (may contain HTML/Markdown):
{content_to_analyze}

EVALUATION TASK:
1. Assess the heading quality (clarity, accuracy, specificity)
2. Evaluate structural elements (lists, tables, paragraphs, code blocks)
3. Judge readability and scanability for AI systems
4. Determine if formatting choices match content needs
5. Identify structural issues that hinder chunk quality

IMPORTANT CONSIDERATIONS:
- Headings should be specific and descriptive, not generic
- Lists and tables should be used when they enhance comprehension
- Dense walls of text are problematic for retrieval
- Clear introductory context improves chunk usability
- Logical flow and organization matter for coherence
- Inline artifacts (timestamps, share buttons) are NOT structural issues

STRUCTURAL ELEMENT GUIDELINES:
- Heading: Should accurately describe content ({min_heading_words}-{max_heading_words} words ideal)
- Lists: Effective for enumeration, steps, or multiple related items
- Tables: Best for comparative or structured data
- Paragraphs: Should be reasonably sized, not too long or too short
- Code blocks: Should be properly formatted if present

SCORING GUIDELINES:
- 80-100: Excellent structure that enhances content value and retrieval
- 60-79: Good structure with minor improvements needed
- 40-59: Moderate structural issues affecting usability
- 0-39: Poor structure that significantly hinders chunk quality

Focus on how structure affects AI chunk retrieval effectiveness."""
    
    return prompt

