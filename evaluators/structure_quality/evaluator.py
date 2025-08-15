"""AI-driven Structure Quality evaluator using OpenAI structured outputs."""

from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from .models import StructureQualityResult


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
    
    def _create_evaluation_prompt(self,
                                   chunk_text: str,
                                   chunk_heading: str,
                                   html_content: Optional[str] = None) -> str:
        """Create the evaluation prompt for structure quality assessment.
        
        Args:
            chunk_text: Plain text version of the chunk
            chunk_heading: The chunk's heading
            html_content: Optional HTML/formatted version
            
        Returns:
            Formatted prompt for evaluation
        """
        # Use HTML content if available, otherwise plain text
        content_to_analyze = html_content if html_content else chunk_text
        
        prompt = f"""You are evaluating the structural quality of a content chunk for AI retrieval systems.

CONTEXT:
- This chunk will be retrieved by AI systems to answer user queries
- Good structure aids both AI comprehension and information extraction
- Structure should enhance, not hinder, the content's value
- Consider this is web content that may have extraction artifacts

CHUNK HEADING: {chunk_heading if chunk_heading else "No heading provided"}

CHUNK CONTENT (may contain HTML/Markdown):
{content_to_analyze}

EVALUATION TASK:
1. Assess the heading quality (clarity, accuracy, specificity)
2. Evaluate structural elements (lists, tables, paragraphs, code blocks)
3. Judge readability and scanability for AI systems
4. Determine if formatting choices match content needs
5. Identify structural issues that hinder chunk quality

IMPORTANT CONSIDERATIONS:
- Headings should be specific and descriptive, not generic
- Lists and tables should be used when they enhance comprehension
- Dense walls of text are problematic for retrieval
- Clear introductory context improves chunk usability
- Logical flow and organization matter for coherence
- Inline artifacts (timestamps, share buttons) are NOT structural issues

STRUCTURAL ELEMENT GUIDELINES:
- Heading: Should accurately describe content (3-{self.max_heading_words} words ideal)
- Lists: Effective for enumeration, steps, or multiple related items
- Tables: Best for comparative or structured data
- Paragraphs: Should be reasonably sized, not too long or too short
- Code blocks: Should be properly formatted if present

SCORING GUIDELINES:
- 80-100: Excellent structure that enhances content value and retrieval
- 60-79: Good structure with minor improvements needed
- 40-59: Moderate structural issues affecting usability
- 0-39: Poor structure that significantly hinders chunk quality

Focus on how structure affects AI chunk retrieval effectiveness."""
        
        return prompt
    
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
        prompt = self._create_evaluation_prompt(chunk_text, chunk_heading, html_content)
        
        # Prepare messages for API call
        messages = [
            {
                "role": "system",
                "content": """You are an expert at evaluating content structure for AI retrieval systems.

Your evaluation should:
1. Assess heading quality and accuracy
2. Evaluate structural element effectiveness
3. Judge readability and scanability
4. Identify structural issues and their impact
5. Provide actionable improvement suggestions

Be thorough but fair. Focus on structural aspects that affect AI chunk retrieval.
Remember that perfect HTML/Markdown isn't required - focus on whether the structure aids or hinders comprehension."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Get structured evaluation from OpenAI
        result = await self.parse_structured_output(
            response_model=StructureQualityResult,
            messages=messages
        )
        
        if not result:
            return self.create_empty_result("Failed to get evaluation from AI model")
        
        # Calculate final score based on multiple factors
        score_components = []
        
        # Overall structure score (35% weight)
        score_components.append(result.overall_structure_score * 0.35)
        
        # Formatting effectiveness (25% weight)
        score_components.append(result.formatting_effectiveness * 0.25)
        
        # Retrieval friendliness (25% weight)
        score_components.append(result.retrieval_friendliness * 0.25)
        
        # Heading quality (15% weight)
        avg_heading_score = (
            result.heading_quality.clarity_score +
            result.heading_quality.accuracy_score +
            result.heading_quality.specificity_score
        ) / 3
        score_components.append(avg_heading_score * 0.15)
        
        # Penalty for high-impact issues
        if result.structural_issues:
            high_impact_count = sum(1 for issue in result.structural_issues if issue.impact == "high")
            score_components.append(-5 * high_impact_count)
        
        # Bonus for good readability signals
        readability_bonus = 0
        if result.readability_signals.has_clear_intro:
            readability_bonus += 3
        if result.readability_signals.logical_flow:
            readability_bonus += 3
        if result.readability_signals.appropriate_formatting:
            readability_bonus += 4
        score_components.append(readability_bonus)
        
        final_score = max(0, min(100, sum(score_components)))
        
        # Update result with calculated score
        result.score = int(final_score)
        result.passing = final_score >= 60
        
        # Generate explanation based on score
        if final_score >= 75:
            result.explanation = f"Excellent structure with effective use of {len(result.structural_elements)} key elements enhancing retrieval quality"
        elif final_score >= 60:
            result.explanation = f"Good structural quality with {result.readability_signals.scanability_score}% scanability, minor improvements recommended"
        else:
            issue_count = len(result.structural_issues)
            result.explanation = f"Structure needs improvement - {issue_count} issues affecting retrieval effectiveness"
        
        # Create evaluation result
        import json
        return EvaluationResult(
            query=json.dumps(result.as_json_summary()),
            response="",
            passing=result.passing,
            score=result.score / 100,  # Normalize to 0-1
            feedback=result.as_markdown()
        )