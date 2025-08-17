"""LLM Rubric evaluator using Pydantic structured outputs."""

from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from ..base.models import StandardizedEvaluationResult
from .prompts import get_system_prompt, create_user_prompt, get_few_shot_examples


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
            {"role": "system", "content": get_system_prompt(self.target_min, self.target_max)}
        ]
        
        # Add few-shot examples for consistency
        messages.extend(get_few_shot_examples(self.target_min, self.target_max))
        
        # Add actual evaluation request
        messages.append({
            "role": "user",
            "content": create_user_prompt(chunk_heading, chunk_text, self.target_min, self.target_max)
        })
        
        # Get structured output from OpenAI
        result = await self.parse_structured_output(
            response_model=StandardizedEvaluationResult,
            messages=messages
        )
        
        if not result:
            return self.create_empty_result("Failed to get evaluation from OpenAI")
        
        # Update evaluator name and ensure passing threshold is correct
        result.evaluator_name = self.evaluator_name
        result.passing = result.overall_score >= 65
        
        # Create EvaluationResult for compatibility
        return EvaluationResult(
            query="",  # Not used in this context
            response=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
            passing=result.passing,
            score=result.overall_score / 100,  # Normalize to 0-1
            feedback=result.as_markdown()
        )
    
