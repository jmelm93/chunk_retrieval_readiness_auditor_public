"""AI-driven Structure Quality evaluator using OpenAI structured outputs."""

from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from ..base.models import StandardizedEvaluationResult
from .prompts import SYSTEM_PROMPT, create_evaluation_prompt


class StructureQualityEvaluator(BaseStructuredEvaluator):
    """Evaluate structural quality using AI analysis.
    
    This evaluator uses OpenAI to analyze HTML/Markdown structure,
    checking for proper formatting, semantic elements, and content organization
    in the context of AI chunk retrieval.
    """
    
    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 weight: float = 0.20,
                 config: Any = None):
        """Initialize the structure quality evaluator.
        
        Args:
            openai_api_key: OpenAI API key
            model: Model to use for evaluation
            weight: Weight for this evaluator in composite scoring
            config: Configuration object
        """
        super().__init__(openai_api_key, model, weight, config)
        
        # Configuration for structural analysis
        self.min_heading_words = 3
        self.max_heading_words = 10
        
        if config and hasattr(config, 'evaluation') and hasattr(config.evaluation, 'structure_quality'):
            sq = config.evaluation.structure_quality
            self.min_heading_words = sq.min_heading_words
            self.max_heading_words = sq.max_heading_words
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Structure Quality"
    
    def _get_default_weight(self) -> float:
        """Get the default weight for this evaluator."""
        return 0.20
    
    def _get_config_key(self) -> str:
        """Get the configuration key for model overrides."""
        return "structure_quality"
    
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[List[str]] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously evaluate structure quality using AI.
        
        Args:
            query: Optional query (not used)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including HTML content and heading
            
        Returns:
            EvaluationResult with structure quality evaluation
        """
        # Extract chunk data
        chunk_text = kwargs.get('chunk_text', response or '')
        html_content = kwargs.get('html_content', '')
        chunk_heading = kwargs.get('chunk_heading', '')
        
        # Handle missing content
        if not chunk_text and not html_content:
            return self.create_empty_result("No content provided for evaluation")
        
        # Truncate if needed
        content_to_eval = html_content if html_content else chunk_text
        content_to_eval = self.truncate_content(content_to_eval, 3000)
        
        # Create evaluation prompt
        prompt = create_evaluation_prompt(
            chunk_text, 
            chunk_heading, 
            html_content,
            self.min_heading_words,
            self.max_heading_words
        )
        
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