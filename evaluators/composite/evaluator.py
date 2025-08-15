"""Composite evaluator that orchestrates all evaluators."""

import asyncio
import re
from typing import List, Dict, Any, Optional
from loguru import logger

from llama_index.core.schema import TextNode

from ..query_answer.evaluator import QueryAnswerEvaluator
from ..llm_rubric.evaluator import LLMRubricEvaluator
from ..entity_focus.evaluator import EntityFocusEvaluator
from ..structure_quality.evaluator import StructureQualityEvaluator
from .models import CompositeEvaluationResult


def convert_to_plain_text(content: str, preserve_structure: bool = False) -> str:
    """Simple conversion of HTML/markdown to plain text.
    
    Args:
        content: HTML/markdown content
        preserve_structure: Whether to preserve some structure
        
    Returns:
        Plain text version
    """
    if not content:
        return ""
    
    # Remove common HTML tags
    text = re.sub(r'<[^>]+>', '', content)
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


class CompositeEvaluator:
    """Orchestrate multiple evaluators for comprehensive chunk assessment."""
    
    def __init__(self, config: Any):
        """Initialize the composite evaluator.
        
        Args:
            config: Configuration object with scoring weights
        """
        self.config = config
        
        # Initialize individual evaluators
        self.evaluators = {}
        
        # Query-Answer Evaluator
        self.evaluators['query_answer'] = QueryAnswerEvaluator(
            weight=config.scoring.weights.query_answer,
            config=config
        )
        
        # LLM Rubric Evaluator
        self.evaluators['llm_rubric'] = LLMRubricEvaluator(
            weight=config.scoring.weights.llm_rubric,
            config=config
        )
        
        # Structure Quality Evaluator
        self.evaluators['structure_quality'] = StructureQualityEvaluator(
            weight=config.scoring.weights.structure_quality,
            config=config
        )
        
        # Entity Focus Evaluator
        self.evaluators['entity_focus'] = EntityFocusEvaluator(
            weight=config.scoring.weights.entity_focus,
            config=config
        )
        
        # Store weights for composite scoring
        self.weights = {
            'query_answer': config.scoring.weights.query_answer,
            'llm_rubric': config.scoring.weights.llm_rubric,
            'structure_quality': config.scoring.weights.structure_quality,
            'entity_focus': config.scoring.weights.entity_focus
        }
        
        logger.info(f"Composite evaluator (v2) initialized with {len(self.evaluators)} evaluators")
    
    async def evaluate_node(self, node: TextNode) -> CompositeEvaluationResult:
        """Evaluate a single node with all evaluators.
        
        Args:
            node: TextNode to evaluate
            
        Returns:
            CompositeEvaluationResult with comprehensive evaluation
        """
        # Convert to plain text for RAG evaluation
        plain_text = convert_to_plain_text(node.text)
        
        # Log conversion if significant changes occurred
        if len(plain_text) < len(node.text) * 0.9:
            logger.debug(f"Converted {len(node.text)} chars to {len(plain_text)} plain text chars")
        
        # Prepare evaluation kwargs
        eval_kwargs = {
            'chunk_text': plain_text,  # Plain text for most evaluators
            'chunk_heading': node.metadata.get('heading', ''),
            'html_content': node.text,  # Original formatted text for structure evaluation
            'chunk_index': node.metadata.get('chunk_index', 0),
            'entities': node.metadata.get('entities', []),
            'metadata': node.metadata
        }
        
        # Run all evaluators concurrently
        tasks = {}
        for name, evaluator in self.evaluators.items():
            # Structure quality needs the formatted version
            if name == 'structure_quality':
                kwargs = eval_kwargs.copy()
                kwargs['html_content'] = node.text
                tasks[name] = evaluator.aevaluate(response=node.text, **kwargs)
            else:
                tasks[name] = evaluator.aevaluate(response=plain_text, **eval_kwargs)
        
        # Execute all evaluations concurrently
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Process results
        scores = {}
        feedback = {}
        
        for (name, evaluator), result in zip(self.evaluators.items(), results):
            if isinstance(result, Exception):
                logger.error(f"Evaluator {name} failed: {result}")
                scores[name] = 0.0
                feedback[name] = f"Evaluation failed: {str(result)}"
            else:
                scores[name] = result.score  # Already normalized to 0-1
                feedback[name] = result.feedback
        
        # Calculate weighted total score
        total_score = sum(scores[name] * self.weights[name] for name in scores)
        total_score_pct = total_score * 100
        
        # Determine label
        if total_score_pct >= 80:
            label = "Well Optimized"
        elif total_score_pct >= 60:
            label = "Needs Work"
        else:
            label = "Poorly Optimized"
        
        # Create composite result
        return CompositeEvaluationResult(
            chunk_id=node.id_,
            chunk_index=node.metadata.get('chunk_index', 0),
            heading=node.metadata.get('heading', ''),
            text_preview=node.text,  # Store full text, not preview
            token_count=node.metadata.get('token_count', len(plain_text.split())),
            scores=scores,
            total_score=total_score_pct,
            label=label,
            passing=total_score_pct >= 60,
            feedback=feedback,
            entities=node.metadata.get('entities', []),
            metadata={
                'plain_text_length': len(plain_text),
                'original_length': len(node.text),
                'has_html': '<' in node.text and '>' in node.text
            }
        )
    
    async def evaluate_all(self, nodes: List[TextNode]) -> List[CompositeEvaluationResult]:
        """Evaluate all nodes concurrently.
        
        Args:
            nodes: List of TextNodes to evaluate
            
        Returns:
            List of CompositeEvaluationResults
        """
        logger.info(f"Evaluating {len(nodes)} chunks with v2 evaluators")
        
        # Create evaluation tasks for all nodes
        tasks = [self.evaluate_node(node) for node in nodes]
        
        # Execute all evaluations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any failed evaluations
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to evaluate chunk {i}: {result}")
                # Create a minimal failed result
                valid_results.append(CompositeEvaluationResult(
                    chunk_id=nodes[i].id_,
                    chunk_index=i,
                    heading=nodes[i].metadata.get('heading', ''),
                    text_preview=nodes[i].text,
                    token_count=len(nodes[i].text.split()),
                    scores={},
                    total_score=0.0,
                    label="Evaluation Failed",
                    passing=False,
                    feedback={"error": str(result)},
                    entities=[]
                ))
            else:
                valid_results.append(result)
        
        logger.info(f"Successfully evaluated {len(valid_results)} chunks")
        return valid_results
    
    async def evaluate_nodes(self, nodes: List[TextNode]) -> List[CompositeEvaluationResult]:
        """Compatibility method - alias for evaluate_all.
        
        Args:
            nodes: List of TextNodes to evaluate
            
        Returns:
            List of CompositeEvaluationResults
        """
        return await self.evaluate_all(nodes)
    
    def export_results(self, results: List[CompositeEvaluationResult]) -> Dict[str, Any]:
        """Export results to dictionary format for backward compatibility.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary suitable for JSON export
        """
        return {
            'summary': {
                'total_chunks': len(results),
                'passing_chunks': sum(1 for r in results if r.passing),
                'average_score': sum(r.total_score for r in results) / len(results) if results else 0,
                'well_optimized': sum(1 for r in results if r.label == "Well Optimized"),
                'needs_work': sum(1 for r in results if r.label == "Needs Work"),
                'poorly_optimized': sum(1 for r in results if r.label == "Poorly Optimized")
            },
            'chunks': [r.model_dump() for r in results]  # Use model_dump() for Pydantic models
        }