# Render Deployment Checklist
## Deployment URL: https://profile-builder.onrender.com

---

## 🚨 CRITICAL ISSUES TO FIX

### 1. **CORS Configuration** ⚠️ MUST UPDATE
**Current Issue**: CORS only allows localhost origins
**Impact**: Frontend won't be able to make API calls from Render domain

**Location**: `src/api/app.py:28`

**Current Code**:
```python
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
```

**✅ FIX**: Add to Render Environment Variables:
```bash
ALLOWED_ORIGINS=https://profile-builder.onrender.com,http://localhost:3000,http://localhost:8000
```

**How to add in Render Dashboard**:
1. Go to your service → Environment
2. Add new environment variable:
   - Key: `ALLOWED_ORIGINS`
   - Value: `https://profile-builder.onrender.com,http://localhost:3000,http://localhost:8000`

---

### 2. **OAuth Redirect URI** ⚠️ CRITICAL - MUST UPDATE
**Current Issue**: Hardcoded to `http://localhost:8080`
**Impact**: OAuth will NOT work in production - users can't authenticate

**Location**: `src/auth/gmail_oauth.py:37`

**Current Code**:
```python
"redirect_uris": ["http://localhost:8080"],
```

**✅ REQUIRES TWO FIXES**:

#### A. Update Google Cloud Console
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", add:
   - `https://profile-builder.onrender.com/oauth2callback`
   - Keep `http://localhost:8080` for local development
4. Click "Save"

#### B. Update Code - Make OAuth Redirect Dynamic
**FILE TO UPDATE**: `src/auth/gmail_oauth.py`

Change lines 31-39 from:
```python
def get_oauth_flow(self) -> InstalledAppFlow:
    """Initialize OAuth flow with correct scopes
    
    Returns:
        Configured OAuth flow
    """
    client_config = {
        "installed": {
            "client_id": self.config.google_client_id,
            "client_secret": self.config.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080"],
        }
    }
```

To:
```python
def get_oauth_flow(self) -> InstalledAppFlow:
    """Initialize OAuth flow with correct scopes
    
    Returns:
        Configured OAuth flow
    """
    import os
    # Use environment variable for redirect URI, default to localhost for development
    redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8080")
    
    client_config = {
        "installed": {
            "client_id": self.config.google_client_id,
            "client_secret": self.config.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }
```

And add to Render Environment Variables:
```bash
OAUTH_REDIRECT_URI=https://profile-builder.onrender.com/oauth2callback
```

**⚠️ IMPORTANT**: You'll also need to update the OAuth flow in `src/auth/gmail_oauth.py:59-64` to handle web-based OAuth instead of local server:

```python
# This won't work on Render since it tries to start a local server
credentials = flow.run_local_server(
    port=8080,
    authorization_prompt_message='Please visit this URL to authorize: {url}',
    success_message='Authentication successful! You can close this window.',
    open_browser=True
)
```

**SOLUTION**: For production, you'll need to implement a proper OAuth callback endpoint. See "OAuth Implementation for Production" below.

---

### 3. **Missing Environment Variable in render.yaml**
**Location**: `render.yaml`

**✅ ADD** these environment variables to your render.yaml:

```yaml
services:
  - type: web
    name: digital-footprint-analyzer
    env: python
    region: oregon
    plan: free
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: GEMINI_MODEL
        value: gemini-2.0-flash-exp
      - key: EXA_API_KEY
        sync: false
      - key: APIFY_API_TOKEN
        sync: false
      - key: DATABASE_PATH
        value: /var/data/tokens.db
      # ADD THESE NEW ONES:
      - key: ALLOWED_ORIGINS
        value: https://profile-builder.onrender.com
      - key: OAUTH_REDIRECT_URI
        value: https://profile-builder.onrender.com/oauth2callback
      - key: ENABLE_LLM_ANALYSIS
        value: false
      - key: LLM_MAX_EMAILS_TO_ANALYZE
        value: 10
    disk:
      name: data
      mountPath: /var/data
      sizeGB: 1
```

---

## 🔍 OTHER CONCERNS FOR PRODUCTION

### 4. **OAuth Flow Incompatibility** ⚠️ ARCHITECTURAL ISSUE
**Problem**: Current OAuth implementation uses `run_local_server()` which:
- Starts a local web server on port 8080
- Won't work on Render (can't bind to arbitrary ports)
- Designed for desktop apps, not web apps

**Current Flow** (Desktop):
1. User clicks "Start Analysis"
2. Opens browser to Google OAuth
3. After auth, redirects to `http://localhost:8080`
4. Local server catches redirect, exchanges code for token

**Needed Flow** (Web):
1. User clicks "Start Analysis"
2. Frontend redirects to OAuth URL
3. After auth, redirects to `https://profile-builder.onrender.com/oauth2callback`
4. Backend endpoint handles callback, exchanges code for token
5. Stores session, returns to frontend

**✅ SOLUTION REQUIRED**: See "OAuth Implementation for Production" section below.

---

### 5. **File Permissions on Render**
**Location**: Database path `/var/data/tokens.db`

**Concern**: The persistent disk is mounted at `/var/data`
**Status**: ✅ Already configured correctly in render.yaml
**Verify**: Database writes should work (Render provides writable disk)

---

### 6. **Frontend API Detection**
**Location**: `frontend/static/js/app.js:3`

**Current Code**:
```javascript
const API_BASE = window.location.origin;
```

**Status**: ✅ GOOD - This will automatically use the correct Render URL
- Localhost: `http://localhost:8000`
- Production: `https://profile-builder.onrender.com`

---

### 7. **Python Version**
**Location**: `render.yaml:15` and `runtime.txt`

**Check runtime.txt**:
```
python-3.11.0
```

**Status**: ✅ Matches render.yaml (Python 3.11.0)

---

### 8. **Static Files Serving**
**Location**: `src/api/app.py:37-38`

**Current Code**:
```python
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")
```

**Status**: ✅ Should work on Render
**Verify after deployment**: Check that CSS/JS files load correctly

---

### 9. **Health Check Endpoint**
**Location**: `src/api/app.py:75-82`

**Current Code**: ✅ Already exists
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }
```

**Render Setup**: Configure health check path to `/health`

---

## 🛠️ OAUTH IMPLEMENTATION FOR PRODUCTION

### Current Problem
The desktop OAuth flow (`run_local_server()`) won't work on Render.

### Recommended Solution
Add a proper OAuth callback endpoint:

**FILE**: `src/api/app.py`

**ADD THIS ENDPOINT**:

```python
@app.get("/auth/start")
async def start_oauth_flow():
    """Start OAuth flow for web deployment"""
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
async def oauth_callback(code: str, state: str, session_id: Optional[str] = None):
    """Handle OAuth callback from Google"""
    try:
        # Find session by state
        if not session_id:
            # Search for session with matching state
            with session_lock:
                for sid, session in analysis_sessions.items():
                    if session.get("state") == state:
                        session_id = sid
                        break
        
        if not session_id or session_id not in analysis_sessions:
            raise HTTPException(status_code=400, detail="Invalid session")
        
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
        
        # Redirect to success page or return success HTML
        return HTMLResponse(content="""
        <html>
            <head><title>Authentication Successful</title></head>
            <body>
                <h1>✅ Authentication Successful!</h1>
                <p>You have successfully connected your Gmail account.</p>
                <p>You can now close this window and return to the application.</p>
                <script>
                    setTimeout(() => {
                        window.close();
                        // Or redirect back to main app
                        // window.location.href = '/';
                    }, 2000);
                </script>
            </body>
        </html>
        """)
        
    except Exception as e:
        import traceback
        print(f"OAuth callback error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"OAuth failed: {str(e)}")
```

**UPDATE FRONTEND** (`frontend/static/js/app.js`):

Add this function:
```javascript
async function startOAuthFlow() {
    try {
        const response = await fetch(`${API_BASE}/auth/start`);
        const data = await response.json();
        
        // Open OAuth URL in new window
        window.open(data.auth_url, 'oauth', 'width=600,height=600');
        
        // Store session ID for later use
        localStorage.setItem('oauth_session_id', data.session_id);
        
        // Poll for authentication completion
        pollOAuthStatus(data.session_id);
        
    } catch (error) {
        console.error('OAuth start failed:', error);
        alert('Failed to start authentication');
    }
}

function pollOAuthStatus(sessionId) {
    const interval = setInterval(async () => {
        const response = await fetch(`${API_BASE}/api/analysis/status/${sessionId}`);
        const data = await response.json();
        
        if (data.status === 'authenticated') {
            clearInterval(interval);
            alert('Authentication successful!');
            // Proceed to analysis
        }
    }, 2000);
}
```

---

## 📋 DEPLOYMENT STEPS

### Step 1: Update Google Cloud Console
- [ ] Add `https://profile-builder.onrender.com/oauth2callback` to Authorized redirect URIs

### Step 2: Update Code
- [ ] Make OAuth redirect URI dynamic in `src/auth/gmail_oauth.py`
- [ ] Add OAuth callback endpoints to `src/api/app.py` (see above)
- [ ] Update frontend to use new OAuth flow

### Step 3: Update render.yaml
- [ ] Add `ALLOWED_ORIGINS` environment variable
- [ ] Add `OAUTH_REDIRECT_URI` environment variable

### Step 4: Set Environment Variables in Render Dashboard
All secrets (marked `sync: false` in render.yaml) must be set manually:
- [ ] `GOOGLE_CLIENT_ID`
- [ ] `GOOGLE_CLIENT_SECRET`
- [ ] `GEMINI_API_KEY`
- [ ] `EXA_API_KEY` (if using)
- [ ] `APIFY_API_TOKEN` (if using)

### Step 5: Deploy & Test
- [ ] Push changes to GitHub
- [ ] Render auto-deploys from `main` branch
- [ ] Check deployment logs for errors
- [ ] Test `/health` endpoint: https://profile-builder.onrender.com/health
- [ ] Test CORS by accessing frontend
- [ ] Test OAuth flow end-to-end

---

## ⚡ QUICK FIX (Minimal Changes)

If you need to deploy ASAP without OAuth implementation:

### Option A: CLI-Only Mode
1. Remove OAuth from web interface
2. Users authenticate via CLI (`python -m src.main`)
3. Web interface only shows analysis results for already-authenticated accounts

### Option B: Pre-authenticate Locally
1. Authenticate on your local machine
2. Upload `data/tokens.db` to Render persistent disk
3. Web interface uses existing credentials (no new OAuth)
4. **Security Warning**: This limits to pre-authenticated accounts only

---

## 🎯 RECOMMENDED APPROACH

**For Production-Ready Deployment**:
1. Implement proper OAuth callback endpoints (see "OAuth Implementation" above)
2. Update CORS configuration
3. Add all environment variables
4. Test thoroughly before going live

**Timeline**:
- Quick fixes: 30 minutes
- Full OAuth implementation: 2-3 hours
- Testing & debugging: 1-2 hours

---

## 🚦 DEPLOYMENT STATUS

| Component | Status | Action Required |
|-----------|--------|-----------------|
| CORS | ⚠️ Must Update | Add ALLOWED_ORIGINS env var |
| OAuth Redirect | ❌ Won't Work | Implement web OAuth flow |
| Environment Vars | ⚠️ Incomplete | Add missing vars to render.yaml |
| Frontend | ✅ Ready | Uses dynamic API_BASE |
| Database | ✅ Ready | Persistent disk configured |
| Static Files | ✅ Should Work | Verify after deployment |
| Health Check | ✅ Ready | Already implemented |

---

## 📞 SUPPORT

If you encounter issues:
1. Check Render logs: Dashboard → Logs tab
2. Test health endpoint first
3. Check browser console for CORS errors
4. Verify all environment variables are set

**Common Errors**:
- `CORS error`: ALLOWED_ORIGINS not set correctly
- `OAuth error`: Redirect URI mismatch
- `500 errors`: Check Render logs for Python exceptions

