"""AI-driven Entity Focus evaluator using OpenAI structured outputs."""

from typing import Optional, List, Dict, Any
from loguru import logger

from llama_index.core.evaluation import EvaluationResult

from ..base.base_evaluator import BaseStructuredEvaluator
from .models import EntityFocusResult


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
    
    def _create_evaluation_prompt(self,
                                   chunk_text: str,
                                   chunk_heading: str) -> str:
        """Create the evaluation prompt for entity extraction and focus assessment.
        
        Args:
            chunk_text: The chunk content to evaluate
            chunk_heading: The chunk's heading
            
        Returns:
            Formatted prompt for evaluation
        """
        
        prompt = f"""You are extracting and evaluating entities for a content chunk used in RAG (Retrieval-Augmented Generation) systems.

CONTEXT:
- This chunk will be retrieved alongside 3-5 other chunks to answer user queries
- Chunks should maintain focused topical coherence through their entities
- Entities provide concrete anchors that help with retrieval and comprehension
- Different chunk types (overview, example, detail) have different entity needs

CHUNK HEADING: {chunk_heading if chunk_heading else "No heading provided"}

CHUNK CONTENT:
{chunk_text}

ENTITY EXTRACTION & EVALUATION TASKS:
1. Extract key entities from the chunk (products, organizations, people, concepts, technologies, methods)
2. Identify the primary topic/concept this chunk focuses on
3. Evaluate how well the entities support and align with this topic
4. Assess whether entities are concrete/specific vs generic references
5. Determine if critical entities are missing for the chunk's purpose
6. Judge if entity diversity helps or hinders the chunk's focus

ENTITY TYPES TO EXTRACT:
- PRODUCT: Specific products, services, or tools (e.g., ChatGPT, Google Search, Pinecone)
- ORGANIZATION: Companies, institutions, groups (e.g., OpenAI, Microsoft, Stanford)
- PERSON: Named individuals (e.g., researchers, authors, executives)
- CONCEPT: Abstract ideas or principles (e.g., RAG, machine learning, SEO)
- TECHNOLOGY: Technical systems or standards (e.g., GPT-4, BERT, transformers)
- METHOD: Processes or approaches (e.g., fine-tuning, prompt engineering)

IMPORTANT CONSIDERATIONS:
- Extract entities as they appear in the text (preserve original form)
- Concrete entities (specific names, brands, dates) are more valuable than generic terms
- Entity density should be appropriate for the chunk type
- For overview chunks, some generic entities are acceptable
- For example/detail chunks, concrete entities are critical
- Ignore extraction artifacts: timestamps, author bylines, navigation elements

SCORING GUIDELINES:
- Consider the chunk's purpose (overview vs detail vs example)
- 80-100: Excellent entity focus appropriate for chunk type
- 60-79: Good entity usage with room for improvement
- 40-59: Moderate issues - needs more specific entities for its purpose
- 0-39: Poor entity focus - lacks entities needed for effective retrieval

Provide entity extraction followed by thorough evaluation of entity quality and topical coherence."""
        
        return prompt
    
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
        prompt = self._create_evaluation_prompt(chunk_text, chunk_heading)
        
        # Prepare messages for API call
        messages = [
            {
                "role": "system",
                "content": """You are an expert at extracting and evaluating entities in content chunks for AI retrieval systems.

Your task has two parts:
1. EXTRACT entities from the chunk text (products, organizations, people, concepts, technologies, methods)
2. EVALUATE how well these entities support the chunk's purpose

Remember:
- Different chunk types have different entity needs (overview vs detail vs example)
- Extract entities as they appear in the text
- Evaluate based on the chunk's apparent purpose
- Be thorough but fair in your assessment"""
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