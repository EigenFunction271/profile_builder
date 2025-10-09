# 🔧 Render Manual Setup Guide
## For Manual Dashboard Configuration (Not Using render.yaml)

---

## ✅ Code Changes (Already Done)

All code updates are complete and work with manual setup:
- ✅ CORS configuration
- ✅ OAuth endpoints
- ✅ Dynamic redirect URIs
- ✅ Frontend OAuth flow

---

## 🎯 Manual Configuration Steps

Since you're using manual setup, you need to configure everything through the Render Dashboard.

### Step 1: Create New Web Service (If Not Already Created)

1. Go to: https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure as follows:

**Basic Settings:**
```
Name: digital-footprint-analyzer (or your preferred name)
Region: Oregon (US West) - or your preferred region
Branch: main
Root Directory: (leave blank)
Runtime: Python 3
```

**Build & Deploy:**
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
```
Plan: Free
```

---

### Step 2: Configure Environment Variables

Go to your service → **Environment** tab → Click "Add Environment Variable"

Add **ALL** of these variables:

#### 🔴 REQUIRED (Secrets - Keep Private):

| Key | Value | Notes |
|-----|-------|-------|
| `GOOGLE_CLIENT_ID` | `your_client_id.apps.googleusercontent.com` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | `your_client_secret` | From Google Cloud Console |
| `GEMINI_API_KEY` | `your_gemini_api_key` | From Google AI Studio |

#### 🟢 REQUIRED (Public Config):

| Key | Value | Notes |
|-----|-------|-------|
| `ALLOWED_ORIGINS` | `https://YOUR-SERVICE-NAME.onrender.com` | **Replace with YOUR actual Render URL** |
| `OAUTH_REDIRECT_URI` | `https://YOUR-SERVICE-NAME.onrender.com/oauth2callback` | **Replace with YOUR actual Render URL** |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | LLM model to use |
| `DATABASE_PATH` | `/var/data/tokens.db` | Database location |
| `PYTHON_VERSION` | `3.11.0` | Python version |

#### 🟡 OPTIONAL (Can add later):

| Key | Value | Notes |
|-----|-------|-------|
| `EXA_API_KEY` | `your_exa_api_key` | For Phase 3 - Identity Resolution |
| `APIFY_API_TOKEN` | `apify_api_your_token` | For Phase 4 - Profile Scraping |
| `ENABLE_LLM_ANALYSIS` | `false` | Set to `true` to enable LLM email analysis |
| `LLM_MAX_EMAILS_TO_ANALYZE` | `10` | Max emails for LLM analysis |

---

### Step 3: Add Persistent Disk (For Database)

Go to your service → **Disks** section

1. Click "Add Disk"
2. Configure:
   ```
   Name: data
   Mount Path: /var/data
   Size: 1 GB
   ```
3. Click "Save"

**⚠️ CRITICAL**: Without this disk, your database (user tokens) will be lost on every restart!

---

### Step 4: Find Your Render URL

After creating the service, Render assigns you a URL like:
```
https://profile-builder-xyz123.onrender.com
```

**You MUST update 2 environment variables with this exact URL:**

1. Go back to **Environment** tab
2. Edit `ALLOWED_ORIGINS`:
   ```
   https://profile-builder-xyz123.onrender.com
   ```
   (Replace with YOUR actual URL)

3. Edit `OAUTH_REDIRECT_URI`:
   ```
   https://profile-builder-xyz123.onrender.com/oauth2callback
   ```
   (Replace with YOUR actual URL)

4. Click "Save Changes"

---

### Step 5: Update Google Cloud Console

**⚠️ CRITICAL - Use YOUR Render URL**

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", add:
   ```
   https://YOUR-ACTUAL-RENDER-URL.onrender.com/oauth2callback
   ```
   (Use the exact URL Render gave you!)
4. Click "SAVE"

---

### Step 6: Deploy

Once you've configured everything:

1. **If first deployment**: Render will auto-deploy
2. **If updating config**: Click "Manual Deploy" → "Deploy latest commit"

---

## 📋 Quick Checklist for Manual Setup

### Service Configuration:
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
- [ ] Runtime: Python 3
- [ ] Branch: main

### Environment Variables (11 total):
- [ ] `GOOGLE_CLIENT_ID` (secret)
- [ ] `GOOGLE_CLIENT_SECRET` (secret)
- [ ] `GEMINI_API_KEY` (secret)
- [ ] `ALLOWED_ORIGINS` (with YOUR Render URL)
- [ ] `OAUTH_REDIRECT_URI` (with YOUR Render URL)
- [ ] `GEMINI_MODEL`
- [ ] `DATABASE_PATH`
- [ ] `PYTHON_VERSION`
- [ ] `ENABLE_LLM_ANALYSIS` (optional)
- [ ] `LLM_MAX_EMAILS_TO_ANALYZE` (optional)
- [ ] `EXA_API_KEY` (optional - for later)
- [ ] `APIFY_API_TOKEN` (optional - for later)

### Persistent Storage:
- [ ] Disk added (name: data)
- [ ] Mount path: `/var/data`
- [ ] Size: 1 GB

### Google Cloud Console:
- [ ] Redirect URI added with YOUR Render URL

---

## 🎯 Example Configuration

Here's what your setup should look like (with your actual values):

**Environment Variables (as they appear in Render):**

```
GOOGLE_CLIENT_ID = 123456789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET = GOCSPX-abc123def456
GEMINI_API_KEY = AIzaSyAbc123...
ALLOWED_ORIGINS = https://profile-builder-xyz123.onrender.com
OAUTH_REDIRECT_URI = https://profile-builder-xyz123.onrender.com/oauth2callback
GEMINI_MODEL = gemini-2.0-flash-exp
DATABASE_PATH = /var/data/tokens.db
PYTHON_VERSION = 3.11.0
ENABLE_LLM_ANALYSIS = false
LLM_MAX_EMAILS_TO_ANALYZE = 10
```

**Google Cloud Console → Authorized redirect URIs:**
```
http://localhost:8080
https://profile-builder-xyz123.onrender.com/oauth2callback
```

---

## ⚠️ Common Mistakes with Manual Setup

### Mistake 1: Wrong ALLOWED_ORIGINS
**Wrong:**
```
ALLOWED_ORIGINS = profile-builder.onrender.com  ❌ (missing https://)
ALLOWED_ORIGINS = https://profile-builder.onrender.com/  ❌ (trailing slash)
```

**Correct:**
```
ALLOWED_ORIGINS = https://profile-builder-xyz123.onrender.com  ✅
```

### Mistake 2: Wrong OAUTH_REDIRECT_URI
**Wrong:**
```
OAUTH_REDIRECT_URI = http://profile-builder.onrender.com/oauth2callback  ❌ (http not https)
OAUTH_REDIRECT_URI = https://profile-builder.onrender.com  ❌ (missing /oauth2callback)
```

**Correct:**
```
OAUTH_REDIRECT_URI = https://profile-builder-xyz123.onrender.com/oauth2callback  ✅
```

### Mistake 3: Mismatched URLs
Google Cloud Console redirect URI **MUST EXACTLY MATCH** `OAUTH_REDIRECT_URI` env var:

**Render Environment Variable:**
```
OAUTH_REDIRECT_URI = https://profile-builder-xyz123.onrender.com/oauth2callback
```

**Google Cloud Console:**
```
Authorized redirect URIs:
  https://profile-builder-xyz123.onrender.com/oauth2callback  ✅ (exact match)
```

### Mistake 4: Forgot Persistent Disk
Without the disk at `/var/data`, your database will reset on every deployment!

---

## 🧪 Verification Steps

After everything is configured:

### 1. Check Service Status
- Dashboard should show "Live" with green indicator

### 2. Check Logs
- Go to "Logs" tab
- Look for:
  ```
  INFO:     Started server process
  INFO:     Application startup complete.
  ```

### 3. Test Health Endpoint
Visit: `https://YOUR-URL.onrender.com/health`

Expected:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "0.1.0"
}
```

### 4. Test Frontend
Visit: `https://YOUR-URL.onrender.com/`

Should see the Digital Footprint Analyzer homepage

### 5. Test OAuth
1. Click "Start Analysis"
2. OAuth popup should open
3. Authorize with Google
4. Should redirect to success page
5. Analysis should start

---

## 🔍 Debugging Tips

### Check Environment Variables
In Render Dashboard → Environment tab:
- Count them: Should have at least 8 variables set
- Check for typos in URLs
- Verify ALLOWED_ORIGINS and OAUTH_REDIRECT_URI match your actual Render URL

### Check Logs for Errors
Common errors in logs:

**"Missing configuration: GOOGLE_CLIENT_ID"**
→ Environment variable not set or misspelled

**"CORS policy: No 'Access-Control-Allow-Origin'"**
→ ALLOWED_ORIGINS is wrong or not set

**"redirect_uri_mismatch"**
→ Google Cloud Console doesn't have your callback URL, or URLs don't match exactly

**"database is locked"**
→ Persistent disk not mounted or wrong path

---

## 📝 Pro Tips

### Tip 1: Use Environment Groups (Render Feature)
If you have multiple services, create an Environment Group:
1. Settings → Environment Groups
2. Add common vars (GEMINI_API_KEY, etc.)
3. Link to multiple services

### Tip 2: Test Locally First
Before deploying, test locally with production-like settings:

```bash
# .env file
ALLOWED_ORIGINS=http://localhost:8000
OAUTH_REDIRECT_URI=http://localhost:8080
# ... other vars

python -m uvicorn src.api.app:app --reload
```

### Tip 3: Keep Secrets Secure
- Never commit secrets to git
- Use Render's secret management (environment variables)
- Secrets are encrypted at rest in Render

### Tip 4: Monitor Deployment
After making changes:
1. Watch the Logs tab during deployment
2. First request after deploy may be slow (cold start)
3. Test OAuth immediately after deploy

---

## 🆘 Still Having Issues?

### If OAuth Doesn't Work:

1. **Double-check all URLs match EXACTLY**:
   - Render env var `OAUTH_REDIRECT_URI`
   - Google Cloud Console redirect URI
   - Both should be identical character-for-character

2. **Check for typos**:
   - `oauth2callback` (not `oauth-callback` or `oauthcallback`)
   - `https://` (not `http://`)
   - Your exact Render URL (case-sensitive)

3. **Try a fresh OAuth**:
   - Delete credentials from browser
   - Try in incognito mode
   - Check browser console for errors

### If Analysis Fails:

1. Check Render logs for Python errors
2. Verify GEMINI_API_KEY is set correctly
3. Check that persistent disk is mounted
4. Test health endpoint first

---

## 📊 Summary: Manual vs render.yaml

| What | render.yaml | Manual Setup |
|------|-------------|--------------|
| **Environment Variables** | Auto-configured | You set each one manually |
| **Persistent Disk** | Auto-created | You create manually |
| **Build/Start Commands** | Defined in YAML | You set in dashboard |
| **Code Changes** | Same ✅ | Same ✅ |
| **Flexibility** | Less flexible | More control |
| **Updates** | Git commit updates config | Manual changes in dashboard |

**Bottom line**: Manual setup gives you more control but requires more steps. All our code changes work the same either way!

---

## ✅ Final Checklist

Before going live:

- [ ] All 8+ environment variables set
- [ ] ALLOWED_ORIGINS has YOUR Render URL
- [ ] OAUTH_REDIRECT_URI has YOUR Render URL
- [ ] Persistent disk mounted at /var/data
- [ ] Google Cloud Console has YOUR callback URL
- [ ] Code pushed to GitHub
- [ ] Deployment successful (check logs)
- [ ] Health endpoint returns 200 OK
- [ ] Frontend loads without errors
- [ ] OAuth flow completes successfully
- [ ] Analysis runs and shows results

---

## 🚀 You're Ready!

Your manual setup is complete! The app should work identically to a render.yaml setup.

**Key Difference**: You'll manage environment variables through the Render Dashboard instead of YAML file.

Good luck with your deployment! 🎉

