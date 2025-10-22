# Quick Reference Card

Essential commands and URLs for the Digital Footprint Analyzer.

## 🚀 Local Development

```bash
# Start web server
uvicorn src.api.app:app --reload --port 8000

# Start CLI
python -m src.main

# Run tests
pytest tests/ -v

# Check lints
ruff check src/
```

## 🌐 URLs

| Service | URL |
|---------|-----|
| Local Frontend | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| Render Dashboard | https://dashboard.render.com |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Frontend |
| GET | `/health` | Health check |
| GET | `/api/config/check` | Validate config |
| POST | `/api/analysis/start` | Start analysis |
| GET | `/api/analysis/status/{id}` | Get status |
| GET | `/api/accounts` | List accounts |

## 🔐 Environment Variables

### Required (Phase 1)
```bash
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
DATABASE_PATH=./data/tokens.db  # Local
DATABASE_PATH=/var/data/tokens.db  # Render
```

### Optional (Phase 3+)
```bash
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-2.0-flash-exp
EXA_API_KEY=xxx
APIFY_API_TOKEN=xxx
```

## 🔧 Common Commands

### Local Testing
```bash
# Health check
curl http://localhost:8000/health

# Config check
curl http://localhost:8000/api/config/check

# List accounts
curl http://localhost:8000/api/accounts

# Start analysis
curl -X POST http://localhost:8000/api/analysis/start \
  -H "Content-Type: application/json" \
  -d "{}"
```

### Git Workflow
```bash
# Save changes
git add .
git commit -m "Description"
git push origin main

# Auto-deploys on Render!
```

### Database
```bash
# View tokens
sqlite3 data/tokens.db "SELECT * FROM tokens;"

# Clear tokens
rm data/tokens.db

# Backup
cp data/tokens.db data/tokens.db.backup
```

## 📊 Monitoring

### Render
- Logs: Dashboard → Your Service → Logs
- Metrics: Dashboard → Your Service → Metrics
- Events: Dashboard → Your Service → Events

### Local
```bash
# View logs
# Terminal running uvicorn shows all requests

# Check processes
ps aux | grep uvicorn

# Check port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | `kill -9 $(lsof -t -i:8000)` |
| Module not found | `pip install -r requirements.txt` |
| OAuth error | Check redirect URIs in Google Console |
| Database locked | `rm data/tokens.db-lock` |
| Service sleeping | Wait 30 sec for Render wakeup |

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| [README.md](README.md) | Project overview |
| [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) | Deploy to Render |
| [LOCAL_TESTING.md](LOCAL_TESTING.md) | Local development |
| [WEB_DEPLOYMENT_COMPLETE.md](WEB_DEPLOYMENT_COMPLETE.md) | Implementation summary |

## 🔗 External Resources

| Service | URL |
|---------|-----|
| Google Cloud Console | https://console.cloud.google.com |
| Google AI Studio | https://makersuite.google.com/app/apikey |
| Render Dashboard | https://dashboard.render.com |
| FastAPI Docs | https://fastapi.tiangolo.com |

## 💰 Costs

| Service | Cost |
|---------|------|
| Render Free Tier | $0/month (750 hours) |
| Render Starter | $7/month (always-on) |
| Gmail API | Free |
| Gemini Flash 2.0 | ~$0.003/profile |

## ✅ Quick Checklist

### First Time Setup
- [ ] Clone repo
- [ ] Create `.env` file
- [ ] Get Google OAuth credentials
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test locally: `uvicorn src.api.app:app --reload`
- [ ] Push to GitHub
- [ ] Deploy to Render

### Before Each Deploy
- [ ] Test locally
- [ ] Check no linter errors
- [ ] Update version/changelog
- [ ] Commit and push
- [ ] Verify deploy on Render

## 🎯 Phase Status

| Phase | Status | Cost |
|-------|--------|------|
| Phase 1: OAuth + Email | ✅ Complete | $0 |
| Phase 2: Signal Extraction | 📋 Pending | $0 |
| Phase 3: Identity Resolution | 📋 Pending | ~$0.001 |
| Phase 4: Profile Enrichment | 📋 Pending | ~$0.003 |
| Phase 5: Report Generation | 📋 Pending | ~$0.002 |

---

**Keep this handy! 📌**

