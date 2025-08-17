"""Enhanced base evaluator class for V2 evaluators with improved error handling and dual outputs."""

import os
from typing import Optional, Any, Dict, Type, TypeVar, Tuple
from abc import ABC, abstractmethod
from loguru import logger
from pydantic import BaseModel

from llama_index.core.evaluation import BaseEvaluator, EvaluationResult

from utils.text_converter import truncate_content, get_text_metadata

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")


T = TypeVar('T', bound=BaseModel)


class BaseStructuredEvaluatorV2(BaseEvaluator, ABC):
    """Enhanced base evaluator for V2 with improved error handling and dual outputs.
    
    Key V2 enhancements:
    - Enhanced error handling with graceful degradation
    - Dual output support (markdown + structured JSON)
    - Config-driven thresholds per evaluator
    - Improved text processing integration
    - Better logging and debugging support
    - Removal of temperature/seed (not supported by GPT-5)
    """
    
    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 weight: Optional[float] = None,
                 config: Optional[Any] = None):
        """Initialize the enhanced V2 base evaluator.
        
        Args:
            openai_api_key: OpenAI API key
            model: Model to use for evaluation
            weight: Weight for this evaluator in composite scoring
            config: Configuration object with V2 settings
        """
        self.config = config
        self.weight = weight or self._get_default_weight()
        self.model = self._resolve_model(model, config)
        self.async_client = None
        
        # V2 enhancement: Get evaluator-specific settings
        self.passing_threshold = self._get_passing_threshold()
        self.truncation_length = self._get_truncation_length()
        
        if not OPENAI_AVAILABLE:
            logger.warning(f"{self.evaluator_name}: OpenAI library not installed")
            return
        
        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.async_client = AsyncOpenAI(api_key=api_key)
            logger.info(f"{self.evaluator_name} V2: OpenAI client initialized with model {self.model}")
        else:
            logger.warning(f"No OpenAI API key provided for {self.evaluator_name}")
    
    @property
    @abstractmethod
    def evaluator_name(self) -> str:
        """Name of this evaluator for logging and identification."""
        pass
    
    @abstractmethod
    def _get_default_weight(self) -> float:
        """Get the default weight for this evaluator."""
        pass
    
    @abstractmethod
    def _get_config_key(self) -> str:
        """Get the configuration key for model overrides and thresholds."""
        pass
    
    def _resolve_model(self, model: Optional[str], config: Optional[Any]) -> str:
        """Resolve which model to use based on V2 configuration.
        
        Args:
            model: Explicitly provided model name
            config: Configuration object
            
        Returns:
            Model name to use
        """
        if model:
            return model
        
        if config:
            # Check for V2 model override
            config_key = self._get_config_key()
            if hasattr(config, 'models'):
                if hasattr(config.models, 'overrides') and config.models.overrides and config_key in config.models.overrides:
                    return config.models.overrides[config_key]
                if hasattr(config.models, 'default'):
                    return config.models.default
        
        # V2 default: Use GPT-5 models
        return "gpt-5-mini"
    
    def _get_passing_threshold(self) -> float:
        """Get the passing threshold for this evaluator from V2 config.
        
        Returns:
            Passing threshold (0-100 scale)
        """
        if self.config and hasattr(self.config, 'evaluation') and hasattr(self.config.evaluation, 'thresholds'):
            config_key = self._get_config_key()
            threshold = getattr(self.config.evaluation.thresholds, config_key, None)
            if threshold is not None:
                return threshold
        
        # V2 defaults
        defaults = {
            "query_answer": 75,
            "llm_rubric": 70,
            "entity_focus": 70,
            "structure_quality": 70
        }
        return defaults.get(self._get_config_key(), 60)
    
    def _get_prompts(self) -> Dict[str, Any]:
        """Return prompts used by this evaluator.
        
        V2 evaluators manage prompts in their prompts.py modules,
        so this returns an empty dict for compatibility.
        """
        return {}
    
    def _update_prompts(self, prompts_dict: Dict[str, Any]) -> None:
        """Update prompts used by this evaluator.
        
        V2 evaluators use static prompts defined in prompts.py modules,
        so this is a no-op for compatibility.
        """
        pass
    
    def _get_truncation_length(self) -> int:
        """Get the truncation length from V2 config.
        
        Returns:
            Maximum text length before truncation
        """
        if self.config and hasattr(self.config, 'evaluation'):
            return getattr(self.config.evaluation, 'truncation_length', 3000)
        return 3000
    
    async def parse_structured_output(self,
                                     response_model: Type[T],
                                     messages: list,
                                     max_retries: int = 2) -> Optional[T]:
        """Parse structured output from OpenAI using Pydantic model.
        
        V2 enhancements:
        - Better error handling with detailed logging
        - No temperature/seed parameters (not supported by GPT-5)
        - Enhanced retry logic with exponential backoff
        
        Args:
            response_model: Pydantic model class to parse response into
            messages: Chat messages for the API call
            max_retries: Number of retries on failure
            
        Returns:
            Parsed Pydantic model instance or None on failure
        """
        if not self.async_client:
            logger.error(f"{self.evaluator_name} V2: OpenAI client not available")
            return None
        
        for attempt in range(max_retries + 1):
            try:
                # V2: Use structured outputs without temperature/seed
                response = await self.async_client.beta.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    response_format=response_model
                )

                # Get the parsed result
                result = response.choices[0].message.parsed
                
                # Check for refusal
                if response.choices[0].message.refusal:
                    logger.warning(f"{self.evaluator_name} V2: Model refused - {response.choices[0].message.refusal}")
                    return None
                
                # V2: Log successful parsing with metadata
                if result:
                    logger.debug(f"{self.evaluator_name} V2: Successfully parsed {response_model.__name__}")
                
                return result
                
            except Exception as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.error(f"{self.evaluator_name} V2: Attempt {attempt + 1} failed - {e}")
                
                if attempt < max_retries:
                    logger.info(f"{self.evaluator_name} V2: Retrying in {wait_time} seconds...")
                    import asyncio
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"{self.evaluator_name} V2: All retries exhausted")
                    return None
        
        return None
    
    def create_empty_result(self, error_message: str) -> EvaluationResult:
        """Create an empty evaluation result with error message.
        
        V2 enhancement: Include evaluator version and better error context.
        
        Args:
            error_message: Error message to include
            
        Returns:
            EvaluationResult with error
        """
        return EvaluationResult(
            query="",
            response="",
            passing=False,
            score=0.0,
            feedback=f"{self.evaluator_name} V2: {error_message}"
        )
    
    def prepare_chunk_text(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Prepare chunk text for evaluation with V2 enhancements.
        
        Args:
            text: Raw chunk text
            
        Returns:
            Tuple of (processed_text, metadata)
        """
        if not text:
            return "", {"error": "No text provided"}
        
        # Get text metadata for context
        metadata = get_text_metadata(text)
        
        # Apply intelligent truncation if needed
        if len(text) > self.truncation_length:
            processed_text = truncate_content(text, self.truncation_length)
            metadata["was_truncated"] = True
            metadata["original_length"] = len(text)
            logger.debug(f"{self.evaluator_name} V2: Truncated text from {len(text)} to {len(processed_text)} chars")
        else:
            processed_text = text
            metadata["was_truncated"] = False
        
        return processed_text, metadata
    
    def validate_evaluation_result(self, result: Any, score_field: str = "overall_score") -> bool:
        """Validate that an evaluation result meets V2 standards.
        
        Args:
            result: Parsed evaluation result
            score_field: Name of the score field to validate
            
        Returns:
            True if result is valid
        """
        if not result:
            return False
        
        # Check required fields
        if not hasattr(result, score_field):
            logger.warning(f"{self.evaluator_name} V2: Missing {score_field} field")
            return False
        
        score = getattr(result, score_field)
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            logger.warning(f"{self.evaluator_name} V2: Invalid score {score}, must be 0-100")
            return False
        
        # Check for required assessment field
        if hasattr(result, 'overall_assessment') and not result.overall_assessment:
            logger.warning(f"{self.evaluator_name} V2: Missing overall_assessment")
            return False
        
        return True
    
    def apply_passing_threshold(self, score: float) -> bool:
        """Apply V2 config-driven passing threshold.
        
        Args:
            score: Score to evaluate (0-100 scale)
            
        Returns:
            True if score meets threshold
        """
        return score >= self.passing_threshold
    
    @abstractmethod
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[list] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously evaluate the chunk using V2 enhancements.
        
        Args:
            query: Optional query
            response: The chunk text to evaluate
            contexts: Optional contexts
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with evaluation outcome
        """
        pass
    
    def get_evaluator_info(self) -> Dict[str, Any]:
        """Get information about this V2 evaluator instance.
        
        Returns:
            Dictionary with evaluator configuration and status
        """
        return {
            "evaluator_name": self.evaluator_name,
            "version": "V2",
            "model": self.model,
            "weight": self.weight,
            "passing_threshold": self.passing_threshold,
            "truncation_length": self.truncation_length,
            "openai_available": OPENAI_AVAILABLE,
            "client_initialized": self.async_client is not None
        }