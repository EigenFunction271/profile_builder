# 🗄️ Supabase Setup for Render Deployment
## Free Alternative to Render Persistent Disks

---

## ✅ Why Supabase?

Render's free tier doesn't include persistent disks, but **Supabase** offers a perfect free alternative:

- ✅ **Completely FREE** forever tier
- ✅ **500MB PostgreSQL database** (more than enough for OAuth tokens)
- ✅ **2GB bandwidth/month**
- ✅ **Persistent storage** - data never lost on deploys
- ✅ **Production-ready** PostgreSQL
- ✅ **Easy setup** - 5 minutes

---

## 🚀 Setup Steps

### Step 1: Create Supabase Account & Project (2 minutes)

1. **Go to**: https://supabase.com/
2. **Sign up** with GitHub or email (free account)
3. **Click** "New Project"
4. **Fill in**:
   ```
   Organization: (create new or select existing)
   Project Name: profile-builder
   Database Password: (CREATE A STRONG PASSWORD - SAVE THIS!)
   Region: (choose closest to your Render region)
   Pricing Plan: Free
   ```
5. **Click** "Create new project"
6. **Wait** 2-3 minutes while Supabase sets up your database

---

### Step 2: Get Your Database Connection URL (1 minute)

Once your project is ready:

1. **Click** "Settings" (⚙️ gear icon in sidebar)
2. **Click** "Database" in settings menu
3. **Scroll down** to "Connection string" section
4. **Copy** the **"URI"** format (not "Transaction" or "Session"):
   ```
   postgresql://postgres.xxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
   ```
5. **Replace** `[YOUR-PASSWORD]` with the password you created in Step 1

**Example** (yours will be different):
```
postgresql://postgres.abcdefghijk:MySecurePassword123!@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```

**⚠️ SAVE THIS!** You'll add it to Render in the next step.

---

### Step 3: Add to Render Environment Variables (1 minute)

In **Render Dashboard** → Your Service → **Environment** tab:

1. **Click** "Add Environment Variable"
2. **Add**:
   ```
   Key: DATABASE_URL
   Value: (paste your Supabase connection URL from Step 2)
   ```
3. **Click** "Save"

**Example**:
```
Key: DATABASE_URL
Value: postgresql://postgres.abcdefghijk:MySecurePassword123!@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```

---

### Step 4: Remove Old Database Path (If Set)

Since you're using Supabase now, you can remove/ignore:
- ❌ `DATABASE_PATH` environment variable (not needed anymore)

The app will **automatically detect** `DATABASE_URL` and use PostgreSQL instead of SQLite.

---

## ✅ That's It!

Your app will now:
1. ✅ Use Supabase PostgreSQL for token storage
2. ✅ Persist OAuth tokens across deployments
3. ✅ Work on Render's free tier (no disk needed)
4. ✅ Scale better than SQLite

---

## 🔍 How It Works

The code **automatically detects** which database to use:

**Production (Render):**
- Checks for `DATABASE_URL` environment variable
- If found → Uses PostgreSQL (Supabase) ✅
- Prints: `🗄️ Using PostgreSQL storage (Supabase)`

**Local Development:**
- No `DATABASE_URL` → Uses SQLite
- Prints: `🗄️ Using SQLite storage (local)`
- Data stored in `./data/tokens.db`

**No code changes needed!** It switches automatically based on environment.

---

## 🧪 Verify It's Working

### After Deployment:

1. **Check Render logs** for:
   ```
   🗄️ Using PostgreSQL storage (Supabase)
   ```

2. **Test OAuth flow**:
   - Go to your app
   - Click "Start Analysis"
   - Complete OAuth
   - Check Supabase dashboard

3. **In Supabase Dashboard**:
   - Go to "Table Editor" in sidebar
   - Should see `tokens` table
   - After OAuth, should see a row with your email

---

## 📊 Environment Variables Summary

**For Render with Supabase:**

### Required (9 variables):
```
GOOGLE_CLIENT_ID = (your OAuth client ID)
GOOGLE_CLIENT_SECRET = (your OAuth secret)
GEMINI_API_KEY = (your Gemini key)
DATABASE_URL = postgresql://postgres... (Supabase URL)
ALLOWED_ORIGINS = https://your-app.onrender.com
OAUTH_REDIRECT_URI = https://your-app.onrender.com/oauth2callback
GEMINI_MODEL = gemini-2.0-flash-exp
PYTHON_VERSION = 3.11.0
```

### Optional:
```
ENABLE_LLM_ANALYSIS = false
LLM_MAX_EMAILS_TO_ANALYZE = 10
EXA_API_KEY = (Phase 3)
APIFY_API_TOKEN = (Phase 4)
```

### ❌ NOT Needed Anymore:
```
DATABASE_PATH  (❌ remove this - using DATABASE_URL instead)
```

---

## 🔐 Security Notes

### ✅ What's Secure:
- Connection URL includes credentials
- SSL/TLS encryption by default
- Supabase handles security patches
- OAuth tokens encrypted in transit

### ⚠️ Keep Secret:
Your `DATABASE_URL` contains:
- Database password
- Host information

**Never commit to git!** ✅ Already in `.gitignore`

---

## 🆘 Troubleshooting

### Issue: "DATABASE_URL environment variable is required"

**Cause**: `DATABASE_URL` not set in Render

**Fix**:
1. Go to Render → Environment tab
2. Check if `DATABASE_URL` exists
3. If not, add it with your Supabase connection URL

---

### Issue: "could not connect to server"

**Cause**: Wrong Supabase URL or password

**Fix**:
1. Go back to Supabase → Settings → Database
2. Copy the URI connection string again
3. Make sure password is correct (no `[YOUR-PASSWORD]` placeholder)
4. Update in Render environment variables

---

### Issue: "psycopg2 not installed"

**Cause**: `requirements.txt` not updated or build failed

**Fix**:
1. Check that `requirements.txt` includes:
   ```
   psycopg2-binary==2.9.9
   ```
2. Trigger a new deploy in Render
3. Check build logs for pip install errors

---

### Issue: Tokens not persisting

**Cause**: Still using SQLite instead of PostgreSQL

**Fix**:
1. Check Render logs for: `🗄️ Using PostgreSQL storage (Supabase)`
2. If you see SQLite instead, `DATABASE_URL` is not set correctly
3. Verify `DATABASE_URL` has the full connection string

---

## 💰 Supabase Free Tier Limits

Your free tier includes:
- ✅ 500MB database (enough for ~50,000 tokens)
- ✅ 2GB bandwidth/month
- ✅ Unlimited API requests
- ✅ 7-day log retention
- ✅ Community support

**More than enough for this app!**

If you exceed limits:
- Supabase will notify you
- Can upgrade to paid tier ($25/mo) if needed
- But unlikely for personal use

---

## 📋 Quick Checklist

- [ ] Created Supabase account
- [ ] Created new project
- [ ] Saved database password
- [ ] Copied DATABASE_URL connection string
- [ ] Added DATABASE_URL to Render environment
- [ ] Removed DATABASE_PATH from Render (if it exists)
- [ ] Deployed to Render
- [ ] Checked logs for "Using PostgreSQL storage"
- [ ] Tested OAuth flow
- [ ] Verified token stored in Supabase table

---

## 🎉 You're Done!

Your app now uses **Supabase** for persistent storage - completely free and production-ready!

**Benefits:**
✅ No more "database is locked" errors
✅ Data persists across deploys
✅ Better performance than SQLite
✅ Can view/manage tokens in Supabase dashboard
✅ Works on Render free tier

---

## 🔄 Local Development

Your local dev environment still uses SQLite automatically!

**Local:**
```bash
# No DATABASE_URL in .env
# Uses ./data/tokens.db automatically
python -m uvicorn src.api.app:app --reload
```

**Production (Render):**
```bash
# DATABASE_URL set in environment
# Uses Supabase automatically
```

**Perfect!** SQLite for local, PostgreSQL for production. 🚀

