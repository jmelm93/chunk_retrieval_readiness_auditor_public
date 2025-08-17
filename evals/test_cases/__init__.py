"""Test cases v3 focused on AI chunk retrieval readiness factors."""

from .high_quality import HIGH_QUALITY_CASES
from .medium_quality import MEDIUM_QUALITY_CASES  
from .low_quality import LOW_QUALITY_CASES

# Combine all test cases
ALL_TEST_CASES = (
    HIGH_QUALITY_CASES + 
    MEDIUM_QUALITY_CASES + 
    LOW_QUALITY_CASES
)

# Group by category for easy access
TEST_CASES_BY_CATEGORY = {
    "high_quality": HIGH_QUALITY_CASES,
    "medium_quality": MEDIUM_QUALITY_CASES,
    "low_quality": LOW_QUALITY_CASES
}

__all__ = [
    "HIGH_QUALITY_CASES",
    "MEDIUM_QUALITY_CASES", 
    "LOW_QUALITY_CASES",
    "ALL_TEST_CASES",
    "TEST_CASES_BY_CATEGORY"
]