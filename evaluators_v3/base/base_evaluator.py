"""Simplified base evaluator for V3 with cleaner architecture."""

import os
from typing import Optional, Type, TypeVar, Dict, Any
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


class BaseStructuredEvaluatorV3(BaseEvaluator, ABC):
    """Simplified base evaluator for V3 with cleaner architecture.
    
    Key simplifications from V2:
    - No duplicate metadata tracking
    - Single model output (no dual format)
    - Cleaner configuration handling
    - Simpler error handling
    - No complex validation methods
    """
    
    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 weight: Optional[float] = None,
                 config: Optional[Any] = None):
        """Initialize the V3 evaluator.
        
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
        
        # Get evaluator-specific settings
        self.passing_threshold = self._get_passing_threshold()
        self.truncation_length = self._get_truncation_length()
        
        if not OPENAI_AVAILABLE:
            logger.warning(f"{self.evaluator_name}: OpenAI library not installed")
            return
        
        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.async_client = AsyncOpenAI(api_key=api_key)
            logger.info(f"{self.evaluator_name} V3: Initialized with model {self.model}")
        else:
            logger.warning(f"No OpenAI API key provided for {self.evaluator_name}")
    
    @property
    @abstractmethod
    def evaluator_name(self) -> str:
        """Name of this evaluator for logging."""
        pass
    
    @abstractmethod
    def _get_default_weight(self) -> float:
        """Get the default weight for this evaluator."""
        pass
    
    @abstractmethod
    def _get_config_key(self) -> str:
        """Get the configuration key for this evaluator."""
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
            config_key = self._get_config_key()
            if hasattr(config, 'models'):
                # Check for evaluator-specific override
                if hasattr(config.models, 'overrides') and config.models.overrides:
                    if config_key in config.models.overrides:
                        return config.models.overrides[config_key]
                # Use default model
                if hasattr(config.models, 'default'):
                    return config.models.default
        
        # Fallback default
        return "gpt-5-mini"
    
    def _get_passing_threshold(self) -> float:
        """Get the passing threshold for this evaluator.
        
        Returns:
            Passing threshold (0-100 scale)
        """
        if self.config and hasattr(self.config, 'evaluation'):
            if hasattr(self.config.evaluation, 'thresholds'):
                config_key = self._get_config_key()
                threshold = getattr(self.config.evaluation.thresholds, config_key, None)
                if threshold is not None:
                    return threshold
        
        # Default thresholds
        defaults = {
            "query_answer": 75,
            "llm_rubric": 70,
            "entity_focus": 70,
            "structure_quality": 70
        }
        return defaults.get(self._get_config_key(), 60)
    
    def _get_truncation_length(self) -> int:
        """Get the truncation length from config.
        
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
        
        Simplified from V2: Less complex error handling and logging.
        
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
                # Use structured outputs
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
                
                if result:
                    logger.debug(f"{self.evaluator_name}: Successfully parsed response")
                
                return result
                
            except Exception as e:
                logger.error(f"{self.evaluator_name}: Attempt {attempt + 1} failed - {e}")
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"{self.evaluator_name}: Retrying in {wait_time} seconds...")
                    import asyncio
                    await asyncio.sleep(wait_time)
                else:
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
    
    def prepare_chunk_text(self, text: str) -> tuple[str, Dict[str, Any]]:
        """Prepare chunk text for evaluation.
        
        Args:
            text: Raw chunk text
            
        Returns:
            Tuple of (processed_text, metadata)
        """
        if not text:
            return "", {"error": "No text provided"}
        
        # Get text metadata
        metadata = get_text_metadata(text)
        
        # Apply truncation if needed
        if len(text) > self.truncation_length:
            processed_text = truncate_content(text, self.truncation_length)
            metadata["was_truncated"] = True
            metadata["original_length"] = len(text)
            logger.debug(f"{self.evaluator_name}: Truncated from {len(text)} to {len(processed_text)} chars")
        else:
            processed_text = text
            metadata["was_truncated"] = False
        
        return processed_text, metadata
    
    def calculate_score_from_issues(self, issues: list) -> int:
        """Calculate score based on issues found. Fallback in case the AI model doesn't return a score. 
        
        Standard scoring algorithm used across evaluators.
        Can be overridden for custom scoring logic.
        
        Args:
            issues: List of Issue objects
            
        Returns:
            Score from 0-100
        """
        score = 95  # Start higher (excellent baseline)
        
        severe_count = 0
        moderate_count = 0
        
        for issue in issues:
            severity = issue.severity if hasattr(issue, 'severity') else issue.get('severity', 'minor')
            
            if severity == "minor":
                score -= 5  # Smaller penalty for minor issues
            elif severity == "moderate":
                score -= 10  # Moderate penalty
                moderate_count += 1
            elif severity == "severe":
                score -= 20  # Significant but not devastating
                severe_count += 1
        
        # More lenient caps
        if severe_count > 0:
            score = min(score, 65)  # Less harsh cap for severe issues
        elif moderate_count >= 3:
            score = min(score, 75)  # Less harsh cap for multiple moderate issues
        
        # Excellence bonus - perfect content gets 100
        if len(issues) == 0:
            score = 100
        
        return max(10, min(100, score))  # Bounded between 10-100
    
    def _get_prompts(self) -> Dict[str, Any]:
        """Return prompts used by this evaluator.
        
        Required by PromptMixin interface from LlamaIndex.
        V3 evaluators manage prompts internally, so this returns empty.
        """
        return {}
    
    def _update_prompts(self, prompts_dict: Dict[str, Any]) -> None:
        """Update prompts used by this evaluator.
        
        Required by PromptMixin interface from LlamaIndex.
        V3 evaluators use static prompts, so this is a no-op.
        """
        pass
    
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
            **kwargs: Additional arguments
            
        Returns:
            EvaluationResult with evaluation outcome
        """
        pass