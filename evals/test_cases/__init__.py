"""Test cases for evaluator validation."""

from .high_quality import HIGH_QUALITY_CASES
from .medium_quality import MEDIUM_QUALITY_CASES
from .low_quality import LOW_QUALITY_CASES
from .extraction_artifacts import EXTRACTION_ARTIFACT_CASES
from .diverse_high_quality import DIVERSE_HIGH_QUALITY_CASES
from .diverse_medium_quality import DIVERSE_MEDIUM_QUALITY_CASES
from .diverse_low_quality import DIVERSE_LOW_QUALITY_CASES
from .diverse_extraction_artifacts import DIVERSE_EXTRACTION_ARTIFACT_CASES

ALL_TEST_CASES = (
    HIGH_QUALITY_CASES +
    MEDIUM_QUALITY_CASES +
    LOW_QUALITY_CASES +
    EXTRACTION_ARTIFACT_CASES +
    DIVERSE_HIGH_QUALITY_CASES +
    DIVERSE_MEDIUM_QUALITY_CASES +
    DIVERSE_LOW_QUALITY_CASES +
    DIVERSE_EXTRACTION_ARTIFACT_CASES
)