"""Query-Answer evaluator using Pydantic structured outputs."""

import re
from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from .models import QueryAnswerResult, QueryEvaluation, ChunkType, SelfContainmentIssue


class QueryAnswerEvaluator(BaseStructuredEvaluator):
    """Evaluate if a chunk can completely answer potential queries using structured outputs."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Query-Answer Completeness"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.25
    
    def _get_config_key(self) -> str:
        """Configuration key for model overrides."""
        return "query_answer"
    
    def __init__(self, **kwargs):
        """Initialize the Query-Answer evaluator."""
        super().__init__(**kwargs)
        
        # Set truncation length from config or default
        if self.config and hasattr(self.config, 'evaluation'):
            self.truncation_length = self.config.evaluation.truncation_length
        else:
            self.truncation_length = 3000
    
    def _detect_self_containment_issues(self, text: str) -> List[SelfContainmentIssue]:
        """Detect self-containment issues in the text.
        
        Args:
            text: Chunk text to analyze
            
        Returns:
            List of detected self-containment issues
        """
        issues = []
        
        # Patterns to detect with their issue types
        patterns = [
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
        
        for pattern, issue_type, impact in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Extract context around the match
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end].strip()
                
                if start > 0:
                    context = "..." + context
                if end < len(text):
                    context = context + "..."
                
                issues.append(SelfContainmentIssue(
                    issue_type=issue_type,
                    example_text=context,
                    impact=impact
                ))
        
        # Check for key information front-loading
        first_150 = text[:150] if len(text) > 150 else text
        if not re.search(r'\b(\d+|percent|cost|price|value|data|fact|statistic|step|rule|requirement)\b',
                         first_150, re.IGNORECASE):
            issues.append(SelfContainmentIssue(
                issue_type='weak_opening',
                example_text=first_150[:50] + "...",
                impact='Lacks concrete information at the start'
            ))
        
        return issues[:5]  # Limit to top 5 issues
    
    def _calculate_penalty(self, issues: List[SelfContainmentIssue]) -> int:
        """Calculate penalty points for self-containment issues.
        
        Args:
            issues: List of detected issues
            
        Returns:
            Penalty points (0-15)
        """
        if not issues:
            return 0
        return min(len(issues) * 3, 15)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for evaluation."""
        return """You are an expert SEO analyst evaluating individual content chunks for RAG (Retrieval-Augmented Generation) systems.

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
    
    def _create_user_prompt(self, heading: str, text: str) -> str:
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
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[List[str]] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously evaluate if chunk answers potential queries.
        
        Args:
            query: Optional query (not used directly)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with query-answer completeness score
        """
        # Extract chunk information
        chunk_text = kwargs.get('chunk_text', response)
        chunk_heading = kwargs.get('chunk_heading', '')
        
        if not chunk_text:
            return self.create_empty_result("No chunk text provided")
        
        # Truncate if too long
        chunk_text = self.truncate_content(chunk_text, self.truncation_length)
        
        # Detect self-containment issues first
        self_containment_issues = self._detect_self_containment_issues(chunk_text)
        penalty = self._calculate_penalty(self_containment_issues)
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": self._create_user_prompt(chunk_heading, chunk_text)}
        ]
        
        # Get structured output from OpenAI
        result = await self.parse_structured_output(
            response_model=QueryAnswerResult,
            messages=messages
        )
        
        if not result:
            return self.create_empty_result("Failed to get evaluation from OpenAI")
        
        # Update result with detected issues
        result.self_containment_issues = self_containment_issues
        result.self_containment_penalty = penalty
        
        # Apply penalty to score
        adjusted_score = max(0, result.score - penalty)
        result.score = adjusted_score
        result.passing = adjusted_score >= 60
        
        # Update evaluator name
        result.evaluator_name = self.evaluator_name
        
        # Create EvaluationResult for compatibility with LlamaIndex
        import json
        return EvaluationResult(
            query=json.dumps(result.as_json_summary()),  # Store summary data as JSON string
            response=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
            passing=result.passing,
            score=result.score / 100,  # Normalize to 0-1
            feedback=result.as_markdown()
        )