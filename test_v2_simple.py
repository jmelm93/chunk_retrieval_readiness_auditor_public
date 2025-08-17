#!/usr/bin/env python3
"""Simple test for V2 evaluators integration with main.py"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

async def test_v2_main():
    """Test V2 integration through main.py"""
    try:
        print("🧪 Testing V2 Integration...")
        
        # Import main function
        from main import analyze_content
        
        # Test content
        sample_content = """
        <h1>V2 Test Content</h1>
        <p>This is a test paragraph to verify that the V2 evaluators 
        are working correctly. It should be evaluated by all four 
        V2 evaluators: Query-Answer, LLM Rubric, Entity Focus, and 
        Structure Quality.</p>
        
        <h2>Key Features</h2>
        <ul>
        <li>Procedural prompts for deterministic scoring</li>
        <li>Structured evidence tracking</li>
        <li>Enhanced error handling</li>
        </ul>
        """
        
        print("🚀 Running V2 evaluation...")
        results = await analyze_content(sample_content, format='html')
        
        print("✅ V2 evaluation completed!")
        
        # Handle Pydantic model vs dict results
        if hasattr(results, 'summary'):
            print(f"📊 Summary: {results.summary}")
        elif hasattr(results, 'model_dump'):
            # Convert Pydantic model to dict for inspection
            results_dict = results.model_dump()
            print(f"📊 Summary: {results_dict.get('summary', {})}")
        else:
            print(f"📊 Results type: {type(results)}")
        
        # Check if we got V2 results
        chunks = getattr(results, 'chunks', None) or (results.get('chunks', []) if hasattr(results, 'get') else [])
        if chunks:
            chunk = chunks[0]
            chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else chunk
            if 'feedback_markdown' in chunk_dict or 'normalized_weights' in chunk_dict:
                print("✅ V2 results structure detected")
            else:
                print("⚠️ Legacy results structure detected")
        else:
            print("⚠️ No chunks found in results")
        
        return True
        
    except Exception as e:
        print(f"❌ V2 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_v2_main())
    if success:
        print("\n🎉 V2 integration test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 V2 integration test FAILED!")
        sys.exit(1)