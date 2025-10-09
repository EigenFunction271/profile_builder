# 🚀 Render Deployment - Quick Start
## Deploy in 5 Minutes

---

## ✅ What Was Fixed for Production

All code is ready! Here's what was updated for your Render deployment:

1. **CORS** - Now accepts requests from `https://profile-builder.onrender.com`
2. **OAuth** - Added web-based OAuth flow (replaces localhost-only flow)
3. **Environment Variables** - All configuration now in render.yaml
4. **Frontend** - Auto-detects production URL and handles OAuth popup

---

## 🎯 3 CRITICAL STEPS BEFORE DEPLOYING

### 1️⃣ Update Google Cloud Console (2 minutes)

**URL**: https://console.cloud.google.com/apis/credentials

1. Click your OAuth 2.0 Client ID
2. Under "Authorized redirect URIs", add:
   ```
   https://profile-builder.onrender.com/oauth2callback
   ```
3. Click SAVE

**⚠️ This MUST be done or OAuth will fail!**

---

### 2️⃣ Set Secrets in Render Dashboard (3 minutes)

**URL**: Your Render Service → Environment Tab

Add these 3 required secrets:

| Key | Value |
|-----|-------|
| `GOOGLE_CLIENT_ID` | Your OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Your OAuth client secret |
| `GEMINI_API_KEY` | Your Gemini API key |

**Everything else is already configured in render.yaml**

---

### 3️⃣ Push to GitHub (30 seconds)

```bash
git add .
git commit -m "Add production deployment support"
git push origin main
```

Render will auto-deploy!

---

## ✅ Verification (After Deployment)

### Test These URLs:

1. **Health Check**:
   ```
   https://profile-builder.onrender.com/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Frontend**:
   ```
   https://profile-builder.onrender.com/
   ```
   Should load the homepage

3. **OAuth Flow**:
   - Click "Start Analysis"
   - Should open Google OAuth popup
   - After auth, should start analysis

---

## 🚨 Troubleshooting

### Problem: CORS Error
**Fix**: Verify `ALLOWED_ORIGINS` in render.yaml is `https://profile-builder.onrender.com`

### Problem: OAuth Redirect Error
**Fix**: Double-check Google Cloud Console has the callback URL exactly as:
```
https://profile-builder.onrender.com/oauth2callback
```
(No trailing slash!)

### Problem: 500 Error
**Fix**: Check Render logs for Python errors. Usually missing env vars.

---

## 📁 Files Changed

All changes are committed and ready. Key files updated:

- ✅ `src/api/app.py` - Added OAuth endpoints, CORS config
- ✅ `src/auth/gmail_oauth.py` - Dynamic redirect URI
- ✅ `frontend/static/js/app.js` - Web OAuth flow
- ✅ `render.yaml` - Added environment variables

---

## 🎯 Environment Variables Summary

### Already in render.yaml (Auto-configured):
- `ALLOWED_ORIGINS` = https://profile-builder.onrender.com
- `OAUTH_REDIRECT_URI` = https://profile-builder.onrender.com/oauth2callback
- `GEMINI_MODEL` = gemini-2.0-flash-exp
- `DATABASE_PATH` = /var/data/tokens.db

### You Must Add in Render Dashboard:
- `GOOGLE_CLIENT_ID` (required)
- `GOOGLE_CLIENT_SECRET` (required)
- `GEMINI_API_KEY` (required)
- `EXA_API_KEY` (optional - for Phase 3)
- `APIFY_API_TOKEN` (optional - for Phase 4)

---

## ⏱️ Timeline

- **Google Cloud Setup**: 2 minutes
- **Render Env Vars**: 3 minutes
- **Git Push**: 30 seconds
- **Render Deploy**: 3-5 minutes
- **Testing**: 2 minutes

**Total: ~10 minutes**

---

## 📋 Quick Checklist

- [ ] Added redirect URI to Google Cloud Console
- [ ] Set GOOGLE_CLIENT_ID in Render
- [ ] Set GOOGLE_CLIENT_SECRET in Render
- [ ] Set GEMINI_API_KEY in Render
- [ ] Pushed code to GitHub
- [ ] Watched deployment in Render logs
- [ ] Tested /health endpoint
- [ ] Tested frontend loads
- [ ] Tested OAuth flow works
- [ ] Tested analysis completes

---

## 🎉 You're Ready!

**Deployment URL**: https://profile-builder.onrender.com

For detailed troubleshooting, see:
- `DEPLOYMENT_STEPS.md` - Complete step-by-step guide
- `RENDER_DEPLOYMENT_CHECKLIST.md` - Comprehensive troubleshooting

Good luck! 🚀

