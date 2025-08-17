"""Structure Quality V2 evaluator with checklist approach and penalty system."""

import time
from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator_v2 import BaseStructuredEvaluatorV2
from ..base.models import V2EvaluationMetadata, MarkdownResult
from .models import StructureEval, StructuralIssue, PENALTY_SEVERITY
from .prompts import get_system_prompt, create_user_prompt


class StructureQualityEvaluatorV2(BaseStructuredEvaluatorV2):
    """V2 Structure Quality evaluator with checklist approach and evidence tracking."""
    
    @property
    def evaluator_name(self) -> str:
        """Name of this evaluator."""
        return "Structure Quality"
    
    def _get_default_weight(self) -> float:
        """Default weight for this evaluator."""
        return 0.20
    
    def _get_config_key(self) -> str:
        """Configuration key for model overrides and thresholds."""
        return "structure_quality"
    
    def __init__(self, **kwargs):
        """Initialize the Structure Quality V2 evaluator."""
        super().__init__(**kwargs)
        logger.info(f"{self.evaluator_name} V2 initialized with threshold {self.passing_threshold}")
    
    def _validate_structural_issues(self, issues: List[StructuralIssue]) -> List[StructuralIssue]:
        """Validate and fix structural issues if needed.
        
        Args:
            issues: List of detected structural issues
            
        Returns:
            List of validated issues
        """
        validated = []
        
        for issue in issues:
            # Ensure penalty points match severity
            expected_points = PENALTY_SEVERITY.get(issue.severity, 0)
            if issue.points != expected_points:
                logger.warning(f"Fixing penalty points for {issue.kind} {issue.severity}: {issue.points} -> {expected_points}")
                issue.points = expected_points
            
            # Ensure evidence spans are provided
            if not issue.evidence_spans:
                logger.warning(f"Missing evidence spans for {issue.kind} {issue.severity} issue")
                issue.evidence_spans = [f"Evidence not provided for {issue.kind} issue"]
            
            validated.append(issue)
        
        return validated
    
    def _analyze_structure_breakdown(self, issues: List[StructuralIssue]) -> Dict[str, Any]:
        """Analyze the breakdown of structural issues by category and severity.
        
        Args:
            issues: List of structural issues
            
        Returns:
            Dictionary with breakdown analysis
        """
        breakdown = {
            "by_category": {},
            "by_severity": {},
            "total_issues": len(issues),
            "total_penalties": sum(issue.points for issue in issues)
        }
        
        # Count by category
        for issue in issues:
            if issue.kind not in breakdown["by_category"]:
                breakdown["by_category"][issue.kind] = {"count": 0, "penalties": 0}
            breakdown["by_category"][issue.kind]["count"] += 1
            breakdown["by_category"][issue.kind]["penalties"] += issue.points
        
        # Count by severity
        for issue in issues:
            if issue.severity not in breakdown["by_severity"]:
                breakdown["by_severity"][issue.severity] = {"count": 0, "penalties": 0}
            breakdown["by_severity"][issue.severity]["count"] += 1
            breakdown["by_severity"][issue.severity]["penalties"] += issue.points
        
        return breakdown
    
    def _create_markdown_result(self, machine_result: StructureEval) -> MarkdownResult:
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
            recommendations=machine_result.recommendations,
            passing=machine_result.passing
        )
    
    def _create_fallback_result(self, error_msg: str, chunk_text: str) -> StructureEval:
        """Create a fallback result when evaluation fails.
        
        Args:
            error_msg: Error message explaining the failure
            chunk_text: Original chunk text for context
            
        Returns:
            Minimal StructureEval result
        """
        return StructureEval(
            structural_issues=[],
            base_score=100,
            total_penalties=0,
            overall_score=0,
            overall_assessment=f"Evaluation failed: {error_msg}",
            strengths=[],
            issues=[],
            recommendations=["Retry evaluation or check chunk content format"],
            passing=False
        )
    
    async def aevaluate(self,
                        query: Optional[str] = None,
                        response: Optional[str] = None,
                        contexts: Optional[List[str]] = None,
                        **kwargs) -> EvaluationResult:
        """Asynchronously evaluate chunk using V2 Structure Quality algorithm.
        
        Args:
            query: Optional query (not used directly)
            response: The chunk text to evaluate
            contexts: Optional contexts (not used)
            **kwargs: Additional arguments including chunk metadata
            
        Returns:
            EvaluationResult with V2 structure quality feedback
        """
        start_time = time.time()
        
        # Extract chunk information
        # Structure quality evaluator can use both plain text and HTML content
        chunk_text = kwargs.get('chunk_text', response)
        html_content = kwargs.get('html_content', chunk_text)  # Prefer HTML if available
        chunk_heading = kwargs.get('chunk_heading', '')
        
        if not chunk_text:
            return self.create_empty_result("No chunk text provided")
        
        # For structure evaluation, use the HTML content if available (preserves formatting)
        content_to_evaluate = html_content if html_content != chunk_text else chunk_text
        
        # Prepare text with V2 enhancements (but don't truncate HTML structure)
        if content_to_evaluate == html_content:
            # For HTML content, just do basic validation
            processed_content = content_to_evaluate[:self.truncation_length] if len(content_to_evaluate) > self.truncation_length else content_to_evaluate
            text_metadata = {"char_count": len(content_to_evaluate), "was_truncated": len(content_to_evaluate) > self.truncation_length}
        else:
            # For plain text, use the standard processing
            processed_content, text_metadata = self.prepare_chunk_text(content_to_evaluate)
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": create_user_prompt(chunk_heading, processed_content)}
        ]
        
        # Get structured output from OpenAI
        retry_count = 0
        machine_result = await self.parse_structured_output(
            response_model=StructureEval,
            messages=messages
        )
        
        if not machine_result:
            logger.error(f"{self.evaluator_name} V2: Failed to get structured evaluation")
            machine_result = self._create_fallback_result(
                "OpenAI API call failed after retries",
                processed_content
            )
            retry_count = 2  # Indicate max retries were used
        else:
            # Validate and fix structural issues
            machine_result.structural_issues = self._validate_structural_issues(machine_result.structural_issues)
        
        # Validate the result
        if not self.validate_evaluation_result(machine_result):
            logger.warning(f"{self.evaluator_name} V2: Invalid result, creating fallback")
            machine_result = self._create_fallback_result(
                "Invalid structured output received",
                processed_content
            )
        
        # Ensure passing threshold is correct
        machine_result.passing = self.apply_passing_threshold(machine_result.overall_score)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Create evaluation metadata
        metadata = V2EvaluationMetadata(
            model_used=self.model,
            chunk_char_count=text_metadata.get("char_count", 0),
            chunk_word_count=text_metadata.get("word_count", len(processed_content.split())),
            was_truncated=text_metadata.get("was_truncated", False),
            processing_time_ms=processing_time,
            retry_count=retry_count,
            config_threshold=self.passing_threshold
        )
        
        # Create markdown result for human consumption
        markdown_result = self._create_markdown_result(machine_result)
        
        # Create LlamaIndex-compatible result
        chunk_preview = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
        
        return EvaluationResult(
            query="",  # Not used in this context
            response=chunk_preview,
            passing=machine_result.passing,
            score=machine_result.overall_score / 100,  # Normalize to 0-1
            feedback=markdown_result.as_markdown()
        )
    
    def get_structure_analysis(self, result: StructureEval) -> Dict[str, Any]:
        """Get detailed analysis of structural issues and penalties.
        
        Args:
            result: Structure Quality evaluation result
            
        Returns:
            Dictionary with structural analysis
        """
        breakdown = self._analyze_structure_breakdown(result.structural_issues)
        
        return {
            "scoring": {
                "base_score": result.base_score,
                "total_penalties": result.total_penalties,
                "final_score": result.overall_score
            },
            "issues_breakdown": breakdown,
            "detailed_issues": [
                {
                    "category": issue.kind,
                    "severity": issue.severity,
                    "penalty": issue.points,
                    "evidence": issue.evidence_spans
                }
                for issue in result.structural_issues
            ],
            "categories_evaluated": [
                "heading", "paragraphs", "lists", "tables", "code", "flow"
            ]
        }