"""Persona report generation using Google Gemini
TEMPLATE FILE - For Phase 5 implementation
"""
from typing import Dict, Any, List
from datetime import datetime
from ..utils.llm_client import LLMClient
from ..utils.config import Config


class PersonaReportGenerator:
    """Generate comprehensive persona reports"""
    
    def __init__(self, config: Config):
        """Initialize report generator
        
        Args:
            config: Application configuration
        """
        self.llm = LLMClient(config)
    
    def generate_report(
        self,
        email_signals: Dict[str, Any],
        matched_profiles: List[Dict[str, Any]],
        enrichment_data: Dict[str, Any],
        user_email: str
    ) -> str:
        """Generate comprehensive persona report
        
        Args:
            email_signals: Signals extracted from emails
            matched_profiles: Matched social profiles
            enrichment_data: Enriched profile data
            user_email: User's email address
        
        Returns:
            Markdown formatted report
        """
        prompt = self._build_report_prompt(
            email_signals,
            matched_profiles,
            enrichment_data,
            user_email
        )
        
        # Generate report with higher token limit
        report = self.llm.generate(
            prompt=prompt,
            max_tokens=3000,
            temperature=0.7,
            system_instruction="You are a digital footprint analyst who creates insightful persona reports."
        )
        
        return report
    
    def _build_report_prompt(
        self,
        email_signals: Dict[str, Any],
        matched_profiles: List[Dict[str, Any]],
        enrichment_data: Dict[str, Any],
        user_email: str
    ) -> str:
        """Build prompt for report generation
        
        Args:
            email_signals: Email signals
            matched_profiles: Matched profiles
            enrichment_data: Enrichment data
            user_email: User email
        
        Returns:
            Formatted prompt
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format matched profiles
        profiles_summary = "\n".join([
            f"- {p['platform']}: {p['profile_url']} (confidence: {p.get('confidence_score', 0)}%)"
            for p in matched_profiles
        ])
        
        return f"""You are a digital footprint analyst. Generate a comprehensive persona report based on the user's digital signals.

INPUT DATA:

EMAIL SIGNALS:
- User Email: {user_email}
- Newsletter Subscriptions: {email_signals.get('newsletter_categories', {})}
  Top Newsletters: {', '.join(email_signals.get('top_newsletters', [])[:10])}
- Communication Style:
  * Avg Email Length: {email_signals.get('avg_email_length', 0)} words
  * Formality Score: {email_signals.get('formality_score', 0):.2f}/1.0
  * Response Time: {email_signals.get('avg_response_time_hours', 0):.1f} hours
  * Emoji Usage: {email_signals.get('emoji_usage_rate', 0):.1f}%
- Professional Context:
  * Top Contact Domains: {', '.join(email_signals.get('top_contact_domains', [])[:10])}
  * Inferred Industry: {email_signals.get('inferred_industry', 'unknown')}
- Activity Patterns:
  * Emails/Day: {email_signals.get('emails_per_day', 0):.1f}
  * Peak Hours: {email_signals.get('peak_activity_hours', [])}

MATCHED PROFILES:
{profiles_summary}

ENRICHMENT DATA:
{enrichment_data}

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

**Data Sources**: Gmail ({len(email_signals)} signals), {len(matched_profiles)} matched profiles

INSTRUCTIONS:
1. Be specific and insightful, not generic
2. Support claims with data points
3. Highlight interesting patterns or contradictions
4. Keep professional but engaging tone
5. Assign overall confidence score 1-10 based on data quality
6. If data is limited, be transparent about it
"""
    
    def export_markdown(self, report: str, output_path: str) -> None:
        """Save report as markdown file
        
        Args:
            report: Generated report text
            output_path: Output file path
        """
        from pathlib import Path
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
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
    generator = PersonaReportGenerator(config)
    
    # Example data
    email_signals = {
        'newsletter_categories': {'tech': 20, 'ai': 15, 'startup': 10},
        'top_newsletters': ['TechCrunch', 'The Verge', 'AI Weekly'],
        'avg_email_length': 150,
        'formality_score': 0.65,
        'avg_response_time_hours': 4.5,
        'emoji_usage_rate': 2.3,
        'top_contact_domains': ['github.com', 'linkedin.com', 'techcorp.com'],
        'inferred_industry': 'technology',
        'emails_per_day': 25.5,
        'peak_activity_hours': [9, 10, 14, 15]
    }
    
    matched_profiles = [
        {
            'platform': 'LinkedIn',
            'profile_url': 'https://linkedin.com/in/example',
            'confidence_score': 85
        }
    ]
    
    report = generator.generate_report(
        email_signals,
        matched_profiles,
        {},
        'example@techcorp.com'
    )
    
    print(report)
    print(f"\nUsage stats: {generator.get_usage_stats()}")

