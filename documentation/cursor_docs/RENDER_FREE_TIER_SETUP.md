# 🆓 Render Free Tier Setup (No Disks)
## Complete Guide with Supabase for Storage

---

## ✅ Solution: Supabase (Free Database)

Since Render's free tier doesn't include persistent disks, use **Supabase** for free PostgreSQL storage!

**Quick Summary:**
1. ✅ Supabase = Free PostgreSQL database
2. ✅ Code automatically switches to PostgreSQL when `DATABASE_URL` is set
3. ✅ SQLite for local dev, PostgreSQL for production
4. ✅ Takes 5 minutes to setup

---

## 🚀 Complete Setup (10 Minutes)

### Part 1: Supabase Setup (5 minutes)

#### 1. Create Supabase Project
1. Go to https://supabase.com/
2. Sign up (free account)
3. Click "New Project"
4. Fill in:
   - Name: `profile-builder`
   - Password: (CREATE STRONG PASSWORD - SAVE IT!)
   - Region: (closest to you)
5. Click "Create"
6. Wait 2-3 minutes

#### 2. Get Connection URL
1. Click "Settings" → "Database"
2. Scroll to "Connection string"
3. Copy **"URI"** format:
   ```
   postgresql://postgres.xxx:[YOUR-PASSWORD]@xxx.supabase.com:5432/postgres
   ```
4. Replace `[YOUR-PASSWORD]` with your actual password
5. **SAVE THIS URL!**

---

### Part 2: Render Setup (5 minutes)

#### 1. Create Web Service (If Not Created)
1. Go to https://dashboard.render.com/
2. "New +" → "Web Service"
3. Connect GitHub repo
4. Configure:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
   ```

#### 2. Add Environment Variables

In Render → Environment tab, add these **9 variables**:

**Secrets** (keep private):
```
GOOGLE_CLIENT_ID = your_oauth_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET = your_oauth_client_secret
GEMINI_API_KEY = your_gemini_api_key
DATABASE_URL = postgresql://postgres... (from Supabase Step 2)
```

**Public Config** (⚠️ UPDATE with YOUR Render URL):
```
ALLOWED_ORIGINS = https://YOUR-APP-NAME.onrender.com
OAUTH_REDIRECT_URI = https://YOUR-APP-NAME.onrender.com/oauth2callback
GEMINI_MODEL = gemini-2.0-flash-exp
PYTHON_VERSION = 3.11.0
```

**Optional**:
```
ENABLE_LLM_ANALYSIS = false
LLM_MAX_EMAILS_TO_ANALYZE = 10
```

#### 3. Update Google Cloud Console
1. Go to https://console.cloud.google.com/apis/credentials
2. Click your OAuth Client ID
3. Add redirect URI:
   ```
   https://YOUR-APP-NAME.onrender.com/oauth2callback
   ```
   (Use YOUR actual Render URL!)
4. Click "SAVE"

---

## 📋 Environment Variables Checklist

### ✅ Required (9 variables):
- [ ] `GOOGLE_CLIENT_ID`
- [ ] `GOOGLE_CLIENT_SECRET`
- [ ] `GEMINI_API_KEY`
- [ ] `DATABASE_URL` (Supabase connection string)
- [ ] `ALLOWED_ORIGINS` (with YOUR Render URL)
- [ ] `OAUTH_REDIRECT_URI` (with YOUR Render URL)
- [ ] `GEMINI_MODEL`
- [ ] `PYTHON_VERSION`

### 🟡 Optional:
- [ ] `ENABLE_LLM_ANALYSIS`
- [ ] `LLM_MAX_EMAILS_TO_ANALYZE`

### ❌ NOT Needed (Free Tier):
- ~~Persistent Disk~~ (using Supabase instead!)
- ~~`DATABASE_PATH`~~ (using `DATABASE_URL` instead)

---

## 🎯 Key Differences: Free Tier vs Paid

| Feature | Free Tier | With Paid Disk |
|---------|-----------|----------------|
| **Storage** | Supabase PostgreSQL (free) | Render Disk ($7/mo) |
| **Database** | External (Supabase) | Internal (SQLite) |
| **Performance** | Better ✅ | Good |
| **Cost** | $0 ✅ | $7/mo |
| **Setup** | Slightly more steps | Simpler |
| **Scalability** | Excellent ✅ | Limited |

**Free tier with Supabase is actually BETTER!** 🎉

---

## 🧪 Verify Everything Works

### 1. Check Render Deployment
```
Render Dashboard → Your Service → Logs
```

Look for:
```
✅ Build successful 🎉
✅ INFO: Started server process
✅ 🗄️ Using PostgreSQL storage (Supabase)
```

### 2. Test Endpoints

**Health Check:**
```
https://YOUR-APP.onrender.com/health
→ Should return: {"status": "healthy"}
```

**Frontend:**
```
https://YOUR-APP.onrender.com/
→ Should load homepage
```

### 3. Test OAuth Flow
1. Click "Start Analysis"
2. OAuth popup opens
3. Authorize Gmail
4. Success page shows
5. Analysis starts

### 4. Verify Supabase
1. Go to Supabase Dashboard
2. Click "Table Editor"
3. Should see `tokens` table
4. After OAuth, should have 1 row

---

## 🔍 Troubleshooting

### "DATABASE_URL environment variable is required"
**Fix**: Add `DATABASE_URL` to Render environment variables

### "redirect_uri_mismatch"
**Fix**: 
1. Check Google Cloud Console has YOUR Render URL
2. Check `OAUTH_REDIRECT_URI` matches exactly

### "CORS policy error"
**Fix**: Update `ALLOWED_ORIGINS` with YOUR Render URL

### Tokens not persisting
**Fix**: Check logs for "Using PostgreSQL storage (Supabase)"

---

## 💡 Pro Tips

### Tip 1: Check Logs First
Always check Render logs to see:
- Which database is being used (PostgreSQL vs SQLite)
- Any errors during startup
- OAuth flow errors

### Tip 2: Match URLs Exactly
These must be IDENTICAL:
- `OAUTH_REDIRECT_URI` in Render
- Redirect URI in Google Cloud Console

### Tip 3: Use Incognito for Testing
When testing OAuth, use incognito to avoid cached credentials

### Tip 4: Monitor Supabase
Supabase Dashboard shows:
- Database size
- Active connections
- Bandwidth usage
- All within free limits

---

## 📊 What You Get (Free Tier)

**Render Free:**
- ✅ 750 hours/month (enough for 24/7)
- ✅ Automatic deploys from GitHub
- ✅ SSL certificate
- ❌ No persistent disk

**Supabase Free:**
- ✅ 500MB PostgreSQL database
- ✅ 2GB bandwidth/month
- ✅ Unlimited API requests
- ✅ SSL/TLS encryption

**Total Cost: $0/month** 🎉

---

## 🚀 Deploy Checklist

### Before Deployment:
- [ ] Supabase project created
- [ ] Database URL copied
- [ ] All 9 environment variables set in Render
- [ ] Google Cloud Console redirect URI added
- [ ] Code pushed to GitHub

### After Deployment:
- [ ] Check Render logs (no errors)
- [ ] Test /health endpoint
- [ ] Test frontend loads
- [ ] Test OAuth flow
- [ ] Check Supabase table for token

### If All Green:
- [ ] Share app URL with users
- [ ] Monitor Render logs
- [ ] Monitor Supabase usage

---

## 📚 Documentation Reference

**Detailed Guides:**
- `SUPABASE_SETUP.md` - Complete Supabase instructions
- `RENDER_MANUAL_SETUP.md` - Full Render manual setup
- `DEPLOYMENT_STEPS.md` - Step-by-step deployment

**Quick Reference:**
- `RENDER_QUICK_START.md` - 5-minute setup
- `BUGFIX_SUMMARY.md` - Code fixes applied

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✅ Render shows "Live" status
2. ✅ Health endpoint returns 200
3. ✅ Frontend loads without errors
4. ✅ OAuth completes successfully
5. ✅ Analysis runs and shows results
6. ✅ Logs show "Using PostgreSQL storage"
7. ✅ Token appears in Supabase table

---

## 🎉 You're Done!

**Your app is now live on Render's free tier with Supabase!**

**URL**: `https://your-app-name.onrender.com`

**Cost**: $0/month

**Storage**: Persistent PostgreSQL (Supabase)

**Performance**: Production-ready

Good luck! 🚀

---

## 🆘 Need Help?

If you encounter issues:
1. Check Render logs (most errors show here)
2. Verify all environment variables are set
3. Test each endpoint individually
4. Check browser console for frontend errors
5. See `SUPABASE_SETUP.md` for Supabase troubleshooting

