"""Signal extraction from emails (Zero LLM Cost)

Extracts four categories of signals:
1. Newsletter subscriptions
2. Communication style
3. Professional context
4. Activity patterns

All analysis uses pure regex/heuristics - no LLM calls.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict

from ..models.schemas import (
    EmailSignals,
    NewsletterSignals,
    CommunicationStyleSignals,
    ProfessionalContextSignals,
    ActivityPatternSignals
)
from ..utils.config import Config
from .parsers import (
    extract_domain,
    is_newsletter,
    categorize_domain,
    calculate_formality_score,
    extract_greeting,
    extract_signoff,
    count_words,
    count_emojis,
    extract_hour,
    extract_day_of_week,
    extract_recipients_count,
    is_likely_response,
    extract_company_from_domain,
    find_most_common,
    calculate_percentage,
    parse_timestamp
)


class SignalExtractor:
    """Extract behavioral signals from email data"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize signal extractor
        
        Args:
            config: Optional configuration for LLM analysis
        """
        self.config = config
    
    def extract_all_signals(
        self,
        emails: List[Dict[str, Any]],
        sent_emails: List[Dict[str, Any]],
        user_email: str
    ) -> EmailSignals:
        """Extract all signal categories from email data
        
        Args:
            emails: List of received email metadata
            sent_emails: List of sent email metadata
            user_email: User's email address
        
        Returns:
            Complete EmailSignals object
        """
        # Extract each category
        newsletter_signals = self.extract_newsletter_signals(emails)
        communication_style = self.extract_communication_style(sent_emails)
        professional_context = self.extract_professional_context(emails, sent_emails)
        activity_patterns = self.extract_activity_patterns(emails + sent_emails)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            len(emails), len(sent_emails), newsletter_signals, communication_style
        )
        
        return EmailSignals(
            user_email=user_email,
            newsletter_signals=newsletter_signals,
            communication_style=communication_style,
            professional_context=professional_context,
            activity_patterns=activity_patterns,
            total_emails_analyzed=len(emails),
            sent_emails_analyzed=len(sent_emails),
            analysis_quality_score=quality_score
        )
    
    def extract_newsletter_signals(self, emails: List[Dict[str, Any]]) -> NewsletterSignals:
        """Identify newsletters by headers, domains, and subject patterns
        
        Args:
            emails: List of email metadata
        
        Returns:
            NewsletterSignals object
        """
        newsletters = []
        newsletter_domains = []
        newsletter_names = []
        
        for email in emails:
            if is_newsletter(email):
                newsletters.append(email)
                
                # Extract domain
                from_email = email.get('from', '')
                domain = extract_domain(from_email)
                if domain:
                    newsletter_domains.append(domain)
                
                # Extract newsletter name from From field
                if '<' in from_email:
                    name = from_email.split('<')[0].strip().strip('"')
                    if name:
                        newsletter_names.append(name)
        
        # Categorize newsletters
        categories = defaultdict(int)
        for domain in newsletter_domains:
            category = categorize_domain(domain)
            if category:
                categories[category] += 1
            else:
                categories['other'] += 1
        
        # Get top newsletters
        top_newsletters = find_most_common(newsletter_names, top_n=10)
        
        # Calculate percentage
        total_emails = len(emails)
        newsletter_percentage = calculate_percentage(len(newsletters), total_emails)
        
        return NewsletterSignals(
            newsletter_domains=list(set(newsletter_domains)),
            newsletter_categories=dict(categories),
            top_newsletters=top_newsletters,
            total_newsletters=len(newsletters),
            newsletter_percentage=newsletter_percentage
        )
    
    def extract_communication_style(
        self,
        sent_emails: List[Dict[str, Any]],
        email_bodies: Optional[List[str]] = None
    ) -> CommunicationStyleSignals:
        """Analyze sent emails for communication style
        
        Args:
            sent_emails: List of sent email metadata
            email_bodies: Optional list of full email bodies for LLM analysis
        
        Returns:
            CommunicationStyleSignals object with optional LLM insights
        """
        if not sent_emails:
            return CommunicationStyleSignals(sent_email_count=0)
        
        # For Phase 2, we'll analyze what we can from metadata
        # Subject lines can give us some insights
        subjects = [email.get('subject', '') for email in sent_emails]
        
        # Approximate formality from subjects
        formality_scores = []
        for subject in subjects:
            score = calculate_formality_score(subject)
            formality_scores.append(score)
        
        avg_formality = sum(formality_scores) / len(formality_scores) if formality_scores else 0.5
        
        # Count emojis in snippets (approximation)
        emoji_count = 0
        total_snippets = 0
        for email in sent_emails:
            snippet = email.get('snippet', '')
            if snippet:
                emoji_count += count_emojis(snippet)
                total_snippets += 1
        
        emoji_rate = calculate_percentage(emoji_count, total_snippets)
        
        # Estimate word count from snippets (rough approximation)
        word_counts = []
        for email in sent_emails:
            snippet = email.get('snippet', '')
            if snippet:
                # Snippet is usually truncated, so multiply by estimated factor
                words = count_words(snippet) * 3  # Approximate full email
                word_counts.append(words)
        
        avg_length = int(sum(word_counts) / len(word_counts)) if word_counts else 0
        
        # Count recipients
        recipient_counts = []
        for email in sent_emails:
            to_field = email.get('to', '')
            count = extract_recipients_count(to_field)
            if count > 0:
                recipient_counts.append(count)
        
        avg_recipients = sum(recipient_counts) / len(recipient_counts) if recipient_counts else 1.0
        
        # Extract common patterns from subjects
        greetings_found = []
        signoffs_found = []
        
        # Try to extract from snippets
        for email in sent_emails:
            snippet = email.get('snippet', '')
            greeting = extract_greeting(snippet)
            if greeting:
                greetings_found.append(greeting)
            
            signoff = extract_signoff(snippet)
            if signoff:
                signoffs_found.append(signoff)
        
        common_greetings = find_most_common(greetings_found, top_n=3)
        common_signoffs = find_most_common(signoffs_found, top_n=3)
        
        # Response time analysis would require thread analysis
        # Skipping for Phase 2 (can be added when we fetch full bodies)
        
        # Base communication style signals
        base_signals = CommunicationStyleSignals(
            avg_email_length=avg_length,
            formality_score=round(avg_formality, 2),
            avg_response_time_hours=None,  # Requires deeper analysis
            emoji_usage_rate=emoji_rate,
            common_greetings=common_greetings,
            common_signoffs=common_signoffs,
            sent_email_count=len(sent_emails),
            avg_recipients_per_email=round(avg_recipients, 1)
        )
        
        # Optional: Enhance with LLM analysis if enabled and bodies available
        if self.config and self.config.enable_llm_analysis and email_bodies:
            llm_insights = self._enhance_with_llm_analysis(email_bodies)
            if llm_insights:
                base_signals.llm_tone = llm_insights.get('tone')
                base_signals.llm_writing_style = llm_insights.get('writing_style')
                base_signals.llm_common_topics = llm_insights.get('common_topics', [])
                base_signals.llm_relationship_quality = llm_insights.get('relationship_quality')
                base_signals.llm_professionalism_level = llm_insights.get('professionalism_level')
                base_signals.llm_personality_traits = llm_insights.get('personality_traits', [])
                base_signals.llm_communication_strengths = llm_insights.get('communication_strengths', [])
                base_signals.llm_analysis_available = True
        
        return base_signals
    
    def extract_professional_context(
        self,
        emails: List[Dict[str, Any]],
        sent_emails: List[Dict[str, Any]]
    ) -> ProfessionalContextSignals:
        """Extract professional context from contact patterns
        
        Args:
            emails: Received emails
            sent_emails: Sent emails
        
        Returns:
            ProfessionalContextSignals object
        """
        # Collect all contact domains
        contact_domains = []
        unique_contacts = set()
        
        # From received emails
        for email in emails:
            from_email = email.get('from', '')
            domain = extract_domain(from_email)
            if domain and not self._is_personal_domain(domain):
                contact_domains.append(domain)
            if from_email:
                unique_contacts.add(from_email.lower())
        
        # From sent emails (To field)
        for email in sent_emails:
            to_field = email.get('to', '')
            if to_field:
                # Split multiple recipients
                recipients = to_field.split(',')
                for recipient in recipients:
                    domain = extract_domain(recipient)
                    if domain and not self._is_personal_domain(domain):
                        contact_domains.append(domain)
                    if recipient:
                        unique_contacts.add(recipient.lower().strip())
        
        # Get top domains
        top_domains = find_most_common(contact_domains, top_n=15)
        
        # Categorize domains
        categories = defaultdict(int)
        for domain in contact_domains:
            category = categorize_domain(domain)
            if category:
                categories[category] += 1
        
        # Infer industry (most common category)
        inferred_industry = None
        if categories:
            inferred_industry = max(categories.items(), key=lambda x: x[1])[0].title()
        
        # Extract company affiliations
        companies = []
        for domain in top_domains[:10]:  # Top 10 domains
            company = extract_company_from_domain(domain)
            if company:
                companies.append(company)
        
        # Extract professional keywords from subjects
        all_subjects = [e.get('subject', '') for e in emails + sent_emails]
        keywords = self._extract_professional_keywords(all_subjects)
        
        return ProfessionalContextSignals(
            top_contact_domains=top_domains,
            domain_categories=dict(categories),
            inferred_industry=inferred_industry,
            company_affiliations=companies[:5],  # Top 5 companies
            professional_keywords=keywords,
            total_unique_contacts=len(unique_contacts)
        )
    
    def extract_activity_patterns(self, all_emails: List[Dict[str, Any]]) -> ActivityPatternSignals:
        """Calculate activity patterns from timestamps
        
        Args:
            all_emails: All emails (received + sent)
        
        Returns:
            ActivityPatternSignals object
        """
        if not all_emails:
            return ActivityPatternSignals()
        
        # Extract hours and days
        hours = []
        days = []
        timestamps = []
        thread_ids = []
        response_count = 0
        
        for email in all_emails:
            date_str = email.get('date', '')
            
            # Extract hour
            hour = extract_hour(date_str)
            if hour is not None:
                hours.append(hour)
            
            # Extract day
            day = extract_day_of_week(date_str)
            if day:
                days.append(day)
            
            # Parse timestamp
            ts = parse_timestamp(date_str)
            if ts:
                timestamps.append(ts)
            
            # Track threads
            thread_id = email.get('thread_id')
            if thread_id:
                thread_ids.append(thread_id)
            
            # Count responses
            if is_likely_response(email):
                response_count += 1
        
        # Calculate emails per day
        emails_per_day = 0.0
        date_range_days = 0
        
        if timestamps:
            timestamps.sort()
            earliest = timestamps[0]
            latest = timestamps[-1]
            date_range = (latest - earliest).days
            date_range_days = max(date_range, 1)  # At least 1 day
            emails_per_day = round(len(timestamps) / date_range_days, 1)
        
        # Find peak activity hours (top 3)
        peak_hours = []
        if hours:
            hour_counts = Counter(hours)
            peak_hours = [hour for hour, _ in hour_counts.most_common(3)]
        
        # Find peak activity days (top 3)
        peak_days = []
        if days:
            day_counts = Counter(days)
            peak_days = [day for day, _ in day_counts.most_common(3)]
        
        # Calculate thread depth
        unique_threads = len(set(thread_ids)) if thread_ids else 0
        thread_depth_avg = len(thread_ids) / unique_threads if unique_threads > 0 else 1.0
        
        # Calculate response rate
        response_rate = calculate_percentage(response_count, len(all_emails))
        
        return ActivityPatternSignals(
            emails_per_day=emails_per_day,
            peak_activity_hours=peak_hours,
            peak_activity_days=peak_days,
            thread_depth_avg=round(thread_depth_avg, 1),
            response_rate=response_rate,
            date_range_days=date_range_days,
            total_threads=unique_threads
        )
    
    def _is_personal_domain(self, domain: str) -> bool:
        """Check if domain is a personal email provider
        
        Args:
            domain: Domain name
        
        Returns:
            True if personal domain
        """
        personal_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'aol.com', 'protonmail.com', 'mail.com'
        }
        return domain.lower() in personal_domains
    
    def _extract_professional_keywords(self, subjects: List[str]) -> List[str]:
        """Extract professional keywords from email subjects
        
        Args:
            subjects: List of email subjects
        
        Returns:
            List of common professional keywords
        """
        # Common professional terms
        professional_terms = [
            'meeting', 'project', 'proposal', 'contract', 'invoice',
            'report', 'update', 'review', 'deadline', 'schedule',
            'presentation', 'call', 'conference', 'quarterly', 'budget',
            'strategy', 'planning', 'analysis', 'development', 'launch',
            'client', 'team', 'manager', 'director', 'executive'
        ]
        
        # Count occurrences
        keyword_counts = defaultdict(int)
        for subject in subjects:
            subject_lower = subject.lower()
            for term in professional_terms:
                if term in subject_lower:
                    keyword_counts[term] += 1
        
        # Return top keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:10] if count > 1]
    
    def _calculate_quality_score(
        self,
        email_count: int,
        sent_count: int,
        newsletter_signals: NewsletterSignals,
        communication_style: CommunicationStyleSignals
    ) -> float:
        """Calculate data quality score based on completeness
        
        Args:
            email_count: Number of emails analyzed
            sent_count: Number of sent emails
            newsletter_signals: Newsletter analysis results
            communication_style: Communication style results
        
        Returns:
            Quality score 0-1
        """
        score = 0.0
        
        # Email volume (max 0.4)
        if email_count >= 100:
            score += 0.2
        elif email_count >= 50:
            score += 0.1
        
        if sent_count >= 50:
            score += 0.2
        elif sent_count >= 25:
            score += 0.1
        
        # Newsletter detection (max 0.2)
        if newsletter_signals.total_newsletters > 0:
            score += 0.1
        if len(newsletter_signals.newsletter_categories) > 2:
            score += 0.1
        
        # Communication style data (max 0.2)
        if communication_style.avg_email_length > 0:
            score += 0.1
        if communication_style.common_greetings or communication_style.common_signoffs:
            score += 0.1
        
        # Activity patterns (max 0.2)
        score += 0.2  # Always have some activity data if we have emails
        
        return round(min(score, 1.0), 2)
    
    def _enhance_with_llm_analysis(self, email_bodies: List[str]) -> Optional[Dict[str, Any]]:
        """Use LLM to analyze email bodies for richer insights (optional)
        
        Args:
            email_bodies: List of email body texts
        
        Returns:
            Dictionary with LLM insights or None
        """
        try:
            from .llm_analyzer import EmailLLMAnalyzer
            
            analyzer = EmailLLMAnalyzer(self.config)
            max_emails = self.config.llm_max_emails_to_analyze
            
            print(f"🤖 Enhanced LLM analysis enabled (analyzing up to {max_emails} emails)...")
            result = analyzer.analyze_sent_emails(email_bodies, max_emails=max_emails)
            
            if result:
                print("✓ LLM analysis complete!")
            
            return result
            
        except ImportError:
            print("⚠️  LLM analyzer not available")
            return None
        except Exception as e:
            print(f"⚠️  LLM analysis error: {e}")
            return None

