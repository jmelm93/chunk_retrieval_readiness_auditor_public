"""Query-Answer evaluator using Pydantic structured outputs."""

import re
from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from .models import QueryAnswerResult, QueryEvaluation, ChunkType, SelfContainmentIssue
from .prompts import SYSTEM_PROMPT, create_user_prompt, SELF_CONTAINMENT_PATTERNS


class QueryAnswerEvaluator(BaseStructuredEvaluator):
    """Evaluate if a chunk can completely answer potential queries using structured outputs."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Query-Answer Completeness"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.25
    
    def _get_config_key(self) -> str:
        """Configuration key for model overrides."""
        return "query_answer"
    
    def __init__(self, **kwargs):
        """Initialize the Query-Answer evaluator."""
        super().__init__(**kwargs)
        
        # Set truncation length from config or default
        if self.config and hasattr(self.config, 'evaluation'):
            self.truncation_length = self.config.evaluation.truncation_length
        else:
            self.truncation_length = 3000
    
    def _detect_self_containment_issues(self, text: str) -> List[SelfContainmentIssue]:
        """Detect self-containment issues in the text.
        
        Args:
            text: Chunk text to analyze
            
        Returns:
            List of detected self-containment issues
        """
        issues = []
        
        # Use patterns from prompts module
        patterns = SELF_CONTAINMENT_PATTERNS
        
        for pattern, issue_type, impact in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Extract context around the match
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end].strip()
                
                if start > 0:
                    context = "..." + context
                if end < len(text):
                    context = context + "..."
                
                issues.append(SelfContainmentIssue(
                    issue_type=issue_type,
                    example_text=context,
                    impact=impact
                ))
        
        # Check for key information front-loading
        first_150 = text[:150] if len(text) > 150 else text
        if not re.search(r'\b(\d+|percent|cost|price|value|data|fact|statistic|step|rule|requirement)\b',
                         first_150, re.IGNORECASE):
            issues.append(SelfContainmentIssue(
                issue_type='weak_opening',
                example_text=first_150[:50] + "...",
                impact='Lacks concrete information at the start'
            ))
        
        return issues[:5]  # Limit to top 5 issues
    
    def _calculate_penalty(self, issues: List[SelfContainmentIssue]) -> int:
        """Calculate penalty points for self-containment issues.
        
        Args:
            issues: List of detected issues
            
        Returns:
            Penalty points (0-15)
        """
        if not issues:
            return 0
        return min(len(issues) * 3, 15)
    
    
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[List[str]] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously evaluate if chunk answers potential queries.
        
        Args:
            query: Optional query (not used directly)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with query-answer completeness score
        """
        # Extract chunk information
        chunk_text = kwargs.get('chunk_text', response)
        chunk_heading = kwargs.get('chunk_heading', '')
        
        if not chunk_text:
            return self.create_empty_result("No chunk text provided")
        
        # Truncate if too long
        chunk_text = self.truncate_content(chunk_text, self.truncation_length)
        
        # Detect self-containment issues first
        self_containment_issues = self._detect_self_containment_issues(chunk_text)
        penalty = self._calculate_penalty(self_containment_issues)
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": create_user_prompt(chunk_heading, chunk_text)}
        ]
        
        # Get structured output from OpenAI
        result = await self.parse_structured_output(
            response_model=QueryAnswerResult,
            messages=messages
        )
        
        if not result:
            return self.create_empty_result("Failed to get evaluation from OpenAI")
        
        # Update result with detected issues
        result.self_containment_issues = self_containment_issues
        result.self_containment_penalty = penalty
        
        # Apply penalty to score
        adjusted_score = max(0, result.score - penalty)
        result.score = adjusted_score
        result.passing = adjusted_score >= 60
        
        # Update evaluator name
        result.evaluator_name = self.evaluator_name
        
        # Create EvaluationResult for compatibility with LlamaIndex
        import json
        return EvaluationResult(
            query=json.dumps(result.as_json_summary()),  # Store summary data as JSON string
            response=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
            passing=result.passing,
            score=result.score / 100,  # Normalize to 0-1
            feedback=result.as_markdown()
        )