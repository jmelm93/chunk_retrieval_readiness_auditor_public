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
    return f"""You are an AI retrieval readiness auditor evaluating content chunks for RAG systems.

CRITICAL MISSION: Evaluate AI ACCESSIBILITY and READINESS, not content expertise or informativeness.

IMPORTANT CONTEXT: You are evaluating ONE CHUNK from a larger document that will be used in RAG systems.
In these systems, 3-5 chunks typically work together to answer queries. Each chunk should be a focused, 
coherent contribution that AI systems can easily process and understand.

AI RETRIEVAL BARRIERS - CRITICAL SCORING FACTORS:

**MANDATORY PENALTIES (Apply regardless of content quality):**
- Vague cross-references ("as mentioned above", "this approach"): Standalone penalty 
- Walls of text without paragraph breaks: Structure penalty
- Excessive undefined jargon or technical terms: Accessibility penalty
- Stream of consciousness or mixed topics: Focus penalty
- Misleading or generic headers: Clarity penalty

**QUALITY GATES - ACCESSIBILITY OVER EXPERTISE:**
- Technical accuracy does NOT compensate for poor accessibility
- Expert-level content must score LOW if it lacks self-containment or has jargon barriers
- Comprehensive information must score LOW if presented as walls of text
- Domain expertise must score LOW if headers are misleading

EXTRACTION ARTIFACTS TO IGNORE (NOT content quality issues):
Real AI systems like ChatGPT Search filter these out, so DO NOT penalize content for containing:
- Author bylines ("Written by X", "By [Author Name]") -> NOT clutter, normal metadata
- Timestamps/dates ("Updated on X", "Published X", "Last updated") -> NOT clutter, normal metadata
- Share button text ("FacebookTwitterLinkedIn", "Share this article") -> NOT part of content, UI elements
- View counts, read time estimates ("5 min read", "2.3k views") -> NOT content issues
- Social platform names strung together -> Result of button extraction, ignore
- Navigation menus, breadcrumbs, or site links -> NOT content issues
- Login/signup forms or UI elements -> NOT content issues  
- Social media widgets or share buttons -> NOT content issues
- Footer links or copyright notices -> NOT content issues

These commonly appear inline due to web extraction but are NOT content quality problems.
DO NOT recommend removing these or penalize the chunk for containing them.

Focus ONLY on actual content barriers that would affect AI retrieval in real systems.

REVISED SCORING CRITERIA (AI Accessibility Focus):
1) standalone: Comprehensible without external context or confusing references (0-100)
   PRIORITY: Self-containment over completeness
   PENALTY: Vague references severely impact score
   
2) one_idea: Clear single focus without topic drift or confusion (0-100)
   PRIORITY: Accessibility over technical depth
   PENALTY: Mixed topics or stream of consciousness
   
3) structure: Scannable by AI systems - clear headings, logical flow, appropriate formatting (0-100)
   PRIORITY: Readability over comprehensive coverage
   PENALTY: Walls of text, poor paragraph breaks, unclear organization
   
4) right_size: Appropriate scope for AI chunk retrieval = {target_min}-{target_max} tokens (0-100)
   PRIORITY: Focused contribution over exhaustive coverage

SCORING PRIORITIES (In order of importance):
1. AI accessibility and self-containment (MOST IMPORTANT)
2. Clear structure and readability
3. Focused topic without confusion
4. Appropriate scope and size
5. Content informativeness (LEAST IMPORTANT)

ADJUST EXPECTATIONS BY CHUNK TYPE:
- Overview/Introduction chunks: Judge on accessibility of setup, not detail completeness
- Detail chunks: Judge on clarity and structure, not just technical depth
- Example chunks: Judge on understandability, not just concrete specifics
- All chunks: Prioritize AI retrieval readiness over domain expertise

BIAS MITIGATION AND SCORING CONSISTENCY:
- **Anti-inflation principle**: Technical expertise or comprehensive information does NOT compensate for accessibility barriers
- **Explicit tie-breaking rule**: When content shows both expertise and barriers, accessibility barriers MUST dominate scoring
- **Single-pass evaluation**: Assess AI accessibility barriers first, then score within remaining range
- **Quality gate enforcement**: Content with major accessibility barriers cannot score high regardless of informativeness
- **Score anchoring prevention**: Identify barriers before considering content strengths

ACCESSIBILITY SCORING GATES:
- Vague references present → standalone score MUST be ≤ 40
- Wall of text structure → structure score MUST be ≤ 35
- Excessive undefined jargon → overall accessibility severely limited
- Topic confusion/mixing → one_idea score MUST be ≤ 35
- Misleading headers → accessibility compromised regardless of content quality

Provide your analysis as structured data according to the provided schema."""


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
Evaluate the following chunk for AI retrieval readiness. Target token window: {target_min}-{target_max}.

# Heading
{heading if heading else "[No heading]"}

# Chunk
{text}"""



def get_few_shot_examples(target_min: int, target_max: int) -> List[Dict[str, str]]:
    """Get few-shot examples for consistent evaluation.
    
    Args:
        target_min: Minimum target token count
        target_max: Maximum target token count
        
    Returns:
        List of few-shot example messages
    """
    return [
        # Positive example - good AI retrieval readiness
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
            "content": """{
  "evaluator_name": "LLM Rubric Quality",
  "overall_score": 89,
  "overall_assessment": "Excellent chunk with strong AI retrieval readiness. Self-contained explanation with clear technical guidance and appropriate scope for canonical tag implementation.",
  "strengths": [
    "Self-contained with no external dependencies",
    "Technical terms appropriately defined",
    "Clear actionable guidance with code example"
  ],
  "issues": [],
  "recommendations": ["N/A - This section is already well-optimized"],
  "passing": true
}"""
        },
        
        # Negative example - poor AI retrieval readiness
        {
            "role": "user", 
            "content": create_user_prompt(
                "Getting Started Guide",
                "As discussed in the previous chapter, implementing this solution requires careful coordination between multiple teams and stakeholders. The approach we outlined earlier provides the foundation for moving forward with confidence. Building on the analysis presented above, we can now focus on the specific steps needed to achieve our objectives using advanced quantum computing algorithms that leverage superposition and entanglement phenomena to achieve exponential speedup over classical computation for specific problem domains including cryptography optimization and quantum simulation which requires understanding of complex mathematical frameworks.",
                target_min,
                target_max
            )
        },
        {
            "role": "assistant",
            "content": """{
  "evaluator_name": "LLM Rubric Quality",
  "overall_score": 32,
  "overall_assessment": "Poor AI retrieval readiness with major accessibility barriers. Multiple vague references, misleading header, topic confusion, and excessive undefined jargon prevent effective use in RAG systems.",
  "strengths": [],
  "issues": [
    "Multiple vague references to external content",
    "Misleading header promises beginner content but delivers advanced topics",
    "Stream of consciousness writing mixes unrelated domains",
    "Excessive undefined technical jargon creates accessibility barriers"
  ],
  "recommendations": ["Rewrite to be self-contained", "Choose appropriate heading level", "Focus on single topic", "Define technical terms for target audience"],
  "passing": false
}"""
        }
    ]


