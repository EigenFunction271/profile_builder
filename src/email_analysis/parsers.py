"""Email parsing utilities for signal extraction (zero LLM cost)"""
import re
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from collections import Counter


# Newsletter detection patterns
NEWSLETTER_INDICATORS = [
    'newsletter', 'digest', 'weekly', 'daily', 'roundup', 'briefing',
    'update', 'bulletin', 'dispatch', 'subscription'
]

NEWSLETTER_DOMAINS = {
    'substack.com', 'substackcdn.com', 'beehiiv.com', 'mailchimp.com',
    'convertkit.com', 'ghost.io', 'buttondown.email', 'revue.co'
}

# Domain categorization
DOMAIN_CATEGORIES = {
    'technology': [
        'techcrunch.com', 'theverge.com', 'wired.com', 'arstechnica.com',
        'hackernews', 'github.com', 'stackoverflow.com', 'dev.to',
        'medium.com', 'substack.com', 'twitter.com'
    ],
    'finance': [
        'bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com',
        'morningbrew.com', 'finimize.com', 'robinhood.com'
    ],
    'business': [
        'linkedin.com', 'harvard.edu', 'forbes.com', 'inc.com',
        'entrepreneur.com', 'fastcompany.com'
    ],
    'news': [
        'nytimes.com', 'washingtonpost.com', 'cnn.com', 'bbc.com',
        'theguardian.com', 'npr.org'
    ],
    'productivity': [
        'notion.so', 'todoist.com', 'trello.com', 'asana.com',
        'slack.com', 'zoom.us', 'calendly.com'
    ],
    'education': [
        '.edu', 'coursera.org', 'udemy.com', 'edx.org',
        'khanacademy.org', 'codecademy.com'
    ]
}

# Formality indicators (for scoring 0-1)
FORMAL_PHRASES = [
    'dear sir', 'dear madam', 'to whom it may concern', 'sincerely',
    'respectfully', 'pursuant to', 'please find attached', 'i am writing to',
    'i would like to', 'thank you for your', 'looking forward to',
    'kind regards', 'yours faithfully', 'yours sincerely'
]

CASUAL_PHRASES = [
    'hey', 'hi there', 'what\'s up', 'cheers', 'thanks!', 'thx',
    'gonna', 'wanna', 'yeah', 'yep', 'nope', 'btw', 'fyi',
    'lol', 'lmk', 'asap', 'cool', 'awesome', 'great!', 'sounds good'
]

# Common greetings and signoffs
GREETINGS = [
    'hi', 'hello', 'hey', 'dear', 'good morning', 'good afternoon',
    'good evening', 'greetings', 'hope you\'re well', 'hope this finds you well'
]

SIGNOFFS = [
    'best', 'thanks', 'regards', 'cheers', 'sincerely', 'best regards',
    'kind regards', 'warm regards', 'thank you', 'talk soon', 'see you',
    'yours', 'yours truly', 'respectfully'
]


def extract_domain(email_address: str) -> Optional[str]:
    """Extract domain from email address
    
    Args:
        email_address: Email address string
    
    Returns:
        Domain or None if invalid
    """
    if not email_address or '@' not in email_address:
        return None
    
    try:
        # Handle "Name <email@domain.com>" format
        if '<' in email_address and '>' in email_address:
            email_address = email_address.split('<')[1].split('>')[0]
        
        domain = email_address.split('@')[-1].strip().lower()
        # Remove any trailing characters
        domain = domain.split()[0] if domain else None
        return domain
    except Exception:
        return None


def is_newsletter(email: Dict) -> bool:
    """Heuristic to identify if email is a newsletter
    
    Args:
        email: Email metadata dictionary
    
    Returns:
        True if likely a newsletter
    """
    # Check for List-Unsubscribe header (strong indicator)
    if email.get('list_unsubscribe'):
        return True
    
    # Check subject for newsletter keywords
    subject = email.get('subject', '').lower()
    if any(indicator in subject for indicator in NEWSLETTER_INDICATORS):
        return True
    
    # Check from domain
    from_email = email.get('from', '')
    domain = extract_domain(from_email)
    if domain and any(newsletter_domain in domain for newsletter_domain in NEWSLETTER_DOMAINS):
        return True
    
    # Check for "no-reply" or "noreply" sender
    if 'noreply' in from_email.lower() or 'no-reply' in from_email.lower():
        return True
    
    return False


def categorize_domain(domain: str) -> Optional[str]:
    """Map domain to category (tech, finance, etc.)
    
    Args:
        domain: Domain name
    
    Returns:
        Category name or None
    """
    if not domain:
        return None
    
    domain = domain.lower()
    
    for category, patterns in DOMAIN_CATEGORIES.items():
        for pattern in patterns:
            if pattern in domain:
                return category
    
    return None


def extract_name_from_email_format(email_address: str) -> Optional[str]:
    """Parse name from email format like john.doe@company.com -> John Doe
    
    Args:
        email_address: Email address
    
    Returns:
        Parsed name or None
    """
    if not email_address or '@' not in email_address:
        return None
    
    try:
        # Extract local part (before @)
        local_part = email_address.split('@')[0]
        
        # Split by common separators
        parts = re.split(r'[._\-+]', local_part)
        
        # Filter out numbers and single characters
        name_parts = [p.capitalize() for p in parts if len(p) > 1 and not p.isdigit()]
        
        if len(name_parts) >= 2:
            return ' '.join(name_parts[:2])  # First and last name
        
        return None
    except Exception:
        return None


def extract_name_from_display(from_field: str) -> Optional[str]:
    """Extract name from "Name <email@domain.com>" format
    
    Args:
        from_field: From header value
    
    Returns:
        Display name or None
    """
    if '<' in from_field and '>' in from_field:
        name = from_field.split('<')[0].strip()
        # Remove quotes
        name = name.strip('"').strip("'")
        if name and len(name) > 2:
            return name
    
    return None


def calculate_formality_score(text: str) -> float:
    """Use regex patterns to score formality 0-1
    
    Args:
        text: Email body text
    
    Returns:
        Formality score (0=casual, 1=formal)
    """
    if not text:
        return 0.5
    
    text_lower = text.lower()
    
    # Count formal vs casual indicators
    formal_count = sum(1 for phrase in FORMAL_PHRASES if phrase in text_lower)
    casual_count = sum(1 for phrase in CASUAL_PHRASES if phrase in text_lower)
    
    # Additional heuristics
    # - Contractions indicate casual
    contractions = len(re.findall(r"\w+n't|\w+'ll|\w+'re|\w+'ve|\w+'d", text))
    casual_count += contractions
    
    # - Professional vocabulary
    if 'pursuant' in text_lower or 'herewith' in text_lower or 'aforementioned' in text_lower:
        formal_count += 2
    
    # - Exclamation marks indicate casual
    casual_count += text.count('!')
    
    # - Question marks can indicate casual
    if text.count('?') > 2:
        casual_count += 1
    
    # Calculate score
    total = formal_count + casual_count
    if total == 0:
        return 0.5  # Neutral if no indicators
    
    score = formal_count / total
    return min(max(score, 0.0), 1.0)  # Clamp to 0-1


def extract_greeting(text: str) -> Optional[str]:
    """Extract greeting from email text
    
    Args:
        text: Email body text (first few lines)
    
    Returns:
        Greeting or None
    """
    if not text:
        return None
    
    # Get first 2-3 lines
    lines = text.split('\n')[:3]
    first_text = ' '.join(lines).lower().strip()
    
    for greeting in GREETINGS:
        if first_text.startswith(greeting):
            return greeting.title()
    
    return None


def extract_signoff(text: str) -> Optional[str]:
    """Extract sign-off from email text
    
    Args:
        text: Email body text (last few lines)
    
    Returns:
        Sign-off or None
    """
    if not text:
        return None
    
    # Get last 3-4 lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    last_lines = ' '.join(lines[-4:]).lower() if lines else ''
    
    for signoff in SIGNOFFS:
        if signoff in last_lines:
            return signoff.title()
    
    return None


def count_words(text: str) -> int:
    """Count words in text
    
    Args:
        text: Text content
    
    Returns:
        Word count
    """
    if not text:
        return 0
    return len(text.split())


def count_emojis(text: str) -> int:
    """Count emoji characters in text
    
    Args:
        text: Text content
    
    Returns:
        Emoji count
    """
    if not text:
        return 0
    
    # Unicode ranges for common emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", 
        flags=re.UNICODE
    )
    return len(emoji_pattern.findall(text))


def parse_timestamp(date_str: str) -> Optional[datetime]:
    """Parse email date string to datetime
    
    Args:
        date_str: Date string from email header
    
    Returns:
        Parsed datetime or None
    """
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except Exception:
        return None


def extract_hour(date_str: str) -> Optional[int]:
    """Extract hour (0-23) from email date
    
    Args:
        date_str: Date string from email header
    
    Returns:
        Hour or None
    """
    dt = parse_timestamp(date_str)
    return dt.hour if dt else None


def extract_day_of_week(date_str: str) -> Optional[str]:
    """Extract day of week from email date
    
    Args:
        date_str: Date string from email header
    
    Returns:
        Day name or None
    """
    dt = parse_timestamp(date_str)
    if dt:
        return dt.strftime('%A')  # Monday, Tuesday, etc.
    return None


def extract_recipients_count(to_field: str) -> int:
    """Count number of recipients in To field
    
    Args:
        to_field: To header value
    
    Returns:
        Number of recipients
    """
    if not to_field:
        return 0
    
    # Split by comma and semicolon
    recipients = re.split(r'[,;]', to_field)
    return len([r for r in recipients if '@' in r])


def is_likely_response(email: Dict) -> bool:
    """Check if email is likely a response/reply
    
    Args:
        email: Email metadata
    
    Returns:
        True if likely a response
    """
    subject = email.get('subject', '')
    
    # Check for Re: or Fwd: prefix
    if subject.lower().startswith(('re:', 'fwd:', 'fw:')):
        return True
    
    # Check if it's part of a thread with multiple messages
    thread_id = email.get('thread_id')
    if thread_id and email.get('labels', []):
        # If it has SENT label but is in a thread, likely a response
        if 'SENT' in email.get('labels', []):
            return True
    
    return False


def extract_company_from_domain(domain: str) -> Optional[str]:
    """Extract likely company name from domain
    
    Args:
        domain: Domain name
    
    Returns:
        Company name or None
    """
    if not domain:
        return None
    
    # Remove common TLDs
    company = domain.replace('.com', '').replace('.org', '').replace('.net', '')
    company = company.replace('.io', '').replace('.co', '').replace('.ai', '')
    
    # Remove subdomains (keep main domain)
    parts = company.split('.')
    if len(parts) > 1:
        company = parts[-1]
    
    # Capitalize
    company = company.title()
    
    # Filter out generic domains
    generic_domains = {'gmail', 'yahoo', 'hotmail', 'outlook', 'icloud', 'mail', 'email'}
    if company.lower() in generic_domains:
        return None
    
    return company if company else None


def find_most_common(items: List[str], top_n: int = 10) -> List[str]:
    """Find most common items in list
    
    Args:
        items: List of items
        top_n: Number of top items to return
    
    Returns:
        List of most common items
    """
    if not items:
        return []
    
    counter = Counter(items)
    return [item for item, count in counter.most_common(top_n)]


def calculate_percentage(part: int, total: int) -> float:
    """Calculate percentage safely
    
    Args:
        part: Part value
        total: Total value
    
    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

