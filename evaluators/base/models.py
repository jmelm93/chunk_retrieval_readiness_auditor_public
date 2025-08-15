"""Base Pydantic models for all evaluators."""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class FormattingOptions(BaseModel):
    """Options for controlling output formatting."""
    
    filter_output: bool = Field(
        default=False,
        description="Whether to limit output to top items for conciseness"
    )
    max_items: int = Field(
        default=3,
        description="Maximum number of items to show in lists when filtering"
    )
    verbosity: str = Field(
        default="normal",
        description="Output verbosity level: concise, normal, or detailed"
    )


class MarkdownFormattable(ABC):
    """Mixin for models that can be formatted as markdown."""
    
    @abstractmethod
    def as_markdown(self, options: Optional[FormattingOptions] = None) -> str:
        """Convert the model to formatted markdown.
        
        Args:
            options: Formatting options for output control
            
        Returns:
            Formatted markdown string
        """
        pass
    
    def as_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        if hasattr(self, 'model_dump'):
            return self.model_dump()
        return {}


class BaseMetrics(BaseModel):
    """Base class for evaluation metrics."""
    
    model_config = ConfigDict(extra='forbid')
    
    score: int = Field(
        ge=0, le=100,
        description="Overall score from 0-100 where 70-89 is typical for good chunks"
    )
    passing: bool = Field(
        description="Whether the chunk meets minimum quality threshold (typically 60+)"
    )
    
    def score_normalized(self) -> float:
        """Get score as a normalized 0-1 float."""
        return self.score / 100.0


class BaseEvaluationResult(BaseModel, MarkdownFormattable):
    """Base class for all evaluation results."""
    
    model_config = ConfigDict(extra='forbid')
    
    evaluator_name: str = Field(
        description="Name of the evaluator that produced this result"
    )
    score: int = Field(
        ge=0, le=100,
        description="Overall score from 0-100"
    )
    passing: bool = Field(
        description="Whether evaluation passed minimum threshold"
    )
    explanation: str = Field(
        description="Brief explanation of the evaluation outcome"
    )
    
    def as_markdown(self, options: Optional[FormattingOptions] = None) -> str:
        """Base markdown formatting - subclasses should override for custom formatting."""
        options = options or FormattingOptions()
        
        lines = []
        lines.append(f"**{self.evaluator_name} Assessment:**")
        lines.append(self.explanation)
        lines.append(f"\nScore: {self.score}/100 ({'Passing' if self.passing else 'Failing'})")
        
        return "\n".join(lines)
    
    def _format_list_items(self, items: List[str], options: FormattingOptions, 
                          prefix: str = "• ") -> List[str]:
        """Helper to format list items with optional filtering.
        
        Args:
            items: List of items to format
            options: Formatting options
            prefix: Prefix for each item (default bullet point)
            
        Returns:
            Formatted list of strings
        """
        if options.filter_output and len(items) > options.max_items:
            items = items[:options.max_items]
        
        return [f"{prefix}{item}" for item in items]
    
    def _add_section_if_content(self, lines: List[str], title: str, 
                                content: List[str]) -> None:
        """Helper to add a section only if it has content.
        
        Args:
            lines: List to append to
            title: Section title
            content: Section content
        """
        if content:
            lines.append(f"\n**{title}:**")
            lines.extend(content)