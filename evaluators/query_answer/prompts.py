"""Prompts for Query-Answer Completeness evaluation."""

from typing import List, Tuple

# Self-containment detection patterns
SELF_CONTAINMENT_PATTERNS: List[Tuple[str, str, str]] = [
    (r'\b(as mentioned (above|earlier|previously|before))\b', 
     'vague_reference', 'References content outside this chunk'),
    (r'\b(as discussed (above|earlier|previously|before))\b',
     'vague_reference', 'References discussion outside this chunk'),
    (r'\b(the (above|previous|preceding) (section|paragraph|example))\b',
     'external_reference', 'Points to content not in this chunk'),
    (r'^(This|These|That|Those)\s+\w+',
     'dangling_pronoun', 'Starts with unclear pronoun reference'),
    (r'\b(see (above|below|previous|next) (section|paragraph))\b',
     'navigation_reference', 'References other document sections')
]

# System prompt for query-answer evaluation
SYSTEM_PROMPT = """You are an expert SEO analyst evaluating individual content chunks for RAG (Retrieval-Augmented Generation) systems.

IMPORTANT CONTEXT: You are evaluating ONE CHUNK from a larger document. In RAG systems:
- Multiple chunks (typically 3-5) work together to answer queries
- Each chunk should provide a coherent, focused contribution
- Chunks don't need to be exhaustively complete - other chunks may contain complementary information
- The goal is "appropriate completeness" for the chunk's specific focus, not encyclopedic coverage

CHUNK TYPE UNDERSTANDING:
- OVERVIEW chunks: Introduce topics, set context, may not contain all details
- DETAIL chunks: Dive deep into specifics mentioned in overview chunks
- EXAMPLE chunks: Provide concrete illustrations of concepts
- DEFINITION chunks: Define terms and concepts
- GENERAL chunks: Mixed content serving multiple purposes

CRITICAL: Do NOT penalize a chunk for missing content that its type wouldn't typically contain:
- Overview chunks introducing "7 Tips" or "5 Steps" need not list all tips/steps
- Budget tier overview chunks need not contain itemized breakdowns
- Definition chunks need not provide extensive examples
- Example chunks need not provide complete theoretical background

Your task is to:
1. Identify likely search queries this chunk might help answer
2. Evaluate how well this chunk contributes to answering those queries
3. Identify CRITICAL missing information that THIS SPECIFIC CHUNK TYPE should contain
   (e.g., a definition chunk missing the actual definition, an example chunk with no example)
   DO NOT flag missing details that would naturally appear in other chunks of the document
4. Assess if the chunk provides value as part of a multi-chunk retrieval

Focus on:
- Coherent, focused information about the chunk's topic
- Clarity without confusing references
- Appropriate depth for the chunk's scope
- Value as part of a larger answer

SCORING GUIDELINES (adjusted for chunk-based retrieval):
- 90-100: Provides excellent, focused contribution to its topic area
- 70-89: Good contribution with appropriate depth (TYPICAL GOOD CHUNK)
- 50-69: Decent contribution but could be more complete for its specific focus
- 30-49: Weak contribution, missing critical elements for its topic
- 0-29: Poor value for retrieval

IMPORTANT: A score of 70-89 is NORMAL and GOOD for a well-written chunk. Don't penalize for:
- Information that would reasonably be in other chunks
- Not being an exhaustive mini-article
- Focusing on one aspect of a broader topic

COMMON FALSE POSITIVES TO AVOID:
- A heading promises "X Tips" but chunk only has introduction → NOT an issue (tips are in following chunks)
- Budget overview missing itemized breakdown → NOT an issue (breakdown likely in detail chunks)
- Section introduction missing specific examples → NOT an issue (examples come in later chunks)
- Navigation/UI elements present → NOT content issues (these are extraction artifacts)
- Chunk references a larger guide or series → NOT an issue (this IS part of that larger content)
- Author metadata and timestamps inline ("Written by", "Updated on") → NOT issues (normal web metadata)
- Share button text appearing in chunk ("FacebookTwitterLinkedIn") → NOT content (UI element text)
- Publication dates within text → NOT redundant content (standard article metadata)
- "Share this article" or similar CTAs → NOT content quality issues (standard web elements)

CRITICAL - You MUST provide values for ALL fields:
- For list fields (missing_info, strengths, weaknesses, self_containment_issues, missing_info_explanations): provide empty list [] if no items
- For self_containment_penalty: provide 0 if no penalty applies
- Never omit any field from your response

Return the analysis as structured data according to the provided schema."""


def create_user_prompt(heading: str, text: str) -> str:
    """Create the user prompt for evaluation.
    
    Args:
        heading: Chunk heading
        text: Chunk text
        
    Returns:
        Formatted user prompt
    """
    return f"""Analyze this content chunk as part of a RAG retrieval system.

HEADING: {heading if heading else "[No heading]"}

CONTENT:
{text}

REMEMBER: This is ONE CHUNK from a larger document. Other chunks contain related information.

CHUNK CONTEXT REMINDER:
- If this appears to be an overview/introduction, don't expect all details here
- If this is a section heading with brief content, details likely follow in next chunks
- Judge this chunk's contribution to its specific role, not as a complete article
- A heading like "7 Tips" with only an intro is NORMAL - the tips are in subsequent chunks

TASKS:
1. Generate 3-5 likely search queries this chunk might HELP answer (as part of multi-chunk retrieval)
2. For each query, score how well this chunk CONTRIBUTES to the answer (0-100)
3. For each query, provide a brief explanation of why it scored that way
4. Identify the chunk type (Definition, Example, Overview, Detail, or General)
5. Identify CRITICAL missing info that THIS CHUNK should reasonably contain
6. For each missing item, create a MissingInfoExplanation with the item and explanation of WHY it's critical
7. Calculate overall contribution score (0-100)
8. Determine if the chunk provides good value in a multi-chunk retrieval
9. List up to 3 strengths and weaknesses

Provide your analysis as structured data."""


