# Digital Footprint Analyzer - Development Guide

## Project Overview
Build a Python application that analyzes a user's Gmail inbox to create a comprehensive digital persona report. The system extracts signals from emails, resolves the user's identity across social platforms, enriches with public profile data, and generates an insightful persona report.

**Key Constraint**: Keep costs under $0.01 per profile by minimizing LLM usage through smart pre-processing.

---

## Project Structure

Create this directory structure:
```
digital-footprint-analyzer/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── auth/
│   │   ├── __init__.py
│   │   └── gmail_oauth.py         # Gmail OAuth implementation
│   ├── email_analysis/
│   │   ├── __init__.py
│   │   ├── fetcher.py             # Gmail API calls
│   │   ├── signal_extractor.py    # Extract signals (no LLM)
│   │   └── parsers.py             # Email parsing utilities
│   ├── identity/
│   │   ├── __init__.py
│   │   ├── name_extractor.py      # Extract name from email
│   │   ├── profile_search.py      # Exa API integration
│   │   └── confidence_scorer.py   # LLM-based matching
│   ├── enrichment/
│   │   ├── __init__.py
│   │   └── apify_scraper.py       # LinkedIn/Twitter scraping
│   ├── report/
│   │   ├── __init__.py
│   │   └── generator.py           # Persona report generation
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   └── utils/
│       ├── __init__.py
│       ├── config.py              # Environment config
│       └── storage.py             # Token storage (SQLite)
├── tests/
│   ├── __init__.py
│   ├── test_signal_extractor.py
│   ├── test_name_extractor.py
│   └── test_integration.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── PRD.md                          # (Already provided)
```

---

## Requirements (requirements.txt)

```
# Core
python-dotenv==1.0.0
pydantic==2.5.0

# Gmail
google-auth==2.25.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.110.0

# APIs
google-generativeai==0.3.2
exa-py==1.0.7
apify-client==1.5.0

# Utilities
requests==2.31.0
python-dateutil==2.8.2
```

---

## Environment Variables (.env.example)

```bash
# Gmail OAuth
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# Exa (Identity Resolution)
EXA_API_KEY=your_exa_api_key

# Apify (Social Profile Scraping)
APIFY_API_TOKEN=apify_api_your_token

# Optional: Database
DATABASE_PATH=./data/tokens.db
```

---

## Implementation Priorities

### Phase 1: Gmail OAuth + Email Fetching (Start Here)
**Files to create first:**
1. `src/auth/gmail_oauth.py`
2. `src/email_analysis/fetcher.py`
3. `src/utils/config.py`
4. `src/utils/storage.py`
5. `src/main.py` (basic CLI)

**Success Criteria:**
- User can authenticate via OAuth
- Fetch last 100 emails (metadata only)
- Store refresh token securely
- Handle token refresh automatically

**Key Implementation Details:**

#### gmail_oauth.py
```python
# Implement these functions:
def get_oauth_flow() -> Flow:
    """Initialize OAuth flow with correct scopes"""
    # Scopes: gmail.readonly, userinfo.email

def authenticate_user() -> Credentials:
    """Run OAuth flow, save tokens"""

def load_credentials() -> Optional[Credentials]:
    """Load existing credentials from storage"""

def refresh_token(credentials: Credentials) -> Credentials:
    """Refresh expired token"""
```

#### fetcher.py
```python
# Implement these functions:
def get_gmail_service(credentials: Credentials):
    """Build Gmail API service"""

def fetch_recent_emails(service, max_results=100) -> List[Dict]:
    """Fetch emails using batch requests
    - Use format='metadata' for efficiency
    - Query filters: newsletters + sent emails
    - Return: [{id, from, to, subject, date, snippet}]
    """

def fetch_sent_emails(service, max_results=50) -> List[Dict]:
    """Fetch only sent emails for communication style"""
```

---

### Phase 2: Signal Extraction (Zero LLM Cost)
**Files to create:**
1. `src/email_analysis/signal_extractor.py`
2. `src/email_analysis/parsers.py`
3. `src/models/schemas.py`

**Success Criteria:**
- Extract all 4 signal categories from 100 emails
- Process in <30 seconds
- Output structured EmailSignals object

**Key Implementation Details:**

#### signal_extractor.py
```python
# Implement these classes/functions:

class SignalExtractor:
    def extract_newsletters(self, emails: List[Dict]) -> Dict:
        """
        Identify newsletters by:
        - List-Unsubscribe header
        - Common newsletter domains
        - Subject patterns (Weekly, Newsletter, Digest)
        
        Return: {
            'domains': [...],
            'categories': {'tech': 15, 'finance': 8},
            'top_newsletters': [...]
        }
        """
    
    def extract_communication_style(self, sent_emails: List[Dict]) -> Dict:
        """
        Analyze sent emails for:
        - Average word count
        - Formality score (regex patterns for formal phrases)
        - Response time (thread analysis)
        - Emoji usage count
        - Common greetings/signoffs
        
        Return: {
            'avg_length': 120,
            'formality_score': 0.65,
            'avg_response_time_hours': 4.2,
            ...
        }
        """
    
    def extract_professional_context(self, emails: List[Dict]) -> Dict:
        """
        Extract from contact patterns:
        - Top 10 contact domains
        - Industry inference (regex patterns)
        - Company affiliations
        
        Return: {
            'top_domains': [...],
            'inferred_industry': 'technology',
            ...
        }
        """
    
    def extract_activity_patterns(self, emails: List[Dict]) -> Dict:
        """
        Calculate from timestamps:
        - Emails per day average
        - Peak activity hours
        - Thread depth analysis
        """
```

#### parsers.py
```python
# Utility functions for email parsing

def extract_domain(email_address: str) -> str:
    """Extract domain from email"""

def is_newsletter(email: Dict) -> bool:
    """Heuristic to identify newsletters"""

def extract_name_from_signature(email_body: str) -> Optional[str]:
    """Parse email signature for name"""

def calculate_formality_score(text: str) -> float:
    """Use regex patterns to score formality 0-1"""

def categorize_domain(domain: str) -> str:
    """Map domain to category (tech, finance, etc.)"""
```

#### schemas.py (Pydantic Models)
```python
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class EmailSignals(BaseModel):
    # Newsletter data
    newsletter_domains: List[str]
    newsletter_categories: Dict[str, int]
    top_newsletters: List[str]
    
    # Communication style
    avg_email_length: int
    formality_score: float
    avg_response_time_hours: float
    emoji_usage_rate: float
    
    # Professional context
    top_contact_domains: List[str]
    inferred_industry: Optional[str]
    
    # Activity patterns
    emails_per_day: float
    peak_activity_hours: List[int]

class IdentityMatch(BaseModel):
    platform: str
    profile_url: str
    confidence_score: float
    extracted_data: Dict
    reasoning: str

class PersonaReport(BaseModel):
    user_email: str
    generated_at: datetime
    executive_summary: str
    digital_footprint_score: int
    professional_profile: Dict
    personal_interests: Dict
    communication_style: Dict
    digital_presence: Dict
    confidence_scores: Dict[str, float]
    data_sources: List[str]
    matched_profiles: List[IdentityMatch]
```

---

### Phase 3: Identity Resolution (LLM Usage: Minimal)
**Files to create:**
1. `src/identity/name_extractor.py`
2. `src/identity/profile_search.py`
3. `src/identity/confidence_scorer.py`

**Success Criteria:**
- Extract user's name from email
- Search Exa for LinkedIn/Twitter profiles
- Score matches with LLM (Google Gemini Flash)
- Return matches above 70% confidence

**Key Implementation Details:**

#### name_extractor.py
```python
def extract_name_from_email(email_address: str) -> Optional[str]:
    """
    Parse email format:
    - john.doe@company.com → "John Doe"
    - jdoe@company.com → harder, need other methods
    """

def extract_name_from_sent_emails(sent_emails: List[Dict]) -> Optional[str]:
    """
    Check email signatures, display names
    """

def extract_company_from_domain(domain: str) -> Optional[str]:
    """
    Extract likely company name from domain
    """
```

#### profile_search.py
```python
from exa_py import Exa

class ProfileSearcher:
    def __init__(self, api_key: str):
        self.exa = Exa(api_key)
    
    def search_linkedin(self, name: str, company: Optional[str] = None) -> List[Dict]:
        """
        Search LinkedIn profiles
        Query: "{name} {company} site:linkedin.com"
        Return top 5 results
        """
    
    def search_twitter(self, name: str, keywords: List[str] = None) -> List[Dict]:
        """
        Search Twitter/X profiles
        Use keywords from email signals for better matching
        """
```

#### confidence_scorer.py
```python
from ..utils.llm_client import LLMClient

class ConfidenceScorer:
    def __init__(self, config: Config):
        self.llm = LLMClient(config)
    
    def score_match(
        self, 
        email_signals: EmailSignals,
        candidate_profile: Dict,
        user_email: str
    ) -> IdentityMatch:
        """
        Use Google Gemini Flash to score match 0-100
        
        Prompt structure:
        - User email signals (interests, industry, communication style)
        - Candidate profile data
        - Ask: Likelihood this is the same person?
        
        Keep prompt under 1000 tokens for cost efficiency
        """
```

**LLM Prompt Template (for confidence_scorer.py):**
```python
CONFIDENCE_SCORING_PROMPT = """
You are evaluating if a social media profile belongs to the user of this email.

USER EMAIL SIGNALS:
- Email: {email}
- Inferred Industry: {industry}
- Top Interests: {interests}
- Newsletter Categories: {newsletter_categories}
- Professional Domains: {top_domains}

CANDIDATE PROFILE:
- Platform: {platform}
- Profile URL: {url}
- Name: {name}
- Headline/Bio: {headline}
- Location: {location}
- Company: {company}

TASK:
Score 0-100 how likely this profile belongs to the email user.

Consider:
1. Name match with email format
2. Industry/company alignment
3. Interest overlap
4. Location consistency (if available)
5. Timeline plausibility

OUTPUT FORMAT (JSON):
{
  "score": 85,
  "reasoning": "Strong name match, industry aligns with email domains contacted, shared interest in AI/ML newsletters"
}

Be conservative - only high scores (70+) if confident.
"""
```

---

### Phase 4: Profile Enrichment (Apify Integration)
**Files to create:**
1. `src/enrichment/apify_scraper.py`

**Success Criteria:**
- Scrape LinkedIn profile for matched user
- Scrape Twitter profile for matched user
- Handle rate limits and errors gracefully
- Return structured profile data

**Key Implementation Details:**

#### apify_scraper.py
```python
from apify_client import ApifyClient

class ProfileEnricher:
    def __init__(self, api_token: str):
        self.client = ApifyClient(api_token)
    
    def scrape_linkedin_profile(self, profile_url: str) -> Dict:
        """
        Use: apify/linkedin-profile-scraper
        Input: {"startUrls": [{"url": profile_url}]}
        Extract: headline, experience, skills, education
        
        Handle:
        - Rate limits (retry with backoff)
        - Invalid URLs (return None)
        - Private profiles (return partial data)
        """
    
    def scrape_twitter_profile(self, profile_url: str) -> Dict:
        """
        Use: apify/twitter-scraper
        Input: Profile URL or username
        Extract: bio, recent tweets, following/followers
        
        Focus on bio and pinned tweets for persona building
        """
    
    def enrich_profile(self, matched_profiles: List[IdentityMatch]) -> Dict:
        """
        Aggregate data from all matched profiles
        Return unified enrichment data
        """
```

---

### Phase 5: Report Generation (Main LLM Usage)
**Files to create:**
1. `src/report/generator.py`

**Success Criteria:**
- Generate comprehensive Markdown report
- Single LLM call with optimized prompt
- Cost target: $0.005 per report
- Report includes all required sections

**Key Implementation Details:**

#### generator.py
```python
from ..utils.llm_client import LLMClient
from ..models.schemas import EmailSignals, IdentityMatch, PersonaReport

class PersonaReportGenerator:
    def __init__(self, config: Config):
        self.llm = LLMClient(config)
    
    def generate_report(
        self,
        email_signals: EmailSignals,
        matched_profiles: List[IdentityMatch],
        enrichment_data: Dict,
        user_email: str
    ) -> PersonaReport:
        """
        Generate comprehensive persona report
        
        Use Google Gemini Flash 2.0 for quality
        Single prompt with ALL data compressed
        """
        
        # Prepare compressed input
        prompt = self._build_report_prompt(
            email_signals,
            matched_profiles,
            enrichment_data,
            user_email
        )
        
        # Call Gemini
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=3000,
            temperature=0.7
        )
        
        # Parse response into PersonaReport
        return self._parse_report(response.content[0].text, user_email)
    
    def _build_report_prompt(self, ...) -> str:
        """Build optimized prompt - see template below"""
    
    def _parse_report(self, markdown_report: str, email: str) -> PersonaReport:
        """Parse markdown into PersonaReport object"""
    
    def export_markdown(self, report: PersonaReport, output_path: str):
        """Save report as .md file"""
```

**LLM Prompt Template (for report generation):**
```python
REPORT_GENERATION_PROMPT = """
You are a digital footprint analyst. Generate a comprehensive persona report based on the user's digital signals.

INPUT DATA:

EMAIL SIGNALS:
- User Email: {user_email}
- Newsletter Subscriptions: {newsletter_categories}
  Top Newsletters: {top_newsletters}
- Communication Style:
  * Avg Email Length: {avg_email_length} words
  * Formality Score: {formality_score}/1.0
  * Response Time: {avg_response_time} hours
  * Emoji Usage: {emoji_rate}%
- Professional Context:
  * Top Contact Domains: {top_domains}
  * Inferred Industry: {inferred_industry}
- Activity Patterns:
  * Emails/Day: {emails_per_day}
  * Peak Hours: {peak_hours}

MATCHED PROFILES:
{matched_profiles_summary}

ENRICHMENT DATA:
LinkedIn: {linkedin_data}
Twitter: {twitter_data}

TASK:
Generate a persona report in the following markdown format:

# Digital Footprint Analysis for {user_email}

**Generated**: {timestamp} | **Confidence Score**: X/10

## Executive Summary
[One compelling paragraph summarizing who this person appears to be online. What's their digital persona? What story does their footprint tell?]

## Professional Profile
- **Likely Role**: [Inferred from signals]
- **Industry**: [Primary industry]
- **Key Interests**: [Professional topics]
- **Communication Style**: [In work context]
- **Notable Patterns**: [Any standout observations]

## Personal Interests
[Analyze newsletter subscriptions and topics]
- **Primary Categories**: [Breakdown with percentages]
- **Content Consumption**: [What they're reading/following]
- **Passion Signals**: [Topics they engage with most]

## Communication Style
- **Formality Level**: [Scale with description]
- **Typical Email Pattern**: [How they write]
- **Response Behavior**: [How quickly/thoroughly they respond]
- **Digital Voice**: [Personality in writing]

## Digital Presence
- **Confirmed Profiles**: [List with confidence scores]
- **Public Visibility**: [How visible/active online]
- **Professional Brand**: [How they present professionally]
- **Personal Brand**: [How they present casually]

## Key Insights
[3-5 unique insights about this person that aren't obvious from individual data points but emerge from the full picture]

## Data Quality Assessment
[Brief note on confidence level and data completeness]

**Data Sources**: Gmail ({email_count} emails), LinkedIn (confidence: X%), Twitter (confidence: Y%)

INSTRUCTIONS:
1. Be specific and insightful, not generic
2. Support claims with data points
3. Highlight interesting patterns or contradictions
4. Keep professional but engaging tone
5. Assign overall confidence score 1-10 based on data quality
6. If data is limited, be transparent about it
"""
```

---

### Phase 6: Main Entry Point & CLI
**Files to update/create:**
1. `src/main.py`

**Success Criteria:**
- Simple CLI to run full pipeline
- Error handling at each stage
- Progress indicators for user
- Save report to file

**Key Implementation Details:**

#### main.py
```python
import sys
from pathlib import Path
from .auth.gmail_oauth import authenticate_user, load_credentials
from .email_analysis.fetcher import get_gmail_service, fetch_recent_emails, fetch_sent_emails
from .email_analysis.signal_extractor import SignalExtractor
from .identity.name_extractor import extract_name_from_email, extract_name_from_sent_emails
from .identity.profile_search import ProfileSearcher
from .identity.confidence_scorer import ConfidenceScorer
from .enrichment.apify_scraper import ProfileEnricher
from .report.generator import PersonaReportGenerator
from .utils.config import load_config

def main():
    """
    Main pipeline for digital footprint analysis
    """
    print("🔍 Digital Footprint Analyzer\n")
    
    # Load configuration
    config = load_config()
    
    # Step 1: Authenticate with Gmail
    print("Step 1: Authenticating with Gmail...")
    credentials = load_credentials()
    if not credentials:
        print("First time setup - please authorize access to Gmail")
        credentials = authenticate_user()
    
    gmail_service = get_gmail_service(credentials)
    user_email = get_user_email(gmail_service)
    print(f"✓ Authenticated as: {user_email}\n")
    
    # Step 2: Fetch emails
    print("Step 2: Fetching recent emails...")
    emails = fetch_recent_emails(gmail_service, max_results=100)
    sent_emails = fetch_sent_emails(gmail_service, max_results=50)
    print(f"✓ Fetched {len(emails)} emails ({len(sent_emails)} sent)\n")
    
    # Step 3: Extract signals (no LLM cost)
    print("Step 3: Analyzing email patterns...")
    extractor = SignalExtractor()
    email_signals = extractor.extract_all_signals(emails, sent_emails)
    print(f"✓ Extracted signals:")
    print(f"  - {len(email_signals.newsletter_domains)} newsletter subscriptions")
    print(f"  - Communication style: {email_signals.formality_score:.2f} formality")
    print(f"  - {len(email_signals.top_contact_domains)} professional domains\n")
    
    # Step 4: Identify user
    print("Step 4: Resolving identity...")
    name = extract_name_from_email(user_email) or extract_name_from_sent_emails(sent_emails)
    if not name:
        print("⚠ Could not extract name from email")
        name = input("Please enter your full name: ")
    
    print(f"✓ Identified as: {name}\n")
    
    # Step 5: Search for profiles
    print("Step 5: Searching for social profiles...")
    searcher = ProfileSearcher(config.exa_api_key)
    
    linkedin_results = searcher.search_linkedin(name, email_signals.inferred_industry)
    twitter_results = searcher.search_twitter(name, list(email_signals.newsletter_categories.keys()))
    
    print(f"✓ Found {len(linkedin_results)} LinkedIn candidates")
    print(f"✓ Found {len(twitter_results)} Twitter candidates\n")
    
    # Step 6: Score matches
    print("Step 6: Evaluating profile matches...")
    scorer = ConfidenceScorer(config)
    
    matched_profiles = []
    for result in linkedin_results[:3]:  # Top 3 candidates
        match = scorer.score_match(email_signals, result, user_email)
        if match.confidence_score >= 70:
            matched_profiles.append(match)
            print(f"✓ LinkedIn match: {match.confidence_score:.0f}% - {match.profile_url}")
    
    for result in twitter_results[:3]:
        match = scorer.score_match(email_signals, result, user_email)
        if match.confidence_score >= 70:
            matched_profiles.append(match)
            print(f"✓ Twitter match: {match.confidence_score:.0f}% - {match.profile_url}")
    
    print(f"\n✓ Confirmed {len(matched_profiles)} profile matches\n")
    
    # Step 7: Enrich with profile data
    print("Step 7: Enriching profile data...")
    enricher = ProfileEnricher(config.apify_api_token)
    enrichment_data = enricher.enrich_profile(matched_profiles)
    print("✓ Profile enrichment complete\n")
    
    # Step 8: Generate report
    print("Step 8: Generating persona report...")
    generator = PersonaReportGenerator(config)
    report = generator.generate_report(
        email_signals,
        matched_profiles,
        enrichment_data,
        user_email
    )
    print("✓ Report generated\n")
    
    # Step 9: Save report
    output_path = Path(f"reports/persona_{user_email.replace('@', '_at_')}.md")
    output_path.parent.mkdir(exist_ok=True)
    generator.export_markdown(report, str(output_path))
    
    print(f"✅ Complete! Report saved to: {output_path}")
    print(f"📊 Digital Footprint Score: {report.digital_footprint_score}/10\n")
    
    # Show preview
    print("Preview:")
    print("=" * 60)
    print(report.executive_summary)
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

## Testing Instructions

### Unit Tests (tests/)

```python
# test_signal_extractor.py
def test_newsletter_extraction():
    """Test newsletter identification from sample emails"""
    
def test_formality_scoring():
    """Test formality calculation on known examples"""
    
def test_domain_categorization():
    """Test domain → category mapping"""

# test_name_extractor.py
def test_name_from_email_format():
    """Test john.doe@company.com → John Doe"""
    
def test_name_from_signature():
    """Test signature parsing"""

# test_integration.py
def test_full_pipeline():
    """End-to-end test with sample data"""
```

### Manual Testing Checklist
- [ ] OAuth flow works on fresh install
- [ ] Can fetch 100 emails successfully
- [ ] Newsletter extraction is accurate (verify top 5)
- [ ] Communication style matches reality
- [ ] Name extraction works for your email
- [ ] Identity resolution finds correct LinkedIn
- [ ] Confidence scores are reasonable
- [ ] Report is insightful and accurate
- [ ] Total cost is under $0.02

---

## Development Tips

### Cost Monitoring
```python
# Add to each API call
def track_cost(tokens_used: int, model: str):
    """Log token usage for cost tracking"""
    # Haiku: $0.25/1M input, $1.25/1M output
    # Sonnet: $3/1M input, $15/1M output
```

### Error Handling Patterns
```python
try:
    result = api_call()
except RateLimitError:
    # Implement exponential backoff
    time.sleep(2 ** attempt)
    retry()
except AuthenticationError:
    # Re-authenticate
    refresh_credentials()
except Exception as e:
    # Log but continue with degraded functionality
    logger.error(f"Non-critical error: {e}")
    return fallback_value
```

### Caching Strategy
```python
# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=100)
def categorize_domain(domain: str) -> str:
    """Cache domain categorization"""
    
# Cache Exa searches (avoid duplicate API calls)
def search_with_cache(query: str):
    cache_key = hashlib.md5(query.encode()).hexdigest()
    # Check cache first
```

---

## Success Metrics

Track these for each run:
```python
metrics = {
    'emails_processed': int,
    'newsletters_found': int,
    'profiles_matched': int,
    'api_calls': {
        'gmail': int,
        'exa': int,
        'gemini': int,
        'apify': int
    },
    'tokens_used': {
        'haiku': int,
        'sonnet': int
    },
    'total_cost_usd': float,
    'processing_time_seconds': float,
    'confidence_score': float  # 0-10
}
```

---

## Deployment Checklist

### Before First Run:
- [ ] Set up Google Cloud project for Gmail API
- [ ] Download OAuth credentials JSON
- [ ] Get API keys: Google Gemini, Exa, Apify
- [ ] Create `.env` file from `.env.example`
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Create `data/` and `reports/` directories

### First Test Run:
- [ ] Run on your own email first
- [ ] Verify all signals make sense
- [ ] Check that identity resolution finds you
- [ ] Read the generated report critically
- [ ] Verify total cost is under budget

### Scaling to Test Users:
- [ ] Get consent from 5-10 volunteers
- [ ] Run batch analysis
- [ ] Collect feedback on accuracy
- [ ] Iterate on signal extraction logic
- [ ] Tune confidence thresholds

---

## Known Limitations & Workarounds

1. **Generic email addresses (gmail.com, yahoo.com)**
   - Harder to match to profiles
   - Workaround: Ask user to confirm name manually

2. **Common names**
   - Multiple profile matches
   - Workaround: Show top 3, ask user to select

3. **Private social profiles**
   - Can't scrape data
   - Workaround: Graceful degradation, email-only report

4. **Rate limits**
   - Exa: 1000 searches/month
   - Apify: Credit-based
   - Workaround: Cache aggressively, batch processing

5. **Email history**
   - New accounts have little data
   - Workaround: Set minimum threshold (e.g., 50 emails)

---

## Quick Start Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python -m src.main

# Test
pytest tests/
```

---

## Next Steps After MVP

1. **Add web UI** (Streamlit/Gradio for easy demo)
2. **Batch processing** (analyze multiple users)
3. **Historical tracking** (show changes over time)
4. **Export options** (PDF, JSON API)
5. **Privacy dashboard** (show what's publicly visible)
6. **Comparison mode** (compare two personas)

---

## Resources

- Gmail API Docs: https://developers.google.com/gmail/api
- Exa API Docs: https://docs.exa.ai
- Apify Docs: https://docs.apify.com
- Google Gemini API Docs: https://ai.google.dev/docs
- OAuth Setup Guide: https://developers.google.com/identity/protocols/oauth2

---

## Final Notes for Development

**Development Philosophy:**
- Build incrementally (Phase 1 → 5)
- Test each phase before moving to next
- Optimize for cost from the start
- Handle errors gracefully
- Log everything for debugging

**Code Quality Standards:**
- Type hints everywhere
- Docstrings for all functions
- Pydantic for data validation
- Keep functions under 50 lines
- DRY principle - extract common patterns

**When You Get Stuck:**
- Check API documentation
- Test with minimal examples first
- Add logging to debug data flow
- Validate assumptions with print statements
- Ask for clarification if requirements unclear

**Remember:**
The goal is a working MVP that demonstrates the concept at <$0.01/profile. Don't over-engineer. Focus on the core value: "How much can we learn from an email alone?"

Good luck! 🚀