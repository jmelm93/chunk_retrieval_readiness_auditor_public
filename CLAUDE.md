# Chunk Auditor - AI Assistant Guidelines

## Project Overview

**Purpose**: Evaluate web content for AI retrieval readiness across 4 dimensions:

- Query-Answer completeness
- Entity focus & coherence
- LLM rubric quality
- Structure quality

**Tech Stack**: Python 3.11+ • LlamaIndex • OpenAI API • Firecrawl • Voyage AI (optional)

## Project Structure

```
.
├── config/              # YAML config + dataclass handlers
├── core/                # Document loading, processing pipeline
├── evaluators/          # AI evaluators with Pydantic models
│   ├── base/            # Base classes and shared models
│   ├── query_answer/    # Query-Answer completeness
│   │   ├── prompts.py   # Evaluation prompts
│   │   └── evaluator.py
│   ├── llm_rubric/      # LLM rubric quality
│   │   ├── prompts.py   # Evaluation prompts + few-shot
│   │   └── evaluator.py
│   ├── entity_focus/    # Entity extraction & focus
│   │   ├── prompts.py   # Evaluation prompts
│   │   └── evaluator.py
│   ├── structure_quality/ # Structure assessment
│   │   ├── prompts.py   # Evaluation prompts
│   │   └── evaluator.py
│   └── composite/       # Orchestrator for all evaluators
├── evals/               # Evaluation test framework
│   ├── test_cases/      # Hardcoded test chunks
│   ├── runner.py        # Test runner
│   └── README.md        # Eval documentation
├── extractors/          # Content boundary analyzer
├── reporting/           # Report generation
└── main.py             # CLI entry point
```

## Quick Start

```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt

# Run analysis
python main.py --url "https://example.com"  # Analyze URL
python main.py --file "content.html"        # Analyze file
python main.py                              # Test with sample

# Run evaluations
python -m evals.runner                      # Test all evaluators
python -m evals.runner --category=high_quality  # Test specific category

# Debug
python main.py --debug --url "..."          # Verbose logging
```

## Core Principles

**IMPORTANT**: This tool evaluates chunks for multi-chunk RAG retrieval:

- 3-5 chunks typically retrieved together
- Each chunk = focused contribution, not exhaustive
- "Standalone" = understandable, not complete
- Different chunk types serve different purposes

## Development Guidelines

### Code Conventions

- **Imports**: Group stdlib → third-party → local. NEVER use `from module import *`
- **Async**: All evaluators use `async def aevaluate()`. Use `asyncio.gather()` for concurrency
- **Errors**: Degrade gracefully. Log with `logger.error()`, return default scores on failure
- **Models**: `@dataclass` for simple, Pydantic for OpenAI outputs

### Prompts Organization

- **ALWAYS** keep prompts in dedicated `prompts.py` files
- Each evaluator directory has its own prompts module
- System prompts, user templates, and few-shot examples separated
- No prompts in evaluator logic files

## Key Components

### Configuration (`config/config.yaml`)

**IMPORTANT**: ALL values must be configurable - no hardcoding!

- Model settings: `models.default` and `models.overrides`
- Scoring weights: `scoring.weights` (must sum to 1.0)
- Content preprocessing: boundary detection, filtering

### Evaluators (`evaluators/*/`)

- Each has `evaluator.py` (logic) and `prompts.py` (AI prompts)
- All use structured Pydantic outputs
- Concurrent execution via composite evaluator
- MUST handle extraction artifacts (author bylines, timestamps, social buttons)

### Evaluation Tests (`evals/`)

- 20 hardcoded test cases across 4 categories
- Validates evaluator behavior with tolerance ranges
- Run with: `python -m evals.runner`

## Configuration

### Required Environment Variables

```bash
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
```

### Adding Config Values

1. Add to `config/config.yaml`
2. Update dataclass in `config_handler.py`
3. Access: `config.section.property`

**NEVER** hardcode values - use config!

## Common Tasks

### Add New Evaluator

1. Create directory in `evaluators/your_evaluator/`
2. Add `evaluator.py` (inherit from `BaseStructuredEvaluator`)
3. Add `prompts.py` with system/user prompts
4. Register in `CompositeEvaluator.__init__()`
5. Update weights in `config.yaml`
6. Add test cases in `evals/test_cases/`

### Run Evaluation Tests

```bash
python -m evals.runner                    # All tests
python -m evals.runner --category=high_quality  # Category
python -m evals.runner --verbose          # Detailed output
```

### Modify Prompts

**IMPORTANT**: Before modifying any prompts, review [GPT-5 Prompt Engineering Best Practices](docs/CLAUDE_EVALUATORS_PROMPT_ENGINEERING.md) for current standards on structured outputs and prompt design.

1. Edit relevant `evaluators/*/prompts.py`
2. Follow structured outputs best practices (see documentation above)
3. Run evals to verify behavior: `python -m evals.runner`
4. Adjust expected scores if needed in `evals/test_cases/`

**Key Prompt Guidelines:**

- Focus prompts on evaluation logic only, not output format
- Let Pydantic Field descriptions handle all format requirements
- End prompts with: "Provide structured data per schema"
- Never include OUTPUT FORMAT sections in prompts

## Testing & Validation

### Run Evaluation Suite

```bash
# Full eval suite - validates all evaluators
python -m evals.runner

# Check specific behavior
python -m evals.runner --category=extraction_artifacts
```

### Pre-Commit Checklist

- [ ] Run `python main.py` (basic smoke test)
- [ ] Run `python -m evals.runner` (evaluator validation)
- [ ] No hardcoded values (check for string literals)
- [ ] Prompts in `prompts.py` files only
- [ ] Async/await properly used

## Code Patterns

### ✅ Correct Patterns

```python
# Config access
model = config.models.overrides.get('llm_rubric', config.models.default)

# Error handling with graceful degradation
try:
    result = await evaluator.aevaluate(...)
except Exception as e:
    logger.error(f"Evaluator failed: {e}")
    result = EvaluationResult(score=0.0, passing=False)

# Concurrent async execution
tasks = [eval.aevaluate(node) for eval in evaluators]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### ❌ Never Do

```python
model = "gpt-5-mini"  # Hardcoded value
await evaluator.aevaluate(...)  # No error handling
for eval in evaluators:  # Sequential instead of concurrent
    await eval.aevaluate(node)
```

## Debugging

### Common Issues & Fixes

| Issue                          | Fix                                      |
| ------------------------------ | ---------------------------------------- |
| "model hardcoded"              | Search for string literals, use config   |
| "truncated content"            | Check `text_preview` stores full text    |
| "API timeout"                  | Increase timeout in config               |
| "evaluator scores off"         | Run `python -m evals.runner` to validate |
| "extraction artifacts flagged" | Check prompts ignore web elements        |

### Debug Commands

```bash
# Check config
python -c "from config import load_config; print(load_config().models.default)"

# Test evaluator loading
python -c "from evaluators.query_answer import QueryAnswerEvaluator; print('OK')"

# Verify API keys
python -c "import os; print('APIs:', bool(os.getenv('OPENAI_API_KEY')))"
```

## Critical Rules

**ALWAYS**:

- Store ALL values in config - NO hardcoding
- Keep prompts in `prompts.py` files
- Handle errors gracefully
- Run evals after prompt changes
- Store full text, never truncate

**NEVER**:

- Hardcode API keys, models, or thresholds
- Put prompts in evaluator logic
- Flag web artifacts (author bylines, timestamps) as issues
- Use synchronous code in evaluators
- Commit without running tests

## Extraction Artifacts to Ignore (Keep In Mind for Prompt Engineering on Evaluators)

The evaluators MUST ignore these web extraction artifacts:

- Author metadata (names, bios, "Written by")
- Timestamps ("Published", "Updated on")
- Social buttons ("Share", "Tweet", "FacebookTwitterLinkedIn")
- Navigation elements (breadcrumbs, menus)
- Newsletter signups and CTAs
- View counts, read times
- Footer elements

These are NOT content quality issues - they're normal web elements.
