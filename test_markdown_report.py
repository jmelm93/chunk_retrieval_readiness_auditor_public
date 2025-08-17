#!/usr/bin/env python3
"""Test script to verify V3 generates full markdown reports."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv(override=True)

# Add to path for imports
sys.path.append(str(Path(__file__).parent))

from main import analyze_content, save_results
from config import load_config


async def test_markdown_generation():
    """Test that V3 generates full markdown reports with all sections."""
    
    # Sample content to test
    test_content = """
    <h1>Introduction to Machine Learning</h1>
    
    <p>Machine learning is a subset of artificial intelligence that enables systems 
    to learn and improve from experience without being explicitly programmed. It focuses on 
    developing algorithms that can analyze data, identify patterns, and make decisions with 
    minimal human intervention.</p>
    
    <h2>Types of Machine Learning</h2>
    
    <p>There are three main types of machine learning:</p>
    
    <ul>
        <li><strong>Supervised Learning:</strong> The algorithm learns from labeled training data</li>
        <li><strong>Unsupervised Learning:</strong> The algorithm finds patterns in unlabeled data</li>
        <li><strong>Reinforcement Learning:</strong> The algorithm learns through trial and error</li>
    </ul>
    
    <h2>Applications</h2>
    
    <p>Machine learning has numerous applications across various industries:</p>
    
    <ul>
        <li>Healthcare: Disease diagnosis and drug discovery</li>
        <li>Finance: Fraud detection and risk assessment</li>
        <li>Transportation: Autonomous vehicles and route optimization</li>
        <li>E-commerce: Recommendation systems and customer segmentation</li>
    </ul>
    
    <h2>Getting Started</h2>
    
    <p>To begin with machine learning, you should understand:</p>
    
    <ol>
        <li>Basic statistics and probability</li>
        <li>Linear algebra fundamentals</li>
        <li>Programming skills (Python is recommended)</li>
        <li>Data preprocessing techniques</li>
    </ol>
    
    <p>Popular machine learning libraries include scikit-learn, TensorFlow, and PyTorch.</p>
    """
    
    # Load config
    config = load_config()
    
    logger.info("Starting markdown report generation test...")
    
    try:
        # Analyze content
        results = await analyze_content(test_content, format="html", config=config)
        
        # Save results (this should generate full markdown report)
        output_dir = "test_output"
        save_results(results, output_dir, config)
        
        # Check if markdown file was created
        md_files = list(Path(output_dir).glob("*.md"))
        
        if md_files:
            logger.info(f"✅ Markdown report generated: {md_files[0]}")
            
            # Read and check content
            with open(md_files[0], 'r') as f:
                content = f.read()
            
            # Check for expected sections
            expected_sections = [
                "# Chunk Retrieval Readiness Audit Report",
                "## Executive Summary",
                "## Chunk Performance Overview",
                "## Detailed Chunk Analysis",
                "Score Breakdown",
                "Full Content",
                "Query-Answer",
                "LLM Rubric",
                "Structure Quality",
                "Entity Focus"
            ]
            
            missing_sections = []
            for section in expected_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                logger.warning(f"⚠️ Missing sections: {missing_sections}")
            else:
                logger.info("✅ All expected sections found in markdown report!")
            
            # Display a snippet
            logger.info("\nFirst 1000 characters of report:")
            logger.info("-" * 50)
            print(content[:1000])
            logger.info("-" * 50)
            
            return True
        else:
            logger.error("❌ No markdown file was generated!")
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    # Run test
    success = asyncio.run(test_markdown_generation())
    
    if success:
        logger.info("\n✅ Markdown report generation test passed!")
    else:
        logger.error("\n❌ Markdown report generation test failed!")
        sys.exit(1)