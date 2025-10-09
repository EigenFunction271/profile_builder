# LLM-Enhanced Email Analysis (Phase 2.5)

**Optional Feature**: Analyze sent emails with Google Gemini for richer communication insights

## Overview

Phase 2 provides comprehensive signal extraction using pure regex/heuristics (zero LLM cost). Phase 2.5 adds an **optional** LLM enhancement that analyzes the actual content of your last 10 sent emails to extract richer insights about your communication style.

### Why Optional?

- ✅ **Phase 2 alone** provides excellent insights at zero cost
- 🤖 **Phase 2.5** adds AI-powered depth for ~$0.0002 per analysis
- 👤 **Your choice** - enable only when you want the extra depth

---

## Features

### What LLM Analysis Adds

Beyond the basic metrics (formality score, emoji usage, etc.), LLM analysis provides:

1. **Tone Analysis** - Professional, friendly, enthusiastic, etc.
2. **Writing Style** - Detailed characterization of your writing
3. **Common Topics** - Main subjects you discuss
4. **Relationship Quality** - How you build relationships (warm, collaborative, etc.)
5. **Professionalism Level** - 1-10 scale based on actual content
6. **Personality Traits** - 2-3 traits evident from writing
7. **Communication Strengths** - Your key strengths

### Rate Limiting ✅

Built-in protection against API rate limits:
- **15 requests/minute** (Gemini free tier limit)
- **1,500 requests/day** (Gemini free tier limit)
- Auto-wait when limits approached
- Graceful degradation if limits hit

### Cost Tracking ✅

Automatic token counting and cost calculation:
- Input tokens tracked
- Output tokens tracked
- Real-time cost display
- Cumulative cost reporting

---

## Setup

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your key

### 2. Configure Environment

Add to your `.env` file:

```bash
# Required for LLM analysis
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Enable LLM analysis (default: false)
ENABLE_LLM_ANALYSIS=true

# Max emails to analyze with LLM (default: 10)
LLM_MAX_EMAILS_TO_ANALYZE=10
```

### 3. Run Analysis

```bash
python -m src.main
```

That's it! The system will automatically:
1. Fetch full email bodies for your last 10 sent emails
2. Analyze them with Gemini
3. Display enhanced insights in the output

---

## Usage

### CLI

```bash
# With LLM analysis enabled
python -m src.main
```

**Expected Output:**
```
Step 4: Extracting Email Signals...
Analyzing newsletter subscriptions...
Analyzing communication style...
Extracting professional context...
Detecting activity patterns...

🤖 LLM analysis enabled - fetching full email bodies...
✓ Fetched 10 email bodies for LLM analysis

🤖 Enhanced LLM analysis enabled (analyzing up to 10 emails)...
📊 Analyzing 10 emails with LLM (~3500 tokens)...
✓ LLM analysis complete!
💰 LLM cost: $0.000263 (cumulative)

📊 SIGNAL EXTRACTION RESULTS
============================================================

💬 Communication Style:
  • Average email length: ~120 words
  • Formality score: 0.65/1.0 (Moderately formal)
  • Emoji usage: 15.0%
  • Average recipients: 1.2
  • Common greetings: Hi, Hello
  • Common signoffs: Best, Thanks

  🤖 LLM-Enhanced Insights:
     • Tone: Professional yet friendly
     • Writing style: Direct and action-oriented with clear calls-to-action
     • Professionalism: 7/10
     • Common topics: project updates, meeting coordination, client communication
     • Personality traits: Collaborative, detail-oriented, proactive
```

### Programmatic

```python
from src.email_analysis.signal_extractor import SignalExtractor
from src.email_analysis.fetcher import EmailFetcher
from src.utils.config import load_config

# Load config with LLM enabled
config = load_config()
config.enable_llm_analysis = True  # Or set via env var

# Fetch emails
fetcher = EmailFetcher(credentials)
sent_emails = fetcher.fetch_sent_emails(max_results=50)

# Fetch bodies for LLM analysis
email_bodies = []
for email in sent_emails[:10]:
    body = fetcher.fetch_email_body(email['id'])
    if body:
        email_bodies.append(body)

# Extract signals with LLM enhancement
extractor = SignalExtractor(config)
signals = extractor.extract_all_signals(
    emails, 
    sent_emails, 
    "user@example.com"
)

# Access LLM insights
if signals.communication_style.llm_analysis_available:
    print(f"Tone: {signals.communication_style.llm_tone}")
    print(f"Style: {signals.communication_style.llm_writing_style}")
    print(f"Topics: {signals.communication_style.llm_common_topics}")
```

---

## Cost Analysis

### Per Analysis Costs

**Analyzing 10 emails:**
- Average input: ~3,500 tokens
- Average output: ~300 tokens
- **Cost: ~$0.0002** (two hundredths of a cent)

**Monthly costs (running daily):**
- 30 analyses × $0.0002 = **$0.006/month**
- Well within free tier quotas

### Gemini Pricing

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| gemini-2.0-flash-exp | $0.075 | $0.30 |
| gemini-1.5-flash | $0.075 | $0.30 |

### Free Tier Limits

- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

**You can run ~5,000 analyses per day for free** before hitting token limits.

---

## Rate Limiting Details

### How It Works

The `RateLimiter` class automatically manages API calls:

```python
class RateLimiter:
    def __init__(self, requests_per_minute=15, requests_per_day=1500):
        # Track requests
        self.minute_requests = deque()
        self.day_requests = deque()
    
    def wait_if_needed(self):
        # Auto-wait if needed
        if len(self.minute_requests) >= 15:
            # Wait until oldest request is >1 min old
            time.sleep(wait_seconds)
```

### What You'll See

**Normal operation:**
```
🤖 Enhanced LLM analysis enabled (analyzing up to 10 emails)...
📊 Analyzing 10 emails with LLM (~3500 tokens)...
✓ LLM analysis complete!
```

**Rate limit approached:**
```
⏱️  Rate limit: waiting 12.3s...
📊 Analyzing 10 emails with LLM (~3500 tokens)...
```

**Daily limit hit:**
```
⚠️  Daily rate limit reached! Skipping LLM analysis.
```
(Analysis continues with heuristic-only results)

---

## Configuration Options

### Environment Variables

```bash
# Enable/disable LLM analysis
ENABLE_LLM_ANALYSIS=true  # or false (default)

# Model selection
GEMINI_MODEL=gemini-2.0-flash-exp  # Recommended
# or: gemini-1.5-flash, gemini-1.5-pro

# Number of emails to analyze
LLM_MAX_EMAILS_TO_ANALYZE=10  # Default: 10, Range: 1-50

# Gemini API key (required if enabled)
GEMINI_API_KEY=your_key_here
```

### Programmatic Configuration

```python
from src.utils.config import load_config

config = load_config()

# Enable LLM analysis
config.enable_llm_analysis = True

# Adjust number of emails
config.llm_max_emails_to_analyze = 15

# Use custom model
config.gemini_model = "gemini-1.5-pro"
```

---

## Advanced Usage

### Custom Rate Limiter

```python
from src.email_analysis.llm_analyzer import EmailLLMAnalyzer, RateLimiter

# More conservative rate limits
rate_limiter = RateLimiter(
    requests_per_minute=10,  # Slower
    requests_per_day=500     # Lower daily cap
)

analyzer = EmailLLMAnalyzer(config, rate_limiter=rate_limiter)
result = analyzer.analyze_sent_emails(email_bodies)
```

### Cost Monitoring

```python
from src.email_analysis.llm_analyzer import EmailLLMAnalyzer

analyzer = EmailLLMAnalyzer(config)

# Analyze emails
result = analyzer.analyze_sent_emails(email_bodies)

# Check costs
stats = analyzer.get_cost_stats()
print(f"Input tokens: {stats['input_tokens']}")
print(f"Output tokens: {stats['output_tokens']}")
print(f"Total cost: ${stats['total_cost_usd']:.6f}")

# Check rate limits
status = analyzer.get_rate_limit_status()
print(f"Requests last minute: {status['requests_last_minute']}/{status['minute_limit']}")
print(f"Requests last day: {status['requests_last_day']}/{status['day_limit']}")
```

---

## Comparison: With vs Without LLM

### Without LLM (Phase 2)
```
💬 Communication Style:
  • Average email length: ~120 words
  • Formality score: 0.65/1.0 (Moderately formal)
  • Emoji usage: 15.0%
  • Common greetings: Hi, Hello
  • Common signoffs: Best, Thanks
```
**Cost: $0.00**

### With LLM (Phase 2.5)
```
💬 Communication Style:
  • Average email length: ~120 words
  • Formality score: 0.65/1.0 (Moderately formal)
  • Emoji usage: 15.0%
  • Common greetings: Hi, Hello
  • Common signoffs: Best, Thanks

  🤖 LLM-Enhanced Insights:
     • Tone: Professional yet approachable
     • Writing style: Direct and action-oriented
     • Professionalism: 7/10
     • Common topics: projects, meetings, coordination
     • Personality traits: Collaborative, efficient
```
**Cost: ~$0.0002**

---

## Troubleshooting

### Issue: "No Gemini API key found"
**Solution**: Add `GEMINI_API_KEY` to your `.env` file

### Issue: "Rate limit exceeded"
**Normal**: System will auto-wait or skip if daily limit hit  
**Action**: None needed - gracefully handled

### Issue: "LLM analysis failed"
**Causes**: 
- Invalid API key
- Network issues
- Malformed email content

**Result**: Analysis continues with heuristic-only results  
**Action**: Check logs for specific error

### Issue: Costs higher than expected
**Check**:
1. `LLM_MAX_EMAILS_TO_ANALYZE` setting (default: 10)
2. Number of times you've run analysis
3. Cost stats: `analyzer.get_cost_stats()`

**Normal cost**: ~$0.0002 per 10 emails

---

## Best Practices

### When to Enable LLM Analysis

✅ **Good for:**
- Deep dive into your communication style
- Understanding personality traits
- Identifying communication strengths
- Professional development insights

❌ **Skip if:**
- Just want basic stats (Phase 2 is excellent)
- Running frequently (daily/hourly)
- Budget conscious (though costs are minimal)

### Optimizing Costs

1. **Adjust email count**: Use 5-10 emails (default: 10)
2. **Run selectively**: Not every analysis needs LLM
3. **Cache results**: Save signals to avoid re-analyzing
4. **Use free tier**: 1M tokens/day is generous

### Privacy Considerations

- Email bodies are sent to Google Gemini API
- Only sent emails are analyzed (not received)
- Only last 10 emails (configurable)
- First 500 chars per email (truncated for privacy)
- No data stored by Gemini (per their policy)

---

## Example Output

### Full LLM Analysis Result

```json
{
  "tone": "Professional yet friendly",
  "writing_style": "Direct and action-oriented with clear calls-to-action. Uses structured formatting and bullet points. Concise but warm.",
  "common_topics": [
    "project updates",
    "meeting coordination",
    "client communication",
    "deliverable reviews",
    "team collaboration"
  ],
  "relationship_quality": "Collaborative and supportive. Builds rapport through clear communication and follow-through.",
  "professionalism_level": 7,
  "personality_traits": [
    "Detail-oriented",
    "Proactive",
    "Collaborative"
  ],
  "communication_strengths": [
    "Clear action items",
    "Timely responses",
    "Professional yet approachable tone"
  ]
}
```

---

## API Reference

### EmailLLMAnalyzer

```python
class EmailLLMAnalyzer:
    def __init__(self, config: Config, rate_limiter: Optional[RateLimiter] = None)
    
    def analyze_sent_emails(
        self,
        email_bodies: List[str],
        max_emails: int = 10
    ) -> Optional[Dict[str, Any]]
    
    def get_rate_limit_status(self) -> Dict[str, int]
    
    def get_cost_stats(self) -> Dict[str, Any]
```

### RateLimiter

```python
class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 15,
        requests_per_day: int = 1500
    )
    
    def wait_if_needed(self) -> None
    
    def get_status(self) -> Dict[str, int]
```

---

## FAQ

**Q: Is LLM analysis required?**  
A: No, it's completely optional. Phase 2 provides excellent insights without it.

**Q: How much does it cost?**  
A: ~$0.0002 per analysis (10 emails). About $0.006/month if run daily.

**Q: Can I use a different LLM?**  
A: Yes! Modify `src/email_analysis/llm_analyzer.py` to use your preferred LLM. The rate limiter and cost tracking are modular.

**Q: Is my email data safe?**  
A: Emails are sent to Google Gemini API. Only sent emails (last 10), only first 500 chars each. Review Google's privacy policy.

**Q: Can I analyze more than 10 emails?**  
A: Yes, set `LLM_MAX_EMAILS_TO_ANALYZE` up to 50. Costs scale linearly.

**Q: What if I hit rate limits?**  
A: System auto-waits or gracefully degrades to heuristic-only analysis.

---

## Summary

**Phase 2.5 LLM Enhancement** is a powerful optional feature that:

✅ Adds rich AI-powered insights  
✅ Costs ~$0.0002 per analysis  
✅ Includes automatic rate limiting  
✅ Tracks costs in real-time  
✅ Gracefully degrades if unavailable  
✅ Easy to enable/disable  

**Perfect for:** Deep analysis when you want maximum insight into your communication style.

**Not needed if:** Phase 2 heuristics provide sufficient insights (they're excellent!).

---

**Enable it when you want the extra depth. Disable it when you don't. Your choice!** 🎯

