# Local Testing Guide

Guide to running the Digital Footprint Analyzer web application locally before deploying to Render.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```bash
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GEMINI_API_KEY=your_gemini_api_key  # Optional for Phase 1
DATABASE_PATH=./data/tokens.db
```

### 3. Run the Server

```bash
# Option 1: Using uvicorn directly
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python -m src.api.app
```

### 4. Open Browser

Visit: http://localhost:8000

## 📋 Testing Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Config Check
```bash
curl http://localhost:8000/api/config/check
```

### List Accounts
```bash
curl http://localhost:8000/api/accounts
```

### Start Analysis
```bash
curl -X POST http://localhost:8000/api/analysis/start \
  -H "Content-Type: application/json" \
  -d "{}"
```

## 🔧 Development Mode

### Enable Auto-Reload

```bash
uvicorn src.api.app:app --reload
```

Changes to Python files will auto-restart the server.

### Debug Mode

Add to `src/api/app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### CORS for Frontend Development

If developing frontend separately:
```python
# src/api/app.py
allow_origins=["http://localhost:3000", "http://localhost:8000"]
```

## 🧪 Testing Flow

### 1. Test Health Check
```bash
curl http://localhost:8000/health
```

### 2. Test Configuration
```bash
curl http://localhost:8000/api/config/check
```

Should return:
```json
{
  "configured": true,
  "missing_vars": [],
  "features_available": {...}
}
```

### 3. Test Frontend
1. Open http://localhost:8000
2. Click "Start Analysis"
3. Authenticate with Gmail
4. Verify results display

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### OAuth Redirect Error

For local testing, ensure Google OAuth has:
- Authorized redirect URI: `http://localhost:8000`

### Database Locked

```bash
# Remove lock
rm data/tokens.db-lock

# Or use new database
DATABASE_PATH=./data/tokens_test.db
```

## 📊 Performance Testing

### Load Test with Apache Bench

```bash
# Install
# Mac: brew install httpd
# Ubuntu: apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health
```

### Monitor Resource Usage

```bash
# Check memory usage
ps aux | grep uvicorn

# Check CPU usage
top -p $(pgrep uvicorn)
```

## 🎨 Frontend Development

### Live Reload

Use browser extensions:
- **Chrome**: Live Server
- **Firefox**: Live Reload

Or serve static files:
```bash
cd frontend
python -m http.server 3000
```

### Test Static Files

```bash
curl http://localhost:8000/static/js/app.js
```

## 🔐 Testing OAuth Flow

### 1. Setup Test Account

Use a test Gmail account (don't use personal)

### 2. Clear Stored Tokens

```bash
rm data/tokens.db
```

### 3. Test Full Flow

1. Visit http://localhost:8000
2. Click "Start Analysis"
3. Authenticate
4. Verify token stored:
   ```bash
   sqlite3 data/tokens.db "SELECT email FROM tokens;"
   ```

### 4. Test Stored Account

1. Restart server
2. Click "Use Stored Account"
3. Should work without re-authentication

## 📝 API Documentation

### Interactive Docs

Visit: http://localhost:8000/docs

FastAPI auto-generates:
- API documentation
- Try-it-out interface
- Schema definitions

### Alternative Docs

Visit: http://localhost:8000/redoc

## 🔄 Testing Updates

### Test After Changes

```bash
# 1. Stop server (Ctrl+C)
# 2. Make changes
# 3. Restart server
uvicorn src.api.app:app --reload

# Or use --reload for auto-restart
```

### Test Database Migrations

```bash
# Backup
cp data/tokens.db data/tokens.db.backup

# Test changes
# ...

# Restore if needed
cp data/tokens.db.backup data/tokens.db
```

## 🚀 Pre-Deployment Checklist

Before deploying to Render:

- [ ] All endpoints work locally
- [ ] OAuth flow completes successfully
- [ ] Frontend displays correctly
- [ ] No console errors
- [ ] Database persists tokens
- [ ] Environment variables work
- [ ] CORS configured correctly
- [ ] Error handling works
- [ ] Mobile responsive (test in browser dev tools)

## 📱 Mobile Testing

### Test Responsive Design

Chrome DevTools:
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test different devices:
   - iPhone 12
   - iPad
   - Galaxy S20

### Test Touch Events

Use Chrome DevTools touch emulation

## 🎯 What to Test

### Phase 1 Features

- [ ] Health check endpoint
- [ ] Config validation
- [ ] OAuth authentication
- [ ] Email fetching (100 recent)
- [ ] Sent email fetching (50)
- [ ] Statistics display
- [ ] Sample emails display
- [ ] Stored accounts list
- [ ] Progress tracking
- [ ] Error handling

### UI/UX

- [ ] Loading states
- [ ] Progress bar updates
- [ ] Error messages
- [ ] Success messages
- [ ] Button states
- [ ] Modal interactions
- [ ] Responsive layout
- [ ] Gradient animation
- [ ] Font loading

## 🔍 Debugging Tips

### Check Logs

```bash
# Terminal shows all requests
uvicorn src.api.app:app --reload --log-level debug
```

### Python Debugger

Add breakpoint:
```python
import pdb; pdb.set_trace()
```

### Browser Console

Open browser console (F12) to see:
- API requests
- JavaScript errors
- Network timing

### Network Tab

Monitor API calls:
1. Open DevTools → Network
2. Filter by XHR
3. Check request/response

## 📈 Performance Optimization

### Check Startup Time

```bash
time uvicorn src.api.app:app
```

### Profile Code

```python
import cProfile
cProfile.run('function_to_profile()')
```

### Monitor Memory

```python
import tracemalloc
tracemalloc.start()
# ... code ...
print(tracemalloc.get_traced_memory())
```

## ✅ Ready for Deployment

Once all tests pass locally:
1. Commit changes
2. Push to GitHub
3. Follow [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

---

**Happy Testing! 🧪**

