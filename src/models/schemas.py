"""Pydantic data models for email signals and persona reports"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional
from datetime import datetime


class NewsletterSignals(BaseModel):
    """Signals extracted from newsletter subscriptions"""
    newsletter_domains: List[str] = Field(default_factory=list, description="Unique newsletter domains")
    newsletter_categories: Dict[str, int] = Field(default_factory=dict, description="Categories with email counts")
    top_newsletters: List[str] = Field(default_factory=list, description="Most frequent newsletters")
    total_newsletters: int = Field(default=0, description="Total newsletter emails found")
    newsletter_percentage: float = Field(default=0.0, description="Percentage of emails that are newsletters")


class CommunicationStyleSignals(BaseModel):
    """Signals about user's communication style from sent emails"""
    avg_email_length: int = Field(default=0, description="Average word count in sent emails")
    formality_score: float = Field(default=0.5, description="Formality score 0-1 (0=casual, 1=formal)")
    avg_response_time_hours: Optional[float] = Field(default=None, description="Average time to respond to emails")
    emoji_usage_rate: float = Field(default=0.0, description="Percentage of emails with emojis")
    common_greetings: List[str] = Field(default_factory=list, description="Most used greetings")
    common_signoffs: List[str] = Field(default_factory=list, description="Most used sign-offs")
    sent_email_count: int = Field(default=0, description="Total sent emails analyzed")
    avg_recipients_per_email: float = Field(default=1.0, description="Average number of recipients")
    
    # LLM-enhanced insights (optional)
    llm_tone: Optional[str] = Field(default=None, description="LLM-analyzed overall tone")
    llm_writing_style: Optional[str] = Field(default=None, description="LLM-analyzed writing style")
    llm_common_topics: List[str] = Field(default_factory=list, description="LLM-identified common topics")
    llm_relationship_quality: Optional[str] = Field(default=None, description="How relationships are built")
    llm_professionalism_level: Optional[int] = Field(default=None, ge=1, le=10, description="LLM professionalism 1-10")
    llm_personality_traits: List[str] = Field(default_factory=list, description="LLM-identified personality traits")
    llm_communication_strengths: List[str] = Field(default_factory=list, description="Communication strengths")
    llm_analysis_available: bool = Field(default=False, description="Whether LLM analysis was performed")


class ProfessionalContextSignals(BaseModel):
    """Signals about professional context from email contacts"""
    top_contact_domains: List[str] = Field(default_factory=list, description="Most frequent contact domains")
    domain_categories: Dict[str, int] = Field(default_factory=dict, description="Domain categories with counts")
    inferred_industry: Optional[str] = Field(default=None, description="Likely industry based on contacts")
    company_affiliations: List[str] = Field(default_factory=list, description="Likely company affiliations")
    professional_keywords: List[str] = Field(default_factory=list, description="Common professional terms")
    total_unique_contacts: int = Field(default=0, description="Number of unique email contacts")


class ActivityPatternSignals(BaseModel):
    """Signals about email activity patterns"""
    emails_per_day: float = Field(default=0.0, description="Average emails per day")
    peak_activity_hours: List[int] = Field(default_factory=list, description="Hours with most activity (0-23)")
    peak_activity_days: List[str] = Field(default_factory=list, description="Days with most activity")
    thread_depth_avg: float = Field(default=1.0, description="Average conversation depth")
    response_rate: float = Field(default=0.0, description="Percentage of emails that are responses")
    date_range_days: int = Field(default=0, description="Number of days covered in analysis")
    total_threads: int = Field(default=0, description="Total conversation threads")


class EmailSignals(BaseModel):
    """Comprehensive email signals extracted from inbox"""
    user_email: EmailStr
    analyzed_at: datetime = Field(default_factory=datetime.now)
    
    # Signal categories
    newsletter_signals: NewsletterSignals
    communication_style: CommunicationStyleSignals
    professional_context: ProfessionalContextSignals
    activity_patterns: ActivityPatternSignals
    
    # Metadata
    total_emails_analyzed: int = Field(default=0, description="Total emails processed")
    sent_emails_analyzed: int = Field(default=0, description="Total sent emails processed")
    analysis_quality_score: float = Field(default=0.0, description="Quality score 0-1 based on data completeness")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_email": "john.doe@example.com",
                "analyzed_at": "2024-01-15T10:30:00",
                "newsletter_signals": {
                    "newsletter_domains": ["techcrunch.com", "substack.com"],
                    "newsletter_categories": {"technology": 25, "finance": 10},
                    "top_newsletters": ["TechCrunch Daily", "The Hustle"],
                    "total_newsletters": 35,
                    "newsletter_percentage": 35.0
                },
                "communication_style": {
                    "avg_email_length": 120,
                    "formality_score": 0.65,
                    "avg_response_time_hours": 4.2,
                    "emoji_usage_rate": 15.0,
                    "common_greetings": ["Hi", "Hello"],
                    "common_signoffs": ["Best", "Thanks"],
                    "sent_email_count": 50
                },
                "professional_context": {
                    "top_contact_domains": ["company.com", "client.com"],
                    "domain_categories": {"technology": 30, "consulting": 15},
                    "inferred_industry": "Technology",
                    "company_affiliations": ["TechCorp"]
                },
                "activity_patterns": {
                    "emails_per_day": 15.5,
                    "peak_activity_hours": [9, 14, 16],
                    "peak_activity_days": ["Monday", "Wednesday"],
                    "thread_depth_avg": 3.2
                },
                "total_emails_analyzed": 100,
                "sent_emails_analyzed": 50,
                "analysis_quality_score": 0.85
            }
        }


class IdentityMatch(BaseModel):
    """A matched social media profile"""
    platform: str = Field(..., description="Platform name (LinkedIn, Twitter, etc.)")
    profile_url: str = Field(..., description="URL to the profile")
    confidence_score: float = Field(..., ge=0, le=100, description="Match confidence 0-100")
    extracted_data: Dict = Field(default_factory=dict, description="Profile data extracted")
    reasoning: str = Field(..., description="Why this match was scored this way")
    matched_at: datetime = Field(default_factory=datetime.now)


class PersonaReport(BaseModel):
    """Complete persona report for a user"""
    user_email: EmailStr
    generated_at: datetime = Field(default_factory=datetime.now)
    
    # Report sections
    executive_summary: str = Field(..., description="High-level summary of digital persona")
    digital_footprint_score: int = Field(..., ge=0, le=10, description="Overall footprint score 0-10")
    
    # Detailed sections
    professional_profile: Dict = Field(default_factory=dict)
    personal_interests: Dict = Field(default_factory=dict)
    communication_style: Dict = Field(default_factory=dict)
    digital_presence: Dict = Field(default_factory=dict)
    
    # Confidence and sources
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    data_sources: List[str] = Field(default_factory=list)
    matched_profiles: List[IdentityMatch] = Field(default_factory=list)
    
    # Metadata
    analysis_version: str = Field(default="1.0")
    phases_completed: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_email": "john.doe@example.com",
                "generated_at": "2024-01-15T12:00:00",
                "executive_summary": "Tech-savvy professional with strong digital presence...",
                "digital_footprint_score": 8,
                "professional_profile": {
                    "likely_role": "Software Engineer",
                    "industry": "Technology",
                    "experience_level": "Senior"
                },
                "personal_interests": {
                    "primary_categories": ["Technology", "Finance", "Productivity"],
                    "passion_signals": ["AI/ML", "Startups"]
                },
                "data_sources": ["Gmail", "LinkedIn"],
                "phases_completed": ["1", "2", "3", "5"]
            }
        }

