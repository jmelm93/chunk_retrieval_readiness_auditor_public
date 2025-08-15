# Evaluators V2: Pydantic Structured Output Implementation

## Overview

This is a refactored version of the chunk evaluators using **Pydantic models** and **OpenAI's structured output** features. This implementation provides type safety, better validation, self-documenting code, and significantly reduced complexity compared to manual JSON parsing.

## Key Improvements

### 1. **Pydantic Models for All Responses**
- Every evaluator uses strongly-typed Pydantic models
- Field descriptions provide context to both developers AND the AI
- Built-in validation ensures data consistency
- ~40% less code than the original implementation

### 2. **OpenAI Structured Outputs**
```python
# Direct Pydantic model parsing with guaranteed structure
response = await client.beta.chat.completions.parse(
    model=self.model,
    messages=messages,
    response_format=QueryAnswerResult,  # Pydantic model
    temperature=0.1
)
result = response.choices[0].message.parsed  # Type-safe result
```

### 3. **Built-in Formatting Methods**
Every result model includes:
- `as_markdown(options)` - Generate formatted markdown with verbosity control
- `as_json_summary()` - Create concise JSON summaries
- `as_json()` - Full model serialization

### 4. **Configurable Output Formatting**
```python
options = FormattingOptions(
    filter_output=True,      # Limit lists to top items
    verbosity="concise",     # concise/normal/detailed
    max_items=3              # Max items in filtered lists
)
```

## Directory Structure

```
evaluators_v2/
├── base/                    # Base classes and shared models
│   ├── base_evaluator.py   # Abstract evaluator with OpenAI integration
│   └── models.py           # BaseEvaluationResult, FormattingOptions
│
├── query_answer/           # Query-Answer Completeness
│   ├── evaluator.py       # Evaluator implementation
│   └── models.py          # QueryAnswerResult, QueryEvaluation
│
├── llm_rubric/            # LLM Rubric Quality
│   ├── evaluator.py
│   └── models.py          # LLMRubricResult, RubricScores
│
├── entity_focus/          # Entity Focus & Coherence
│   ├── evaluator.py
│   └── models.py          # EntityFocusResult, EntityInfo
│
├── structure_quality/     # Structure Quality Analysis
│   ├── evaluator.py
│   └── models.py          # StructureQualityResult, StructureSignals
│
└── composite/             # Orchestration
    ├── evaluator.py
    └── models.py          # CompositeEvaluationResult
```

## Usage Example

```python
from evaluators_v2.composite.evaluator import CompositeEvaluator
from evaluators_v2.base.models import FormattingOptions

# Initialize with config
evaluator = CompositeEvaluator(config)

# Evaluate a node
result = await evaluator.evaluate_node(text_node)

# Generate formatted output
options = FormattingOptions(filter_output=True, verbosity="normal")
markdown = result.as_markdown(options)
```

## Model Examples

### QueryAnswerResult
```python
class QueryAnswerResult(BaseEvaluationResult):
    query_evaluations: List[QueryEvaluation]  # 3-5 evaluated queries
    chunk_type: ChunkType                     # Definition/Example/Overview/etc
    average_query_score: int                  # Average across queries
    missing_info: List[str]                   # Critical gaps
    strengths: List[str]                      # Key strengths
    weaknesses: List[str]                     # Areas for improvement
    self_containment_issues: List[...]        # Detected issues
```

### Field Descriptions as AI Context
```python
score: int = Field(
    ge=0, le=100,
    description="Contribution score where 70-89 is typical for good chunks, "
                "90+ is exceptional, 50-69 needs improvement"
)
```

## Benefits Over Original Implementation

1. **Type Safety**: Pydantic validates all data at runtime
2. **Self-Documenting**: Field descriptions explain the data model
3. **Consistent Structure**: All evaluators follow the same pattern
4. **Less Code**: No manual JSON parsing or validation
5. **Better AI Integration**: Structured outputs guarantee valid responses
6. **Flexible Formatting**: Built-in markdown/JSON generation with options
7. **Error Handling**: Automatic validation and clear error messages

## Testing

```bash
# Test without API key (Entity Focus, Structure Quality)
python demo_evaluators_v2.py

# Full test with API key
export OPENAI_API_KEY=your-key-here
python test_evaluators_v2.py
```

## Migration Path

The new evaluators are designed to be drop-in replacements:
1. Both versions can coexist during migration
2. Use feature flag to switch between v1 and v2
3. Output format is compatible with existing reporting

## Configuration

Uses the same configuration as v1:
- Model selection with overrides per evaluator
- Configurable weights for composite scoring
- Truncation lengths and thresholds

## Future Enhancements

- Add more sophisticated `as_html()` formatting
- Implement caching for repeated evaluations
- Add streaming support for real-time feedback
- Create evaluation templates for common use cases