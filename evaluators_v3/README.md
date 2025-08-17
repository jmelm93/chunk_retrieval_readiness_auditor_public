# Evaluators V3 - Simplified Architecture for Chunk Evaluation

## Overview

V3 represents a dramatic simplification of the evaluation system, reducing model complexity by 50-70% while maintaining the deterministic methodology from V2. The key innovation is chain-of-thought field ordering that helps AI models build context before scoring.

## Key Improvements Over V2

### Simplified Models (50-70% Less Code)
- **Single score field** - Eliminated `overall_score`, `final_score`, `provisional_score` redundancy
- **Unified issues list** - Merged penalties and issues into one concept
- **No calculated fields** - Removed `penalties_total`, `weighted_score` from models
- **No field synchronization** - Eliminated complex `model_post_init()` logic
- **Cleaner hierarchy** - Base model with minimal extensions

### Chain-of-Thought Field Ordering
Models now follow a logical progression that builds context:
1. **Issues** - Identify problems first
2. **Strengths** - Note positive aspects
3. **Assessment** - Synthesize findings
4. **Recommendations** - Suggest improvements
5. **Score** - Calculate informed by prior analysis
6. **Passing** - Final determination

This ordering helps the AI reason through the evaluation before assigning scores.

### Architecture Simplifications
- **Base model reuse** - LLM Rubric and Structure Quality use base model directly
- **Minimal extensions** - Query-Answer and Entity Focus add only 2-3 fields
- **Single output format** - No dual markdown/JSON complexity
- **Cleaner composite** - Simple weighted average without complex metadata

## Directory Structure

```
evaluators_v3/
├── base/
│   ├── models.py          # BaseEvaluationResult, Issue (60 lines vs 120 in V2)
│   └── base_evaluator.py  # Simplified base class (180 lines vs 340 in V2)
├── query_answer/
│   ├── models.py          # 15 lines (vs 95 in V2)
│   ├── prompts.py         # Same proven prompts, reordered
│   └── evaluator.py       # Simplified logic
├── entity_focus/
│   ├── models.py          # 20 lines (vs 85 in V2)
│   ├── prompts.py         # Same prompts, reordered
│   └── evaluator.py       # Simplified logic
├── llm_rubric/
│   ├── prompts.py         # Same prompts, reordered
│   └── evaluator.py       # Uses BaseEvaluationResult directly
├── structure_quality/
│   ├── prompts.py         # Same prompts, reordered
│   └── evaluator.py       # Uses BaseEvaluationResult directly
└── composite/
    └── evaluator.py       # Simplified orchestrator (200 lines vs 400 in V2)
```

## Model Architecture

### Base Model (Used by All)
```python
class Issue:
    barrier_type: str        # Type of issue found
    severity: str           # minor|moderate|severe
    description: str        # Human-readable explanation
    evidence: Optional[str] # Text excerpt

class BaseEvaluationResult:
    # Analysis fields (first)
    issues: List[Issue]     # Problems found
    strengths: List[str]    # Positive aspects
    
    # Synthesis fields (second)
    assessment: str         # Overall assessment
    recommendations: List[str]  # Improvements
    
    # Scoring fields (last)
    score: int             # 0-100 score
    passing: bool          # Pass/fail
```

### Minimal Extensions
```python
# Query-Answer adds only:
chunk_type: str
likely_queries: List[str]

# Entity Focus adds only:
primary_entities: List[Entity]
primary_topic: str
entity_coverage: float

# LLM Rubric: Uses base model as-is
# Structure Quality: Uses base model as-is
```

## Usage

V3 evaluators maintain the same interface as V2:

```python
from evaluators_v3.composite.evaluator import CompositeEvaluatorV3

# Initialize
evaluator = CompositeEvaluatorV3(config)

# Evaluate nodes
results = await evaluator.evaluate_all(nodes)

# Generate summary
summary = evaluator.generate_summary(results)
```

## Migration from V2

### What Changed
- **Models** - Dramatically simplified, no duplicate fields
- **Field ordering** - Optimized for chain-of-thought reasoning
- **Scoring logic** - Moved from models to evaluators
- **Base class** - Removed unnecessary methods

### What Stayed the Same
- **Prompts** - Proven V2 prompts, just reordered
- **Methodology** - Same deterministic barrier-based scoring
- **Interface** - Compatible with existing code
- **Weights** - Same evaluator weighting system

### Migration Steps
1. Update imports from `evaluators_v2` to `evaluators_v3`
2. If accessing model fields, note simplified structure
3. Test with existing evaluation suite
4. Verify scores are within ±5 points of V2

## Configuration

Same configuration as V2:

```yaml
evaluation:
  thresholds:
    query_answer: 75
    llm_rubric: 70
    entity_focus: 70
    structure_quality: 70
    composite_threshold: 70
```

## Benefits of V3

### For Developers
- **Easier to understand** - Clear, simple models
- **Easier to maintain** - No complex synchronization
- **Easier to extend** - Just add fields to base model
- **Less bug-prone** - No duplicate fields to sync

### For Performance
- **Faster evaluation** - Less model overhead
- **Better reasoning** - Chain-of-thought ordering
- **Same accuracy** - Maintains V2's determinism
- **Cleaner output** - Single unified format

### Code Metrics
- **50-70% less model code**
- **40% less base evaluator code**
- **60% less composite code**
- **Zero complex post-init logic**

## Testing

Test V3 evaluators against V2 for compatibility:

```bash
# Run evaluation suite
python -m evals.runner

# Compare V2 vs V3 scores
python compare_evaluators.py
```

Expected: V3 scores within ±5 points of V2 scores.

## Design Principles

1. **Simplicity First** - Remove all unnecessary complexity
2. **Chain-of-Thought** - Order fields for logical reasoning
3. **Single Source of Truth** - One field for each concept
4. **Separation of Concerns** - Models hold data, evaluators calculate
5. **Proven Prompts** - Keep what works from V2

## Future Improvements

- Add caching for repeated evaluations
- Support for batch processing
- Streaming evaluation results
- Custom issue types per evaluator
- Configurable severity thresholds

## Summary

V3 achieves the same evaluation quality as V2 with dramatically simpler code. By removing redundancy, optimizing field ordering, and separating concerns properly, V3 is easier to understand, maintain, and extend while maintaining backward compatibility.