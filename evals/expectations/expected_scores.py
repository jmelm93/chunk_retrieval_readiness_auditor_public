"""Expected score ranges and tolerance settings for evaluations."""

# Default tolerance for score comparisons (±points from expected range)
DEFAULT_TOLERANCE = 10

# Evaluator-specific tolerances (some evaluators have more variance)
EVALUATOR_TOLERANCES = {
    "query_answer": 10,
    "llm_rubric": 10,
    "structure_quality": 10,
    "entity_focus": 15,  # Entity extraction can vary more
    "overall": 10
}

# Category-level expectations (general ranges)
CATEGORY_EXPECTATIONS = {
    "high_quality": {
        "overall": {"min": 70, "max": 95},
        "description": "Should score well across all dimensions"
    },
    "medium_quality": {
        "overall": {"min": 45, "max": 75},
        "description": "Should have noticeable issues but some value"
    },
    "low_quality": {
        "overall": {"min": 0, "max": 35},
        "description": "Should score poorly - minimal retrieval value"
    },
    "extraction_artifacts": {
        "overall": {"min": 65, "max": 90},
        "description": "Should score well despite artifacts if content is good"
    }
}

# Flags for concerning deviations
DEVIATION_THRESHOLDS = {
    "critical": 30,  # Points outside expected range
    "major": 20,     # Points outside expected range
    "minor": 10      # Points outside expected range
}

def get_tolerance(evaluator_name: str) -> int:
    """Get the tolerance for a specific evaluator.
    
    Args:
        evaluator_name: Name of the evaluator
        
    Returns:
        Tolerance in points
    """
    return EVALUATOR_TOLERANCES.get(evaluator_name, DEFAULT_TOLERANCE)

def get_category_expectation(category: str) -> dict:
    """Get the general expectation for a category.
    
    Args:
        category: Test category name
        
    Returns:
        Dictionary with overall range and description
    """
    return CATEGORY_EXPECTATIONS.get(category, {
        "overall": {"min": 0, "max": 100},
        "description": "Unknown category"
    })

def classify_deviation(actual: float, expected_min: float, expected_max: float) -> str:
    """Classify how far a score deviates from expectations.
    
    Args:
        actual: Actual score
        expected_min: Minimum expected score
        expected_max: Maximum expected score
        
    Returns:
        Deviation level: 'none', 'minor', 'major', or 'critical'
    """
    if expected_min <= actual <= expected_max:
        return "none"
    
    # Calculate distance from expected range
    if actual < expected_min:
        deviation = expected_min - actual
    else:
        deviation = actual - expected_max
    
    if deviation >= DEVIATION_THRESHOLDS["critical"]:
        return "critical"
    elif deviation >= DEVIATION_THRESHOLDS["major"]:
        return "major"
    elif deviation >= DEVIATION_THRESHOLDS["minor"]:
        return "minor"
    else:
        return "none"