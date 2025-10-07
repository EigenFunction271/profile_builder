# Render Deployment Guide

Complete guide to deploying **Digital Footprint Analyzer** on Render with a FastAPI backend and HTML/CSS/JS frontend.

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a Git repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free tier available)
3. **Google OAuth Credentials** - Set up in Google Cloud Console
4. **Gemini API Key** (Optional for Phase 1) - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Render Web Service          │
│  ┌──────────────┐  ┌──────────────┐ │
│  │   FastAPI    │  │   Frontend   │ │
│  │   Backend    │←→│  HTML/CSS/JS │ │
│  │   (Python)   │  │  (Tailwind)  │ │
│  └──────────────┘  └──────────────┘ │
│          ↓                           │
│  ┌──────────────┐                   │
│  │  Persistent  │                   │
│  │     Disk     │                   │
│  │  (tokens.db) │                   │
│  └──────────────┘                   │
└─────────────────────────────────────┘
           ↓
    ┌──────────────┐
    │  Gmail API   │
    └──────────────┘
```

## 🚀 Quick Deploy (5 minutes)

### Option 1: Deploy with Blueprint (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add web interface and Render config"
   git push origin main
   ```

2. **Create New Web Service on Render**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables** (see below)

4. **Deploy!**
   - Click "Create Web Service"
   - Wait 3-5 minutes for build
   - Your app will be live at `https://your-app.onrender.com`

### Option 2: Manual Setup

1. **Create New Web Service**
   - Name: `digital-footprint-analyzer`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`

2. **Add Persistent Disk**
   - Name: `data`
   - Mount Path: `/var/data`
   - Size: 1 GB (free tier)

3. **Configure Environment Variables** (see below)

4. **Deploy**

## 🔐 Environment Variables

Add these in Render Dashboard → Your Service → Environment:

### Required for Phase 1 (Gmail OAuth)

```bash
# Google OAuth (Required)
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

# Database Path (Use persistent disk)
DATABASE_PATH=/var/data/tokens.db
```

### Optional (For Future Phases)

```bash
# Google Gemini (Phase 3+)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# Exa API (Phase 3+)
EXA_API_KEY=your_exa_api_key

# Apify (Phase 4+)
APIFY_API_TOKEN=your_apify_token
```

## 🔧 Google OAuth Setup for Render

### 1. Update OAuth Consent Screen

In [Google Cloud Console](https://console.cloud.google.com):

1. Navigate to "APIs & Services" → "OAuth consent screen"
2. Under "Authorized domains", add:
   - `onrender.com`

### 2. Update OAuth Client

1. Go to "Credentials" → Your OAuth 2.0 Client ID
2. Under "Authorized redirect URIs", add:
   ```
   https://your-app-name.onrender.com
   http://localhost:8000
   ```
3. Replace `your-app-name` with your actual Render service name

### 3. Important Note

⚠️ **Render's free tier sleeps after 15 minutes of inactivity**. The OAuth flow needs a running server, so:
- Wake up your service by visiting it first
- Or upgrade to a paid plan ($7/month) for always-on service

## 📦 What Gets Deployed

### Backend (FastAPI)
- **File**: `src/api/app.py`
- **Endpoints**:
  - `GET /` - Frontend
  - `GET /health` - Health check
  - `GET /api/config/check` - Check configuration
  - `POST /api/analysis/start` - Start analysis
  - `GET /api/analysis/status/{id}` - Get status
  - `GET /api/accounts` - List stored accounts

### Frontend (HTML/CSS/JS)
- **File**: `frontend/templates/index.html`
- **Features**:
  - Beautiful gradient UI with Tailwind CSS
  - Real-time progress tracking
  - Email statistics display
  - Sample emails preview
  - Stored accounts management

### Persistent Storage
- **Location**: `/var/data/tokens.db`
- **Contents**: OAuth tokens (encrypted by Google)
- **Size**: 1 GB (plenty for tokens)

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "0.1.0"
}
```

### 2. Config Check
```bash
curl https://your-app.onrender.com/api/config/check
```

### 3. Visit Frontend
Open `https://your-app.onrender.com` in your browser

### 4. Run Analysis
1. Click "Start Analysis"
2. Authenticate with Gmail
3. View your results!

## 🐛 Troubleshooting

### "Missing GOOGLE_CLIENT_ID" Error

**Cause**: Environment variables not set

**Fix**:
1. Go to Render Dashboard → Your Service → Environment
2. Add all required environment variables
3. Click "Save Changes" (auto-deploys)

### OAuth Redirect Error

**Cause**: Redirect URI not authorized

**Fix**:
1. Check your Render URL: `https://your-app.onrender.com`
2. Add this URL to Google Cloud Console → Credentials → Authorized redirect URIs
3. Wait 5 minutes for Google to update

### "Service Unavailable" or 503 Error

**Cause**: Free tier service is sleeping

**Fix**:
- Wait 30-60 seconds for service to wake up
- Refresh the page

### Database Permission Error

**Cause**: Database path not configured correctly

**Fix**:
1. Ensure persistent disk is mounted at `/var/data`
2. Set `DATABASE_PATH=/var/data/tokens.db` in environment variables

### Build Fails

**Cause**: Missing dependencies

**Fix**:
1. Check `requirements.txt` is committed
2. Verify Python version in `runtime.txt` (3.11.0)
3. Check build logs in Render Dashboard

## 📊 Monitoring

### Render Dashboard

Monitor your service:
- **Metrics**: CPU, Memory, Response times
- **Logs**: Real-time application logs
- **Events**: Deployments, restarts

### Application Logs

View logs in Render Dashboard → Your Service → Logs

Look for:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 💰 Cost Breakdown

### Free Tier
- ✅ 750 hours/month (enough for 1 service)
- ✅ 1 GB persistent disk
- ✅ Automatic SSL
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ Limited compute

**Perfect for**: Testing, demos, personal use

### Paid Plans
- **Starter ($7/month)**:
  - Always on (no sleep)
  - More CPU/RAM
  - Better for production

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ Never commit secrets to Git
- ✅ Use Render's environment variables
- ✅ Rotate API keys regularly

### 2. OAuth Security
- ✅ Only authorize specific redirect URIs
- ✅ Use read-only Gmail scopes
- ✅ Tokens stored encrypted

### 3. CORS
- Update `allow_origins` in `src/api/app.py` for production
- Current setting: `["*"]` (development)
- Production: `["https://your-app.onrender.com"]`

## 🚀 Going to Production

### 1. Update CORS
```python
# src/api/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.onrender.com"],  # Your actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Add Custom Domain (Optional)
1. Render Dashboard → Your Service → Settings
2. Add custom domain
3. Update DNS records

### 3. Enable Redis (Optional)
For production, replace in-memory session storage:
```python
# Install redis
pip install redis

# Use Redis instead of dict
import redis
redis_client = redis.Redis(host='your-redis-host')
```

### 4. Upgrade to Paid Plan
- Always-on service
- Better performance
- More storage

## 📱 Mobile Responsiveness

The frontend is fully responsive:
- ✅ Mobile-first design
- ✅ Tailwind CSS breakpoints
- ✅ Touch-friendly buttons
- ✅ Works on all devices

## 🔄 Continuous Deployment

Render automatically deploys when you push to main:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render will:
1. Detect changes
2. Build automatically
3. Deploy new version
4. Zero downtime

## 📈 Scaling

### Horizontal Scaling
- Render auto-scales based on traffic
- Free tier: Limited
- Paid tier: Better scaling

### Vertical Scaling
- Upgrade plan for more resources
- Standard: 0.5 GB RAM
- Pro: 4 GB RAM

## 🎯 Next Steps

After deploying Phase 1:

1. **Test thoroughly** with your Gmail account
2. **Monitor logs** for any errors
3. **Implement Phase 2** (Signal Extraction)
4. **Add Phase 3** (Identity Resolution with Gemini)
5. **Complete Phase 4-5** for full pipeline

## 📚 Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Project README](README.md)

## 🆘 Need Help?

1. Check [Render Community Forum](https://community.render.com/)
2. Review application logs in Render Dashboard
3. Check GitHub issues
4. Contact support

---

## ✅ Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create Render account
- [ ] Set up Google OAuth credentials
- [ ] Add authorized redirect URIs
- [ ] Create Render web service
- [ ] Add persistent disk
- [ ] Configure environment variables
- [ ] Deploy and test
- [ ] Update CORS for production
- [ ] Monitor logs

---

**Your Digital Footprint Analyzer is now live! 🎉**

Visit `https://your-app.onrender.com` to start analyzing!

