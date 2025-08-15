"""LLM Rubric evaluator using Pydantic structured outputs."""

from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from .models import LLMRubricResult, RubricScores, RubricJustifications, ContentFlag


class LLMRubricEvaluator(BaseStructuredEvaluator):
    """Evaluate chunks using LLM-based rubric scoring with structured outputs."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "LLM Rubric Quality"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.20
    
    def _get_config_key(self) -> str:
        """Configuration key for model overrides."""
        return "llm_rubric"
    
    def __init__(self, **kwargs):
        """Initialize the LLM Rubric evaluator."""
        super().__init__(**kwargs)
        
        # Set configuration parameters
        if self.config:
            if hasattr(self.config, 'chunking'):
                self.target_min = self.config.chunking.min_chunk_size
                self.target_max = self.config.chunking.max_chunk_size
            else:
                self.target_min = 200
                self.target_max = 450
            
            if hasattr(self.config, 'evaluation'):
                self.truncation_length = self.config.evaluation.truncation_length
            else:
                self.truncation_length = 3000
        else:
            self.target_min = 200
            self.target_max = 450
            self.truncation_length = 3000
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for rubric evaluation."""
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
4) right_size: Concise; assume ideal token window = {self.target_min}-{self.target_max}. Penalize if obviously too short/long.

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
    
    def _create_user_prompt(self, heading: str, text: str) -> str:
        """Create the user prompt for evaluation.
        
        Args:
            heading: Chunk heading
            text: Chunk text
            
        Returns:
            Formatted user prompt
        """
        return f"""# Instruction
Evaluate the following chunk for chunk-level retrieval readiness. Target token window: {self.target_min}-{self.target_max}.

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
    
    def _get_few_shot_examples(self) -> List[Dict[str, str]]:
        """Get few-shot examples for consistent evaluation."""
        return [
            {
                "role": "user",
                "content": self._create_user_prompt(
                    "Creating Canonical Tags for Duplicate URLs",
                    "A canonical tag tells search engines which URL is the master version when duplicates exist. Add `<link rel=\"canonical\" href=\"https://example.com/product\" />` to duplicate pages so signals consolidate to the preferred URL. Use canonicals when content is substantially similar; use `noindex` when a page should not appear in search at all."
                )
            },
            {
                "role": "assistant",
                "content": "I'll evaluate this chunk for retrieval readiness."
            }
        ]
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[List[str]] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously evaluate using LLM rubric.
        
        Args:
            query: Optional query (not used)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with LLM rubric score
        """
        # Extract chunk information
        chunk_text = kwargs.get('chunk_text', response)
        chunk_heading = kwargs.get('chunk_heading', '')
        
        if not chunk_text:
            return self.create_empty_result("No chunk text provided")
        
        # Truncate if too long
        chunk_text = self.truncate_content(chunk_text, self.truncation_length)
        
        # Create messages with few-shot examples
        messages = [
            {"role": "system", "content": self._get_system_prompt()}
        ]
        
        # Add few-shot examples for consistency
        messages.extend(self._get_few_shot_examples())
        
        # Add actual evaluation request
        messages.append({
            "role": "user",
            "content": self._create_user_prompt(chunk_heading, chunk_text)
        })
        
        # Get structured output from OpenAI
        result = await self.parse_structured_output(
            response_model=LLMRubricResult,
            messages=messages
        )
        
        if not result:
            return self.create_empty_result("Failed to get evaluation from OpenAI")
        
        # Calculate overall score
        overall_score = result.scores.average_score()
        result.score = int(overall_score)
        result.passing = overall_score >= 65
        result.evaluator_name = self.evaluator_name
        result.explanation = self._generate_explanation(result.scores)
        
        # Create EvaluationResult for compatibility
        import json
        return EvaluationResult(
            query=json.dumps(result.as_json_summary()),
            response=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
            passing=result.passing,
            score=result.score / 100,
            feedback=result.as_markdown()
        )
    
    def _generate_explanation(self, scores: RubricScores) -> str:
        """Generate overall explanation based on scores.
        
        Args:
            scores: Rubric scores
            
        Returns:
            Brief explanation of evaluation
        """
        avg = scores.average_score()
        
        # Identify strongest and weakest dimensions
        dimensions = {
            "standalone clarity": scores.standalone,
            "topic focus": scores.one_idea,
            "structure": scores.structure,
            "content size": scores.right_size
        }
        
        strongest = max(dimensions.items(), key=lambda x: x[1])
        weakest = min(dimensions.items(), key=lambda x: x[1])
        
        if avg >= 80:
            return f"Excellent chunk with strong {strongest[0]} ({strongest[1]}/100). Well-optimized for retrieval."
        elif avg >= 60:
            return f"Good chunk quality. Strong in {strongest[0]} but could improve {weakest[0]} ({weakest[1]}/100)."
        else:
            return f"Needs improvement, particularly in {weakest[0]} ({weakest[1]}/100). Multiple areas require attention."