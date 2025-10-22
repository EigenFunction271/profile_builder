# Quick Start Guide - Phase 1

This guide will get you up and running with Phase 1 (Gmail OAuth + Email Fetching) in 5 minutes.

## ✅ Checklist

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Setup (5 minutes)

#### Step-by-Step:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. **Enable Gmail API:**
   - Navigation menu → "APIs & Services" → "Library"
   - Search "Gmail API"
   - Click "Enable"

4. **Create OAuth Credentials:**
   - "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure OAuth consent screen:
     - Choose "External"
     - App name: "Digital Footprint Analyzer"
     - User support email: your email
     - Developer contact: your email
     - Save and continue (skip optional sections)
   - Back to "Create OAuth client ID":
     - Application type: "Desktop app"
     - Name: "Digital Footprint Analyzer"
     - Click "Create"
   
5. **Download Credentials:**
   - You'll see Client ID and Client Secret
   - Copy these values

### 3. Create .env File

Create a file named `.env` in the project root:

```bash
GOOGLE_CLIENT_ID=paste_your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=paste_your_client_secret_here

# Optional for Phase 1, required for Phase 3+
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Important:** Make sure there are no spaces around the `=` sign!

### 4. Run the Application

```bash
python -m src.main
```

Expected flow:
1. ✅ "Step 1: Authenticating with Gmail..."
2. 🌐 Browser opens automatically
3. 🔐 Sign in with your Google account
4. ✅ Grant permissions
5. 📧 App fetches your emails
6. 📊 Shows statistics and samples

### 5. Verify Success

You should see:
```
✅ Phase 1 Complete!
```

And a summary showing:
- Your authenticated email
- Number of emails fetched
- Sample email subjects
- Confirmation that credentials are stored

## What's Stored?

- **Token database**: `data/tokens.db` (SQLite)
- Contains: OAuth refresh tokens (encrypted by Google)
- **NO email content** is stored locally

## Next Run

On subsequent runs, the app will automatically use stored credentials - no need to authenticate again!

## Troubleshooting

### "Missing GOOGLE_CLIENT_ID"
- Check that `.env` file exists in project root
- Verify no typos in variable names
- Make sure `.env` is NOT named `.env.txt`

### Browser doesn't open
- Check the terminal - it shows a URL
- Copy and paste the URL into your browser manually

### "Invalid client"
- Double-check Client ID and Secret in `.env`
- Ensure you copied the complete values from Google Cloud

### "Access blocked"
- In OAuth consent screen, add your email as a test user
- Status should be "Testing" (not "In production")

### Permission denied errors
- Check Gmail API is enabled in Google Cloud Console
- Verify OAuth scopes include `gmail.readonly`

## Testing Different Accounts

Want to test with multiple Gmail accounts?

1. Run: `python -m src.main`
2. When prompted "Use existing credentials?", type `n`
3. Authenticate with a different account
4. The app stores credentials for all accounts

## What's Next?

After Phase 1 is working:
- **Phase 2**: Signal extraction (newsletters, communication style)
- **Phase 3**: Identity resolution (find LinkedIn/Twitter)
- **Phase 4**: Profile enrichment (scrape public profiles)
- **Phase 5**: Generate persona report

Each phase will be implemented incrementally.

## Need Help?

1. Check the main [README.md](README.md)
2. Review [documentation/prd.md](documentation/prd.md)
3. Open an issue with:
   - Error message (full text)
   - Steps you followed
   - Your Python version: `python --version`

---

**Ready to analyze your digital footprint! 🚀**

