# Render Deployment - Step-by-Step Guide
## URL: https://profile-builder.onrender.com

---

## ✅ CODE CHANGES COMPLETED

All necessary code changes have been made. Here's what was updated:

### 1. **CORS Configuration** ✅
- **File**: `src/api/app.py`
- **Change**: Made CORS origins environment-configurable
- **Added**: `ALLOWED_ORIGINS` environment variable support

### 2. **OAuth Redirect URI** ✅
- **File**: `src/auth/gmail_oauth.py`
- **Change**: Made redirect URI dynamic via `OAUTH_REDIRECT_URI` env var
- **Added**: Support for both localhost (dev) and production URLs

### 3. **OAuth Callback Endpoints** ✅
- **File**: `src/api/app.py`
- **Added**: `/auth/start` - Initiates OAuth flow
- **Added**: `/oauth2callback` - Handles Google's OAuth callback
- **Added**: Beautiful success/error pages

### 4. **Frontend OAuth Integration** ✅
- **File**: `frontend/static/js/app.js`
- **Added**: `startOAuthFlow()` - Opens OAuth in popup
- **Added**: `handleOAuthCallback()` - Handles OAuth completion
- **Added**: `pollOAuthStatus()` - Fallback polling mechanism
- **Added**: Automatic account check before analysis

### 5. **Environment Variables in render.yaml** ✅
- **File**: `render.yaml`
- **Added**: `ALLOWED_ORIGINS`
- **Added**: `OAUTH_REDIRECT_URI`
- **Added**: `ENABLE_LLM_ANALYSIS`
- **Added**: `LLM_MAX_EMAILS_TO_ANALYZE`

---

## 📋 DEPLOYMENT CHECKLIST

### Step 1: Update Google Cloud Console OAuth Settings
**⚠️ CRITICAL - DO THIS FIRST**

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", click "ADD URI"
4. Add: `https://profile-builder.onrender.com/oauth2callback`
5. **Keep** `http://localhost:8080` for local development
6. Click "SAVE"

**Your redirect URIs should look like:**
```
✓ http://localhost:8080
✓ https://profile-builder.onrender.com/oauth2callback
```

---

### Step 2: Set Environment Variables in Render Dashboard

Go to your Render service → **Environment** tab

**Add these SECRET variables** (these are marked `sync: false` in render.yaml):

```bash
GOOGLE_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_actual_client_secret
GEMINI_API_KEY=your_actual_gemini_api_key
```

**Optional** (if using later phases):
```bash
EXA_API_KEY=your_exa_api_key
APIFY_API_TOKEN=your_apify_token
```

**All other variables** are already in render.yaml and will be set automatically:
- ✅ ALLOWED_ORIGINS=https://profile-builder.onrender.com
- ✅ OAUTH_REDIRECT_URI=https://profile-builder.onrender.com/oauth2callback
- ✅ GEMINI_MODEL=gemini-2.0-flash-exp
- ✅ DATABASE_PATH=/var/data/tokens.db
- ✅ ENABLE_LLM_ANALYSIS=false
- ✅ LLM_MAX_EMAILS_TO_ANALYZE=10

---

### Step 3: Push Code to GitHub

```bash
# Commit all changes
git add .
git commit -m "Add production OAuth support and CORS configuration for Render deployment"
git push origin main
```

**Render will automatically deploy** when you push to the `main` branch.

---

### Step 4: Monitor Deployment

1. Go to Render Dashboard → Your Service
2. Click on "Logs" tab
3. Watch for deployment progress

**Look for:**
```
==> Build successful 🎉
==> Starting service with 'uvicorn src.api.app:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 5: Verify Deployment

#### Test 1: Health Check
Open in browser:
```
https://profile-builder.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX...",
  "version": "0.1.0"
}
```

#### Test 2: Frontend
Open in browser:
```
https://profile-builder.onrender.com/
```

You should see the Digital Footprint Analyzer homepage.

#### Test 3: CORS Check
Open browser console (F12), navigate to the site, and check for CORS errors.

**Should NOT see:**
```
❌ Access to fetch blocked by CORS policy
```

#### Test 4: OAuth Flow
1. Click "Start Analysis"
2. Should open Google OAuth popup
3. Authorize your Gmail account
4. Should redirect to success page
5. Analysis should start automatically

---

## 🔍 TROUBLESHOOTING

### Issue 1: CORS Error
**Symptom**: Browser console shows CORS policy error

**Solution**:
1. Check Render environment variables
2. Verify `ALLOWED_ORIGINS` is set to `https://profile-builder.onrender.com`
3. Restart the service if you just added the variable

### Issue 2: OAuth Redirect Mismatch
**Symptom**: Error "redirect_uri_mismatch"

**Solution**:
1. Verify Google Cloud Console has `https://profile-builder.onrender.com/oauth2callback`
2. Verify Render has `OAUTH_REDIRECT_URI` environment variable
3. Check for typos in the URL (https vs http, trailing slashes)

### Issue 3: 500 Internal Server Error
**Symptom**: API calls return 500 errors

**Solution**:
1. Check Render logs for Python traceback
2. Common causes:
   - Missing environment variables (GOOGLE_CLIENT_ID, etc.)
   - Database permission issues
   - Missing dependencies in requirements.txt

### Issue 4: OAuth Popup Blocked
**Symptom**: Popup window doesn't open

**Solution**:
1. Allow popups for profile-builder.onrender.com
2. Or use fallback: app will redirect instead of popup

### Issue 5: Database Errors
**Symptom**: "database is locked" or write errors

**Solution**:
1. Check that persistent disk is mounted at `/var/data`
2. Verify render.yaml has disk configuration
3. Check logs for permission errors

---

## 🧪 TESTING CHECKLIST

After deployment, test each feature:

- [ ] Homepage loads correctly
- [ ] CSS and JavaScript load (check Network tab)
- [ ] Health endpoint returns 200 OK
- [ ] No CORS errors in console
- [ ] OAuth flow opens correctly
- [ ] Google authorization works
- [ ] Callback redirects to success page
- [ ] Analysis starts after OAuth
- [ ] Email statistics display correctly
- [ ] Signal extraction shows results
- [ ] Can view stored accounts

---

## 🚨 KNOWN LIMITATIONS ON RENDER FREE TIER

1. **Cold Starts**: Service spins down after 15 minutes of inactivity
   - First request after idle will be slow (30-60 seconds)
   - Solution: Keep service awake with external pinger (optional)

2. **OAuth Sessions**: In-memory sessions lost on restart
   - Stored credentials persist (in database)
   - Active OAuth flows will need to restart
   - Solution: Use Redis for production (not free)

3. **Disk Space**: 1GB persistent storage
   - Should be enough for hundreds of user tokens
   - Monitor usage in Render dashboard

4. **Request Timeout**: 30 second timeout
   - Long-running analyses might timeout
   - Current implementation should be fine (<30s)

---

## 🔒 SECURITY NOTES

### What's Secure:
✅ CORS properly configured
✅ OAuth credentials encrypted by Google
✅ Refresh tokens stored in database
✅ Environment variables for secrets
✅ HTTPS enforced by Render

### What to Monitor:
⚠️ Session storage is in-memory (sessions lost on restart)
⚠️ No rate limiting on OAuth endpoints
⚠️ Database not encrypted at rest (free tier)

### For Production Upgrade:
- Use Redis for session storage
- Add rate limiting middleware
- Enable database encryption
- Add request logging/monitoring
- Implement proper error tracking (Sentry)

---

## 📊 MONITORING

### Check These Regularly:

1. **Deployment Status**
   - Render Dashboard → Your Service
   - Should show "Live" with green indicator

2. **Logs**
   - Click "Logs" tab
   - Watch for errors or warnings

3. **Disk Usage**
   - Render Dashboard → Metrics
   - Monitor `/var/data` usage

4. **Request Metrics**
   - Check response times
   - Monitor error rates

---

## 🎯 POST-DEPLOYMENT TASKS

### Immediate (Next 24 Hours):
- [ ] Test OAuth flow with multiple Gmail accounts
- [ ] Verify all email analyses complete successfully
- [ ] Check logs for any unexpected errors
- [ ] Test from different browsers/devices

### Short Term (Next Week):
- [ ] Set up uptime monitoring (e.g., UptimeRobot)
- [ ] Create backup of database
- [ ] Document any issues encountered
- [ ] Gather user feedback

### Long Term:
- [ ] Consider upgrading to paid tier for better reliability
- [ ] Implement proper session management (Redis)
- [ ] Add analytics to track usage
- [ ] Set up error tracking (Sentry)

---

## 🆘 GETTING HELP

### If Deployment Fails:

1. **Check Render Logs**
   - Most errors will show here
   - Look for Python tracebacks

2. **Verify Environment Variables**
   - Go to Environment tab
   - Ensure all required vars are set

3. **Check Build Logs**
   - Go to Events tab
   - Look for pip install errors

4. **Common Issues Document**
   - See RENDER_DEPLOYMENT_CHECKLIST.md
   - Contains detailed troubleshooting

---

## ✅ SUCCESS CRITERIA

Deployment is successful when:

1. ✅ Health endpoint returns 200 OK
2. ✅ Frontend loads without errors
3. ✅ No CORS errors in console
4. ✅ OAuth flow completes successfully
5. ✅ Analysis runs and shows results
6. ✅ No errors in Render logs

---

## 🎉 YOU'RE DONE!

Your Digital Footprint Analyzer is now live at:
**https://profile-builder.onrender.com**

Share it with users and monitor the logs for any issues.

Good luck! 🚀

