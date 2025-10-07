"""Tests for Phase 1: Gmail OAuth + Email Fetching"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import os

from src.utils.config import Config, load_config
from src.utils.storage import TokenStorage
from src.auth.gmail_oauth import GmailAuthenticator


class TestConfig:
    """Test configuration management"""
    
    def test_load_config(self):
        """Test configuration loading"""
        config = Config()
        assert isinstance(config, Config)
        assert isinstance(config.gmail_scopes, list)
        assert len(config.gmail_scopes) > 0
    
    def test_validate_phase1(self):
        """Test Phase 1 validation"""
        config = Config()
        # Should require Google credentials
        missing = config.validate_phase1()
        assert isinstance(missing, list)
    
    def test_gmail_scopes(self):
        """Test that Gmail scopes are correct"""
        config = Config()
        assert "https://www.googleapis.com/auth/gmail.readonly" in config.gmail_scopes
        assert "https://www.googleapis.com/auth/userinfo.email" in config.gmail_scopes


class TestTokenStorage:
    """Test token storage functionality"""
    
    def test_init_creates_database(self):
        """Test database initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_tokens.db")
            storage = TokenStorage(db_path)
            assert Path(db_path).exists()
    
    def test_save_and_load_token(self):
        """Test saving and loading tokens"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_tokens.db")
            storage = TokenStorage(db_path)
            
            # Save token
            token_data = {
                'token': 'test_token_123',
                'refresh_token': 'refresh_token_456',
                'scopes': ['scope1', 'scope2']
            }
            storage.save_token('gmail', 'test@example.com', token_data)
            
            # Load token
            loaded = storage.load_token('gmail', 'test@example.com')
            assert loaded is not None
            assert loaded['token'] == 'test_token_123'
            assert loaded['refresh_token'] == 'refresh_token_456'
    
    def test_load_nonexistent_token(self):
        """Test loading token that doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_tokens.db")
            storage = TokenStorage(db_path)
            
            loaded = storage.load_token('gmail', 'nonexistent@example.com')
            assert loaded is None
    
    def test_delete_token(self):
        """Test token deletion"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_tokens.db")
            storage = TokenStorage(db_path)
            
            # Save token
            token_data = {'token': 'test_token'}
            storage.save_token('gmail', 'test@example.com', token_data)
            
            # Delete token
            storage.delete_token('gmail', 'test@example.com')
            
            # Verify deleted
            loaded = storage.load_token('gmail', 'test@example.com')
            assert loaded is None
    
    def test_list_stored_emails(self):
        """Test listing stored emails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_tokens.db")
            storage = TokenStorage(db_path)
            
            # Save multiple tokens
            storage.save_token('gmail', 'user1@example.com', {'token': 'token1'})
            storage.save_token('gmail', 'user2@example.com', {'token': 'token2'})
            
            # List emails
            emails = storage.list_stored_emails('gmail')
            assert len(emails) == 2
            assert 'user1@example.com' in emails
            assert 'user2@example.com' in emails


class TestGmailAuthenticator:
    """Test Gmail authentication"""
    
    def test_init(self):
        """Test authenticator initialization"""
        config = Config()
        config.google_client_id = "test_client_id"
        config.google_client_secret = "test_secret"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config.database_path = os.path.join(tmpdir, "test_tokens.db")
            auth = GmailAuthenticator(config)
            
            assert auth.config == config
            assert auth.storage is not None
            assert len(auth.scopes) > 0
    
    def test_get_oauth_flow(self):
        """Test OAuth flow initialization"""
        config = Config()
        config.google_client_id = "test_client_id.apps.googleusercontent.com"
        config.google_client_secret = "test_secret"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config.database_path = os.path.join(tmpdir, "test_tokens.db")
            auth = GmailAuthenticator(config)
            
            flow = auth.get_oauth_flow()
            assert flow is not None
            assert flow.oauth2session.scope == auth.scopes
    
    def test_get_stored_emails(self):
        """Test retrieving stored emails"""
        config = Config()
        with tempfile.TemporaryDirectory() as tmpdir:
            config.database_path = os.path.join(tmpdir, "test_tokens.db")
            auth = GmailAuthenticator(config)
            
            # Save some tokens
            auth.storage.save_token('gmail', 'user1@example.com', {'token': 'token1'})
            auth.storage.save_token('gmail', 'user2@example.com', {'token': 'token2'})
            
            # Get stored emails
            emails = auth.get_stored_emails()
            assert len(emails) == 2
            assert 'user1@example.com' in emails


class TestEmailFetcher:
    """Test email fetching functionality"""
    
    @patch('src.email_analysis.fetcher.build')
    def test_init(self, mock_build):
        """Test fetcher initialization"""
        from src.email_analysis.fetcher import EmailFetcher
        
        mock_credentials = Mock()
        fetcher = EmailFetcher(mock_credentials)
        
        assert fetcher.user_id == 'me'
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_credentials)
    
    @patch('src.email_analysis.fetcher.build')
    def test_parse_date(self, mock_build):
        """Test date parsing"""
        from src.email_analysis.fetcher import EmailFetcher
        
        mock_credentials = Mock()
        fetcher = EmailFetcher(mock_credentials)
        
        # Test valid date
        date_str = "Mon, 01 Jan 2024 12:00:00 +0000"
        parsed = fetcher._parse_date(date_str)
        assert parsed is not None
        
        # Test invalid date
        parsed = fetcher._parse_date("invalid date")
        assert parsed is None


def test_imports():
    """Test that all modules can be imported"""
    from src import __version__
    from src.auth import gmail_oauth
    from src.email_analysis import fetcher
    from src.utils import config, storage
    
    assert __version__ == "0.1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

