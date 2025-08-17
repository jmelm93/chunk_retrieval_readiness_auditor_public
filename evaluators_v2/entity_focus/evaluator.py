"""Entity Focus V2 evaluator with entity extraction and alignment analysis."""

import time
from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator_v2 import BaseStructuredEvaluatorV2
from ..base.models import V2EvaluationMetadata
from .models import EntityFocusEval, EntityFocusMarkdownResult, Entity, DIMENSION_WEIGHTS
from .prompts import get_system_prompt, create_user_prompt


class EntityFocusEvaluatorV2(BaseStructuredEvaluatorV2):
    """V2 Entity Focus evaluator with entity extraction and coherence analysis."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Entity Focus & Coherence"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.25
    
    def _get_config_key(self) -> str:
        """Configuration key for model overrides and thresholds."""
        return "entity_focus"
    
    def __init__(self, **kwargs):
        """Initialize the Entity Focus V2 evaluator."""
        super().__init__(**kwargs)
        logger.info(f"{self.evaluator_name} V2 initialized with threshold {self.passing_threshold}")
    
    def _validate_entities(self, entities: List[Entity], text: str) -> List[Entity]:
        """Validate and fix entity positions if needed.
        
        Args:
            entities: List of extracted entities
            text: Original text for validation
            
        Returns:
            List of validated entities
        """
        validated = []
        text_length = len(text)
        
        for entity in entities:
            # Check if positions are valid
            if entity.start < 0 or entity.end > text_length or entity.start >= entity.end:
                logger.warning(f"Invalid entity positions for '{entity.text}': {entity.start}-{entity.end}")
                # Try to find the entity in the text
                start_pos = text.find(entity.text)
                if start_pos != -1:
                    entity.start = start_pos
                    entity.end = start_pos + len(entity.text)
                else:
                    # Skip this entity if we can't find it
                    logger.warning(f"Could not locate entity '{entity.text}' in text")
                    continue
            
            # Validate that the text matches the extracted span
            extracted_span = text[entity.start:entity.end]
            if extracted_span != entity.text:
                logger.warning(f"Entity text mismatch: '{entity.text}' vs '{extracted_span}'")
                # Use the actual span from the text
                entity.text = extracted_span
            
            validated.append(entity)
        
        return validated
    
    def _analyze_entity_distribution(self, entities: List[Entity]) -> Dict[str, Any]:
        """Analyze the distribution of entity types and specificity.
        
        Args:
            entities: List of extracted entities
            
        Returns:
            Dictionary with distribution analysis
        """
        if not entities:
            return {
                "type_counts": {},
                "specificity_counts": {},
                "total_entities": 0,
                "specificity_ratio": 0.0
            }
        
        # Count by type
        type_counts = {}
        for entity in entities:
            type_counts[entity.type] = type_counts.get(entity.type, 0) + 1
        
        # Count by specificity
        specificity_counts = {}
        for entity in entities:
            specificity_counts[entity.specificity] = specificity_counts.get(entity.specificity, 0) + 1
        
        # Calculate specificity ratio (specific + proper) / total
        specific_count = specificity_counts.get("specific", 0) + specificity_counts.get("proper", 0)
        specificity_ratio = specific_count / len(entities) if entities else 0.0
        
        return {
            "type_counts": type_counts,
            "specificity_counts": specificity_counts,
            "total_entities": len(entities),
            "specificity_ratio": specificity_ratio
        }
    
    def _create_markdown_result(self, machine_result: EntityFocusEval) -> EntityFocusMarkdownResult:
        """Convert machine result to markdown-compatible format.
        
        Args:
            machine_result: Structured evaluation result
            
        Returns:
            Markdown-compatible result
        """
        return EntityFocusMarkdownResult(
            evaluator_name=self.evaluator_name,
            overall_score=machine_result.overall_score,
            overall_assessment=machine_result.overall_assessment,
            strengths=machine_result.strengths,
            issues=machine_result.issues,
            recommendations=machine_result.recommendations,
            passing=machine_result.passing
        )
    
    def _create_fallback_result(self, error_msg: str, chunk_text: str) -> EntityFocusEval:
        """Create a fallback result when evaluation fails.
        
        Args:
            error_msg: Error message explaining the failure
            chunk_text: Original chunk text for context
            
        Returns:
            Minimal EntityFocusEval result
        """
        return EntityFocusEval(
            evaluator_name=self.evaluator_name,
            primary_topic="Unknown (evaluation failed)",
            entities=[],
            alignment=0,
            specificity_score=0,
            coverage=0,
            missing_critical_entities=["Unable to analyze due to evaluation failure"],
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
        """Asynchronously evaluate chunk using V2 Entity Focus algorithm.
        
        Args:
            query: Optional query (not used directly)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with V2 entity focus feedback
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
            response_model=EntityFocusEval,
            messages=messages
        )
        
        if not machine_result:
            logger.error(f"{self.evaluator_name} V2: Failed to get structured evaluation")
            machine_result = self._create_fallback_result(
                "OpenAI API call failed after retries",
                processed_text
            )
            retry_count = 2  # Indicate max retries were used
        else:
            # Validate and fix entity positions
            machine_result.entities = self._validate_entities(machine_result.entities, processed_text)
        
        # Validate the result
        if not self.validate_evaluation_result(machine_result):
            logger.warning(f"{self.evaluator_name} V2: Invalid result, creating fallback")
            machine_result = self._create_fallback_result(
                "Invalid structured output received",
                processed_text
            )
        
        # Ensure evaluator name and passing threshold are correct
        machine_result.evaluator_name = self.evaluator_name
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
    
    def get_entity_analysis(self, result: EntityFocusEval) -> Dict[str, Any]:
        """Get detailed analysis of extracted entities.
        
        Args:
            result: Entity Focus evaluation result
            
        Returns:
            Dictionary with entity analysis
        """
        distribution = self._analyze_entity_distribution(result.entities)
        
        return {
            "primary_topic": result.primary_topic,
            "entity_count": len(result.entities),
            "entity_distribution": distribution,
            "dimensions": {
                "alignment": {
                    "score": result.alignment,
                    "weight": DIMENSION_WEIGHTS["alignment"],
                    "contribution": result.alignment * DIMENSION_WEIGHTS["alignment"]
                },
                "specificity": {
                    "score": result.specificity_score,
                    "weight": DIMENSION_WEIGHTS["specificity"],
                    "contribution": result.specificity_score * DIMENSION_WEIGHTS["specificity"]
                },
                "coverage": {
                    "score": result.coverage,
                    "weight": DIMENSION_WEIGHTS["coverage"],
                    "contribution": result.coverage * DIMENSION_WEIGHTS["coverage"]
                }
            },
            "missing_entities": result.missing_critical_entities,
            "calculation": {
                "weighted_score": result.weighted_score,
                "final_score": result.overall_score
            }
        }