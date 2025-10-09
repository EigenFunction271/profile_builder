"""Main entry point for Digital Footprint Analyzer - Phase 1 & 2"""
import sys
from pathlib import Path
from typing import Optional
import json

from .auth.gmail_oauth import GmailAuthenticator
from .email_analysis.fetcher import EmailFetcher
from .email_analysis.signal_extractor import SignalExtractor
from .utils.config import load_config


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🔍 Digital Footprint Analyzer - Phase 1 & 2")
    print("   Gmail OAuth + Email Fetching + Signal Extraction")
    print("=" * 60)
    print()


def validate_environment(config) -> bool:
    """Validate that required environment variables are set
    
    Args:
        config: Configuration object
    
    Returns:
        True if valid, False otherwise
    """
    missing = config.validate_phase1()
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print()
        print("Please create a .env file with these variables.")
        print("See .env.example for reference.")
        return False
    
    return True


def authenticate_gmail(config) -> Optional[EmailFetcher]:
    """Authenticate with Gmail and return fetcher
    
    Args:
        config: Configuration object
    
    Returns:
        EmailFetcher instance or None if authentication fails
    """
    print("Step 1: Authenticating with Gmail...")
    print("-" * 60)
    
    authenticator = GmailAuthenticator(config)
    
    # Check for existing credentials
    stored_emails = authenticator.get_stored_emails()
    
    if stored_emails:
        print(f"Found existing credentials for {len(stored_emails)} account(s):")
        for i, email in enumerate(stored_emails, 1):
            print(f"  {i}. {email}")
        print()
        
        choice = input("Use existing credentials? (y/n): ").lower().strip()
        
        if choice == 'y':
            # Use first stored email
            credentials = authenticator.load_credentials(stored_emails[0])
            if credentials:
                print(f"✓ Loaded credentials for: {stored_emails[0]}")
                return EmailFetcher(credentials)
            else:
                print("⚠ Failed to load credentials. Re-authenticating...")
    
    # New authentication
    print()
    print("Starting OAuth flow...")
    print("Your browser will open to authorize Gmail access.")
    print()
    
    try:
        credentials = authenticator.authenticate_user()
        fetcher = EmailFetcher(credentials)
        user_email = fetcher.get_user_email()
        
        print()
        print(f"✓ Successfully authenticated as: {user_email}")
        print()
        
        return fetcher
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None


def fetch_and_analyze_emails(fetcher: EmailFetcher) -> None:
    """Fetch emails, extract signals, and display results
    
    Args:
        fetcher: EmailFetcher instance
    """
    user_email = fetcher.get_user_email()
    
    print()
    print("Step 2: Fetching Email Statistics...")
    print("-" * 60)
    
    # Get email counts
    counts = fetcher.get_email_count()
    print(f"Account: {user_email}")
    print(f"Total messages: {counts['total']}")
    print(f"Total threads: {counts['threads']}")
    print(f"Inbox messages: {counts['inbox']}")
    print(f"Sent messages: {counts['sent']}")
    print()
    
    print("Step 3: Fetching Recent Emails...")
    print("-" * 60)
    
    # Fetch recent emails
    print("Fetching last 100 emails (metadata only)...")
    emails = fetcher.fetch_recent_emails(max_results=100)
    print(f"✓ Fetched {len(emails)} emails")
    print()
    
    # Fetch sent emails
    print("Fetching last 50 sent emails...")
    sent_emails = fetcher.fetch_sent_emails(max_results=50)
    print(f"✓ Fetched {len(sent_emails)} sent emails")
    print()
    
    # Phase 2: Extract Signals
    print("Step 4: Extracting Email Signals...")
    print("-" * 60)
    print("Analyzing newsletter subscriptions...")
    print("Analyzing communication style...")
    print("Extracting professional context...")
    print("Detecting activity patterns...")
    
    # Optional: Fetch full email bodies for LLM analysis
    sent_email_bodies = None
    config = load_config()
    if config.enable_llm_analysis and config.gemini_api_key:
        print()
        print("🤖 LLM analysis enabled - fetching full email bodies...")
        sent_email_bodies = []
        for email in sent_emails[:config.llm_max_emails_to_analyze]:
            body = fetcher.fetch_email_body(email['id'])
            if body:
                sent_email_bodies.append(body)
        print(f"✓ Fetched {len(sent_email_bodies)} email bodies for LLM analysis")
    
    print()
    
    extractor = SignalExtractor(config)
    signals = extractor.extract_all_signals(emails, sent_emails, user_email)
    
    print("✓ Signal extraction complete!")
    print()
    
    # Display results
    display_signal_summary(signals)
    
    # Save signals to file
    save_signals(signals)
    
    # Display sample emails
    if emails:
        print()
        print("Step 5: Sample of Recent Emails")
        print("-" * 60)
        
        for i, email in enumerate(emails[:3], 1):
            print(f"{i}. From: {email['from'][:50]}")
            print(f"   Subject: {email['subject'][:60]}")
            print(f"   Date: {email['date']}")
            print()
    
    # Final summary
    print("=" * 60)
    print("✅ Phase 1 & 2 Complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  • Successfully authenticated as {user_email}")
    print(f"  • Fetched {len(emails)} recent emails")
    print(f"  • Fetched {len(sent_emails)} sent emails")
    print(f"  • Extracted {len(signals.newsletter_signals.newsletter_domains)} newsletter subscriptions")
    print(f"  • Analyzed communication style from {signals.communication_style.sent_email_count} sent emails")
    print(f"  • Identified {len(signals.professional_context.top_contact_domains)} top contact domains")
    print(f"  • Analysis quality score: {signals.analysis_quality_score}/1.0")
    print()
    print("Next Phases:")
    print("  Phase 3: Identity Resolution (LLM-based profile matching)")
    print("  Phase 4: Profile Enrichment (LinkedIn/Twitter scraping)")
    print("  Phase 5: Report Generation (AI-powered persona reports)")
    print()


def display_signal_summary(signals) -> None:
    """Display summary of extracted signals
    
    Args:
        signals: EmailSignals object
    """
    print("=" * 60)
    print("📊 SIGNAL EXTRACTION RESULTS")
    print("=" * 60)
    print()
    
    # Newsletter Signals
    print("📧 Newsletter Subscriptions:")
    print(f"  • Total newsletters found: {signals.newsletter_signals.total_newsletters}")
    print(f"  • Newsletter percentage: {signals.newsletter_signals.newsletter_percentage}%")
    print(f"  • Unique domains: {len(signals.newsletter_signals.newsletter_domains)}")
    
    if signals.newsletter_signals.newsletter_categories:
        print("  • Categories:")
        for category, count in sorted(
            signals.newsletter_signals.newsletter_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            print(f"    - {category.title()}: {count} emails")
    
    if signals.newsletter_signals.top_newsletters:
        print(f"  • Top newsletters: {', '.join(signals.newsletter_signals.top_newsletters[:3])}")
    print()
    
    # Communication Style
    print("💬 Communication Style:")
    print(f"  • Average email length: ~{signals.communication_style.avg_email_length} words")
    print(f"  • Formality score: {signals.communication_style.formality_score}/1.0 ", end="")
    
    if signals.communication_style.formality_score > 0.7:
        print("(Very formal)")
    elif signals.communication_style.formality_score > 0.5:
        print("(Moderately formal)")
    else:
        print("(Casual)")
    
    print(f"  • Emoji usage: {signals.communication_style.emoji_usage_rate}%")
    print(f"  • Average recipients: {signals.communication_style.avg_recipients_per_email}")
    
    if signals.communication_style.common_greetings:
        print(f"  • Common greetings: {', '.join(signals.communication_style.common_greetings)}")
    if signals.communication_style.common_signoffs:
        print(f"  • Common signoffs: {', '.join(signals.communication_style.common_signoffs)}")
    
    # Display LLM-enhanced insights if available
    if signals.communication_style.llm_analysis_available:
        print()
        print("  🤖 LLM-Enhanced Insights:")
        if signals.communication_style.llm_tone:
            print(f"     • Tone: {signals.communication_style.llm_tone}")
        if signals.communication_style.llm_writing_style:
            print(f"     • Writing style: {signals.communication_style.llm_writing_style}")
        if signals.communication_style.llm_professionalism_level:
            print(f"     • Professionalism: {signals.communication_style.llm_professionalism_level}/10")
        if signals.communication_style.llm_common_topics:
            print(f"     • Common topics: {', '.join(signals.communication_style.llm_common_topics[:3])}")
        if signals.communication_style.llm_personality_traits:
            print(f"     • Personality traits: {', '.join(signals.communication_style.llm_personality_traits)}")
    
    print()
    
    # Professional Context
    print("💼 Professional Context:")
    if signals.professional_context.inferred_industry:
        print(f"  • Inferred industry: {signals.professional_context.inferred_industry}")
    
    print(f"  • Unique contacts: {signals.professional_context.total_unique_contacts}")
    print(f"  • Top contact domains: {', '.join(signals.professional_context.top_contact_domains[:5])}")
    
    if signals.professional_context.company_affiliations:
        print(f"  • Company affiliations: {', '.join(signals.professional_context.company_affiliations)}")
    
    if signals.professional_context.professional_keywords:
        print(f"  • Professional keywords: {', '.join(signals.professional_context.professional_keywords[:5])}")
    
    if signals.professional_context.domain_categories:
        print("  • Domain categories:")
        for category, count in sorted(
            signals.professional_context.domain_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]:
            print(f"    - {category.title()}: {count} contacts")
    print()
    
    # Activity Patterns
    print("📈 Activity Patterns:")
    print(f"  • Emails per day: {signals.activity_patterns.emails_per_day}")
    print(f"  • Date range analyzed: {signals.activity_patterns.date_range_days} days")
    print(f"  • Total threads: {signals.activity_patterns.total_threads}")
    print(f"  • Average thread depth: {signals.activity_patterns.thread_depth_avg}")
    print(f"  • Response rate: {signals.activity_patterns.response_rate}%")
    
    if signals.activity_patterns.peak_activity_hours:
        hours_str = ', '.join(f"{h}:00" for h in signals.activity_patterns.peak_activity_hours)
        print(f"  • Peak activity hours: {hours_str}")
    
    if signals.activity_patterns.peak_activity_days:
        print(f"  • Peak activity days: {', '.join(signals.activity_patterns.peak_activity_days)}")
    print()


def save_signals(signals) -> None:
    """Save extracted signals to JSON file
    
    Args:
        signals: EmailSignals object
    """
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate filename
    email_safe = signals.user_email.replace('@', '_at_').replace('.', '_')
    timestamp = signals.analyzed_at.strftime('%Y%m%d_%H%M%S')
    filename = f"signals_{email_safe}_{timestamp}.json"
    filepath = reports_dir / filename
    
    # Save to JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(signals.model_dump(), f, indent=2, default=str)
    
    print(f"💾 Signals saved to: {filepath}")
    print()


def main():
    """Main application entry point"""
    try:
        print_banner()
        
        # Load configuration
        config = load_config()
        
        # Validate environment
        if not validate_environment(config):
            sys.exit(1)
        
        # Authenticate with Gmail
        fetcher = authenticate_gmail(config)
        if not fetcher:
            sys.exit(1)
        
        # Fetch and analyze emails
        fetch_and_analyze_emails(fetcher)
        
    except KeyboardInterrupt:
        print()
        print("Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

