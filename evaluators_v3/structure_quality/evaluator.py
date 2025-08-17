"""Structure Quality V3 evaluator using base model directly."""

import time
from typing import Optional
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluatorV3
from ..base.models import BaseEvaluationResult
from .prompts import get_system_prompt, create_user_prompt


class StructureQualityEvaluatorV3(BaseStructuredEvaluatorV3):
    """V3 Structure Quality evaluator with simplified structural analysis.
    
    Uses BaseEvaluationResult directly without extensions.
    """
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Structure Quality"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.25
    
    def _get_config_key(self) -> str:
        """Configuration key for this evaluator."""
        return "structure_quality"
    
    def __init__(self, **kwargs):
        """Initialize the Structure Quality V3 evaluator."""
        super().__init__(**kwargs)
        logger.info(f"{self.evaluator_name} V3 initialized with threshold {self.passing_threshold}")
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[list] = None,
                        **kwargs) -> EvaluationResult:
        """Evaluate chunk for structural quality.
        
        Args:
            query: Optional query (not used)
            response: The chunk text/HTML to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with evaluation outcome
        """
        start_time = time.time()
        
        # Extract chunk content and metadata
        chunk_content = response or ""
        chunk_metadata = kwargs.get("chunk_metadata", {})
        heading = chunk_metadata.get("heading", "")
        
        # V3: Can handle either text or HTML content
        # Use raw_html if available for better structure analysis
        if "raw_html" in chunk_metadata:
            chunk_content = chunk_metadata["raw_html"]
        
        if not chunk_content:
            logger.warning(f"{self.evaluator_name}: No chunk content provided")
            return self.create_empty_result("No chunk content provided")
        
        # Prepare content for evaluation
        processed_content, text_metadata = self.prepare_chunk_text(chunk_content)
        
        try:
            # Create messages for OpenAI
            messages = [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": create_user_prompt(heading, processed_content)}
            ]
            
            # Parse structured output - using base model directly
            result = await self.parse_structured_output(
                response_model=BaseEvaluationResult,
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
            issue_count = len(result.issues) if result.issues else 0
            logger.debug(
                f"{self.evaluator_name}: Evaluated in {eval_time:.2f}s, "
                f"score: {result.score}, structural issues: {issue_count}"
            )
            
            # Return LlamaIndex-compatible result
            return EvaluationResult(
                query=query or "",
                response=chunk_content,
                passing=result.passing,
                score=result.score / 100.0,  # Convert to 0-1 scale
                feedback=result.to_markdown()
            )
            
        except Exception as e:
            logger.error(f"{self.evaluator_name}: Evaluation failed - {e}")
            return self.create_empty_result(f"Evaluation failed: {str(e)}")