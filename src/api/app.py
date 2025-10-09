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
import os
import threading

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

# CORS middleware - environment-specific origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
session_lock = threading.Lock()  # Thread safety for concurrent access


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
        
        # Store session (thread-safe)
        with session_lock:
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
        
        # Initialize session (thread-safe)
        with session_lock:
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
    with session_lock:
        if session_id not in analysis_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = analysis_sessions[session_id].copy()  # Copy to avoid race conditions
    
    return AnalysisStatus(
        session_id=session_id,
        status=session["status"],
        progress=session.get("progress", 0),
        message=session.get("message", ""),
        result=session.get("result")
    )


def run_analysis_phase1(session_id: str, email: Optional[str] = None):
    """Run Phase 1 & 2 analysis in background (sync function for blocking I/O)
    
    Args:
        session_id: Session ID
        email: Optional email to analyze specific account
    """
    try:
        # Update status (thread-safe)
        with session_lock:
            analysis_sessions[session_id]["progress"] = 10
            analysis_sessions[session_id]["message"] = "Authenticating..."
        
        # Initialize authenticator
        authenticator = GmailAuthenticator(config)
        
        # Load or authenticate
        credentials = authenticator.load_credentials(email)
        if not credentials:
            with session_lock:
                analysis_sessions[session_id]["status"] = "failed"
                analysis_sessions[session_id]["message"] = "No stored credentials. Please authenticate first."
                analysis_sessions[session_id]["progress"] = 0
            return
        
        # Verify credentials are still valid
        if credentials.expired and credentials.refresh_token:
            try:
                credentials = authenticator.refresh_token(credentials, email)
            except Exception as e:
                with session_lock:
                    analysis_sessions[session_id]["status"] = "failed"
                    analysis_sessions[session_id]["message"] = f"Failed to refresh credentials: {str(e)}"
                    analysis_sessions[session_id]["progress"] = 0
                return
        
        with session_lock:
            analysis_sessions[session_id]["progress"] = 30
            analysis_sessions[session_id]["message"] = "Fetching email statistics..."
        
        # Initialize fetcher
        fetcher = EmailFetcher(credentials)
        user_email = fetcher.get_user_email()
        
        with session_lock:
            analysis_sessions[session_id]["progress"] = 40
            analysis_sessions[session_id]["message"] = "Fetching recent emails..."
        
        # Get email counts
        counts = fetcher.get_email_count()
        
        # Fetch recent emails
        recent_emails = fetcher.fetch_recent_emails(max_results=100)
        sent_emails = fetcher.fetch_sent_emails(max_results=50)
        
        with session_lock:
            analysis_sessions[session_id]["progress"] = 60
            analysis_sessions[session_id]["message"] = "Extracting email signals..."
        
        # Phase 2: Extract signals (FIX: Pass config parameter)
        extractor = SignalExtractor(config)
        signals = extractor.extract_all_signals(recent_emails, sent_emails, user_email)
        
        with session_lock:
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
        
        # Update session (thread-safe)
        with session_lock:
            analysis_sessions[session_id]["status"] = "completed"
            analysis_sessions[session_id]["progress"] = 100
            analysis_sessions[session_id]["message"] = "Analysis complete! (Phase 1 & 2)"
            analysis_sessions[session_id]["result"] = result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Analysis error for session {session_id}: {error_details}")
        
        with session_lock:
            analysis_sessions[session_id]["status"] = "failed"
            analysis_sessions[session_id]["message"] = f"Analysis failed: {str(e)}"
            analysis_sessions[session_id]["progress"] = 0
            analysis_sessions[session_id]["error_details"] = error_details


@app.get("/auth/start")
async def start_oauth_flow_web():
    """Start OAuth flow for web deployment (production)
    
    Returns OAuth URL that user should visit to authorize
    """
    try:
        # Create session
        session_id = str(uuid.uuid4())
        
        # Initialize authenticator
        authenticator = GmailAuthenticator(config)
        flow = authenticator.get_oauth_flow()
        
        # Generate auth URL
        auth_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true'
        )
        
        # Store flow in session for callback
        with session_lock:
            analysis_sessions[session_id] = {
                "status": "awaiting_auth",
                "flow": flow,
                "state": state,
                "created_at": datetime.now().isoformat()
            }
        
        return {
            "auth_url": auth_url,
            "session_id": session_id,
            "state": state
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/oauth2callback")
async def oauth_callback(code: str, state: str):
    """Handle OAuth callback from Google
    
    This endpoint receives the OAuth code after user authorizes
    """
    try:
        # Find session by state
        session_id = None
        with session_lock:
            for sid, session in analysis_sessions.items():
                if session.get("state") == state and session.get("status") == "awaiting_auth":
                    session_id = sid
                    break
        
        if not session_id:
            return HTMLResponse(content="""
            <html>
                <head><title>Authentication Error</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #e53e3e;">❌ Authentication Error</h1>
                    <p>Session not found or expired. Please try again.</p>
                    <p><a href="/">Return to Home</a></p>
                </body>
            </html>
            """, status_code=400)
        
        with session_lock:
            session = analysis_sessions[session_id]
            flow = session.get("flow")
        
        if not flow:
            raise HTTPException(status_code=400, detail="OAuth flow not found")
        
        # Exchange code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Save credentials
        authenticator = GmailAuthenticator(config)
        fetcher = EmailFetcher(credentials)
        user_email = fetcher.get_user_email()
        
        # Store credentials
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        authenticator.storage.save_token('gmail', user_email, token_data)
        
        # Update session
        with session_lock:
            analysis_sessions[session_id]["status"] = "authenticated"
            analysis_sessions[session_id]["user_email"] = user_email
        
        # Return success page
        return HTMLResponse(content=f"""
        <html>
            <head>
                <title>Authentication Successful</title>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                        background: linear-gradient(-45deg, #667eea, #764ba2);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        flex-direction: column;
                    }}
                    .success-box {{
                        background: white;
                        color: #333;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        max-width: 500px;
                    }}
                    h1 {{ color: #48bb78; margin-bottom: 20px; }}
                    p {{ font-size: 18px; line-height: 1.6; }}
                    .email {{ color: #667eea; font-weight: bold; }}
                    .button {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 12px 24px;
                        background: #667eea;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                    }}
                    .button:hover {{ background: #5568d3; }}
                </style>
            </head>
            <body>
                <div class="success-box">
                    <h1>✅ Authentication Successful!</h1>
                    <p>You have successfully connected your Gmail account:</p>
                    <p class="email">{user_email}</p>
                    <p>You can now close this window and return to the application to start your analysis.</p>
                    <a href="/" class="button">Return to App</a>
                </div>
                <script>
                    // Auto-close after 5 seconds if window was opened as popup
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'oauth_success',
                            session_id: '{session_id}',
                            email: '{user_email}'
                        }}, '*');
                        setTimeout(() => window.close(), 3000);
                    }}
                </script>
            </body>
        </html>
        """)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"OAuth callback error: {error_details}")
        
        return HTMLResponse(content=f"""
        <html>
            <head><title>Authentication Error</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #e53e3e;">❌ Authentication Failed</h1>
                <p>Error: {str(e)}</p>
                <p><a href="/">Return to Home</a></p>
            </body>
        </html>
        """, status_code=500)


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

