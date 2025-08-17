"""Main runner for the evaluation framework."""

import sys
import asyncio
import argparse
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv(override=True)

# Add parent directory to path to import main project modules
sys.path.append(str(Path(__file__).parent.parent))

from config import load_config
from core.pipeline import ChunkAuditorPipeline
from evaluators_v3.composite.evaluator import CompositeEvaluatorV3
from llama_index.core.schema import TextNode

from .test_cases import ALL_TEST_CASES
from .test_cases.high_quality import HIGH_QUALITY_CASES
from .test_cases.medium_quality import MEDIUM_QUALITY_CASES
from .test_cases.low_quality import LOW_QUALITY_CASES
from .evaluator import EvalComparator, EvaluationResult


class EvalRunner:
    """Runs evaluation test cases through the chunk auditor."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the eval runner.
        
        Args:
            config_path: Optional path to config file
        """
        self.config = load_config(config_path)
        self.pipeline = ChunkAuditorPipeline(self.config)
        self.composite_evaluator = CompositeEvaluatorV3(self.config)
        self.comparator = EvalComparator()
        # Create semaphore for rate limiting concurrent API calls
        self.semaphore = asyncio.Semaphore(self.config.concurrency.max_llm_calls)
        
    async def run_single_test(self, test_case: dict) -> EvaluationResult:
        """Run a single test case.
        
        Args:
            test_case: Test case dictionary
            
        Returns:
            EvaluationResult with comparison
        """
        logger.info(f"Running test: {test_case['id']} - {test_case['name']}")
        
        # Create a TextNode from the test case
        node = TextNode(
            text=test_case["chunk_text"],
            metadata={
                "heading": test_case["chunk_heading"],
                "chunk_index": 0,
                "test_id": test_case["id"],
                "test_category": test_case["category"]
            }
        )
        
        try:
            # Run through the V3 composite evaluator with semaphore for rate limiting
            async with self.semaphore:
                results = await self.composite_evaluator.evaluate_all([node])
            
            if results and len(results) > 0:
                result = results[0]
                
                # Convert V3 format to dictionary for comparison
                actual_results = {
                    "scores": {
                        name: res["score"]
                        for name, res in result.get("individual_results", {}).items()
                    },
                    "total_score": result.get("composite_score", 0),
                    "label": "passing" if result.get("composite_passing") else "failing",
                    "passing": result.get("composite_passing", False)
                }
                
                # Compare with expected
                eval_result = self.comparator.compare_test_case(test_case, actual_results)
                
                return eval_result
            else:
                logger.error(f"No results returned for test {test_case['id']}")
                return EvaluationResult(
                    test_id=test_case["id"],
                    test_name=test_case["name"],
                    category=test_case["category"],
                    passed=False,
                    evaluator_scores={},
                    overall_score=0,
                    overall_expected=test_case["expected"]["overall"],
                    overall_passed=False,
                    issues=["Failed to get evaluation results"],
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Error running test {test_case['id']}: {e}")
            return EvaluationResult(
                test_id=test_case["id"],
                test_name=test_case["name"],
                category=test_case["category"],
                passed=False,
                evaluator_scores={},
                overall_score=0,
                overall_expected=test_case["expected"]["overall"],
                overall_passed=False,
                issues=[f"Error: {str(e)}"],
                timestamp=datetime.now().isoformat()
            )
    
    async def run_category(self, category: str) -> List[EvaluationResult]:
        """Run all tests in a category.
        
        Args:
            category: Category name
            
        Returns:
            List of evaluation results
        """
        # Select test cases
        if category == "high_quality":
            test_cases = HIGH_QUALITY_CASES
        elif category == "medium_quality":
            test_cases = MEDIUM_QUALITY_CASES
        elif category == "low_quality":
            test_cases = LOW_QUALITY_CASES
        else:
            logger.error(f"Unknown category: {category}")
            return []
        
        logger.info(f"Running {len(test_cases)} tests in category: {category}")
        
        # Run all tests concurrently
        tasks = [self.run_single_test(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Filter out any exceptions and convert to proper EvaluationResult
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Test failed with exception: {result}")
                # Create a failed result
                test_case = test_cases[i]
                valid_results.append(EvaluationResult(
                    test_id=test_case["id"],
                    test_name=test_case["name"],
                    category=test_case["category"],
                    passed=False,
                    evaluator_scores={},
                    overall_score=0,
                    overall_expected=test_case["expected"]["overall"],
                    overall_passed=False,
                    issues=[f"Exception: {str(result)}"],
                    timestamp=datetime.now().isoformat()
                ))
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def run_all(self) -> List[EvaluationResult]:
        """Run all test cases.
        
        Returns:
            List of all evaluation results
        """
        logger.info(f"Running all {len(ALL_TEST_CASES)} test cases")
        
        # Run all tests concurrently
        tasks = [self.run_single_test(test_case) for test_case in ALL_TEST_CASES]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Filter out any exceptions and convert to proper EvaluationResult
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Test failed with exception: {result}")
                # Create a failed result
                test_case = ALL_TEST_CASES[i]
                valid_results.append(EvaluationResult(
                    test_id=test_case["id"],
                    test_name=test_case["name"],
                    category=test_case["category"],
                    passed=False,
                    evaluator_scores={},
                    overall_score=0,
                    overall_expected=test_case["expected"]["overall"],
                    overall_passed=False,
                    issues=[f"Exception: {str(result)}"],
                    timestamp=datetime.now().isoformat()
                ))
            else:
                valid_results.append(result)
        
        return valid_results
    
    def generate_report(self, results: List[EvaluationResult], output_path: Optional[str] = None) -> str:
        """Generate a report from evaluation results.
        
        Args:
            results: List of evaluation results
            output_path: Optional path to save report
            
        Returns:
            Report as string
        """
        summary = self.comparator.generate_summary(results)
        
        # Build report
        lines = []
        lines.append("# Chunk Auditor Evaluation Report")
        lines.append(f"Generated: {summary['timestamp']}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append(f"- Total Tests: {summary['total_tests']}")
        lines.append(f"- Passed: {summary['passed']}")
        lines.append(f"- Failed: {summary['failed']}")
        lines.append(f"- Pass Rate: {summary['pass_rate']:.1f}%")
        lines.append("")
        
        # By category
        lines.append("## Results by Category")
        for category, stats in summary['by_category'].items():
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            lines.append(f"- **{category}**: {stats['passed']}/{stats['total']} passed ({pass_rate:.1f}%)")
        lines.append("")
        
        # Common issues
        if summary['evaluator_issues']:
            lines.append("## Evaluator Issues")
            lines.append("Evaluators with major/critical deviations:")
            for evaluator, count in sorted(summary['evaluator_issues'].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- {evaluator}: {count} issues")
            lines.append("")
        
        # Detailed results
        lines.append("## Detailed Results")
        lines.append("")
        
        for result in results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"### {result.test_id}: {result.test_name} [{status}]")
            lines.append(f"**Category**: {result.category}")
            lines.append(f"**Overall Score**: {result.overall_score:.1f} (expected: {result.overall_expected['min']}-{result.overall_expected['max']})")
            
            if result.issues:
                lines.append("**Issues**:")
                for issue in result.issues:
                    lines.append(f"- {issue}")
            
            lines.append("")
            
            # Evaluator scores
            lines.append("**Evaluator Scores**:")
            for evaluator, score_data in result.evaluator_scores.items():
                status = "✓" if score_data['passed'] else "✗"
                lines.append(f"- {evaluator}: {score_data['actual']:.1f} {status} (expected: {score_data['expected']['min']}-{score_data['expected']['max']})")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        report = "\n".join(lines)
        
        # Save if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report)
            logger.info(f"Report saved to: {output_path}")
        
        return report


async def main():
    """Main entry point for the eval runner."""
    parser = argparse.ArgumentParser(description="Run chunk auditor evaluations")
    parser.add_argument(
        "--category",
        choices=["all", "high_quality", "medium_quality", "low_quality"],
        default="all",
        help="Category of tests to run"
    )
    parser.add_argument(
        "--output",
        help="Path to save report (default: evals/reports/eval_TIMESTAMP.md)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--config",
        help="Path to config file"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    if not args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    
    # Initialize runner
    runner = EvalRunner(args.config)
    
    # Run tests
    if args.category == "all":
        results = await runner.run_all()
    else:
        results = await runner.run_category(args.category)
    
    # Generate report
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"evals/reports/eval_{timestamp}.md"
    
    report = runner.generate_report(results, args.output)
    
    # Print summary
    summary = runner.comparator.generate_summary(results)
    print(f"\n{'='*50}")
    print(f"Evaluation Complete!")
    print(f"{'='*50}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}% ({summary['passed']}/{summary['total_tests']})")
    print(f"Report saved to: {args.output}")
    
    # Exit with error code if tests failed
    if summary['passed'] < summary['total_tests']:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())