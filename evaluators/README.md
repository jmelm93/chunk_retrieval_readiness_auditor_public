# Evaluators: Standardized AI Evaluation Framework

## Overview

Unified evaluator framework using **standardized Pydantic models** and **OpenAI's structured outputs**. All evaluators now use a consistent `StandardizedEvaluationResult` format with emoji-enhanced markdown output and List[str] recommendations.

## Key Features

### 1. **Standardized Output Format**

All evaluators use the same `StandardizedEvaluationResult` model:

```python
class StandardizedEvaluationResult(BaseModel):
    evaluator_name: str                    # Name of evaluator
    overall_score: int                     # Score 0-100
    overall_assessment: str                # Clear assessment
    # score_breakdown: Optional[Dict[str, ScoreBreakdownItem]]  # Optional sub-scores
    strengths: List[str]                   # Key strengths (AI determines count)
    issues: List[str]                      # Key issues (AI determines count)
    recommendations: List[str]             # List of recommendations
    passing: bool                          # Pass/fail threshold
```

### 2. **Emoji-Enhanced Markdown Output**

Consistent visual structure across all evaluators:

```markdown
**Score:** 85/100

**Breakdown:**
• Dimension: 90/100 - explanation

**Score Reasoning:**

📋 **Overall Assessment:**
[Assessment text]

✅ **Strengths:**

- [strength items]

⚠️ **Issues:**

- [issue items]

🎯 **Recommendations:**

- [recommendation items]
```

### 3. **AI-Powered Analysis**

- OpenAI structured outputs ensure consistent format
- AI determines appropriate number of strengths/issues/recommendations
- Sophisticated penalty systems built into prompts
- No manual regex pattern matching

## Current Architecture

```
evaluators/
├── base/                    # Shared models and base classes
│   ├── base_evaluator.py   # BaseStructuredEvaluator
│   └── models.py           # StandardizedEvaluationResult, FormattingOptions
│
├── query_answer/           # Query-Answer Completeness
│   ├── evaluator.py        # QueryAnswerEvaluator
│   └── prompts.py          # AI prompts
│
├── llm_rubric/             # LLM Rubric Quality
│   ├── evaluator.py        # LLMRubricEvaluator
│   └── prompts.py          # AI prompts + few-shot examples
│
├── entity_focus/           # Entity Focus & Coherence
│   ├── evaluator.py        # EntityFocusEvaluator
│   └── prompts.py          # AI prompts
│
├── structure_quality/      # Structure Quality Analysis
│   ├── evaluator.py        # StructureQualityEvaluator
│   └── prompts.py          # AI prompts
│
└── composite/              # Orchestration
    ├── evaluator.py        # CompositeEvaluator
    └── models.py           # CompositeEvaluationResult
```

Each evaluator focuses on a specific aspect of chunk quality:

### 1. **Query-Answer Completeness** (`query_answer/`)

- **Purpose**: Evaluates how well a chunk contributes to answering potential queries
- **Focus**: AI retrieval barriers, self-containment, query contribution
- **Key Features**:
  - Sophisticated graduated penalty system for vague references
  - Quality gates for different barrier types
  - AI determines appropriate query list and scores

### 2. **LLM Rubric Quality** (`llm_rubric/`)

- **Purpose**: Evaluates chunks against LLM accessibility rubric
- **Focus**: Standalone clarity, topic focus, structure, appropriate size
- **Key Features**:
  - 4-dimension scoring system
  - Few-shot examples for consistency
  - Accessibility-first evaluation approach

### 3. **Entity Focus & Coherence** (`entity_focus/`)

- **Purpose**: Evaluates entity extraction and topical coherence
- **Focus**: Entity relevance, specificity, and focus alignment
- **Key Features**:
  - AI-powered entity extraction
  - Focus alignment assessment
  - Concrete vs generic entity evaluation

### 4. **Structure Quality** (`structure_quality/`)

- **Purpose**: Evaluates structural organization and formatting
- **Focus**: Heading quality, formatting effectiveness, scanability
- **Key Features**:
  - HTML/Markdown structure analysis
  - Heading-content alignment checking
  - Readability assessment

## Usage Example

```python
from evaluators.composite.evaluator import CompositeEvaluator
from evaluators.base.models import FormattingOptions

# Initialize composite evaluator
evaluator = CompositeEvaluator(config)

# Evaluate a chunk
result = await evaluator.evaluate_node(text_node)

# Get standardized markdown output
options = FormattingOptions(verbosity="normal")
markdown = result.as_markdown(options)
```

## Key Benefits

### 1. **Unified Output Format**

- Single `StandardizedEvaluationResult` model across all evaluators
- Consistent emoji-enhanced markdown structure
- Standardized List[str] recommendations

### 2. **AI-Powered Intelligence**

- OpenAI structured outputs ensure reliability
- No hardcoded pattern matching
- AI determines appropriate number of items
- Sophisticated penalty systems in prompts

### 3. **Clean Architecture**

- No individual model files per evaluator
- Shared base classes and utilities
- Minimal code duplication
- Easy to extend and maintain

### 4. **Production Ready**

- Comprehensive error handling
- Graceful degradation on failures
- Configurable thresholds and weights
- Type-safe implementation

## Configuration

All evaluators use the same configuration system:

```python
# Model selection with per-evaluator overrides
models:
  default: "gpt-4o-mini"
  overrides:
    query_answer: "gpt-4o"

# Scoring weights (must sum to 1.0)
scoring:
  weights:
    query_answer: 0.25
    llm_rubric: 0.20
    entity_focus: 0.25
    structure_quality: 0.20
```

## Testing

```bash
# Basic functionality test
python main.py

# Full evaluation test suite
python -m evals.runner

# Specific evaluator testing
python -m evals.runner --category=high_quality
```

## Architecture Notes

- **No Legacy Code**: All individual evaluator model files removed for simplicity
- **Standardized Output**: Single result format ensures consistency across all evaluators
- **AI-First Design**: Leverages OpenAI structured outputs for reliable parsing
- **Clean Imports**: Minimal dependencies and clear module boundaries
- **Production Focus**: Built for reliability and maintainability
