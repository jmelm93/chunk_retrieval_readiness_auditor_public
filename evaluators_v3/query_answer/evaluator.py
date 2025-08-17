"""Query-Answer V3 evaluator with simplified architecture."""

import time
from typing import Optional
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluatorV3
from .models import QueryAnswerResult
from .prompts import get_system_prompt, create_user_prompt, QUALITY_GATE_THRESHOLDS


class QueryAnswerEvaluatorV3(BaseStructuredEvaluatorV3):
    """V3 Query-Answer evaluator with simplified scoring logic."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Query-Answer Completeness"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.25
    
    def _get_config_key(self) -> str:
        """Configuration key for this evaluator."""
        return "query_answer"
    
    def __init__(self, **kwargs):
        """Initialize the Query-Answer V3 evaluator."""
        super().__init__(**kwargs)
        logger.info(f"{self.evaluator_name} V3 initialized with threshold {self.passing_threshold}")
    
    def _apply_quality_gates(self, score: int, result: QueryAnswerResult) -> int:
        """Apply quality gates based on detected issues.
        
        V3: Simplified logic that works directly with Issue objects.
        
        Args:
            score: Current score
            result: Evaluation result with issues
            
        Returns:
            Score after applying quality caps
        """
        min_allowed_score = 100  # Start with no cap
        
        # Check issues for gate triggers
        for issue in result.issues:
            # Multiple vague references gate
            if issue.barrier_type == "vague_refs" and issue.severity in ["moderate", "severe"]:
                min_allowed_score = min(min_allowed_score, QUALITY_GATE_THRESHOLDS["multiple_vague_references"])
            
            # Misleading headers gate
            elif issue.barrier_type == "misleading_headers" and issue.severity in ["moderate", "severe"]:
                min_allowed_score = min(min_allowed_score, QUALITY_GATE_THRESHOLDS["misleading_headers"])
            
            # Wall of text gate
            elif issue.barrier_type == "wall_of_text" and issue.severity in ["moderate", "severe"]:
                min_allowed_score = min(min_allowed_score, QUALITY_GATE_THRESHOLDS["wall_of_text"])
            
            # Mixed topics gate
            elif issue.barrier_type == "topic_confusion" and issue.severity in ["moderate", "severe"]:
                min_allowed_score = min(min_allowed_score, QUALITY_GATE_THRESHOLDS["mixed_unrelated_topics"])
        
        return min(score, min_allowed_score)
    
    def _calculate_final_score(self, result: QueryAnswerResult) -> int:
        """Calculate final score from issues with quality gates.
        
        Args:
            result: Evaluation result with issues
            
        Returns:
            Final score after penalties and quality gates
        """
        # Calculate base score from issues
        score = self.calculate_score_from_issues(result.issues)
        
        # Apply quality gates
        score = self._apply_quality_gates(score, result)
        
        return score
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[list] = None,
                        **kwargs) -> EvaluationResult:
        """Evaluate chunk for query-answer completeness.
        
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
                response_model=QueryAnswerResult,
                messages=messages,
                max_retries=2
            )
            
            if not result:
                logger.error(f"{self.evaluator_name}: Failed to parse structured output")
                return self.create_empty_result("Failed to parse evaluation")
            
            # V3: Score is already calculated by the model following our prompts
            # But we can verify/adjust if needed
            if result.score == 0 and result.issues:
                # Model might have returned 0, recalculate
                result.score = self._calculate_final_score(result)
            
            # Ensure passing status is correct
            result.passing = result.score >= self.passing_threshold
            
            # Log evaluation time
            eval_time = time.time() - start_time
            logger.debug(f"{self.evaluator_name}: Evaluated in {eval_time:.2f}s, score: {result.score}")
            
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