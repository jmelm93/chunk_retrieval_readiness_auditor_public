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
{text}

# Critical AI Retrieval Assessment

**FIRST: Detect AI Accessibility Barriers**
1. Scan for vague references ("as mentioned above", "this method") that break self-containment
2. Check for walls of text without proper paragraph breaks or structure
3. Assess jargon density - are technical terms defined or accessible?
4. Look for topic confusion or stream of consciousness writing
5. Verify header accurately describes the content level and topic

**SECOND: Apply Accessibility-First Scoring**
- standalone: Penalize heavily for vague references, reward self-containment
- one_idea: Penalize topic mixing, reward clear focus accessible to AI systems
- structure: Penalize walls of text, reward scannable organization 
- right_size: Judge appropriateness for AI chunk retrieval scope

**REMEMBER**: Technical expertise does NOT excuse accessibility barriers.
Expert quantum physics content must score LOW if it has jargon barriers or vague references.

# Tasks
1. Calculate overall AI retrieval readiness score (0-100) prioritizing accessibility over informativeness
2. Provide clear assessment explaining the chunk's AI accessibility and quality
3. List key strengths for AI retrieval (determine appropriate number based on chunk quality)
4. List key issues affecting AI accessibility (determine appropriate number based on problems found)
5. Provide list of specific recommendations if score < 80, or ["N/A - This section is already well-optimized"] if score ≥ 80

CHUNK CONTEXT:
- If heading promises "X Tips" but only introduces them, that's NORMAL for an overview chunk
- Budget tier chunks don't need full breakdowns if they're tier overviews
- Judge based on AI accessibility for the chunk's role, not as a standalone article

Remember: Focus on AI retrieval barriers in actual content, ignore extraction artifacts like author bylines and social buttons.

Provide your analysis as structured data according to the provided schema."""

# 3. Score the 4 rubric dimensions in score_breakdown section:
#    - Standalone Clarity: How well it reads without context
#    - Topic Focus: Consistency and coherence of subject matter  
#    - Structure Quality: Organization and flow
#    - Content Size: Appropriateness for chunk retrieval


#   "score_breakdown": {
#     "Standalone Clarity": {"score": 88, "explanation": "Clear self-contained explanation with proper context"},
#     "Topic Focus": {"score": 92, "explanation": "Focused exclusively on canonical tags without topic drift"},
#     "Structure Quality": {"score": 85, "explanation": "Good logical flow, could benefit from better formatting"},
#     "Content Size": {"score": 90, "explanation": "Appropriate scope and length for the topic"}
#   },

#   "score_breakdown": {
#     "Standalone Clarity": {"score": 25, "explanation": "Severe vague reference issues break self-containment"},
#     "Topic Focus": {"score": 30, "explanation": "Mixes unrelated topics (project management and quantum physics)"},
#     "Structure Quality": {"score": 35, "explanation": "Poor organization with run-on sentences"},
#     "Content Size": {"score": 40, "explanation": "Appropriate length but wrong scope for 'Getting Started'"}
#   },

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


