"""LLM Rubric V2 evaluator with dimensional scoring and barrier gates."""

import time
from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator_v2 import BaseStructuredEvaluatorV2
from ..base.models import V2EvaluationMetadata, MarkdownResult
from .models import LLMRubricEval, BARRIER_GATES, DIMENSION_WEIGHTS
from .prompts import get_system_prompt, create_user_prompt


class LLMRubricEvaluatorV2(BaseStructuredEvaluatorV2):
    """V2 LLM Rubric evaluator with dimensional scoring and procedural gates."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "LLM Rubric Quality"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.30
    
    def _get_config_key(self) -> str:
        """Configuration key for model overrides and thresholds."""
        return "llm_rubric"
    
    def __init__(self, **kwargs):
        """Initialize the LLM Rubric V2 evaluator."""
        super().__init__(**kwargs)
        logger.info(f"{self.evaluator_name} V2 initialized with threshold {self.passing_threshold}")
    
    def _apply_barrier_gates(self, 
                            standalone: int, 
                            structure: int, 
                            one_idea: int, 
                            right_size: int,
                            evidence_spans: Dict[str, List[str]]) -> tuple[int, int, int, int, List[str]]:
        """Apply barrier gates to dimensional scores.
        
        Args:
            standalone: Initial standalone score
            structure: Initial structure score
            one_idea: Initial one_idea score
            right_size: Initial right_size score
            evidence_spans: Detected evidence spans by barrier type
            
        Returns:
            Tuple of (adjusted_standalone, adjusted_structure, adjusted_one_idea, adjusted_right_size, gates_triggered)
        """
        gates_triggered = []
        
        # Apply vague_refs gate to standalone
        if "vague_refs" in evidence_spans and evidence_spans["vague_refs"]:
            standalone = min(standalone, BARRIER_GATES["vague_refs"]["max_score"])
            gates_triggered.append("vague_refs")
        
        # Apply wall_of_text gate to structure
        if "wall_of_text" in evidence_spans and evidence_spans["wall_of_text"]:
            structure = min(structure, BARRIER_GATES["wall_of_text"]["max_score"])
            gates_triggered.append("wall_of_text")
        
        # Apply topic_confusion gate to one_idea
        if "topic_confusion" in evidence_spans and evidence_spans["topic_confusion"]:
            one_idea = min(one_idea, BARRIER_GATES["topic_confusion"]["max_score"])
            gates_triggered.append("topic_confusion")
        
        # Apply jargon penalty to standalone (if detected)
        if "jargon" in evidence_spans and evidence_spans["jargon"]:
            # Apply moderate penalty (10 points) for jargon detection
            # Could be made more sophisticated with severity detection
            standalone = max(0, standalone - 10)
            gates_triggered.append("jargon")
        
        # Note: misleading_headers affects recommendations, not dimensional scores
        if "misleading_headers" in evidence_spans and evidence_spans["misleading_headers"]:
            gates_triggered.append("misleading_headers")
        
        return standalone, structure, one_idea, right_size, gates_triggered
    
    def _create_markdown_result(self, machine_result: LLMRubricEval) -> MarkdownResult:
        """Convert machine result to markdown-compatible format.
        
        Args:
            machine_result: Structured evaluation result
            
        Returns:
            Markdown-compatible result
        """
        return MarkdownResult(
            overall_score=machine_result.overall_score,
            overall_assessment=machine_result.overall_assessment,
            strengths=machine_result.strengths,
            issues=machine_result.issues,
            recommendations=machine_result.recommendations,
            passing=machine_result.passing
        )
    
    def _create_fallback_result(self, error_msg: str, chunk_text: str) -> LLMRubricEval:
        """Create a fallback result when evaluation fails.
        
        Args:
            error_msg: Error message explaining the failure
            chunk_text: Original chunk text for context
            
        Returns:
            Minimal LLMRubricEval result
        """
        return LLMRubricEval(
            standalone=0,
            one_idea=0,
            structure=0,
            right_size=0,
            gates_triggered=[],
            evidence_spans={},
            weighted_score=0.0,
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
        """Asynchronously evaluate chunk using V2 LLM Rubric algorithm.
        
        Args:
            query: Optional query (not used directly)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with V2 dimensional scoring feedback
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
            response_model=LLMRubricEval,
            messages=messages
        )
        
        if not machine_result:
            logger.error(f"{self.evaluator_name} V2: Failed to get structured evaluation")
            machine_result = self._create_fallback_result(
                "OpenAI API call failed after retries",
                processed_text
            )
            retry_count = 2  # Indicate max retries were used
        
        # Validate the result
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
    
    def get_dimension_breakdown(self, result: LLMRubricEval) -> Dict[str, Any]:
        """Get detailed breakdown of dimensional scoring.
        
        Args:
            result: LLM Rubric evaluation result
            
        Returns:
            Dictionary with dimensional analysis
        """
        return {
            "dimensions": {
                "standalone": {
                    "score": result.standalone,
                    "weight": DIMENSION_WEIGHTS["standalone"],
                    "contribution": result.standalone * DIMENSION_WEIGHTS["standalone"]
                },
                "structure": {
                    "score": result.structure,
                    "weight": DIMENSION_WEIGHTS["structure"],
                    "contribution": result.structure * DIMENSION_WEIGHTS["structure"]
                },
                "one_idea": {
                    "score": result.one_idea,
                    "weight": DIMENSION_WEIGHTS["one_idea"],
                    "contribution": result.one_idea * DIMENSION_WEIGHTS["one_idea"]
                },
                "right_size": {
                    "score": result.right_size,
                    "weight": DIMENSION_WEIGHTS["right_size"],
                    "contribution": result.right_size * DIMENSION_WEIGHTS["right_size"]
                }
            },
            "calculation": {
                "weighted_score": result.weighted_score,
                "rounded_score": result.overall_score,
                "gates_triggered": result.gates_triggered
            },
            "evidence": result.evidence_spans
        }