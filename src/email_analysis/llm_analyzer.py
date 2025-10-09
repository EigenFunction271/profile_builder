"""LLM-based email analysis with rate limiting (Optional Enhancement)

This module provides optional LLM-enhanced analysis of email content.
Uses Google Gemini with careful rate limiting and cost tracking.

Rate Limits (Gemini Free Tier):
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

Cost (Gemini Flash 2.0):
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- ~10 emails: ~$0.0002 (well within budget)
"""
import time
from typing import List, Dict, Any, Optional
from collections import deque
from datetime import datetime, timedelta

from ..utils.llm_client import LLMClient
from ..utils.config import Config


class RateLimiter:
    """Simple token bucket rate limiter for API calls"""
    
    def __init__(self, requests_per_minute: int = 15, requests_per_day: int = 1500):
        """Initialize rate limiter
        
        Args:
            requests_per_minute: Max requests per minute
            requests_per_day: Max requests per day
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        
        # Track recent requests
        self.minute_requests: deque = deque()
        self.day_requests: deque = deque()
    
    def wait_if_needed(self) -> None:
        """Wait if rate limits would be exceeded
        
        Blocks until a request can be made safely.
        """
        now = datetime.now()
        
        # Clean old requests from tracking
        self._clean_old_requests(now)
        
        # Check minute limit
        if len(self.minute_requests) >= self.requests_per_minute:
            # Wait until oldest request is >1 minute old
            oldest = self.minute_requests[0]
            wait_until = oldest + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()
            
            if wait_seconds > 0:
                print(f"⏱️  Rate limit: waiting {wait_seconds:.1f}s...")
                time.sleep(wait_seconds)
                self._clean_old_requests(datetime.now())
        
        # Check day limit
        if len(self.day_requests) >= self.requests_per_day:
            print("⚠️  Daily rate limit reached! Skipping LLM analysis.")
            raise RateLimitException("Daily rate limit exceeded")
        
        # Record this request
        now = datetime.now()
        self.minute_requests.append(now)
        self.day_requests.append(now)
    
    def _clean_old_requests(self, now: datetime) -> None:
        """Remove requests older than tracking window
        
        Args:
            now: Current timestamp
        """
        # Remove requests older than 1 minute
        cutoff_minute = now - timedelta(minutes=1)
        while self.minute_requests and self.minute_requests[0] < cutoff_minute:
            self.minute_requests.popleft()
        
        # Remove requests older than 1 day
        cutoff_day = now - timedelta(days=1)
        while self.day_requests and self.day_requests[0] < cutoff_day:
            self.day_requests.popleft()
    
    def get_status(self) -> Dict[str, int]:
        """Get current rate limit status
        
        Returns:
            Dictionary with current usage
        """
        self._clean_old_requests(datetime.now())
        return {
            'requests_last_minute': len(self.minute_requests),
            'requests_last_day': len(self.day_requests),
            'minute_limit': self.requests_per_minute,
            'day_limit': self.requests_per_day
        }


class RateLimitException(Exception):
    """Raised when rate limit is exceeded"""
    pass


class EmailLLMAnalyzer:
    """Analyzes email content using LLM for richer insights"""
    
    # Prompt for analyzing sent emails
    ANALYSIS_PROMPT = """Analyze these sent emails to understand the sender's communication style and characteristics.

EMAILS:
{emails}

Extract the following insights in JSON format:

1. **tone**: Overall tone (professional, friendly, casual, formal, enthusiastic, etc.)
2. **writing_style**: Key characteristics of writing style
3. **common_topics**: Main topics discussed (list of 3-5)
4. **relationship_quality**: How they build relationships (warm, transactional, collaborative, etc.)
5. **professionalism_level**: 1-10 scale (1=very casual, 10=very formal)
6. **personality_traits**: 2-3 personality traits evident from writing
7. **communication_strengths**: 2-3 strengths in their communication

Be specific and evidence-based. Focus on patterns across multiple emails.

Respond ONLY with valid JSON."""
    
    def __init__(self, config: Config, rate_limiter: Optional[RateLimiter] = None):
        """Initialize LLM analyzer
        
        Args:
            config: Application configuration
            rate_limiter: Optional custom rate limiter
        """
        self.config = config
        self.llm = LLMClient(config)
        self.rate_limiter = rate_limiter or RateLimiter()
    
    def analyze_sent_emails(
        self,
        email_bodies: List[str],
        max_emails: int = 10
    ) -> Optional[Dict[str, Any]]:
        """Analyze sent email bodies for communication insights
        
        Args:
            email_bodies: List of email body texts
            max_emails: Maximum emails to analyze (default: 10)
        
        Returns:
            Dictionary with LLM insights or None if analysis fails
        """
        if not email_bodies:
            return None
        
        # Limit to max_emails
        emails_to_analyze = email_bodies[:max_emails]
        
        # Check if we have Gemini API key
        if not self.config.gemini_api_key:
            print("⚠️  No Gemini API key found. Skipping LLM analysis.")
            return None
        
        try:
            # Wait for rate limit
            self.rate_limiter.wait_if_needed()
            
            # Prepare email text
            email_texts = []
            for i, body in enumerate(emails_to_analyze, 1):
                # Truncate long emails (keep first 500 chars)
                truncated = body[:500] if len(body) > 500 else body
                email_texts.append(f"Email {i}:\n{truncated}\n")
            
            combined_emails = "\n---\n".join(email_texts)
            
            # Create prompt
            prompt = self.ANALYSIS_PROMPT.format(emails=combined_emails)
            
            # Count tokens for cost tracking
            input_tokens = self.llm.count_tokens(prompt)
            print(f"📊 Analyzing {len(emails_to_analyze)} emails with LLM (~{input_tokens} tokens)...")
            
            # Call LLM
            result = self.llm.generate_json(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3,  # Lower for more consistent analysis
                system_instruction="You are an expert at analyzing communication styles from email content."
            )
            
            # Log cost
            stats = self.llm.get_usage_stats()
            print(f"💰 LLM cost: ${stats['total_cost_usd']:.6f} (cumulative)")
            
            return result
            
        except RateLimitException as e:
            print(f"⚠️  {e}")
            return None
        except Exception as e:
            print(f"⚠️  LLM analysis failed: {e}")
            return None
    
    def get_rate_limit_status(self) -> Dict[str, int]:
        """Get current rate limit status
        
        Returns:
            Rate limit usage statistics
        """
        return self.rate_limiter.get_status()
    
    def get_cost_stats(self) -> Dict[str, Any]:
        """Get LLM usage and cost statistics
        
        Returns:
            Cost and token usage stats
        """
        return self.llm.get_usage_stats()


def analyze_emails_with_llm(
    config: Config,
    email_bodies: List[str],
    max_emails: int = 10
) -> Optional[Dict[str, Any]]:
    """Convenience function to analyze emails with LLM
    
    Args:
        config: Application configuration
        email_bodies: List of email body texts
        max_emails: Maximum number of emails to analyze
    
    Returns:
        LLM analysis results or None
    """
    analyzer = EmailLLMAnalyzer(config)
    return analyzer.analyze_sent_emails(email_bodies, max_emails=max_emails)

