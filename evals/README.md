# Chunk Auditor Evaluation Framework

This directory contains the evaluation framework for testing and validating the Chunk Auditor's AI evaluators.

## Purpose

The evaluation framework ensures that our AI-powered evaluators behave consistently and correctly across different types of content. It helps:

1. **Catch regressions** when prompts are updated
2. **Validate behavior** on edge cases  
3. **Document expectations** through test cases
4. **Build confidence** in evaluator outputs

## Structure

```
evals/
├── test_cases/           # Test case definitions
│   ├── high_quality.py   # Content expected to score well
│   ├── medium_quality.py # Content with some issues
│   ├── low_quality.py    # Poor quality content
│   └── extraction_artifacts.py # Content with web artifacts
├── expectations/         # Expected score ranges
│   └── expected_scores.py
├── runner.py            # Main test runner
├── evaluator.py         # Comparison logic
└── reports/             # Generated evaluation reports
```

## Running Evaluations

### Run All Tests
```bash
python -m evals.runner
```

### Run Specific Category
```bash
# Run only high quality tests
python -m evals.runner --category=high_quality

# Other categories: medium_quality, low_quality, extraction_artifacts
```

### Generate Detailed Report
```bash
python -m evals.runner --verbose --output=report.md
```

## Understanding Test Cases

Each test case includes:
- **id**: Unique identifier
- **name**: Descriptive name
- **category**: Quality category
- **chunk_heading**: The heading text
- **chunk_text**: The content to evaluate
- **expected**: Score ranges for each evaluator
- **notes**: Explanation of expectations

Example:
```python
{
    "id": "high_001",
    "name": "Well-structured API documentation",
    "category": "high_quality",
    "chunk_heading": "Authentication with API Keys",
    "chunk_text": "...",
    "expected": {
        "query_answer": {"min": 75, "max": 95},
        "llm_rubric": {"min": 70, "max": 90},
        "structure_quality": {"min": 75, "max": 95},
        "entity_focus": {"min": 65, "max": 85},
        "overall": {"min": 70, "max": 90}
    }
}
```

## Tolerance and Scoring

- **Default Tolerance**: ±10 points from expected range
- **Entity Focus**: ±15 points (more variance expected)
- **Pass Criteria**: Score within tolerance range
- **Deviation Levels**:
  - **None**: Within expected range
  - **Minor**: 10-19 points outside range
  - **Major**: 20-29 points outside range  
  - **Critical**: 30+ points outside range

## Test Categories

### High Quality (5 cases)
Content that should score well (70-95):
- API documentation
- FAQ sections
- Product descriptions
- Tutorials
- Technical explanations

### Medium Quality (5 cases)
Content with noticeable issues (45-75):
- Vague references
- Mismatched headings
- Missing entities
- Poor structure
- Generic content

### Low Quality (5 cases)
Poor content with minimal value (0-35):
- Navigation menus
- Footer content
- Extremely short text
- No clear focus
- Missing headings

### Extraction Artifacts (5 cases)
Good content with web artifacts (65-90):
- Author bylines
- Social share buttons
- Newsletter signups
- Navigation breadcrumbs
- Timestamps and metadata

## Adding New Test Cases

1. Choose the appropriate category file in `test_cases/`
2. Add your test case to the list:
```python
{
    "id": "unique_id",
    "name": "Descriptive name",
    "category": "category_name",
    "chunk_heading": "Your Heading",
    "chunk_text": """Your content here""",
    "expected": {
        "query_answer": {"min": 60, "max": 80},
        "llm_rubric": {"min": 65, "max": 85},
        "structure_quality": {"min": 70, "max": 90},
        "entity_focus": {"min": 55, "max": 75},
        "overall": {"min": 65, "max": 85}
    },
    "notes": "Why these scores are expected"
}
```

## Interpreting Results

The evaluation report shows:
- **Summary**: Overall pass rate and statistics
- **Category Breakdown**: Performance by test category
- **Common Issues**: Evaluators frequently outside expectations
- **Detailed Results**: Individual test outcomes with scores

### Pass/Fail Criteria
- **PASS**: Overall score within tolerance AND no critical deviations
- **FAIL**: Overall score outside tolerance OR any critical deviation

## Troubleshooting

### High Failure Rate
- Check if prompts were recently changed
- Review tolerance settings in `expected_scores.py`
- Verify API keys and model availability

### Inconsistent Results
- AI evaluations have natural variance
- Run multiple times to identify patterns
- Consider increasing tolerance for problematic evaluators

### Adding Tolerance
Modify `EVALUATOR_TOLERANCES` in `expectations/expected_scores.py`:
```python
EVALUATOR_TOLERANCES = {
    "query_answer": 10,
    "llm_rubric": 10,
    "structure_quality": 10,
    "entity_focus": 15,  # Higher tolerance
    "overall": 10
}
```

## Best Practices

1. **Run regularly**: After any prompt changes
2. **Review failures**: Understand why tests fail before adjusting expectations
3. **Document changes**: Update test case notes when expectations change
4. **Start conservative**: Begin with wider ranges, tighten as needed
5. **Category balance**: Maintain tests across all quality levels

## Future Enhancements

- [ ] Statistical analysis across multiple runs
- [ ] Automated CI/CD integration
- [ ] Prompt version comparison
- [ ] Performance benchmarking
- [ ] Cross-model evaluation