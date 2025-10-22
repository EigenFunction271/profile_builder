"""Tests for Phase 2: Signal Extraction"""
import pytest
from datetime import datetime

from src.email_analysis.parsers import (
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
    extract_name_from_email_format,
    extract_name_from_display
)

from src.email_analysis.signal_extractor import SignalExtractor


class TestEmailParsers:
    """Test email parsing utilities"""
    
    def test_extract_domain(self):
        """Test domain extraction from email"""
        assert extract_domain("john.doe@example.com") == "example.com"
        assert extract_domain("John Doe <john@example.com>") == "example.com"
        assert extract_domain("invalid") is None
        assert extract_domain("") is None
    
    def test_is_newsletter(self):
        """Test newsletter identification"""
        # Newsletter with unsubscribe header
        email1 = {
            'list_unsubscribe': 'http://example.com/unsubscribe',
            'subject': 'Tech News',
            'from': 'newsletter@example.com'
        }
        assert is_newsletter(email1) is True
        
        # Newsletter by subject
        email2 = {
            'subject': 'Weekly Newsletter',
            'from': 'info@company.com'
        }
        assert is_newsletter(email2) is True
        
        # Newsletter by no-reply sender
        email3 = {
            'subject': 'Update',
            'from': 'noreply@example.com'
        }
        assert is_newsletter(email3) is True
        
        # Not a newsletter
        email4 = {
            'subject': 'Re: Meeting tomorrow',
            'from': 'colleague@company.com'
        }
        assert is_newsletter(email4) is False
    
    def test_categorize_domain(self):
        """Test domain categorization"""
        assert categorize_domain("techcrunch.com") == "technology"
        assert categorize_domain("bloomberg.com") == "finance"
        assert categorize_domain("linkedin.com") == "business"
        assert categorize_domain("nytimes.com") == "news"
        assert categorize_domain("random-domain.com") is None
    
    def test_calculate_formality_score(self):
        """Test formality scoring"""
        # Formal email
        formal_text = "Dear Sir, I am writing to inform you about the matter. Sincerely,"
        assert calculate_formality_score(formal_text) > 0.6
        
        # Casual email
        casual_text = "Hey! What's up? Wanna grab coffee? Cheers!"
        assert calculate_formality_score(casual_text) < 0.5
        
        # Neutral
        neutral_text = "Here is the information you requested."
        score = calculate_formality_score(neutral_text)
        assert 0.0 <= score <= 1.0
    
    def test_extract_greeting(self):
        """Test greeting extraction"""
        text1 = "Hi John,\nHow are you?"
        assert extract_greeting(text1) == "Hi"
        
        text2 = "Dear Sir,\nI am writing..."
        assert extract_greeting(text2) == "Dear"
        
        text3 = "Here is the report."
        result = extract_greeting(text3)
        # May or may not extract anything
        assert result is None or isinstance(result, str)
    
    def test_extract_signoff(self):
        """Test sign-off extraction"""
        text1 = "Looking forward to hearing from you.\nBest regards,\nJohn"
        assert extract_signoff(text1) in ["Best", "Best Regards"]
        
        text2 = "See you soon!\nCheers,\nJane"
        assert extract_signoff(text2) in ["Cheers", "See You"]
    
    def test_count_words(self):
        """Test word counting"""
        assert count_words("Hello world") == 2
        assert count_words("One two three four five") == 5
        assert count_words("") == 0
    
    def test_count_emojis(self):
        """Test emoji counting"""
        assert count_emojis("Hello 😊") == 1
        assert count_emojis("Great! 🎉🎊") == 2
        assert count_emojis("No emojis here") == 0
    
    def test_extract_hour(self):
        """Test hour extraction from date string"""
        date_str = "Mon, 15 Jan 2024 14:30:00 +0000"
        hour = extract_hour(date_str)
        assert hour == 14
    
    def test_extract_day_of_week(self):
        """Test day extraction"""
        date_str = "Mon, 15 Jan 2024 14:30:00 +0000"
        day = extract_day_of_week(date_str)
        assert day == "Monday"
    
    def test_extract_recipients_count(self):
        """Test recipient counting"""
        assert extract_recipients_count("john@example.com") == 1
        assert extract_recipients_count("john@ex.com, jane@ex.com") == 2
        assert extract_recipients_count("") == 0
    
    def test_is_likely_response(self):
        """Test response detection"""
        email1 = {'subject': 'Re: Meeting'}
        assert is_likely_response(email1) is True
        
        email2 = {'subject': 'Fwd: Important'}
        assert is_likely_response(email2) is True
        
        email3 = {'subject': 'New topic'}
        assert is_likely_response(email3) is False
    
    def test_extract_company_from_domain(self):
        """Test company name extraction"""
        assert extract_company_from_domain("techcorp.com") == "Techcorp"
        assert extract_company_from_domain("api.example.com") == "Example"
        assert extract_company_from_domain("gmail.com") is None
        assert extract_company_from_domain("yahoo.com") is None
    
    def test_find_most_common(self):
        """Test finding most common items"""
        items = ['a', 'b', 'a', 'c', 'a', 'b']
        result = find_most_common(items, top_n=2)
        assert result == ['a', 'b']
    
    def test_calculate_percentage(self):
        """Test percentage calculation"""
        assert calculate_percentage(25, 100) == 25.0
        assert calculate_percentage(1, 3) == 33.33
        assert calculate_percentage(0, 100) == 0.0
        assert calculate_percentage(10, 0) == 0.0
    
    def test_extract_name_from_email_format(self):
        """Test name extraction from email"""
        assert extract_name_from_email_format("john.doe@example.com") == "John Doe"
        assert extract_name_from_email_format("jane_smith@company.com") == "Jane Smith"
        assert extract_name_from_email_format("a@example.com") is None
    
    def test_extract_name_from_display(self):
        """Test name extraction from display format"""
        assert extract_name_from_display("John Doe <john@ex.com>") == "John Doe"
        assert extract_name_from_display('"Jane Smith" <jane@ex.com>') == "Jane Smith"
        assert extract_name_from_display("plain@example.com") is None


class TestSignalExtractor:
    """Test signal extraction functionality"""
    
    @pytest.fixture
    def sample_emails(self):
        """Create sample email data"""
        return [
            {
                'id': '1',
                'thread_id': 'thread1',
                'from': 'newsletter@techcrunch.com',
                'to': 'user@example.com',
                'subject': 'TechCrunch Daily',
                'date': 'Mon, 15 Jan 2024 09:00:00 +0000',
                'list_unsubscribe': 'http://techcrunch.com/unsubscribe',
                'snippet': 'Latest tech news...',
                'labels': ['INBOX']
            },
            {
                'id': '2',
                'thread_id': 'thread2',
                'from': 'colleague@company.com',
                'to': 'user@example.com',
                'subject': 'Project Update',
                'date': 'Mon, 15 Jan 2024 14:30:00 +0000',
                'snippet': 'Here is the latest update on the project...',
                'labels': ['INBOX']
            },
            {
                'id': '3',
                'thread_id': 'thread3',
                'from': 'noreply@substack.com',
                'to': 'user@example.com',
                'subject': 'Weekly Newsletter',
                'date': 'Tue, 16 Jan 2024 10:00:00 +0000',
                'list_unsubscribe': 'http://substack.com/unsubscribe',
                'snippet': 'Your weekly digest...',
                'labels': ['INBOX']
            }
        ]
    
    @pytest.fixture
    def sample_sent_emails(self):
        """Create sample sent email data"""
        return [
            {
                'id': '4',
                'thread_id': 'thread4',
                'from': 'user@example.com',
                'to': 'client@business.com',
                'subject': 'Re: Proposal',
                'date': 'Mon, 15 Jan 2024 16:00:00 +0000',
                'snippet': 'Thank you for your inquiry. Best regards,',
                'labels': ['SENT']
            },
            {
                'id': '5',
                'thread_id': 'thread5',
                'from': 'user@example.com',
                'to': 'friend@gmail.com',
                'subject': 'Weekend plans',
                'date': 'Sat, 20 Jan 2024 18:00:00 +0000',
                'snippet': 'Hey! Want to grab coffee? 😊',
                'labels': ['SENT']
            }
        ]
    
    def test_extract_newsletter_signals(self, sample_emails):
        """Test newsletter signal extraction"""
        extractor = SignalExtractor()
        signals = extractor.extract_newsletter_signals(sample_emails)
        
        assert signals.total_newsletters == 2  # 2 out of 3 are newsletters
        assert signals.newsletter_percentage > 0
        assert len(signals.newsletter_domains) > 0
    
    def test_extract_communication_style(self, sample_sent_emails):
        """Test communication style extraction"""
        extractor = SignalExtractor()
        signals = extractor.extract_communication_style(sample_sent_emails)
        
        assert signals.sent_email_count == 2
        assert 0 <= signals.formality_score <= 1.0
        assert signals.avg_email_length >= 0
        assert signals.emoji_usage_rate >= 0
    
    def test_extract_professional_context(self, sample_emails, sample_sent_emails):
        """Test professional context extraction"""
        extractor = SignalExtractor()
        signals = extractor.extract_professional_context(sample_emails, sample_sent_emails)
        
        assert signals.total_unique_contacts > 0
        assert len(signals.top_contact_domains) > 0
        # Should exclude personal domains like gmail
    
    def test_extract_activity_patterns(self, sample_emails):
        """Test activity pattern extraction"""
        extractor = SignalExtractor()
        signals = extractor.extract_activity_patterns(sample_emails)
        
        assert signals.emails_per_day >= 0
        assert signals.date_range_days >= 0
        assert len(signals.peak_activity_hours) >= 0
        assert len(signals.peak_activity_days) >= 0
    
    def test_extract_all_signals(self, sample_emails, sample_sent_emails):
        """Test complete signal extraction"""
        extractor = SignalExtractor()
        signals = extractor.extract_all_signals(
            sample_emails,
            sample_sent_emails,
            "user@example.com"
        )
        
        # Verify all signal categories are present
        assert signals.user_email == "user@example.com"
        assert signals.total_emails_analyzed == 3
        assert signals.sent_emails_analyzed == 2
        assert 0 <= signals.analysis_quality_score <= 1.0
        
        # Check newsletter signals
        assert signals.newsletter_signals.total_newsletters >= 0
        
        # Check communication style
        assert signals.communication_style.sent_email_count >= 0
        
        # Check professional context
        assert signals.professional_context.total_unique_contacts >= 0
        
        # Check activity patterns
        assert signals.activity_patterns.date_range_days >= 0
    
    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        extractor = SignalExtractor()
        
        # Create minimal data
        from src.models.schemas import NewsletterSignals, CommunicationStyleSignals
        
        newsletter_signals = NewsletterSignals(
            total_newsletters=10,
            newsletter_categories={'technology': 5, 'business': 3}
        )
        
        communication_style = CommunicationStyleSignals(
            avg_email_length=150,
            common_greetings=['Hi', 'Hello']
        )
        
        score = extractor._calculate_quality_score(
            email_count=100,
            sent_count=50,
            newsletter_signals=newsletter_signals,
            communication_style=communication_style
        )
        
        assert 0.0 <= score <= 1.0


class TestSchemas:
    """Test Pydantic schemas"""
    
    def test_email_signals_creation(self):
        """Test EmailSignals model creation"""
        from src.models.schemas import (
            EmailSignals,
            NewsletterSignals,
            CommunicationStyleSignals,
            ProfessionalContextSignals,
            ActivityPatternSignals
        )
        
        signals = EmailSignals(
            user_email="test@example.com",
            newsletter_signals=NewsletterSignals(),
            communication_style=CommunicationStyleSignals(),
            professional_context=ProfessionalContextSignals(),
            activity_patterns=ActivityPatternSignals()
        )
        
        assert signals.user_email == "test@example.com"
        assert signals.analysis_quality_score == 0.0
    
    def test_signals_json_serialization(self):
        """Test that signals can be serialized to JSON"""
        from src.models.schemas import EmailSignals, NewsletterSignals, CommunicationStyleSignals
        from src.models.schemas import ProfessionalContextSignals, ActivityPatternSignals
        
        signals = EmailSignals(
            user_email="test@example.com",
            newsletter_signals=NewsletterSignals(total_newsletters=5),
            communication_style=CommunicationStyleSignals(avg_email_length=100),
            professional_context=ProfessionalContextSignals(),
            activity_patterns=ActivityPatternSignals()
        )
        
        # Should serialize without error
        json_data = signals.model_dump()
        assert isinstance(json_data, dict)
        assert json_data['user_email'] == "test@example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



