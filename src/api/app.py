"""FastAPI application for Digital Footprint Analyzer"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import asyncio
from pathlib import Path
import uuid
from datetime import datetime

from ..auth.gmail_oauth import GmailAuthenticator
from ..email_analysis.fetcher import EmailFetcher
from ..email_analysis.signal_extractor import SignalExtractor
from ..utils.config import load_config

# Initialize FastAPI app
app = FastAPI(
    title="Digital Footprint Analyzer",
    description="Analyze Gmail inboxes to create comprehensive digital persona reports",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")

# Load configuration
config = load_config()

# In-memory storage for analysis sessions (use Redis in production)
analysis_sessions: Dict[str, Dict[str, Any]] = {}


# Pydantic models
class AnalysisRequest(BaseModel):
    """Request to start analysis"""
    email: Optional[EmailStr] = None


class AnalysisStatus(BaseModel):
    """Status of analysis"""
    session_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    result: Optional[Dict[str, Any]] = None


class AuthURLResponse(BaseModel):
    """OAuth URL response"""
    auth_url: str
    session_id: str


# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend"""
    index_file = frontend_dir / "templates" / "index.html"
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }


@app.get("/api/config/check")
async def check_config():
    """Check if required configuration is present"""
    missing = config.validate_phase1()
    
    return {
        "configured": len(missing) == 0,
        "missing_vars": missing,
        "phase": "1",
        "features_available": {
            "gmail_oauth": len(missing) == 0,
            "email_analysis": len(missing) == 0,
            "identity_resolution": config.gemini_api_key != "",
            "profile_enrichment": config.apify_api_token != ""
        }
    }


@app.post("/api/auth/start", response_model=AuthURLResponse)
async def start_auth():
    """Start OAuth authentication flow
    
    Returns:
        OAuth URL for user to visit
    """
    try:
        # Validate config
        missing = config.validate_phase1()
        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Missing configuration: {', '.join(missing)}"
            )
        
        # Create session
        session_id = str(uuid.uuid4())
        
        # Initialize authenticator
        authenticator = GmailAuthenticator(config)
        flow = authenticator.get_oauth_flow()
        
        # Generate auth URL
        auth_url, state = flow.authorization_url(prompt='consent')
        
        # Store session
        analysis_sessions[session_id] = {
            "status": "awaiting_auth",
            "flow": flow,
            "state": state,
            "created_at": datetime.now().isoformat()
        }
        
        return AuthURLResponse(
            auth_url=auth_url,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analysis/start", response_model=AnalysisStatus)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start email analysis
    
    For Phase 1: Fetches emails and returns basic statistics
    """
    try:
        # Create session
        session_id = str(uuid.uuid4())
        
        # Initialize session
        analysis_sessions[session_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Authenticating with Gmail...",
            "result": None,
            "created_at": datetime.now().isoformat()
        }
        
        # Start background task
        background_tasks.add_task(
            run_analysis_phase1,
            session_id,
            request.email
        )
        
        return AnalysisStatus(
            session_id=session_id,
            status="processing",
            progress=0,
            message="Starting analysis..."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/status/{session_id}", response_model=AnalysisStatus)
async def get_analysis_status(session_id: str):
    """Get status of analysis"""
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = analysis_sessions[session_id]
    
    return AnalysisStatus(
        session_id=session_id,
        status=session["status"],
        progress=session.get("progress", 0),
        message=session.get("message", ""),
        result=session.get("result")
    )


async def run_analysis_phase1(session_id: str, email: Optional[str] = None):
    """Run Phase 1 & 2 analysis in background
    
    Args:
        session_id: Session ID
        email: Optional email to analyze specific account
    """
    try:
        # Update status
        analysis_sessions[session_id]["progress"] = 10
        analysis_sessions[session_id]["message"] = "Authenticating..."
        
        # Initialize authenticator
        authenticator = GmailAuthenticator(config)
        
        # Load or authenticate
        credentials = authenticator.load_credentials(email)
        if not credentials:
            analysis_sessions[session_id]["status"] = "failed"
            analysis_sessions[session_id]["message"] = "No stored credentials. Please authenticate first."
            return
        
        analysis_sessions[session_id]["progress"] = 30
        analysis_sessions[session_id]["message"] = "Fetching email statistics..."
        
        # Initialize fetcher
        fetcher = EmailFetcher(credentials)
        user_email = fetcher.get_user_email()
        
        analysis_sessions[session_id]["progress"] = 40
        analysis_sessions[session_id]["message"] = "Fetching recent emails..."
        
        # Get email counts
        counts = fetcher.get_email_count()
        
        # Fetch recent emails
        recent_emails = fetcher.fetch_recent_emails(max_results=100)
        sent_emails = fetcher.fetch_sent_emails(max_results=50)
        
        analysis_sessions[session_id]["progress"] = 60
        analysis_sessions[session_id]["message"] = "Extracting email signals..."
        
        # Phase 2: Extract signals
        extractor = SignalExtractor()
        signals = extractor.extract_all_signals(recent_emails, sent_emails, user_email)
        
        analysis_sessions[session_id]["progress"] = 90
        analysis_sessions[session_id]["message"] = "Finalizing results..."
        
        # Prepare result with Phase 2 signals
        result = {
            "user_email": user_email,
            "statistics": {
                "total_messages": counts['total'],
                "total_threads": counts['threads'],
                "inbox_count": counts['inbox'],
                "sent_count": counts['sent']
            },
            "analysis": {
                "recent_emails_analyzed": len(recent_emails),
                "sent_emails_analyzed": len(sent_emails),
                "analysis_quality_score": signals.analysis_quality_score
            },
            "signals": {
                "newsletters": {
                    "total_newsletters": signals.newsletter_signals.total_newsletters,
                    "newsletter_percentage": signals.newsletter_signals.newsletter_percentage,
                    "unique_domains": len(signals.newsletter_signals.newsletter_domains),
                    "categories": signals.newsletter_signals.newsletter_categories,
                    "top_newsletters": signals.newsletter_signals.top_newsletters[:5]
                },
                "communication_style": {
                    "avg_email_length": signals.communication_style.avg_email_length,
                    "formality_score": signals.communication_style.formality_score,
                    "emoji_usage_rate": signals.communication_style.emoji_usage_rate,
                    "avg_recipients": signals.communication_style.avg_recipients_per_email,
                    "common_greetings": signals.communication_style.common_greetings,
                    "common_signoffs": signals.communication_style.common_signoffs
                },
                "professional_context": {
                    "inferred_industry": signals.professional_context.inferred_industry,
                    "total_unique_contacts": signals.professional_context.total_unique_contacts,
                    "top_contact_domains": signals.professional_context.top_contact_domains[:10],
                    "domain_categories": signals.professional_context.domain_categories,
                    "company_affiliations": signals.professional_context.company_affiliations,
                    "professional_keywords": signals.professional_context.professional_keywords
                },
                "activity_patterns": {
                    "emails_per_day": signals.activity_patterns.emails_per_day,
                    "date_range_days": signals.activity_patterns.date_range_days,
                    "total_threads": signals.activity_patterns.total_threads,
                    "thread_depth_avg": signals.activity_patterns.thread_depth_avg,
                    "response_rate": signals.activity_patterns.response_rate,
                    "peak_activity_hours": signals.activity_patterns.peak_activity_hours,
                    "peak_activity_days": signals.activity_patterns.peak_activity_days
                }
            },
            "sample_emails": [
                {
                    "from": email.get("from", "")[:50],
                    "subject": email.get("subject", "")[:60],
                    "date": email.get("date", ""),
                    "snippet": email.get("snippet", "")[:100]
                }
                for email in recent_emails[:5]
            ]
        }
        
        # Update session
        analysis_sessions[session_id]["status"] = "completed"
        analysis_sessions[session_id]["progress"] = 100
        analysis_sessions[session_id]["message"] = "Analysis complete! (Phase 1 & 2)"
        analysis_sessions[session_id]["result"] = result
        
    except Exception as e:
        analysis_sessions[session_id]["status"] = "failed"
        analysis_sessions[session_id]["message"] = f"Error: {str(e)}"
        analysis_sessions[session_id]["progress"] = 0


@app.get("/api/accounts")
async def list_accounts():
    """List stored Gmail accounts"""
    try:
        authenticator = GmailAuthenticator(config)
        emails = authenticator.get_stored_emails()
        
        return {
            "accounts": emails,
            "count": len(emails)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

