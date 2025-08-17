"""Entity Focus V3 evaluator with simplified architecture."""

import time
from typing import Optional
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluatorV3
from .models import EntityFocusResult
from .prompts import get_system_prompt, create_user_prompt


class EntityFocusEvaluatorV3(BaseStructuredEvaluatorV3):
    """V3 Entity Focus evaluator with simplified entity analysis."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Entity Focus & Coherence"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.25
    
    def _get_config_key(self) -> str:
        """Configuration key for this evaluator."""
        return "entity_focus"
    
    def __init__(self, **kwargs):
        """Initialize the Entity Focus V3 evaluator."""
        super().__init__(**kwargs)
        logger.info(f"{self.evaluator_name} V3 initialized with threshold {self.passing_threshold}")
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[list] = None,
                        **kwargs) -> EvaluationResult:
        """Evaluate chunk for entity focus and coherence.
        
        Args:
            query: Optional query (not used)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with evaluation outcome
        """
        start_time = time.time()
        
        # Extract chunk text and metadata
        chunk_text = response or ""
        chunk_metadata = kwargs.get("chunk_metadata", {})
        heading = chunk_metadata.get("heading", "")
        
        if not chunk_text:
            logger.warning(f"{self.evaluator_name}: No chunk text provided")
            return self.create_empty_result("No chunk text provided")
        
        # Prepare text for evaluation
        processed_text, text_metadata = self.prepare_chunk_text(chunk_text)
        
        try:
            # Create messages for OpenAI
            messages = [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": create_user_prompt(heading, processed_text)}
            ]
            
            # Parse structured output
            result = await self.parse_structured_output(
                response_model=EntityFocusResult,
                messages=messages,
                max_retries=2
            )
            
            if not result:
                logger.error(f"{self.evaluator_name}: Failed to parse structured output")
                return self.create_empty_result("Failed to parse evaluation")
            
            # V3: Score is calculated by the model following our prompts
            # Verify passing status
            result.passing = result.score >= self.passing_threshold
            
            # Log evaluation details
            eval_time = time.time() - start_time
            entity_count = len(result.primary_entities) if result.primary_entities else 0
            logger.debug(
                f"{self.evaluator_name}: Evaluated in {eval_time:.2f}s, "
                f"score: {result.score}, entities: {entity_count}"
            )
            
            # Return LlamaIndex-compatible result
            return EvaluationResult(
                query=query or "",
                response=chunk_text,
                passing=result.passing,
                score=result.score / 100.0,  # Convert to 0-1 scale
                feedback=result.to_markdown()
            )
            
        except Exception as e:
            logger.error(f"{self.evaluator_name}: Evaluation failed - {e}")
            return self.create_empty_result(f"Evaluation failed: {str(e)}")