"""Query-Answer V2 evaluator with structured penalties and algorithmic consistency."""

import time
from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator_v2 import BaseStructuredEvaluatorV2
from ..base.models import V2EvaluationMetadata
from .models import QueryAnswerEval, QueryAnswerMarkdownResult, QUALITY_GATES
from .prompts import get_system_prompt, create_user_prompt


class QueryAnswerEvaluatorV2(BaseStructuredEvaluatorV2):
    """V2 Query-Answer evaluator with algorithmic consistency and structured penalties."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Query-Answer Completeness"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.25
    
    def _get_config_key(self) -> str:
        """Configuration key for model overrides and thresholds."""
        return "query_answer"
    
    def __init__(self, **kwargs):
        """Initialize the Query-Answer V2 evaluator."""
        super().__init__(**kwargs)
        logger.info(f"{self.evaluator_name} V2 initialized with threshold {self.passing_threshold}")
    
    def _apply_quality_gates(self, provisional_score: int, penalties: List[Any]) -> tuple[int, List[str]]:
        """Apply quality gates based on detected barriers.
        
        Args:
            provisional_score: Score before quality gates
            penalties: List of detected penalties
            
        Returns:
            Tuple of (final_score, caps_applied)
        """
        caps_applied = []
        min_allowed_score = 100  # Start with no cap
        
        # Check each penalty for gate triggers
        for penalty in penalties:
            barrier = penalty.barrier if hasattr(penalty, 'barrier') else penalty.get('barrier')
            severity = penalty.severity if hasattr(penalty, 'severity') else penalty.get('severity')
            
            # Multiple vague references gate
            if barrier == "vague_refs" and severity in ["moderate", "severe"]:
                min_allowed_score = min(min_allowed_score, QUALITY_GATES["multiple_vague_references"]["max_score"])
                if "multiple_vague_references" not in caps_applied:
                    caps_applied.append("multiple_vague_references")
            
            # Misleading headers gate
            if barrier == "misleading_headers" and severity in ["moderate", "severe"]:
                min_allowed_score = min(min_allowed_score, QUALITY_GATES["misleading_headers"]["max_score"])
                if "misleading_headers" not in caps_applied:
                    caps_applied.append("misleading_headers")
            
            # Wall of text gate
            if barrier == "wall_of_text" and severity in ["moderate", "severe"]:
                min_allowed_score = min(min_allowed_score, QUALITY_GATES["wall_of_text"]["max_score"])
                if "wall_of_text" not in caps_applied:
                    caps_applied.append("wall_of_text")
            
            # Mixed unrelated topics gate  
            if barrier == "topic_confusion" and severity in ["moderate", "severe"]:
                min_allowed_score = min(min_allowed_score, QUALITY_GATES["mixed_unrelated_topics"]["max_score"])
                if "mixed_unrelated_topics" not in caps_applied:
                    caps_applied.append("mixed_unrelated_topics")
        
        final_score = min(provisional_score, min_allowed_score)
        
        return final_score, caps_applied
    
    def _create_markdown_result(self, machine_result: QueryAnswerEval) -> QueryAnswerMarkdownResult:
        """Convert machine result to markdown-compatible format.
        
        Args:
            machine_result: Structured evaluation result
            
        Returns:
            Markdown-compatible result
        """
        return QueryAnswerMarkdownResult(
            evaluator_name=self.evaluator_name,
            overall_score=machine_result.overall_score,
            overall_assessment=machine_result.overall_assessment,
            strengths=machine_result.strengths,
            issues=machine_result.issues,
            recommendations=machine_result.recommendations,
            passing=machine_result.passing
        )
    
    def _create_fallback_result(self, error_msg: str, chunk_text: str) -> QueryAnswerEval:
        """Create a fallback result when evaluation fails.
        
        Args:
            error_msg: Error message explaining the failure
            chunk_text: Original chunk text for context
            
        Returns:
            Minimal QueryAnswerEval result
        """
        return QueryAnswerEval(
            chunk_type="general",
            likely_queries=["Error: Could not analyze queries"],
            penalties=[],
            penalties_total=0,
            quality_caps_applied=[],
            base_score=100,
            provisional_score=0,
            final_score=0,
            overall_score=0,
            overall_assessment=f"Evaluation failed: {error_msg}",
            strengths=[],
            issues=[f"Technical evaluation failure: {error_msg}"],
            recommendations=["Retry evaluation or check chunk content format"],
            passing=False
        )
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[List[str]] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously evaluate chunk using V2 Query-Answer algorithm.
        
        Args:
            query: Optional query (not used directly)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with V2 structured feedback
        """
        start_time = time.time()
        
        # Extract chunk information
        chunk_text = kwargs.get('chunk_text', response)
        chunk_heading = kwargs.get('chunk_heading', '')
        
        if not chunk_text:
            return self.create_empty_result("No chunk text provided")
        
        # Prepare text with V2 enhancements
        processed_text, text_metadata = self.prepare_chunk_text(chunk_text)
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": create_user_prompt(chunk_heading, processed_text)}
        ]
        
        # Get structured output from OpenAI
        retry_count = 0
        machine_result = await self.parse_structured_output(
            response_model=QueryAnswerEval,
            messages=messages
        )
        
        if not machine_result:
            logger.error(f"{self.evaluator_name} V2: Failed to get structured evaluation")
            machine_result = self._create_fallback_result(
                "OpenAI API call failed after retries", 
                processed_text
            )
            retry_count = 2  # Indicate max retries were used
        
        # Validate and fix the result if needed
        if not self.validate_evaluation_result(machine_result):
            logger.warning(f"{self.evaluator_name} V2: Invalid result, creating fallback")
            machine_result = self._create_fallback_result(
                "Invalid structured output received",
                processed_text  
            )
        
        # Ensure passing threshold is correct
        machine_result.passing = self.apply_passing_threshold(machine_result.overall_score)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Create evaluation metadata
        metadata = V2EvaluationMetadata(
            model_used=self.model,
            chunk_char_count=text_metadata.get("char_count", 0),
            chunk_word_count=text_metadata.get("word_count", 0),
            was_truncated=text_metadata.get("was_truncated", False),
            processing_time_ms=processing_time,
            retry_count=retry_count,
            config_threshold=self.passing_threshold
        )
        
        # Create markdown result for human consumption
        markdown_result = self._create_markdown_result(machine_result)
        
        # Create LlamaIndex-compatible result
        chunk_preview = processed_text[:200] + "..." if len(processed_text) > 200 else processed_text
        
        return EvaluationResult(
            query="",  # Not used in this context
            response=chunk_preview,
            passing=machine_result.passing,
            score=machine_result.overall_score / 100,  # Normalize to 0-1
            feedback=markdown_result.as_markdown()
        )
    
    # get_detailed_result method removed - evaluators now return QueryAnswerEval directly