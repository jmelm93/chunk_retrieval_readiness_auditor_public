"""Evaluation comparison logic for test cases."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .expectations.expected_scores import (
    get_tolerance,
    classify_deviation,
    DEFAULT_TOLERANCE
)


@dataclass
class EvaluationResult:
    """Result of comparing actual vs expected scores."""
    test_id: str
    test_name: str
    category: str
    passed: bool
    evaluator_scores: Dict[str, dict]  # evaluator -> {actual, expected, passed, deviation}
    overall_score: float
    overall_expected: dict
    overall_passed: bool
    issues: List[str]
    timestamp: str


class EvalComparator:
    """Compares actual evaluation results with expected ranges."""
    
    def __init__(self, tolerance_override: Optional[int] = None):
        """Initialize the comparator.
        
        Args:
            tolerance_override: Optional tolerance to use instead of defaults
        """
        self.tolerance_override = tolerance_override
        
    def compare_score(self, 
                     actual: float, 
                     expected: dict,
                     evaluator_name: str = "overall") -> dict:
        """Compare a single score against expected range.
        
        Args:
            actual: Actual score (0-100)
            expected: Dict with 'min' and 'max' keys
            evaluator_name: Name of evaluator for tolerance lookup
            
        Returns:
            Dict with comparison results
        """
        tolerance = self.tolerance_override or get_tolerance(evaluator_name)
        
        # Adjust expected range with tolerance
        adjusted_min = max(0, expected["min"] - tolerance)
        adjusted_max = min(100, expected["max"] + tolerance)
        
        # Check if within range
        passed = adjusted_min <= actual <= adjusted_max
        
        # Classify deviation
        deviation = classify_deviation(actual, adjusted_min, adjusted_max)
        
        # Calculate distance from expected
        if actual < adjusted_min:
            distance = adjusted_min - actual
        elif actual > adjusted_max:
            distance = actual - adjusted_max
        else:
            distance = 0
            
        return {
            "actual": actual,
            "expected": expected,
            "adjusted_range": {"min": adjusted_min, "max": adjusted_max},
            "passed": passed,
            "deviation": deviation,
            "distance": distance,
            "notes": expected.get("notes", "")
        }
    
    def compare_test_case(self, test_case: dict, actual_results: dict) -> EvaluationResult:
        """Compare a complete test case against actual results.
        
        Args:
            test_case: Test case with expected scores
            actual_results: Actual evaluation results
            
        Returns:
            EvaluationResult with detailed comparison
        """
        issues = []
        evaluator_scores = {}
        
        # Compare each evaluator
        for evaluator_name, expected in test_case["expected"].items():
            if evaluator_name == "overall":
                continue
                
            actual_score = actual_results.get("scores", {}).get(evaluator_name, 0) * 100
            comparison = self.compare_score(actual_score, expected, evaluator_name)
            evaluator_scores[evaluator_name] = comparison
            
            if not comparison["passed"]:
                severity = comparison["deviation"]
                issues.append(
                    f"{evaluator_name}: {severity} deviation - "
                    f"expected {expected['min']}-{expected['max']}, "
                    f"got {actual_score:.1f}"
                )
        
        # Compare overall score
        overall_actual = actual_results.get("total_score", 0)
        overall_expected = test_case["expected"]["overall"]
        overall_comparison = self.compare_score(overall_actual, overall_expected, "overall")
        
        if not overall_comparison["passed"]:
            severity = overall_comparison["deviation"]
            issues.append(
                f"Overall: {severity} deviation - "
                f"expected {overall_expected['min']}-{overall_expected['max']}, "
                f"got {overall_actual:.1f}"
            )
        
        # Determine if test passed
        passed = overall_comparison["passed"] and all(
            score["deviation"] != "critical" 
            for score in evaluator_scores.values()
        )
        
        return EvaluationResult(
            test_id=test_case["id"],
            test_name=test_case["name"],
            category=test_case["category"],
            passed=passed,
            evaluator_scores=evaluator_scores,
            overall_score=overall_actual,
            overall_expected=overall_expected,
            overall_passed=overall_comparison["passed"],
            issues=issues,
            timestamp=datetime.now().isoformat()
        )
    
    def generate_summary(self, results: List[EvaluationResult]) -> dict:
        """Generate a summary of evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Summary dictionary
        """
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        
        # Group by category
        by_category = {}
        for result in results:
            if result.category not in by_category:
                by_category[result.category] = {"passed": 0, "total": 0}
            by_category[result.category]["total"] += 1
            if result.passed:
                by_category[result.category]["passed"] += 1
        
        # Find common issues
        evaluator_issues = {}
        for result in results:
            for evaluator, score_data in result.evaluator_scores.items():
                if score_data["deviation"] in ["major", "critical"]:
                    if evaluator not in evaluator_issues:
                        evaluator_issues[evaluator] = 0
                    evaluator_issues[evaluator] += 1
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "by_category": by_category,
            "evaluator_issues": evaluator_issues,
            "timestamp": datetime.now().isoformat()
        }