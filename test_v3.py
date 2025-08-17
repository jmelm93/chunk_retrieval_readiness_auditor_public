#!/usr/bin/env python3
"""Quick test script for V3 evaluators."""

import asyncio
import os
from dotenv import load_dotenv
from loguru import logger
from llama_index.core.schema import TextNode

# Load environment variables
load_dotenv(override=True)

# Import V3 evaluators
from config import load_config
from evaluators_v3 import CompositeEvaluatorV3


async def test_v3_evaluators():
    """Test V3 evaluators with sample chunks."""
    
    # Load config
    config = load_config()
    
    # Initialize V3 composite evaluator
    evaluator = CompositeEvaluatorV3(config)
    
    # Test chunks
    test_chunks = [
        {
            "heading": "Introduction to Python",
            "text": """Python is a high-level, interpreted programming language known for its simplicity 
            and readability. Created by Guido van Rossum and first released in 1991, Python has become 
            one of the most popular programming languages in the world.
            
            Key features of Python include:
            - Easy-to-learn syntax that emphasizes readability
            - Support for multiple programming paradigms
            - Extensive standard library
            - Strong community and ecosystem
            
            Python is widely used in web development, data science, artificial intelligence, 
            scientific computing, and automation."""
        },
        {
            "heading": "Understanding Machine Learning",
            "text": """Machine learning is a subset of artificial intelligence that enables systems 
            to learn and improve from experience without being explicitly programmed. It focuses on 
            developing algorithms that can analyze data, identify patterns, and make decisions with 
            minimal human intervention.
            
            There are three main types of machine learning:
            1. Supervised Learning: The algorithm learns from labeled training data
            2. Unsupervised Learning: The algorithm finds patterns in unlabeled data
            3. Reinforcement Learning: The algorithm learns through trial and error
            
            Applications of machine learning include image recognition, natural language processing, 
            recommendation systems, and predictive analytics."""
        }
    ]
    
    # Convert to TextNodes
    nodes = [
        TextNode(
            text=chunk["text"],
            metadata={"heading": chunk["heading"]}
        )
        for chunk in test_chunks
    ]
    
    logger.info("Testing V3 evaluators with sample chunks...")
    
    try:
        # Run evaluation
        results = await evaluator.evaluate_all(nodes)
        
        # Display results
        for i, result in enumerate(results):
            logger.info(f"\n{'='*50}")
            logger.info(f"Chunk {i+1}: {test_chunks[i]['heading']}")
            logger.info(f"{'='*50}")
            logger.info(f"Composite Score: {result['composite_score']}/100")
            logger.info(f"Passing: {'✅' if result['composite_passing'] else '❌'}")
            
            # Individual evaluator scores
            logger.info("\nIndividual Evaluator Scores:")
            for name, eval_result in result.get('individual_results', {}).items():
                status = '✅' if eval_result['passing'] else '❌'
                logger.info(f"  {name}: {eval_result['score']}/100 {status}")
            
            logger.info(f"\nEvaluation Time: {result.get('evaluation_time_seconds', 0):.2f}s")
        
        # Generate and display summary
        summary = evaluator.generate_summary(results)
        logger.info(f"\n{'='*50}")
        logger.info("SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(summary)
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment")
        exit(1)
    
    # Run test
    success = asyncio.run(test_v3_evaluators())
    
    if success:
        logger.info("\n✅ V3 evaluators test completed successfully!")
    else:
        logger.error("\n❌ V3 evaluators test failed!")
        exit(1)