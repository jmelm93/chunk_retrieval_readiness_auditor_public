"""Query-Answer evaluator using Pydantic structured outputs."""

from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from ..base.models import StandardizedEvaluationResult
from .prompts import SYSTEM_PROMPT, create_user_prompt


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

        
        # Create messages for API call
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": create_user_prompt(chunk_heading, chunk_text)}
        ]
        
        # Get structured output from OpenAI
        result = await self.parse_structured_output(
            response_model=StandardizedEvaluationResult,
            messages=messages
        )

        if not result:
            return self.create_empty_result("Failed to get evaluation from OpenAI")
        
        # Update evaluator name and ensure passing threshold is correct
        result.evaluator_name = self.evaluator_name
        result.passing = result.overall_score >= 60
        
        # Create EvaluationResult for compatibility with LlamaIndex
        return EvaluationResult(
            query="",  # Not used in this context
            response=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
            passing=result.passing,
            score=result.overall_score / 100,  # Normalize to 0-1
            feedback=result.as_markdown()
        )