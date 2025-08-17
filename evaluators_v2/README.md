# Evaluators V2 - GPT-5 Optimized Chunk Evaluation System

## Overview

This directory contains the V2 implementation of the chunk evaluation system, optimized for GPT-5 with enhanced determinism, auditability, and structured outputs.

## Key Improvements Over V1

- **Deterministic Grading**: Near-identical scores across runs (±2 points)
- **Auditability**: Structured evidence spans for all deductions and barriers
- **Procedural Prompts**: Short, algorithm-focused prompts reduce variance
- **Enhanced Models**: Evaluator-specific Pydantic models with detailed breakdowns
- **Dual Output**: Both human-readable markdown and machine-readable JSON
- **Better Text Processing**: Structure-preserving HTML conversion

## Directory Structure

```
evaluators_v2/
├── shared/                    # Shared utilities and constants
│   ├── ignore_web_artifacts.md    # Single source of truth for extraction artifacts
│   └── text_processing.py         # Enhanced text processing utilities
├── base/                      # Base classes and models
│   ├── base_evaluator_v2.py      # Enhanced base evaluator class
│   └── models.py                  # V2 base models
├── query_answer/              # Query-Answer completeness evaluator
│   ├── evaluator.py               # V2 implementation with penalties
│   ├── prompts.py                 # Procedural prompts
│   └── models.py                  # QueryAnswerEval model
├── llm_rubric/                # LLM rubric quality evaluator
│   ├── evaluator.py               # V2 implementation with dimensions
│   ├── prompts.py                 # Short procedural prompts
│   └── models.py                  # LLMRubricEval model
├── entity_focus/              # Entity focus & coherence evaluator
│   ├── evaluator.py               # V2 implementation with extraction
│   ├── prompts.py                 # Entity-focused prompts
│   └── models.py                  # EntityFocusEval model
├── structure_quality/         # Structure quality evaluator
│   ├── evaluator.py               # V2 implementation with checklist
│   ├── prompts.py                 # Structure-focused prompts
│   └── models.py                  # StructureEval model
└── composite/                 # Composite orchestrator
    ├── evaluator.py               # V2 composite with weight normalization
    └── models.py                  # Enhanced composite models
```

## Core Design Principles

1. **Barrier-First Scoring**: Detection of AI retrieval barriers dominates scoring
2. **Evidence-Based**: All deductions backed by specific text spans
3. **Algorithmic Consistency**: Procedural prompts with explicit steps
4. **Config-Driven**: Per-evaluator thresholds and settings from configuration
5. **Graceful Degradation**: Robust error handling with meaningful fallbacks

## Usage

The V2 evaluators are designed to be drop-in replacements for V1 with the same interface:

```python
from evaluators_v2.composite.evaluator import CompositeEvaluator

# Initialize with config
evaluator = CompositeEvaluator(config)

# Evaluate nodes (same interface as V1)
results = await evaluator.evaluate_all(nodes)
```

## Migration from V1

V2 evaluators can run in parallel with V1 evaluators for validation and comparison. The interface remains compatible while providing enhanced structured outputs.

## Configuration Requirements

Add to `config.yaml`:

```yaml
evaluation:
  thresholds:
    query_answer: 75
    llm_rubric: 70
    entity_focus: 70
    structure_quality: 70
```

## Testing

V2 evaluators include deterministic testing to ensure consistent results across runs:

```bash
python -m evals.runner  # Tests both V1 and V2 evaluators
```