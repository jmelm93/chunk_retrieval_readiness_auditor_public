"""Base evaluator class with OpenAI structured output support."""

import os
from typing import Optional, Any, Dict, Type, TypeVar
from abc import ABC, abstractmethod
from loguru import logger
from pydantic import BaseModel

from llama_index.core.evaluation import BaseEvaluator, EvaluationResult

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")


T = TypeVar('T', bound=BaseModel)


class BaseStructuredEvaluator(BaseEvaluator, ABC):
    """Base evaluator with OpenAI structured output support.
    
    This abstract base class provides:
    - OpenAI client initialization and management
    - Structured output parsing using Pydantic models
    - Common error handling and retry logic
    - Configuration management
    - Standard interface for all evaluators
    """
    
    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 weight: Optional[float] = None,
                 config: Optional[Any] = None):
        """
        Initialize the base evaluator.
        
        Args:
            openai_api_key: OpenAI API key
            model: Model to use for evaluation
            weight: Weight for this evaluator in composite scoring
            config: Configuration object
        """
        self.config = config
        self.weight = weight or self._get_default_weight()
        self.model = self._resolve_model(model, config)
        self.async_client = None
        
        if not OPENAI_AVAILABLE:
            logger.warning(f"{self.evaluator_name}: OpenAI library not installed")
            return
        
        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.async_client = AsyncOpenAI(api_key=api_key)
            logger.info(f"OpenAI client initialized for {self.evaluator_name}")
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
        """Get the configuration key for model overrides."""
        pass
    
    def _resolve_model(self, model: Optional[str], config: Optional[Any]) -> str:
        """Resolve which model to use based on configuration.
        
        Args:
            model: Explicitly provided model name
            config: Configuration object
            
        Returns:
            Model name to use
        """
        if model:
            return model
        
        if config:
            # Check for model override
            config_key = self._get_config_key()
            if hasattr(config, 'models'):
                if hasattr(config.models, 'overrides') and config.models.overrides and config_key in config.models.overrides:
                    return config.models.overrides[config_key]
                if hasattr(config.models, 'default'):
                    return config.models.default
        
        # Fallback default
        return "gpt-5-mini"
    
    def _get_prompts(self) -> Dict[str, Any]:
        """Return prompts used by this evaluator."""
        return {}
    
    def _update_prompts(self, prompts_dict: Dict[str, Any]) -> None:
        """Update prompts used by this evaluator."""
        pass
    
    async def parse_structured_output(self,
                                     response_model: Type[T],
                                     messages: list,
                                     max_retries: int = 2) -> Optional[T]:
        """Parse structured output from OpenAI using Pydantic model.
        
        Args:
            response_model: Pydantic model class to parse response into
            messages: Chat messages for the API call
            max_retries: Number of retries on failure
            
        Returns:
            Parsed Pydantic model instance or None on failure
        """
        if not self.async_client:
            logger.error(f"{self.evaluator_name}: OpenAI client not available")
            return None
        
        for attempt in range(max_retries + 1):
            try:
                # Use the beta structured outputs API
                # Note: gpt-5 models don't support temperature parameter
                response = await self.async_client.beta.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    response_format=response_model
                )

                # Get the parsed result
                result = response.choices[0].message.parsed
                
                # Check for refusal
                if response.choices[0].message.refusal:
                    logger.warning(f"{self.evaluator_name}: Model refused - {response.choices[0].message.refusal}")
                    return None
                
                return result
                
            except Exception as e:
                logger.error(f"{self.evaluator_name}: Attempt {attempt + 1} failed - {e}")
                if attempt == max_retries:
                    logger.error(f"{self.evaluator_name}: All retries exhausted")
                    return None
        
        return None
    
    def create_empty_result(self, error_message: str) -> EvaluationResult:
        """Create an empty evaluation result with error message.
        
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
            feedback=f"{self.evaluator_name}: {error_message}"
        )
    
    def truncate_content(self, text: str, max_length: int = 3000) -> str:
        """Truncate content if too long, preserving readability.
        
        Args:
            text: Text to potentially truncate
            max_length: Maximum length
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        
        # Try to truncate at a sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.8:  # If we found a period in the last 20%
            truncated = truncated[:last_period + 1]
        
        return truncated + " (...truncated)"
    
    @abstractmethod
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[list] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously evaluate the chunk.
        
        Args:
            query: Optional query
            response: The chunk text to evaluate
            contexts: Optional contexts
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with evaluation outcome
        """
        pass