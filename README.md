# Digital Footprint Analyzer

A Python application that analyzes Gmail inboxes to create comprehensive digital persona reports. The system extracts behavioral signals from emails, resolves user identity across social platforms, enriches with public profile data, and generates insightful persona reports.

**Key Constraint**: Costs under $0.01 per profile through smart pre-processing and minimal LLM usage.

## Features

### Web Interface ✨ NEW
- **FastAPI Backend**: Modern async Python API
- **Beautiful Frontend**: Responsive HTML/CSS/JS with Tailwind
- **Real-time Progress**: Live updates during analysis
- **Easy Deployment**: One-click deploy to Render
- **Mobile Friendly**: Works on all devices

### Phase 1: Gmail OAuth + Email Fetching ✅
- Secure OAuth 2.0 authentication
- Efficient email fetching with metadata-only requests
- Automatic token refresh and storage
- Support for multiple Gmail accounts

### Phase 2: Signal Extraction ✅
- Newsletter identification and categorization (zero LLM cost)
- Communication style analysis (formality scoring, emoji detection)
- Professional context extraction (industry inference, domain analysis)
- Activity pattern detection (peak hours, thread analysis)

### Phase 3: Identity Resolution (Coming Soon)
- Name extraction from email
- LinkedIn/Twitter profile search via Exa
- AI-powered confidence scoring (Google Gemini)

### Phase 4: Profile Enrichment (Coming Soon)
- LinkedIn profile scraping via Apify
- Twitter profile scraping via Apify

### Phase 5: Report Generation (Coming Soon)
- Comprehensive persona reports
- Digital footprint scoring
- Markdown export

## Project Structure

```
digital-footprint-analyzer/
├── src/
│   ├── auth/                  # Gmail OAuth implementation
│   ├── email_analysis/        # Email fetching and signal extraction
│   ├── identity/              # Identity resolution
│   ├── enrichment/            # Profile enrichment
│   ├── report/                # Report generation
│   ├── models/                # Pydantic data models
│   └── utils/                 # Configuration and utilities
├── tests/                     # Test suite
├── data/                      # Local data storage (tokens)
├── reports/                   # Generated reports
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

## Setup

### Prerequisites
- Python 3.10 or higher
- Google Cloud account (for Gmail API)
- API keys for Claude, Exa, and Apify (for later phases)

### 1. Clone Repository

```bash
git clone <repository-url>
cd digital-footprint-analyzer
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Name it (e.g., "Digital Footprint Analyzer")
   - Click "Create"
5. Note your **Client ID** and **Client Secret**

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Gmail OAuth
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

# For later phases (optional for now)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
EXA_API_KEY=your_exa_api_key
APIFY_API_TOKEN=apify_api_your_token

# Optional
DATABASE_PATH=./data/tokens.db
```

### 6. Run Phase 1

```bash
python -m src.main
```

On first run:
1. Your browser will open for Gmail authorization
2. Sign in and grant permissions
3. The app will fetch and display your email statistics
4. Credentials are securely stored for future use

## Usage

### Web Interface (Recommended)

**Local Development:**
```bash
# Start the web server
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Open browser
# Visit: http://localhost:8000
```

**Deploy to Render:**
See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for complete guide.

### Command Line Interface

```bash
# Run the CLI application
python -m src.main
```

The Phase 1 CLI will:
- Authenticate with Gmail via OAuth
- Fetch last 100 emails (metadata only)
- Fetch last 50 sent emails
- Display email statistics and samples
- Store credentials for future use

### Using Stored Credentials

After first authentication, the app will automatically use stored credentials. To re-authenticate:
1. Delete the token database: `rm data/tokens.db`
2. Run the app again: `python -m src.main`

## Development

### Project Phases

#### ✅ Phase 1: Gmail OAuth + Email Fetching (Complete)
- OAuth 2.0 authentication flow
- Email fetching with Gmail API
- Token storage and refresh

#### ✅ Phase 2: Signal Extraction (Complete)
- Newsletter detection and categorization
- Communication style analysis (formality, emoji usage)
- Professional context extraction (industry, contacts)
- Activity patterns (peak hours, response rates)

#### 🚧 Phase 3: Identity Resolution (Next)
- Name extraction from emails
- Social profile search (Exa)
- AI-powered confidence scoring (Gemini)

#### 📋 Phase 3: Identity Resolution
- Name extraction
- Social profile search (Exa)
- Confidence scoring (Claude)

#### 📋 Phase 4: Profile Enrichment
- LinkedIn scraping (Apify)
- Twitter scraping (Apify)

#### 📋 Phase 5: Report Generation
- Persona report creation
- Markdown export

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Code Quality

The project follows these standards:
- Type hints everywhere
- Docstrings for all public functions
- Pydantic for data validation
- Keep functions under 50 lines
- DRY principle

## Cost Optimization

The application is designed to minimize costs:

| Phase | LLM Usage | Cost per Profile | Status |
|-------|-----------|------------------|--------|
| 1. Email Fetching | None | $0.00 | ✅ Complete |
| 2. Signal Extraction | None | $0.00 | ✅ Complete |
| 3. Identity Resolution | Minimal (Gemini Flash) | ~$0.001 | 🔜 Next |
| 4. Profile Enrichment | None (Apify credits) | ~$0.003 | 📋 Planned |
| 5. Report Generation | Single call (Gemini Flash 2.0) | ~$0.002 | 📋 Planned |
| **Total** | | **<$0.01** | |

## Security & Privacy

- OAuth tokens stored locally in SQLite
- No email content uploaded to external services
- Only metadata used for signal extraction
- User consent required for all operations
- Credentials can be deleted at any time

## API Keys Required

### Phase 1 (Current)
- ✅ Google OAuth (Client ID + Secret) - **Free**

### Future Phases
- 🔜 Google Gemini API - [Get key](https://makersuite.google.com/app/apikey)
- 🔜 Exa API - [Get key](https://exa.ai/)
- 🔜 Apify API - [Get key](https://apify.com/)

## Troubleshooting

### Authentication Issues

**Problem**: "Missing GOOGLE_CLIENT_ID"
- **Solution**: Create `.env` file with your Google OAuth credentials

**Problem**: "Authentication failed"
- **Solution**: Verify OAuth credentials in Google Cloud Console
- Ensure Gmail API is enabled
- Check that redirect URIs include `http://localhost`

### Email Fetching Issues

**Problem**: "Error fetching emails"
- **Solution**: Check Gmail API quota in Google Cloud Console
- Verify OAuth scopes include `gmail.readonly`

**Problem**: "No emails returned"
- **Solution**: Check that you have emails in your inbox
- Try increasing `max_results` parameter

### Token Storage Issues

**Problem**: "Failed to load credentials"
- **Solution**: Delete `data/tokens.db` and re-authenticate
- Check database file permissions

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 Setup Guide](https://developers.google.com/identity/protocols/oauth2)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Exa API Docs](https://docs.exa.ai/)
- [Apify API Docs](https://docs.apify.com/)

## Roadmap

- [x] Phase 1: Gmail OAuth + Email Fetching
- [x] Phase 2: Signal Extraction
- [x] Web UI (FastAPI + Tailwind)
- [ ] Phase 3: Identity Resolution
- [ ] Phase 4: Profile Enrichment
- [ ] Phase 5: Report Generation
- [ ] Batch processing
- [ ] Historical tracking
- [ ] PDF export
- [ ] Privacy dashboard

## Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing GitHub issues
3. Create a new issue with detailed information

---

**Built with ❤️ for digital privacy awareness and persona analysis**

