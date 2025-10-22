# Security Configuration Guide

This document explains the security features implemented in the Digital Footprint Analyzer and how to configure them properly.

## 🔒 Security Features

### 1. Token Encryption
All OAuth tokens are encrypted at rest using Fernet encryption (AES-128).

**How it works:**
- Tokens are encrypted before being stored in the database
- A secret key is derived from your `SECRET_KEY` environment variable
- Uses PBKDF2 with 100,000 iterations for key derivation
- Backward compatible with existing unencrypted tokens

**Configuration:**
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
SECRET_KEY=your_generated_key_here
```

**Important:**
- ⚠️ If you lose your SECRET_KEY, you cannot decrypt existing tokens
- ✅ Store your SECRET_KEY securely (use environment variables, never commit to git)
- ✅ Use the same SECRET_KEY across deployments to maintain access to tokens

---

### 2. HMAC State Validation
OAuth state parameters are cryptographically signed using HMAC-SHA256.

**How it works:**
- Each OAuth state includes an HMAC signature
- Prevents CSRF attacks on the OAuth flow
- State tokens are validated on callback

**Configuration:**
```bash
# Generate a session secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
SESSION_SECRET=your_generated_key_here
```

**Benefits:**
- ✅ Prevents state fixation attacks
- ✅ Validates that callbacks match initiated requests
- ✅ Constant-time comparison prevents timing attacks

---

### 3. CORS Protection
Strict Cross-Origin Resource Sharing configuration.

**Configuration:**
```bash
# Local development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Production (Render)
ALLOWED_ORIGINS=https://your-app-name.onrender.com
```

**Security measures:**
- ❌ No wildcard origins allowed
- ✅ Explicit whitelist required for production
- ✅ Credentials enabled only for whitelisted origins
- ⚠️ Application warns if ALLOWED_ORIGINS is not set

---

### 4. Environment Validation
Critical configuration is validated on application startup.

**What's validated:**
- Required environment variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, etc.)
- CORS configuration
- Encryption keys

**Benefits:**
- ✅ Fails fast if misconfigured
- ✅ Clear error messages
- ✅ Prevents runtime surprises

---

### 5. CSRF Protection (Ready for Implementation)
CSRF token generation and validation utilities are available but not yet enforced on all endpoints.

**Configuration:**
```bash
# Generate a CSRF secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
CSRF_SECRET=your_generated_key_here
```

**Implementation:**
```python
from src.utils.security import get_csrf_protection

csrf = get_csrf_protection()
token = csrf.generate_token(session_id)
is_valid = csrf.validate_token(token, session_id)
```

---

## 🚀 Production Deployment Checklist

### Required Environment Variables

```bash
# OAuth
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret

# Gemini API
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# Database (Supabase)
DATABASE_URL=postgresql://postgres.xxx:password@host:5432/postgres

# CORS & OAuth Redirect
ALLOWED_ORIGINS=https://your-app.onrender.com
OAUTH_REDIRECT_URI=https://your-app.onrender.com/oauth2callback

# Security Keys (CRITICAL)
SECRET_KEY=<generate with secrets.token_urlsafe(32)>
SESSION_SECRET=<generate with secrets.token_urlsafe(32)>
CSRF_SECRET=<generate with secrets.token_urlsafe(32)>
```

### Generate All Secrets at Once

```bash
python -c "
import secrets
print('SECRET_KEY=' + secrets.token_urlsafe(32))
print('SESSION_SECRET=' + secrets.token_urlsafe(32))
print('CSRF_SECRET=' + secrets.token_urlsafe(32))
"
```

Copy the output and add to your environment variables.

---

## 🔐 Best Practices

### For Development

1. **Use .env file** for local secrets (never commit)
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

2. **Generate development secrets** (can be ephemeral)
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Test with production-like configuration**
   - Set ALLOWED_ORIGINS to test CORS
   - Test OAuth flow with HMAC validation

### For Production

1. **Use environment variables** (Render, Heroku, etc.)
   - Never hardcode secrets in code
   - Use platform's secret management

2. **Generate strong production secrets**
   - Use cryptographically secure random values
   - Different keys for each environment
   - Store securely (password manager, etc.)

3. **Enable encryption** (default: enabled)
   - Always set SECRET_KEY in production
   - Use same key across instances/deployments

4. **Monitor logs on startup**
   ```
   ✅ Environment validation complete
   ⚠️  WARNING: Messages indicate issues
   ```

5. **Regular security audits**
   - Review allowed origins
   - Rotate secrets periodically
   - Check database encryption status

---

## 🐛 Troubleshooting

### "Failed to decrypt token"
**Cause:** SECRET_KEY changed or not set  
**Fix:** Use the same SECRET_KEY, or re-authenticate users

### "OAuth state validation failed"
**Cause:** SESSION_SECRET mismatch or timing issue  
**Fix:** Check SESSION_SECRET is consistent across instances

### "CORS error in browser"
**Cause:** Frontend URL not in ALLOWED_ORIGINS  
**Fix:** Add frontend URL to ALLOWED_ORIGINS (comma-separated)

### "Missing required environment variables"
**Cause:** Critical config not set  
**Fix:** Check startup logs, set missing variables

---

## 📚 Additional Resources

- [OWASP Security Cheat Sheet](https://cheatsheetseries.owasp.org/)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [CORS Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Python Cryptography Documentation](https://cryptography.io/)

---

## 🤝 Contributing

Found a security issue? Please report responsibly:
1. **DO NOT** open a public GitHub issue
2. Email security concerns privately
3. Wait for acknowledgment before disclosure

---

**Last Updated:** 2024
**Security Version:** 1.0

