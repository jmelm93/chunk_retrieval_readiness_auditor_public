# Chunk Auditor V2 - Claude Code Guidelines

## Project Context

**Purpose**: Evaluate web content for AI retrieval readiness by analyzing chunks across 6 dimensions (query-answer, entity focus, LLM rubric, structured data, structure quality, size fit).

**Tech Stack**:

- Python 3.11+
- LlamaIndex (document processing & evaluation)
- OpenAI API (LLM evaluations & entity extraction)
- Firecrawl (web scraping)
- Voyage AI (embeddings, optional)

## Project Structure

```
chunk_auditor_v2/
├── config/              # YAML config + dataclass handlers
├── core/               # Document loading, processing pipeline
├── evaluators/         # [DEPRECATED] Old scoring modules
├── evaluators_v2/      # NEW: Pydantic-based evaluators with structured outputs
│   ├── base/           # Base classes and shared models
│   ├── query_answer/   # Query-Answer completeness evaluator
│   ├── llm_rubric/     # LLM rubric quality evaluator
│   ├── entity_focus/   # Entity focus evaluator
│   ├── structure_quality/ # Structure quality evaluator
│   └── composite/      # Orchestrator for all evaluators
├── extractors/         # Content boundary analyzer
├── reporting/          # JSON/Markdown/Summary generation
└── main.py            # CLI entry point
```

**Note**: The project now uses `evaluators_v2/` which provides Pydantic-based structured outputs with OpenAI integration for better type safety and reduced code complexity.

## Essential Commands

```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt

# Run analysis
python main.py --url "https://example.com"  # Analyze URL
python main.py --file "content.html"        # Analyze file
python main.py                              # Test with sample

# Development
python -m pytest tests/                     # Run tests
pip freeze > requirements.txt               # Update deps

# Debug
python main.py --debug --url "..."          # Verbose logging
```

## RAG Context Philosophy

The tool evaluates chunks as focused contributions in multi-chunk retrieval systems:

- Chunks work together (3-5 typically retrieved)
- Each chunk should be coherent and focused, not exhaustive
- "Standalone" means understandable, not complete
- Different chunk types serve different purposes (definitions, examples, overviews, etc.)
- "General" type serves as catchall for mixed or uncategorized content

## Code Style & Conventions

### Imports

- Use relative imports within package: `from .core import pipeline`
- Group: stdlib, third-party, local
- NEVER use `from module import *`

### Async/Await

- All evaluators use `async def aevaluate()`
- Use `asyncio.gather()` for concurrent operations
- ThreadPoolExecutor fallback for sync-in-async contexts

### Error Handling

- API failures should degrade gracefully (continue with partial results)
- Log errors with `logger.error()`, don't crash
- Return default scores when evaluator fails

### Data Classes

- Use `@dataclass` for simple structures
- Use Pydantic models for OpenAI structured outputs
- Config uses nested dataclasses (see `config_handler.py`)

## Key Files & Their Roles

### config/config.yaml

- **IMPORTANT**: Central config - all hardcoded values should be here
- Model settings under `models:` with override capability
- Scoring weights under `scoring.weights`
- Content preprocessing under `content_preprocessing:`

### core/document_loader.py

- Loads from URL (Firecrawl), file, or direct content
- Applies ContentBoundaryAnalyzer for URL inputs
- Smart truncation at natural boundaries
- **Line 102**: Fallback model should use config.models.default

### evaluators/composite.py

- Orchestrates all evaluators concurrently
- Calculates weighted scores
- Exports results to dict format
- **Line 169**: Now stores full text, not preview

### reporting/report_generator.py

- Generates JSON, Markdown, and Summary reports
- **Line 156**: Shows "Full Content" not "Content Preview"
- Includes terminology section explaining scores

### extractors/content_boundary_analyzer.py

- AI-powered detection of nav/footer boundaries
- Fuzzy matching for header detection
- Only applies to URL-sourced content
- Configurable confidence thresholds

## Configuration Management

### Model Configuration

```yaml
models:
  default: "gpt-5-mini" # Used by all unless overridden
  overrides: # Optional overrides per evaluator
    content_preprocessing: "gpt-5-nano"
    query_answer: "gpt-5"
    llm_rubric: "gpt-4.1"
```

### Adding New Config

1. Add to `config.yaml`
2. Update dataclass in `config_handler.py`
3. Access via `config.section.property`

### Environment Variables

```bash
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
VOYAGE_API_KEY=pa-...
```

## Common Tasks

### Add New Evaluator

1. Create class in `evaluators/` inheriting from `BaseEvaluator`
2. Implement `async def aevaluate()` method
3. Add to `CompositeEvaluator.__init__()`
4. Update scoring weights in config.yaml

### Modify Scoring Weights

1. Edit `config/config.yaml` → `scoring.weights`
2. Weights should sum to 1.0
3. Test impact with `python main.py`

### Debug Content Boundaries

1. Set `content_preprocessing.debug_output: true` in config
2. Check logs for boundary detection details
3. Adjust `min_confidence` if needed (1-5 scale)

### Handle Large Content

1. Adjust `scraping.max_content_length` in config
2. Increase `content_preprocessing.analysis_length` for better boundary detection
3. Consider `chunking.max_chunk_size` for token limits

## Testing & Validation

### Quick Tests

```python
# Test config loading
from config import load_config
config = load_config()
print(config.models.default)

# Test document loader
from core.document_loader import EnhancedDocumentLoader
loader = EnhancedDocumentLoader(config=config)
doc = loader.load_from_content("Test content", format="text")

# Test pipeline
from core.pipeline import ChunkAuditorPipeline
pipeline = ChunkAuditorPipeline(config)
```

### Validation Checklist

- [ ] All API calls use try/except blocks
- [ ] Config values not hardcoded
- [ ] Async methods properly awaited
- [ ] Reports show full text (not truncated)
- [ ] Boundary detection only for URLs

## Important Patterns

### Config Access Pattern

```python
# Good - uses config
model = config.models.overrides.get('llm_rubric', config.models.default)

# Bad - hardcoded
model = "gpt-5-mini"
```

### Error Handling Pattern

```python
try:
    result = await evaluator.aevaluate(...)
except Exception as e:
    logger.error(f"Evaluator failed: {e}")
    result = EvaluationResult(score=0.0, passing=False, feedback=str(e))
```

### Async Execution Pattern

```python
# Concurrent evaluation
tasks = [eval.aevaluate(node) for eval in evaluators]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

## Debugging Tips

### Common Issues

- **"model hardcoded"**: Check for string literals like "gpt-5-mini"
- **"truncated content"**: Ensure `text_preview` stores full text
- **"API timeout"**: Increase timeout in config or use fallback
- **"boundary not detected"**: Check confidence threshold and analysis_length

### Debug Commands

```bash
# See all config values
python -c "from config import load_config; import json; print(json.dumps(load_config().__dict__, default=str, indent=2))"

# Test specific evaluator
python -c "from evaluators_v2.query_answer import QueryAnswerEvaluator; e = QueryAnswerEvaluator(weight=0.25); print('Loaded')"

# Check API connections
python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('Firecrawl:', bool(os.getenv('FIRECRAWL_API_KEY')))"
```

## Workflow Guidelines

### When Making Changes

1. **ALWAYS** check if value should be in config
2. **NEVER** commit hardcoded API keys or models
3. **TEST** with `python main.py` before committing
4. **UPDATE** this file if adding new patterns

### Before Committing

1. Run basic test: `python main.py`
2. Check no hardcoded values remain
3. Verify async/await properly used
4. Ensure error handling in place

### Code Review Checklist

- [ ] No hardcoded configuration values
- [ ] Proper async/await usage
- [ ] Error handling with graceful degradation
- [ ] Config values accessed correctly
- [ ] Full text displayed (not truncated)

## Notes for Claude

- **Priority**: Remove ALL hardcoded values - everything should be configurable
- **Focus**: V2 only - V1 is deprecated and not maintained
- **Testing**: Always run `python main.py` after changes to verify functionality
- **Reports**: Must show full chunk text for context, never truncate
- **Config**: When in doubt, add to config.yaml rather than hardcode
- **Async**: Use async patterns consistently throughout evaluators
- **Entity Extraction**: Now handled by Entity Focus evaluator during evaluation phase (no external APIs)
