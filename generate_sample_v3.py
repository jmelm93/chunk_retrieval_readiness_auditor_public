#!/usr/bin/env python3
"""Generate a sample V3 output for blog.md"""

import asyncio
import os
from dotenv import load_dotenv
from loguru import logger
from llama_index.core.schema import TextNode

# Load environment variables
load_dotenv(override=True)

from config import load_config
from evaluators_v3.composite.evaluator import CompositeEvaluatorV3


async def generate_sample():
    """Generate a sample V3 evaluation for the blog."""
    
    # Sample chunk about backup strategies (similar to the example in blog.md)
    sample_chunk = """### Implementing the 3-2-1 Backup Strategy

The 3-2-1 backup rule is a time-tested strategy that ensures your data remains safe and recoverable. This approach requires maintaining three copies of your critical data: the original plus two backups, stored on two different media types, with one copy kept offsite.

**Why This Strategy Works:**
- **Redundancy**: Multiple copies protect against single points of failure
- **Media Diversity**: Different storage types (local drive, cloud, tape) protect against technology-specific failures
- **Geographic Distribution**: Offsite storage protects against local disasters

**Implementation Steps:**
1. Identify critical data that requires backup
2. Set up automated daily backups to a local external drive
3. Configure weekly backups to cloud storage (Google Drive, Dropbox, AWS S3)
4. Schedule monthly verification of backup integrity
5. Test restoration procedures quarterly

Research shows that businesses following the 3-2-1 rule recover 95% faster from data loss incidents compared to those using single-backup approaches."""
    
    # Load config
    config = load_config()
    
    # Initialize V3 evaluator
    evaluator = CompositeEvaluatorV3(config)
    
    # Create TextNode
    node = TextNode(
        text=sample_chunk,
        metadata={
            "heading": "Implementing the 3-2-1 Backup Strategy",
            "chunk_index": 1
        }
    )
    
    logger.info("Generating V3 sample output...")
    
    try:
        # Evaluate the chunk
        result = await evaluator.evaluate_node(node)
        
        # Print the result structure
        print("\n" + "="*60)
        print("V3 EVALUATION RESULT")
        print("="*60)
        
        # Overall scores
        print(f"\n**Overall Score**: {result['composite_score']}/100")
        print(f"**Passing**: {'✅ Yes' if result['composite_passing'] else '❌ No'}")
        
        # Individual evaluator scores
        print("\n**Score Breakdown**:")
        for name, eval_result in result['individual_results'].items():
            print(f"- {name.replace('_', ' ').title()}: {eval_result['score']}/100")
        
        # Print full feedback from each evaluator
        print("\n" + "="*60)
        print("DETAILED FEEDBACK")
        print("="*60)
        
        for name, eval_result in result['individual_results'].items():
            print(f"\n### {name.replace('_', ' ').title()}")
            print("-" * 40)
            print(eval_result['feedback'])
        
        # Also save to file for reference
        import json
        with open('sample_v3_output.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info("Sample output saved to sample_v3_output.json")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate sample: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment")
        exit(1)
    
    # Run sample generation
    result = asyncio.run(generate_sample())
    
    if result:
        logger.info("\n✅ Sample generation complete!")
    else:
        logger.error("\n❌ Sample generation failed!")
        exit(1)