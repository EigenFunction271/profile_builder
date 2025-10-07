"""Main entry point for Digital Footprint Analyzer - Phase 1 (OAuth + Email Fetching)"""
import sys
from pathlib import Path
from typing import Optional

from .auth.gmail_oauth import GmailAuthenticator
from .email_analysis.fetcher import EmailFetcher
from .utils.config import load_config


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🔍 Digital Footprint Analyzer - Phase 1")
    print("   Gmail OAuth + Email Fetching")
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


def fetch_and_display_emails(fetcher: EmailFetcher) -> None:
    """Fetch emails and display summary
    
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
    
    # Display sample emails
    if emails:
        print("Step 4: Sample of Recent Emails")
        print("-" * 60)
        
        for i, email in enumerate(emails[:5], 1):
            print(f"{i}. From: {email['from'][:50]}")
            print(f"   Subject: {email['subject'][:60]}")
            print(f"   Date: {email['date']}")
            print(f"   Snippet: {email['snippet'][:80]}...")
            print()
    
    # Display sent email sample
    if sent_emails:
        print("Step 5: Sample of Sent Emails")
        print("-" * 60)
        
        for i, email in enumerate(sent_emails[:5], 1):
            print(f"{i}. To: {email['to'][:50]}")
            print(f"   Subject: {email['subject'][:60]}")
            print(f"   Date: {email['date']}")
            print()
    
    # Analysis preview
    print("=" * 60)
    print("✅ Phase 1 Complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  • Successfully authenticated as {user_email}")
    print(f"  • Fetched {len(emails)} recent emails")
    print(f"  • Fetched {len(sent_emails)} sent emails")
    print(f"  • Credentials securely stored for future use")
    print()
    print("Next Phase: Signal Extraction (Zero LLM Cost)")
    print("  - Newsletter identification")
    print("  - Communication style analysis")
    print("  - Professional context extraction")
    print("  - Activity pattern detection")
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
        
        # Fetch and display emails
        fetch_and_display_emails(fetcher)
        
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

