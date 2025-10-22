"""Configuration management using environment variables"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Application configuration loaded from environment variables"""
    
    def __init__(self):
        # Load .env file
        load_dotenv()
        
        # Gmail OAuth
        self.google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
        self.google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
        
        # Google Gemini
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        # Exa (Identity Resolution)
        self.exa_api_key: str = os.getenv("EXA_API_KEY", "")
        
        # Apify (Social Profile Scraping)
        self.apify_api_token: str = os.getenv("APIFY_API_TOKEN", "")
        
        # Database
        self.database_path: str = os.getenv("DATABASE_PATH", "./data/tokens.db")
        self.database_url: str = os.getenv("DATABASE_URL", "")  # PostgreSQL URL for production
        
        # OAuth scopes for Gmail
        self.gmail_scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ]
        
        # LLM Analysis Options (Phase 2.5)
        self.enable_llm_analysis: bool = os.getenv("ENABLE_LLM_ANALYSIS", "false").lower() == "true"
        self.llm_max_emails_to_analyze: int = int(os.getenv("LLM_MAX_EMAILS_TO_ANALYZE", "10"))
        
        # Security Configuration
        self.secret_key: str = os.getenv("SECRET_KEY", "")
        self.session_secret: str = os.getenv("SESSION_SECRET", "")
        self.csrf_secret: str = os.getenv("CSRF_SECRET", "")
    
    def validate(self) -> list[str]:
        """Validate that required configuration is present
        
        Returns:
            List of missing configuration keys
        """
        missing = []
        
        if not self.google_client_id:
            missing.append("GOOGLE_CLIENT_ID")
        if not self.google_client_secret:
            missing.append("GOOGLE_CLIENT_SECRET")
        
        return missing
    
    def validate_phase1(self) -> list[str]:
        """Validate configuration needed for Phase 1 (OAuth + Email Fetching)"""
        return self.validate()
    
    def validate_full(self) -> list[str]:
        """Validate all configuration for full pipeline"""
        missing = self.validate()
        
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.exa_api_key:
            missing.append("EXA_API_KEY")
        if not self.apify_api_token:
            missing.append("APIFY_API_TOKEN")
        
        return missing


def load_config() -> Config:
    """Load and return application configuration
    
    Returns:
        Config object with all settings
    """
    return Config()

