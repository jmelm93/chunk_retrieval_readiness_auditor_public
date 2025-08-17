"""AI-driven Entity Focus evaluator using OpenAI structured outputs."""

from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from .models import EntityFocusResult
from .prompts import SYSTEM_PROMPT, create_evaluation_prompt


class EntityFocusEvaluator(BaseStructuredEvaluator):
    """Evaluate entity focus and coherence using AI analysis.
    
    This evaluator uses OpenAI to analyze how well entities in a chunk relate to the heading
    and whether the chunk maintains topical focus through entity concentration.
    """
    
    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 weight: float = 0.25,
                 config: Any = None):
        """Initialize the entity focus evaluator.
        
        Args:
            openai_api_key: OpenAI API key
            model: Model to use for evaluation
            weight: Weight for this evaluator in composite scoring
            config: Configuration object
        """
        super().__init__(openai_api_key, model, weight, config)
        
        # Extract entities from config if available
        self.min_salience = 0.01
        self.top_entities_count = 5
        
        if config and hasattr(config, 'evaluation') and hasattr(config.evaluation, 'entity_focus'):
            self.min_salience = config.evaluation.entity_focus.min_salience
            self.top_entities_count = config.evaluation.entity_focus.top_entities_count
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Entity Focus & Coherence"
    
    def _get_default_weight(self) -> float:
        """Get the default weight for this evaluator."""
        return 0.25
    
    def _get_config_key(self) -> str:
        """Get the configuration key for model overrides."""
        return "entity_focus"
    
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[List[str]] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously extract and evaluate entity focus using AI.
        
        Args:
            query: Optional query (not used)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including heading
            
        Returns:
            EvaluationResult with entity focus evaluation
        """
        # Extract chunk data
        chunk_text = kwargs.get('chunk_text', response or '')
        chunk_heading = kwargs.get('chunk_heading', '')
        
        # Handle missing content
        if not chunk_text:
            return self.create_empty_result("No content provided for evaluation")
        
        # Truncate if needed
        chunk_text = self.truncate_content(chunk_text, 3000)
        
        # Create evaluation prompt (no entities param needed - AI will extract them)
        prompt = create_evaluation_prompt(chunk_text, chunk_heading)
        
        # Prepare messages for API call
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Get structured evaluation from OpenAI
        result = await self.parse_structured_output(
            response_model=EntityFocusResult,
            messages=messages
        )
        
        if not result:
            return self.create_empty_result("Failed to get evaluation from AI model")
        
        # Calculate final score based on multiple factors
        score_components = []
        
        # Overall focus score (45% weight - increased importance)
        score_components.append(result.overall_focus_score * 0.45)
        
        # Topic alignment (35% weight - increased importance)
        score_components.append(result.entity_coherence.topic_alignment_score * 0.35)
        
        # Concrete entity ratio (10% weight - reduced from 20%)
        # More forgiving for chunks with abstract concepts
        score_components.append(result.concrete_entity_ratio * 100 * 0.10)
        
        # Heading alignment bonus (10% weight)
        if result.heading_entity_alignment:
            score_components.append(10)
        
        # Reduced penalty for missing entities (from -5 to -2 per critical entity)
        # And only apply if impact score is 8+ (not 7+)
        if result.missing_entities:
            critical_missing = sum(1 for e in result.missing_entities if e.impact_score >= 8)
            score_components.append(-2 * critical_missing)
        
        # Add a baseline score boost to prevent extreme lows
        # This acknowledges that having ANY entities is better than none
        if len(result.extracted_entities) > 0:
            score_components.append(5)  # Small boost for having entities
        
        final_score = max(0, min(100, sum(score_components)))
        
        # Update result with calculated score
        result.score = int(final_score)
        result.passing = final_score >= 60
        
        # Generate explanation
        if final_score >= 75:
            result.explanation = f"Strong entity focus on {result.entity_coherence.primary_topic} with {len(result.entity_relevance_evaluations)} relevant entities providing clear topical coherence"
        elif final_score >= 60:
            result.explanation = f"Good entity focus on {result.entity_coherence.primary_topic} but could benefit from more concrete, specific entities"
        else:
            result.explanation = f"Weak entity focus - needs more concrete entities and better alignment with {result.entity_coherence.primary_topic}"
        
        # Create evaluation result
        import json
        return EvaluationResult(
            query=json.dumps(result.as_json_summary()),
            response="",
            passing=result.passing,
            score=result.score / 100,  # Normalize to 0-1
            feedback=result.as_markdown()
        )