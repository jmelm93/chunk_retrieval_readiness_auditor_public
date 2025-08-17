"""Simplified Composite V3 evaluator orchestrating all individual evaluators."""

import asyncio
import time
from typing import List, Dict, Any, Optional
from loguru import logger

from llama_index.core.schema import TextNode
from llama_index.core.evaluation import EvaluationResult

from ..query_answer.evaluator import QueryAnswerEvaluatorV3
from ..entity_focus.evaluator import EntityFocusEvaluatorV3
from ..llm_rubric.evaluator import LLMRubricEvaluatorV3
from ..structure_quality.evaluator import StructureQualityEvaluatorV3


class CompositeEvaluatorV3:
    """Simplified composite evaluator for V3 architecture.
    
    Key simplifications from V2:
    - Single result format (no dual output)
    - Simple weighted average calculation
    - No complex metadata tracking
    - Cleaner error handling
    """
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize the composite evaluator with all sub-evaluators.
        
        Args:
            config: Configuration object with settings
        """
        self.config = config
        
        # Initialize all evaluators
        self.evaluators = {
            "query_answer": QueryAnswerEvaluatorV3(config=config),
            "entity_focus": EntityFocusEvaluatorV3(config=config),
            "llm_rubric": LLMRubricEvaluatorV3(config=config),
            "structure_quality": StructureQualityEvaluatorV3(config=config)
        }
        
        # Get weights and normalize
        self._setup_weights()
        
        logger.info(f"CompositeEvaluator V3 initialized with {len(self.evaluators)} evaluators")
    
    def _setup_weights(self):
        """Setup and normalize evaluator weights."""
        # Get weights from evaluators
        raw_weights = {
            name: evaluator.weight 
            for name, evaluator in self.evaluators.items()
        }
        
        # Normalize weights to sum to 1.0
        total_weight = sum(raw_weights.values())
        if total_weight > 0:
            self.weights = {
                name: weight / total_weight 
                for name, weight in raw_weights.items()
            }
        else:
            # Equal weights if something goes wrong
            self.weights = {
                name: 1.0 / len(self.evaluators) 
                for name in self.evaluators
            }
        
        logger.debug(f"Normalized weights: {self.weights}")
    
    async def evaluate_node(self, node: TextNode) -> Dict[str, Any]:
        """Evaluate a single node with all evaluators.
        
        V3: Simplified result structure, no complex models.
        
        Args:
            node: TextNode to evaluate
            
        Returns:
            Dictionary with evaluation results
        """
        start_time = time.time()
        
        # Extract text and metadata
        chunk_text = node.text
        chunk_metadata = node.metadata or {}
        
        # Prepare evaluation tasks
        tasks = []
        evaluator_names = []
        
        for name, evaluator in self.evaluators.items():
            tasks.append(evaluator.aevaluate(
                response=chunk_text,
                chunk_metadata=chunk_metadata
            ))
            evaluator_names.append(name)
        
        # Run all evaluations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        individual_results = {}
        scores = []
        all_passing = True
        
        for name, result in zip(evaluator_names, results):
            if isinstance(result, Exception):
                logger.error(f"{name} evaluation failed: {result}")
                # Create failed result
                individual_results[name] = {
                    "score": 0,
                    "passing": False,
                    "feedback": f"Evaluation failed: {str(result)}",
                    "error": str(result)
                }
                scores.append(0)
                all_passing = False
            else:
                # Extract result data
                individual_results[name] = {
                    "score": int(result.score * 100),  # Convert back to 0-100
                    "passing": result.passing,
                    "feedback": result.feedback
                }
                scores.append(result.score * 100)
                if not result.passing:
                    all_passing = False
        
        # Calculate weighted composite score
        composite_score = sum(
            score * self.weights[name] 
            for name, score in zip(evaluator_names, scores)
        )
        
        # Determine overall passing status
        passing_threshold = 70  # Default composite threshold
        if self.config and hasattr(self.config, 'evaluation'):
            passing_threshold = getattr(self.config.evaluation, 'composite_threshold', 70)
        
        composite_passing = composite_score >= passing_threshold
        
        # Build final result
        eval_time = time.time() - start_time
        
        return {
            "composite_score": round(composite_score, 1),
            "composite_passing": composite_passing,
            "all_evaluators_passing": all_passing,
            "individual_results": individual_results,
            "weights": self.weights,
            "evaluation_time_seconds": round(eval_time, 2),
            "chunk_metadata": {
                "heading": chunk_metadata.get("heading", ""),
                "text_preview": chunk_text,  # Store the actual chunk text for reports
                "chunk_index": chunk_metadata.get("chunk_index", 0),  # Include chunk index
                "char_count": len(chunk_text),
                "word_count": len(chunk_text.split())
            }
        }
    
    async def evaluate_all(self, nodes: List[TextNode]) -> List[Dict[str, Any]]:
        """Evaluate multiple nodes.
        
        Args:
            nodes: List of TextNodes to evaluate
            
        Returns:
            List of evaluation results
        """
        logger.info(f"Evaluating {len(nodes)} nodes with V3 composite evaluator")
        
        # Ensure chunk indices are set
        for i, node in enumerate(nodes):
            if node.metadata is None:
                node.metadata = {}
            if 'chunk_index' not in node.metadata:
                node.metadata['chunk_index'] = i
        
        # Evaluate all nodes
        tasks = [self.evaluate_node(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Node {i} evaluation failed: {result}")
                final_results.append({
                    "error": str(result),
                    "composite_score": 0,
                    "composite_passing": False
                })
            else:
                final_results.append(result)
        
        # Log summary
        passing_count = sum(1 for r in final_results if r.get("composite_passing", False))
        avg_score = sum(r.get("composite_score", 0) for r in final_results) / len(final_results) if final_results else 0
        
        logger.info(
            f"Evaluation complete: {passing_count}/{len(nodes)} passing, "
            f"average score: {avg_score:.1f}"
        )
        
        return final_results
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> str:
        """Generate a summary of evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Markdown summary string
        """
        if not results:
            return "No results to summarize."
        
        # Calculate statistics
        total_chunks = len(results)
        passing_chunks = sum(1 for r in results if r.get("composite_passing", False))
        avg_score = sum(r.get("composite_score", 0) for r in results) / total_chunks
        
        # Calculate per-evaluator stats
        evaluator_stats = {}
        for name in self.evaluators.keys():
            scores = [
                r["individual_results"][name]["score"] 
                for r in results 
                if name in r.get("individual_results", {})
            ]
            if scores:
                evaluator_stats[name] = {
                    "avg_score": sum(scores) / len(scores),
                    "passing": sum(
                        1 for r in results 
                        if r.get("individual_results", {}).get(name, {}).get("passing", False)
                    )
                }
        
        # Build summary
        lines = [
            "# Evaluation Summary (V3)",
            "",
            f"**Total Chunks Evaluated:** {total_chunks}",
            f"**Passing Chunks:** {passing_chunks}/{total_chunks} ({passing_chunks/total_chunks*100:.1f}%)",
            f"**Average Composite Score:** {avg_score:.1f}/100",
            "",
            "## Individual Evaluator Performance",
            ""
        ]
        
        for name, stats in evaluator_stats.items():
            lines.append(f"### {name.replace('_', ' ').title()}")
            lines.append(f"- Average Score: {stats['avg_score']:.1f}/100")
            lines.append(f"- Passing: {stats['passing']}/{total_chunks}")
            lines.append("")
        
        return "\n".join(lines)