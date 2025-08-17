#!/usr/bin/env python3
"""Main entry point for Chunk Auditor V2."""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import load_config
from core.document_loader import EnhancedDocumentLoader
from core.pipeline import ChunkAuditorPipeline
from evaluators_v2.composite.evaluator import CompositeEvaluatorV2
from reporting.report_generator import EnhancedReportGenerator

# Load environment variables
load_dotenv(override=True)

# Configure logging
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

async def analyze_content(content: str, format: str = "html", config=None):
    """
    Analyze content directly.
    
    Args:
        content: Content to analyze
        format: Content format (html, markdown, text)
        config: Configuration object
        
    Returns:
        Analysis results
    """
    if not config:
        config = load_config()
    
    # Initialize components with content preprocessing config
    loader = EnhancedDocumentLoader(
        enable_boundary_analysis=config.content_preprocessing.enabled,
        boundary_analysis_length=config.content_preprocessing.analysis_length,
        boundary_min_confidence=config.content_preprocessing.min_confidence,
        config=config
    )
    pipeline = ChunkAuditorPipeline(config)
    
    # Load document
    logger.info(f"Loading {format} content...")
    document = loader.load_from_content(content, format=format)
    
    # Process through pipeline
    logger.info("Processing through pipeline...")
    nodes = await pipeline.process_document(document)
    
    # Comprehensive evaluation with CompositeEvaluatorV2
    logger.info("Evaluating chunks with V2 composite evaluator...")
    evaluator = CompositeEvaluatorV2(config)
    
    # Evaluate all nodes
    evaluation_results = await evaluator.evaluate_nodes(nodes)
    
    # Convert to export format
    export_data = evaluator.export_results(evaluation_results)
    
    return export_data

async def analyze_url(url: str, config=None):
    """
    Analyze content from a URL.
    
    Args:
        url: URL to analyze
        config: Configuration object
        
    Returns:
        Analysis results
    """
    if not config:
        config = load_config()
    
    # Initialize components with content preprocessing config
    loader = EnhancedDocumentLoader(
        enable_boundary_analysis=config.content_preprocessing.enabled,
        boundary_analysis_length=config.content_preprocessing.analysis_length,
        boundary_min_confidence=config.content_preprocessing.min_confidence,
        config=config
    )
    pipeline = ChunkAuditorPipeline(config)
    
    # Load from URL
    logger.info(f"Loading content from {url}")
    document = loader.load_from_url(url)
    
    # Process through pipeline
    logger.info("Processing through pipeline...")
    nodes = await pipeline.process_document(document)
    
    # Comprehensive evaluation with CompositeEvaluatorV2
    logger.info("Evaluating chunks with V2 composite evaluator...")
    evaluator = CompositeEvaluatorV2(config)
    
    # Evaluate all nodes
    evaluation_results = await evaluator.evaluate_nodes(nodes)
    
    # Convert to export format
    export_data = evaluator.export_results(evaluation_results)
    
    # Add source metadata
    export_data['metadata'] = {
        'source_url': url,
        'analyzed_at': datetime.now().isoformat(),
        'chunk_count': len(evaluation_results),
        'config': {
            'chunking_strategy': config.chunking.strategy,
            'chunk_size': config.chunking.chunk_size
        }
    }
    
    return export_data

def save_results(results: dict, output_dir: str = "output", config=None):
    """
    Save analysis results to files using EnhancedReportGenerator.
    
    Args:
        results: Analysis results
        output_dir: Output directory
        config: Configuration object
    """
    if not config:
        config = load_config()
    
    # Use EnhancedReportGenerator for comprehensive reports
    from evaluators_v2.composite.models import CompositeEvaluationResultV2
    
    # Convert results to CompositeEvaluationResultV2 objects if needed
    if 'chunks' in results and results['chunks']:
        # Check if already in proper format
        first_chunk = results['chunks'][0]
        if not isinstance(first_chunk, dict) or 'total_score' not in first_chunk:
            # Legacy format - use simplified save
            _save_legacy_results(results, output_dir)
            return
        
        # Convert dict results to CompositeEvaluationResultV2 objects
        chunk_results = []
        for chunk_dict in results['chunks']:
            chunk_results.append(CompositeEvaluationResultV2(
                chunk_id=chunk_dict.get('chunk_id', ''),
                chunk_index=chunk_dict.get('chunk_index', 0),
                heading=chunk_dict.get('heading', ''),
                text_preview=chunk_dict.get('text_preview', ''),
                token_count=chunk_dict.get('token_count', 0),
                feedback_markdown=chunk_dict.get('feedback_markdown', chunk_dict.get('feedback', {})),
                feedback_json=chunk_dict.get('feedback_json', {}),
                scores=chunk_dict.get('scores', {}),
                normalized_weights=chunk_dict.get('normalized_weights', {}),
                total_score=chunk_dict.get('total_score', 0),
                label=chunk_dict.get('label', ''),
                passing=chunk_dict.get('passing', False),
                entities=chunk_dict.get('entities', []),
                metadata=chunk_dict.get('metadata', {}),
                evaluation_metadata=chunk_dict.get('evaluation_metadata', {}),
                processing_summary=chunk_dict.get('processing_summary', {})
            ))
        
        # Generate comprehensive reports
        reporter = EnhancedReportGenerator(config)
        files = reporter.generate_report(
            chunk_results,
            output_dir,
            results.get('metadata')
        )
        
        logger.info(f"Reports generated: {', '.join(files.values())}")
    else:
        _save_legacy_results(results, output_dir)

def _save_legacy_results(results: dict, output_dir: str = "output"):
    """Save results in legacy format for backward compatibility."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = os.path.join(output_dir, f"analysis_{timestamp}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"Legacy results saved to {json_file}")

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Chunk Auditor V2 - LLM SEO Optimization Tool"
    )
    parser.add_argument("--url", type=str, help="URL to analyze")
    parser.add_argument("--file", type=str, help="Local file to analyze")
    parser.add_argument("--content", type=str, help="Direct content to analyze")
    parser.add_argument("--format", type=str, default="html", 
                       choices=["html", "markdown", "text"],
                       help="Content format (default: html)")
    parser.add_argument("--output", type=str, default="output",
                       help="Output directory (default: output)")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure debug logging
    if args.debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # Load configuration
    config = load_config(args.config) if args.config else load_config()
    
    try:
        if args.url:
            # Analyze URL
            results = await analyze_url(args.url, config)
            save_results(results, args.output, config)
            
        elif args.file:
            # Analyze file
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine format from extension
            ext = Path(args.file).suffix.lower()
            format_map = {'.html': 'html', '.md': 'markdown', '.txt': 'text'}
            format = format_map.get(ext, args.format)
            
            results = await analyze_content(content, format, config)
            save_results(results, args.output, config)
            
        elif args.content:
            # Analyze direct content
            results = await analyze_content(args.content, args.format, config)
            save_results(results, args.output, config)
            
        else:
            # Run sample test
            logger.info("No input provided. Running sample test...")
            
            sample_content = """
            <h1>Sample Content for Testing</h1>
            <p>This is a sample paragraph about SEO optimization for LLM retrieval.
            Understanding how large language models retrieve and process information
            is crucial for modern content optimization.</p>
            
            <h2>Key Concepts</h2>
            <p>Entity recognition, semantic chunking, and query-answer completeness
            are fundamental concepts in LLM SEO. Content should be structured to
            provide complete, standalone answers to likely queries.</p>
            
            <h2>Best Practices</h2>
            <p>Use clear headings, maintain topic focus, and ensure each content
            chunk can serve as a complete answer. Include relevant entities and
            maintain appropriate content length for optimal retrieval.</p>
            """
            
            results = await analyze_content(sample_content, 'html', config)
            save_results(results, args.output, config)
            
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())