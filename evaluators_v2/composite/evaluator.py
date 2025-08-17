"""Composite V2 evaluator with weight normalization, dual feedback, and enhanced orchestration."""

import asyncio
import time
from typing import List, Dict, Any, Optional
from loguru import logger

from llama_index.core.schema import TextNode

from utils.text_converter import convert_to_plain_text, get_text_metadata
from ..query_answer.evaluator import QueryAnswerEvaluatorV2
from ..llm_rubric.evaluator import LLMRubricEvaluatorV2
from ..entity_focus.evaluator import EntityFocusEvaluatorV2
from ..structure_quality.evaluator import StructureQualityEvaluatorV2
from .models import CompositeEvaluationResultV2, CompositeResultSummary, ExportFormatV2, DEFAULT_WEIGHTS, DEFAULT_CLASSIFICATION_THRESHOLDS


class CompositeEvaluatorV2:
    """V2 composite evaluator with enhanced orchestration and dual output support.
    
    Key V2 enhancements:
    - Automatic weight normalization
    - Dual feedback storage (markdown + JSON)
    - Config-driven classification thresholds
    - Enhanced error handling and isolation
    - Comprehensive metadata tracking
    """
    
    def __init__(self, config: Any):
        """Initialize the V2 composite evaluator.
        
        Args:
            config: Configuration object with V2 settings
        """
        self.config = config
        
        # Initialize individual V2 evaluators
        self.evaluators = {}
        
        # Query-Answer V2 Evaluator
        self.evaluators['query_answer'] = QueryAnswerEvaluatorV2(
            weight=self._get_weight('query_answer'),
            config=config
        )
        
        # LLM Rubric V2 Evaluator
        self.evaluators['llm_rubric'] = LLMRubricEvaluatorV2(
            weight=self._get_weight('llm_rubric'),
            config=config
        )
        
        # Entity Focus V2 Evaluator
        self.evaluators['entity_focus'] = EntityFocusEvaluatorV2(
            weight=self._get_weight('entity_focus'),
            config=config
        )
        
        # Structure Quality V2 Evaluator
        self.evaluators['structure_quality'] = StructureQualityEvaluatorV2(
            weight=self._get_weight('structure_quality'),
            config=config
        )
        
        # V2 Enhancement: Normalize weights
        self.weights = self._normalize_weights()
        
        # V2 Enhancement: Get classification thresholds from config
        self.classification_thresholds = self._get_classification_thresholds()
        
        logger.info(f"Composite Evaluator V2 initialized with {len(self.evaluators)} evaluators")
        logger.info(f"Normalized weights: {self.weights}")
        logger.info(f"Classification thresholds: {self.classification_thresholds}")
    
    def _get_weight(self, evaluator_name: str) -> float:
        """Get weight for an evaluator from config or default.
        
        Args:
            evaluator_name: Name of the evaluator
            
        Returns:
            Weight value for the evaluator
        """
        if self.config and hasattr(self.config, 'scoring') and hasattr(self.config.scoring, 'weights'):
            return getattr(self.config.scoring.weights, evaluator_name, DEFAULT_WEIGHTS.get(evaluator_name, 0.25))
        return DEFAULT_WEIGHTS.get(evaluator_name, 0.25)
    
    def _normalize_weights(self) -> Dict[str, float]:
        """Normalize evaluator weights to sum to 1.0.
        
        Returns:
            Dictionary of normalized weights
        """
        raw_weights = {name: evaluator.weight for name, evaluator in self.evaluators.items()}
        total_weight = sum(raw_weights.values()) or 1.0
        
        normalized = {name: weight / total_weight for name, weight in raw_weights.items()}
        
        logger.debug(f"Weight normalization: {raw_weights} -> {normalized}")
        return normalized
    
    def _get_classification_thresholds(self) -> Dict[str, float]:
        """Get classification thresholds from config or defaults.
        
        Returns:
            Dictionary of classification thresholds
        """
        if self.config and hasattr(self.config, 'scoring') and hasattr(self.config.scoring, 'thresholds'):
            return {
                'well_optimized': getattr(self.config.scoring.thresholds, 'well_optimized', DEFAULT_CLASSIFICATION_THRESHOLDS['well_optimized']),
                'needs_work': getattr(self.config.scoring.thresholds, 'needs_work', DEFAULT_CLASSIFICATION_THRESHOLDS['needs_work']),
                'poorly_optimized': getattr(self.config.scoring.thresholds, 'poorly_optimized', DEFAULT_CLASSIFICATION_THRESHOLDS['poorly_optimized'])
            }
        return DEFAULT_CLASSIFICATION_THRESHOLDS.copy()
    
    def _classify_chunk(self, total_score: float) -> str:
        """Classify chunk based on V2 config-driven thresholds.
        
        Args:
            total_score: Total weighted score (0-100)
            
        Returns:
            Classification label
        """
        if total_score >= self.classification_thresholds['well_optimized']:
            return "Well Optimized"
        elif total_score >= self.classification_thresholds['needs_work']:
            return "Needs Work"
        else:
            return "Poorly Optimized"
    
    async def evaluate_node(self, node: TextNode) -> CompositeEvaluationResultV2:
        """Evaluate a single node with all V2 evaluators.
        
        Args:
            node: TextNode to evaluate
            
        Returns:
            CompositeEvaluationResultV2 with comprehensive V2 evaluation
        """
        start_time = time.time()
        
        # V2 Enhancement: Convert to plain text with structure preservation
        plain_text = convert_to_plain_text(node.text, preserve_structure=True)
        text_metadata = get_text_metadata(plain_text)
        
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
        
        # V2 Enhancement: Run all evaluators concurrently with enhanced error handling
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
        
        # V2 Enhancement: Process results with enhanced error isolation
        scores = {}
        feedback_markdown = {}
        feedback_json = {}
        evaluation_metadata = {}
        
        for (name, evaluator), result in zip(self.evaluators.items(), results):
            if isinstance(result, Exception):
                logger.error(f"Evaluator {name} V2 failed: {result}")
                scores[name] = 0.0
                feedback_markdown[name] = f"Evaluation failed: {str(result)}"
                feedback_json[name] = {"error": str(result), "evaluator": name}
                evaluation_metadata[name] = None
            else:
                scores[name] = result.score  # Already normalized to 0-1
                feedback_markdown[name] = result.feedback
                # For V2, we would extract structured data here if available
                feedback_json[name] = {
                    "evaluator": name,
                    "score": result.score * 100,  # Convert back to 0-100
                    "passing": result.passing,
                    "summary": "Structured data not yet fully implemented"
                }
                evaluation_metadata[name] = None  # Would be populated with V2 metadata
        
        # V2 Enhancement: Calculate weighted total score with normalized weights
        total_score = sum(scores[name] * self.weights[name] for name in scores)
        total_score_pct = total_score * 100
        
        # V2 Enhancement: Classify using config-driven thresholds
        label = self._classify_chunk(total_score_pct)
        passing = total_score_pct >= self.classification_thresholds['needs_work']
        
        # Calculate processing summary
        processing_time = int((time.time() - start_time) * 1000)
        processing_summary = {
            "total_time_ms": processing_time,
            "evaluator_count": len(self.evaluators),
            "successful_evaluations": sum(1 for score in scores.values() if score > 0),
            "failed_evaluations": sum(1 for result in results if isinstance(result, Exception))
        }
        
        # Create V2 composite result
        return CompositeEvaluationResultV2(
            chunk_id=node.id_,
            chunk_index=node.metadata.get('chunk_index', 0),
            heading=node.metadata.get('heading', ''),
            text_preview=node.text,  # Store full text, not preview
            token_count=text_metadata.get('token_count_estimate', len(plain_text.split())),
            feedback_markdown=feedback_markdown,
            feedback_json=feedback_json,
            scores=scores,
            normalized_weights=self.weights,
            total_score=total_score_pct,
            label=label,
            passing=passing,
            entities=node.metadata.get('entities', []),
            metadata={
                'plain_text_length': len(plain_text),
                'original_length': len(node.text),
                'has_html': '<' in node.text and '>' in node.text,
                'text_metadata': text_metadata
            },
            evaluation_metadata=evaluation_metadata,
            processing_summary=processing_summary
        )
    
    async def evaluate_all(self, nodes: List[TextNode]) -> List[CompositeEvaluationResultV2]:
        """Evaluate all nodes concurrently with V2 enhancements.
        
        Args:
            nodes: List of TextNodes to evaluate
            
        Returns:
            List of CompositeEvaluationResultV2
        """
        logger.info(f"Evaluating {len(nodes)} chunks with V2 evaluators")
        
        # Create evaluation tasks for all nodes
        tasks = [self.evaluate_node(node) for node in nodes]
        
        # Execute all evaluations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any failed evaluations and create minimal results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to evaluate chunk {i}: {result}")
                # Create a minimal failed result
                valid_results.append(CompositeEvaluationResultV2(
                    chunk_id=nodes[i].id_,
                    chunk_index=i,
                    heading=nodes[i].metadata.get('heading', ''),
                    text_preview=nodes[i].text,
                    token_count=len(nodes[i].text.split()),
                    feedback_markdown={"error": str(result)},
                    feedback_json={"error": str(result)},
                    scores={},
                    normalized_weights=self.weights,
                    total_score=0.0,
                    label="Evaluation Failed",
                    passing=False,
                    entities=[],
                    metadata={},
                    evaluation_metadata={},
                    processing_summary={"error": str(result)}
                ))
            else:
                valid_results.append(result)
        
        logger.info(f"Successfully evaluated {len(valid_results)} chunks with V2")
        return valid_results
    
    # Compatibility method for V1 interface
    async def evaluate_nodes(self, nodes: List[TextNode]) -> List[CompositeEvaluationResultV2]:
        """Compatibility method - alias for evaluate_all.
        
        Args:
            nodes: List of TextNodes to evaluate
            
        Returns:
            List of CompositeEvaluationResultV2
        """
        return await self.evaluate_all(nodes)
    
    def export_results(self, results: List[CompositeEvaluationResultV2]) -> ExportFormatV2:
        """Export results in V2 format with dual human/machine views.
        
        Args:
            results: List of evaluation results
            
        Returns:
            ExportFormatV2 with comprehensive export data
        """
        if not results:
            return ExportFormatV2(
                summary=CompositeResultSummary(
                    total_chunks=0,
                    passing_chunks=0,
                    average_score=0.0,
                    well_optimized=0,
                    needs_work=0,
                    poorly_optimized=0,
                    score_distribution={},
                    evaluator_averages={},
                    total_processing_time_ms=0,
                    average_processing_time_ms=0.0,
                    retry_statistics={}
                ),
                chunks=results,
                human_readable={},
                machine_readable={},
                export_metadata={}
            )
        
        # Calculate summary statistics
        total_chunks = len(results)
        passing_chunks = sum(1 for r in results if r.passing)
        average_score = sum(r.total_score for r in results) / total_chunks
        
        # Classification counts
        well_optimized = sum(1 for r in results if r.label == "Well Optimized")
        needs_work = sum(1 for r in results if r.label == "Needs Work")  
        poorly_optimized = sum(1 for r in results if r.label == "Poorly Optimized")
        
        # Score distribution
        score_ranges = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for result in results:
            score = result.total_score
            if score <= 20:
                score_ranges["0-20"] += 1
            elif score <= 40:
                score_ranges["21-40"] += 1
            elif score <= 60:
                score_ranges["41-60"] += 1
            elif score <= 80:
                score_ranges["61-80"] += 1
            else:
                score_ranges["81-100"] += 1
        
        # Evaluator averages
        evaluator_averages = {}
        for evaluator_name in self.evaluators.keys():
            scores = [r.scores.get(evaluator_name, 0) * 100 for r in results]
            evaluator_averages[evaluator_name] = sum(scores) / len(scores) if scores else 0
        
        # Processing metrics
        total_processing_time = sum(
            r.processing_summary.get("total_time_ms", 0) for r in results
        )
        average_processing_time = total_processing_time / total_chunks if total_chunks > 0 else 0
        
        summary = CompositeResultSummary(
            total_chunks=total_chunks,
            passing_chunks=passing_chunks,
            average_score=average_score,
            well_optimized=well_optimized,
            needs_work=needs_work,
            poorly_optimized=poorly_optimized,
            score_distribution=score_ranges,
            evaluator_averages=evaluator_averages,
            total_processing_time_ms=total_processing_time,
            average_processing_time_ms=average_processing_time,
            retry_statistics={}  # Would be populated from evaluation metadata
        )
        
        # Create human and machine readable exports
        human_readable = {
            "summary": summary.model_dump(),
            "chunks": [
                {
                    "chunk_id": r.chunk_id,
                    "heading": r.heading,
                    "score": r.total_score,
                    "label": r.label,
                    "feedback": r.feedback_markdown
                }
                for r in results
            ]
        }
        
        machine_readable = {
            "summary": summary.model_dump(),
            "chunks": [r.model_dump() for r in results]
        }
        
        return ExportFormatV2(
            summary=summary,
            chunks=results,
            human_readable=human_readable,
            machine_readable=machine_readable,
            export_metadata={
                "version": "V2",
                "evaluator_weights": self.weights,
                "classification_thresholds": self.classification_thresholds,
                "export_timestamp": time.time()
            }
        )