"""Confidence scoring for identity matches using Google Gemini
TEMPLATE FILE - For Phase 3 implementation
"""
from typing import Dict, Any
from ..utils.llm_client import LLMClient
from ..utils.config import Config


class ConfidenceScorer:
    """Score confidence of identity matches using LLM"""
    
    def __init__(self, config: Config):
        """Initialize confidence scorer
        
        Args:
            config: Application configuration
        """
        self.llm = LLMClient(config)
    
    def score_match(
        self,
        email_signals: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        user_email: str
    ) -> Dict[str, Any]:
        """Score how likely a profile matches the email user
        
        Args:
            email_signals: Signals extracted from email
            candidate_profile: Candidate profile data
            user_email: User's email address
        
        Returns:
            Dictionary with score and reasoning
        """
        prompt = self._build_scoring_prompt(
            email_signals,
            candidate_profile,
            user_email
        )
        
        # Use JSON response for structured output
        result = self.llm.generate_json(
            prompt=prompt,
            max_tokens=500,
            temperature=0.3,  # Lower temperature for more consistent scoring
            system_instruction="You are an expert at matching digital identities across platforms."
        )
        
        return {
            'score': result.get('score', 0),
            'confidence_score': result.get('score', 0),  # Alias for backward compatibility
            'reasoning': result.get('reasoning', ''),
            'platform': candidate_profile.get('platform', 'unknown'),
            'profile_url': candidate_profile.get('url', ''),
            'extracted_data': candidate_profile
        }
    
    def _build_scoring_prompt(
        self,
        email_signals: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        user_email: str
    ) -> str:
        """Build prompt for confidence scoring
        
        Args:
            email_signals: Email signals dictionary
            candidate_profile: Candidate profile dictionary
            user_email: User email
        
        Returns:
            Formatted prompt
        """
        return f"""You are evaluating if a social media profile belongs to the user of this email.

USER EMAIL SIGNALS:
- Email: {user_email}
- Inferred Industry: {email_signals.get('inferred_industry', 'unknown')}
- Top Interests: {', '.join(email_signals.get('newsletter_categories', {}).keys())}
- Newsletter Categories: {email_signals.get('newsletter_categories', {})}
- Top Professional Domains: {', '.join(email_signals.get('top_contact_domains', [])[:5])}

CANDIDATE PROFILE:
- Platform: {candidate_profile.get('platform', 'unknown')}
- Profile URL: {candidate_profile.get('url', '')}
- Name: {candidate_profile.get('name', '')}
- Headline/Bio: {candidate_profile.get('headline', '')}
- Location: {candidate_profile.get('location', '')}
- Company: {candidate_profile.get('company', '')}

TASK:
Score 0-100 how likely this profile belongs to the email user.

Consider:
1. Name match with email format
2. Industry/company alignment
3. Interest overlap
4. Location consistency (if available)
5. Timeline plausibility

OUTPUT FORMAT (JSON only):
{{
  "score": 85,
  "reasoning": "Strong name match, industry aligns with email domains contacted, shared interest in AI/ML newsletters"
}}

Be conservative - only high scores (70+) if confident.
"""
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get LLM usage statistics
        
        Returns:
            Usage stats dictionary
        """
        return self.llm.get_usage_stats()


# Example usage (for testing)
if __name__ == "__main__":
    from ..utils.config import load_config
    
    config = load_config()
    scorer = ConfidenceScorer(config)
    
    # Example data
    email_signals = {
        'inferred_industry': 'technology',
        'newsletter_categories': {'tech': 15, 'ai': 10},
        'top_contact_domains': ['github.com', 'stackoverflow.com']
    }
    
    candidate = {
        'platform': 'LinkedIn',
        'url': 'https://linkedin.com/in/example',
        'name': 'John Doe',
        'headline': 'Software Engineer at Tech Corp',
        'company': 'Tech Corp'
    }
    
    result = scorer.score_match(email_signals, candidate, 'john.doe@techcorp.com')
    print(f"Match score: {result['score']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"\nUsage stats: {scorer.get_usage_stats()}")

