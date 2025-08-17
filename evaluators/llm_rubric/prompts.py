"""Prompts for LLM Rubric evaluation."""

from typing import List, Dict

# Default configuration constants
TARGET_MIN = 200
TARGET_MAX = 450

def get_system_prompt(target_min: int, target_max: int) -> str:
    """Get the system prompt for rubric evaluation.
    
    Args:
        target_min: Minimum target token count
        target_max: Maximum target token count
    
    Returns:
        Formatted system prompt
    """
    return f"""You are a strict SEO chunk auditor evaluating naturally-occurring sections from web pages.

IMPORTANT CONTEXT: You are evaluating ONE CHUNK from a larger document that will be used in RAG systems.
In these systems, 3-5 chunks typically work together to answer queries. Each chunk should be a focused, 
coherent contribution rather than exhaustively complete.

You are evaluating header-based sections as they appear on the actual webpage. 
Navigation elements, login forms, social links, or other UI elements may be present due to how 
content is extracted from the web - these are NOT content quality issues.

Focus your evaluation on the actual content, NOT extraction artifacts. When you see:
- Navigation menus, breadcrumbs, or site links -> IGNORE, not a content issue
- Login/signup forms or UI elements -> IGNORE, not a content issue  
- Social media widgets or share buttons -> IGNORE, not a content issue
- Footer links or copyright notices -> IGNORE, not a content issue

INLINE EXTRACTION ARTIFACTS TO IGNORE:
- Author bylines ("Written by X", "By [Author Name]") -> NOT clutter, normal metadata
- Timestamps/dates ("Updated on X", "Published X", "Last updated") -> NOT clutter, normal metadata
- Share button text ("FacebookTwitterLinkedIn", "Share this article") -> NOT part of content, UI elements
- View counts, read time estimates ("5 min read", "2.3k views") -> NOT content issues
- Social platform names strung together -> Result of button extraction, ignore

These commonly appear inline due to web extraction but are NOT content quality problems.
DO NOT recommend removing these or penalize the chunk for containing them.
They are normal web page elements that appear in extracted text.

Only flag and recommend fixes for actual content problems that an author could address in their CMS.

Scoring criteria (0-100 each, integers):
1) standalone: Makes sense on its own without confusing forward/backward references.
   OK: Chunk introduces a topic without listing all details
   NOT OK: Chunk says "as mentioned above" without context
   Remember: Standalone means comprehensible, not exhaustive
2) one_idea: Single clear topic with minimal drift; early sentences set context. Remember: focused contribution, not exhaustive coverage.
3) structure: Clear heading, concise intro, uses semantic lists/tables when helpful.
4) right_size: Concise; assume ideal token window = {target_min}-{target_max}. Penalize if obviously too short/long.

ADJUST EXPECTATIONS BY CHUNK TYPE:
- Overview/Introduction chunks: Judge on clarity of setup, not detail completeness
- Detail chunks: Judge on depth and specificity
- Example chunks: Judge on concrete illustration quality
- Budget/tier chunks: Judge on appropriate level of detail for that tier's overview
- Don't penalize chunks for serving their specific role in the document

CRITICAL - You MUST provide values for ALL fields:
- For the flags field: provide empty list [] if no issues detected
- For each ContentFlag in flags: severity must be "low", "medium", or "high"
- Never omit any field from your response

Return your evaluation as structured data according to the provided schema."""


def create_user_prompt(heading: str, text: str, target_min: int, target_max: int) -> str:
    """Create the user prompt for evaluation.
    
    Args:
        heading: Chunk heading
        text: Chunk text
        target_min: Minimum target token count
        target_max: Maximum target token count
        
    Returns:
        Formatted user prompt
    """
    return f"""# Instruction
Evaluate the following chunk for chunk-level retrieval readiness. Target token window: {target_min}-{target_max}.

# Heading
{heading if heading else "[No heading]"}

# Chunk
{text}

# Tasks
1. Score each rubric dimension (0-100)
2. Provide brief justifications (1-2 sentences each)
3. Identify content quality issues/flags
4. Suggest an improved heading (3-8 words ideal)
5. Rewrite the lead paragraph for clarity (2-3 sentences)
6. Provide 1-3 concrete recommendations for improvement

CHUNK CONTEXT:
- If heading promises "X Tips" but only introduces them, that's NORMAL for an overview chunk
- Budget tier chunks don't need full breakdowns if they're tier overviews
- Judge based on the chunk's apparent role, not as a standalone article

Remember: Focus on actual content quality, not extraction artifacts."""


def get_few_shot_examples(target_min: int, target_max: int) -> List[Dict[str, str]]:
    """Get few-shot examples for consistent evaluation.
    
    Args:
        target_min: Minimum target token count
        target_max: Maximum target token count
        
    Returns:
        List of few-shot example messages
    """
    return [
        {
            "role": "user",
            "content": create_user_prompt(
                "Creating Canonical Tags for Duplicate URLs",
                "A canonical tag tells search engines which URL is the master version when duplicates exist. Add `<link rel=\"canonical\" href=\"https://example.com/product\" />` to duplicate pages so signals consolidate to the preferred URL. Use canonicals when content is substantially similar; use `noindex` when a page should not appear in search at all.",
                target_min,
                target_max
            )
        },
        {
            "role": "assistant",
            "content": "I'll evaluate this chunk for retrieval readiness."
        }
    ]


