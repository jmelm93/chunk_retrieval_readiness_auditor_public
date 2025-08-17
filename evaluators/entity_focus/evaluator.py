"""AI-driven Entity Focus evaluator using OpenAI structured outputs."""

from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from ..base.models import StandardizedEvaluationResult
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
            response_model=StandardizedEvaluationResult,
            messages=messages
        )
        
        if not result:
            return self.create_empty_result("Failed to get evaluation from AI model")
        
        # Update evaluator name and ensure passing threshold is correct
        result.evaluator_name = self.evaluator_name
        result.passing = result.overall_score >= 60
        
        # Create evaluation result
        return EvaluationResult(
            query="",  # Not used in this context
            response="",
            passing=result.passing,
            score=result.overall_score / 100,  # Normalize to 0-1
            feedback=result.as_markdown()
        )