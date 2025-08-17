# GPT-5 Prompt Engineering and Structured Outputs Best Practices

## Executive Summary

This document outlines critical best practices for prompt engineering with GPT-5 and OpenAI's Structured Outputs API, based on 2025 guidance and real-world implementation experience. The key insight is the **clean separation of concerns** between prompts (evaluation logic) and Pydantic models (output format).

## Key Principles

### 1. Clean Separation of Concerns

**Prompts Should Handle:**

- Domain-specific evaluation logic
- Scoring criteria and quality gates
- Content analysis instructions
- Business rules and constraints

**Pydantic Models Should Handle:**

- Output structure and format
- Field descriptions and requirements
- Validation rules
- Presentation logic (via `as_markdown()` methods)

### 2. Critical Finding: Field Descriptions vs Prompts

**Research Finding (2024):** "Under the hood OpenAI creates a JSON schema from the Pydantic model, but the docstrings of each field are not included."

**Best Practice:** Use Pydantic's `Field(description="...")` to pass instructions to the model:

```python
# ✅ CORRECT - Use Field descriptions
overall_score: int = Field(
    ge=0, le=100,
    description="Single score from 0-100 based on AI retrieval readiness"
)

# ❌ INCORRECT - Don't repeat this in prompts
# "Provide overall_score: Single score from 0-100..."
```

## Structured Outputs Implementation

### Core Implementation Pattern

```python
# 1. Define Pydantic model with Field descriptions
class StandardizedEvaluationResult(BaseModel):
    overall_score: int = Field(
        ge=0, le=100,
        description="Score based on evaluation criteria"
    )
    strengths: List[str] = Field(
        description="Key strengths - AI determines appropriate number"
    )

# 2. Use in evaluator
result = await self.parse_structured_output(
    response_model=StandardizedEvaluationResult,
    messages=messages
)
```

### Native SDK Integration

The 2024 SDK provides native Pydantic support:

```python
# ✅ Use native SDK support
response = await client.beta.chat.completions.parse(
    model="gpt-5-mini",
    messages=messages,
    response_format=YourPydanticModel
)
```

## GPT-5 Specific Features and Best Practices

### 1. Verbosity Control

GPT-5 introduces a `verbosity` parameter for output length control:

- **Low:** Minimal, functional output
- **Medium:** Explanatory comments and structure
- **High:** Comprehensive, production-ready output

### 2. Context-Free Grammar Support

Use CFG for strict syntax constraints when needed, especially for programming language rules or custom formats.

### 3. Freeform Tool Calling

Send raw text payloads (Python scripts, SQL queries) without JSON wrapping when structured JSON is unnecessary.

### 4. Improved Agentic Performance

GPT-5 excels at "tool preambles" - upfront planning and progress updates. Structure prompts to leverage this capability.

## Prompt Engineering Anti-Patterns

### ❌ What NOT to Do

1. **Don't Duplicate Schema Information in Prompts**

   ```python
   # WRONG - This duplicates Pydantic Field descriptions
   prompt = """
   OUTPUT FORMAT:
   1. overall_score: Single score from 0-100
   2. strengths: List of key strengths
   """
   ```

2. **Don't Mix Format Instructions with Logic**

   ```python
   # WRONG - Mixing concerns
   prompt = """
   Evaluate quality AND provide JSON with these fields...
   """
   ```

3. **Don't Use Verbose Format Explanations**
   ```python
   # WRONG - Redundant with structured outputs
   prompt = """
   CRITICAL - You MUST provide values for ALL fields:
   - For list fields: provide empty list [] if no items
   """
   ```

### ✅ What TO Do

1. **Focus Prompts on Domain Logic Only**

   ```python
   # CORRECT - Pure evaluation logic
   prompt = """
   Evaluate AI retrieval readiness focusing on:
   - Self-containment and clarity
   - Topic coherence and focus
   - Structural effectiveness

   Apply penalties for vague references and jargon barriers.
   """
   ```

2. **Let Pydantic Handle All Format Requirements**

   ```python
   # CORRECT - Schema handles format
   recommendations: str = Field(
       description="If score < 80, provide specific improvements. If score ≥ 80, return 'N/A - This section is already well-optimized'"
   )
   ```

3. **End Prompts Simply**

   ```python
   # CORRECT - Simple, clean ending
   prompt = """
   [evaluation logic here]

   Provide your analysis as structured data according to the provided schema.
   """
   ```

## Implementation Guidelines for This Project

### Evaluator Prompt Structure

```python
SYSTEM_PROMPT = """
[Domain-specific evaluation logic]
[Scoring criteria and quality gates]
[Business rules and constraints]

Provide your analysis as structured data according to the provided schema.
"""
```

### Pydantic Model Structure

```python
class StandardizedEvaluationResult(BaseModel):
    model_config = ConfigDict(extra='forbid')

    overall_score: int = Field(
        ge=0, le=100,
        description="Clear description of what this score represents"
    )

    overall_assessment: str = Field(
        description="Clear and concise assessment explanation"
    )

    # ... other fields with comprehensive descriptions

    def as_markdown(self) -> str:
        """Handle ALL presentation formatting here."""
        # Emoji formatting, structure, etc.
```

### Error Handling Best Practices

```python
# Handle refusals properly
if response.choices[0].message.refusal:
    logger.warning(f"Model refused: {response.choices[0].message.refusal}")
    return None

# Graceful degradation
try:
    result = await self.parse_structured_output(...)
except Exception as e:
    logger.error(f"Structured output failed: {e}")
    return self.create_empty_result("Evaluation failed")
```

## Validation Checklist

When implementing or modifying evaluators:

- [ ] **Prompt focuses only on evaluation logic, not format**
- [ ] **No OUTPUT FORMAT sections in prompts**
- [ ] **All format requirements in Pydantic Field descriptions**
- [ ] **Simple prompt ending: "Provide structured data per schema"**
- [ ] **Pydantic model handles all presentation via `as_markdown()`**
- [ ] **Proper error handling for refusals and failures**
- [ ] **Using supported models (gpt-4o-mini, gpt-4o-2024-08-06+)**

## Performance Considerations

### Latency Optimization

- **First call with new schema:** Additional latency due to preprocessing
- **Subsequent calls:** No latency penalty
- **Recommendation:** Cache schema preprocessing when possible

### Model Selection

- **gpt-4o-2024-08-06:** Best structured output performance (100% compliance)
- **gpt-4o-mini:** Cost-effective option with good compliance
- **GPT-5:** Enhanced agentic performance and new features

## Common Pitfalls and Solutions

| Pitfall                     | Solution                                                  |
| --------------------------- | --------------------------------------------------------- |
| Prompt format redundancy    | Remove OUTPUT FORMAT sections, use Field descriptions     |
| Mixed prompt concerns       | Separate evaluation logic from format requirements        |
| Verbose schema explanations | Trust Pydantic Field descriptions to guide AI             |
| Inconsistent error handling | Implement standard error patterns across evaluators       |
| Poor model selection        | Use gpt-4o-2024-08-06+ for best structured output support |

## Integration with Existing Systems

### LlamaIndex Compatibility

This project maintains compatibility with LlamaIndex's `EvaluationResult` pattern while leveraging structured outputs:

```python
# Structured output evaluation
structured_result = await self.parse_structured_output(...)

# LlamaIndex compatibility layer
return EvaluationResult(
    query="",
    response=chunk_preview,
    passing=structured_result.passing,
    score=structured_result.overall_score / 100,
    feedback=structured_result.as_markdown()  # Pydantic handles formatting
)
```

## Future Considerations

### GPT-5 Advanced Features

Monitor for additional GPT-5 capabilities:

- Enhanced context-free grammar support
- Improved verbosity control options
- Advanced tool calling patterns

### API Evolution

Stay updated on OpenAI API changes:

- New model releases with structured output support
- Schema specification improvements
- Performance optimizations

## Resources and References

- [OpenAI Structured Outputs Documentation](https://platform.openai.com/docs/guides/structured-outputs)
- [GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [OpenAI Cookbook - Structured Outputs](https://cookbook.openai.com/examples/structured_outputs_intro)

---

**Last Updated:** 2024-08-17  
**Version:** 1.0  
**Project:** Chunk Retrieval Readiness Auditor
