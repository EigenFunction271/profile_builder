# Google Gemini Integration Guide

This project uses **Google Gemini Flash 2.0** as the LLM for all AI operations, providing excellent performance at lower costs compared to other models.

## Why Gemini Flash 2.0?

- **Cost-effective**: ~75% cheaper than GPT-4 and Claude
  - Input: $0.075 per 1M tokens
  - Output: $0.30 per 1M tokens
- **Fast**: Sub-second response times
- **Capable**: Excellent reasoning and JSON output
- **Free tier**: Generous free quota for development

## Getting Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add to your `.env` file:

```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

## Model Options

You can switch models by changing the `GEMINI_MODEL` environment variable:

| Model | Best For | Cost |
|-------|----------|------|
| `gemini-2.0-flash-exp` | Most tasks (recommended) | Lowest |
| `gemini-1.5-flash` | Stable production | Low |
| `gemini-1.5-pro` | Complex reasoning | Medium |

## Using the LLM Client

All LLM operations use the unified `LLMClient` wrapper:

```python
from src.utils.llm_client import LLMClient, create_llm_client
from src.utils.config import load_config

# Method 1: Direct initialization
config = load_config()
llm = LLMClient(config)

# Method 2: Factory function
llm = create_llm_client()

# Generate text
response = llm.generate(
    prompt="What is Python?",
    max_tokens=500,
    temperature=0.7
)

# Generate JSON
result = llm.generate_json(
    prompt="List 3 programming languages in JSON",
    max_tokens=200
)

# Check usage
stats = llm.get_usage_stats()
print(f"Cost so far: ${stats['total_cost_usd']}")
```

## Architecture

### LLM Client Wrapper (`src/utils/llm_client.py`)

The `LLMClient` class provides:
- ✅ Unified interface for all LLM calls
- ✅ Automatic token tracking
- ✅ Cost calculation
- ✅ JSON parsing with error handling
- ✅ Easy model switching via config

### Configuration (`src/utils/config.py`)

Environment variables:
```python
GEMINI_API_KEY=your_key          # Required for Phases 3+
GEMINI_MODEL=gemini-2.0-flash-exp  # Optional, defaults shown
```

### Template Implementations

Ready-to-use templates for Phases 3 and 5:

1. **`src/identity/confidence_scorer.py`**
   - Score identity matches (Phase 3)
   - Uses JSON output for structured results
   - Conservative temperature (0.3)

2. **`src/report/generator.py`**
   - Generate persona reports (Phase 5)
   - Markdown output
   - Higher token limit (3000)

## Cost Tracking

The client automatically tracks token usage:

```python
llm = create_llm_client()

# ... perform operations ...

stats = llm.get_usage_stats()
print(f"""
Model: {stats['model']}
Input tokens: {stats['input_tokens']:,}
Output tokens: {stats['output_tokens']:,}
Total cost: ${stats['total_cost_usd']:.6f}
""")

# Reset counters for new session
llm.reset_usage_stats()
```

## Best Practices

### 1. Keep Prompts Concise
```python
# ❌ Bad: Verbose prompt
prompt = "I need you to please analyze this and tell me..."

# ✅ Good: Direct and clear
prompt = "Analyze this email and return JSON with sentiment and topics."
```

### 2. Use System Instructions
```python
llm.generate(
    prompt="Score this profile match 0-100",
    system_instruction="You are an expert at identity matching."
)
```

### 3. Request JSON When Needed
```python
# Structured output
result = llm.generate_json(
    prompt="Extract name, company, role from: John Doe, CTO at TechCorp"
)
# Returns: {'name': 'John Doe', 'company': 'TechCorp', 'role': 'CTO'}
```

### 4. Lower Temperature for Consistency
```python
# For scoring, classification, extraction
llm.generate(prompt, temperature=0.3)

# For creative writing, reports
llm.generate(prompt, temperature=0.7)
```

### 5. Monitor Costs
```python
# Check before expensive operations
stats = llm.get_usage_stats()
if stats['total_cost_usd'] > 0.01:
    print("Warning: approaching budget limit")
```

## Phase-by-Phase Usage

### Phase 1-2: No LLM ✅
- OAuth and email fetching
- Signal extraction (pure regex)
- Cost: $0.00

### Phase 3: Identity Resolution
**File**: `src/identity/confidence_scorer.py`

```python
scorer = ConfidenceScorer(config)
result = scorer.score_match(
    email_signals=signals,
    candidate_profile=profile,
    user_email=email
)
# Cost per match: ~$0.0001
# Total for 3-5 candidates: ~$0.001
```

### Phase 5: Report Generation
**File**: `src/report/generator.py`

```python
generator = PersonaReportGenerator(config)
report = generator.generate_report(
    email_signals=signals,
    matched_profiles=profiles,
    enrichment_data=data,
    user_email=email
)
# Cost per report: ~$0.002
```

## Total Cost Breakdown

For a complete profile analysis:

| Operation | Calls | Tokens In | Tokens Out | Cost |
|-----------|-------|-----------|------------|------|
| Confidence Scoring | 5 | 500 | 100 | $0.0001 |
| Report Generation | 1 | 2000 | 1000 | $0.0005 |
| **Total** | | | | **$0.003** |

**Target**: <$0.01 per profile ✅

## Error Handling

The client includes automatic error handling:

```python
try:
    result = llm.generate_json(prompt)
except json.JSONDecodeError:
    # Handle invalid JSON response
    print("LLM returned invalid JSON")
except Exception as e:
    # Handle API errors
    print(f"LLM error: {e}")
```

## Testing Without API Key

For development without an API key:

```python
# Mock the LLM client
from unittest.mock import Mock

mock_llm = Mock()
mock_llm.generate.return_value = "Test response"
mock_llm.generate_json.return_value = {"score": 85}

# Use in tests
scorer = ConfidenceScorer(config)
scorer.llm = mock_llm  # Inject mock
```

## Rate Limits

Gemini free tier limits:
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

For production, upgrade to paid tier:
- 1,000 requests per minute
- Unlimited daily requests

## Switching Models (Future-Proof)

To switch to a different LLM provider, only modify `src/utils/llm_client.py`:

```python
# Current: Gemini
import google.generativeai as genai

# Future: OpenAI
# import openai

# Future: Anthropic
# import anthropic
```

All other code remains unchanged! 🎉

## Troubleshooting

### "API key not valid"
- Verify key in `.env` file
- Check key hasn't expired
- Get new key from Google AI Studio

### "Quota exceeded"
- Wait 1 minute (rate limit)
- Upgrade to paid tier
- Use exponential backoff

### "Invalid JSON response"
- Add clearer JSON instructions to prompt
- Use `generate_json()` method
- Check prompt for ambiguity

## Resources

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Pricing](https://ai.google.dev/pricing)
- [Quota Management](https://console.cloud.google.com/iam-admin/quotas)

---

**Updated**: Phase 1 complete with Gemini integration ready for Phase 3+ ✅

