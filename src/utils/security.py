"""Security utilities for encryption and token management"""
import os
import hmac
import hashlib
import secrets
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class TokenEncryption:
    """Handles encryption/decryption of OAuth tokens"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """Initialize encryption with secret key
        
        Args:
            secret_key: Secret key for encryption (from env var or generated)
        """
        self.secret_key = secret_key or os.getenv("SECRET_KEY")
        
        if not self.secret_key:
            # Generate a key for local development (warn user)
            print("⚠️  WARNING: No SECRET_KEY found. Using ephemeral key (not secure for production)")
            self.secret_key = Fernet.generate_key().decode()
        
        # Derive encryption key from secret
        self._cipher = self._get_cipher(self.secret_key)
    
    def _get_cipher(self, secret: str) -> Fernet:
        """Derive Fernet cipher from secret key
        
        Args:
            secret: Secret key string
            
        Returns:
            Fernet cipher instance
        """
        # Use PBKDF2 to derive a proper key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'profile_builder_salt',  # Fixed salt for deterministic key
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return Fernet(key)
    
    def encrypt_token_data(self, token_data: Dict[str, Any]) -> str:
        """Encrypt token data for storage
        
        Args:
            token_data: Token dictionary
            
        Returns:
            Encrypted token string
        """
        import json
        
        token_json = json.dumps(token_data)
        encrypted = self._cipher.encrypt(token_json.encode())
        return encrypted.decode()
    
    def decrypt_token_data(self, encrypted_token: str) -> Dict[str, Any]:
        """Decrypt stored token data
        
        Args:
            encrypted_token: Encrypted token string
            
        Returns:
            Decrypted token dictionary
            
        Raises:
            ValueError: If decryption fails
        """
        import json
        
        try:
            decrypted = self._cipher.decrypt(encrypted_token.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt token: {e}")


class StateValidator:
    """Validates OAuth state with HMAC"""
    
    def __init__(self, secret: Optional[str] = None):
        """Initialize state validator
        
        Args:
            secret: Secret for HMAC (from env var or generated)
        """
        self.secret = (secret or os.getenv("SESSION_SECRET") or secrets.token_urlsafe(32)).encode()
    
    def generate_state(self, session_id: str) -> str:
        """Generate cryptographically secure state token
        
        Args:
            session_id: Session identifier
            
        Returns:
            State token with HMAC signature
        """
        # Generate random state
        random_state = secrets.token_urlsafe(32)
        
        # Create HMAC signature
        message = f"{session_id}:{random_state}".encode()
        signature = hmac.new(self.secret, message, hashlib.sha256).hexdigest()
        
        # Return state:signature
        return f"{random_state}:{signature}"
    
    def validate_state(self, state: str, session_id: str) -> bool:
        """Validate state token HMAC
        
        Args:
            state: State token to validate
            session_id: Expected session ID
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if ':' not in state:
                return False
            
            random_state, signature = state.rsplit(':', 1)
            
            # Recompute HMAC
            message = f"{session_id}:{random_state}".encode()
            expected_signature = hmac.new(self.secret, message, hashlib.sha256).hexdigest()
            
            # Constant-time comparison
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False


class CSRFProtection:
    """CSRF token generation and validation"""
    
    def __init__(self, secret: Optional[str] = None):
        """Initialize CSRF protection
        
        Args:
            secret: Secret for token generation
        """
        self.secret = (secret or os.getenv("CSRF_SECRET") or secrets.token_urlsafe(32)).encode()
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            CSRF token
        """
        # Create HMAC of session ID with timestamp
        import time
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}".encode()
        signature = hmac.new(self.secret, message, hashlib.sha256).hexdigest()
        
        return f"{timestamp}:{signature}"
    
    def validate_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Validate CSRF token
        
        Args:
            token: CSRF token to validate
            session_id: Expected session ID
            max_age: Maximum age in seconds (default: 1 hour)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            import time
            
            if ':' not in token:
                return False
            
            timestamp_str, signature = token.rsplit(':', 1)
            timestamp = int(timestamp_str)
            
            # Check if token is too old
            if time.time() - timestamp > max_age:
                return False
            
            # Recompute HMAC
            message = f"{session_id}:{timestamp_str}".encode()
            expected_signature = hmac.new(self.secret, message, hashlib.sha256).hexdigest()
            
            # Constant-time comparison
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False


def generate_secret_key() -> str:
    """Generate a secure random secret key
    
    Returns:
        URL-safe secret key string
    """
    return secrets.token_urlsafe(32)


# Global instances (lazy-loaded)
_token_encryption: Optional[TokenEncryption] = None
_state_validator: Optional[StateValidator] = None
_csrf_protection: Optional[CSRFProtection] = None


def get_token_encryption() -> TokenEncryption:
    """Get global token encryption instance
    
    Returns:
        TokenEncryption instance
    """
    global _token_encryption
    if _token_encryption is None:
        _token_encryption = TokenEncryption()
    return _token_encryption


def get_state_validator() -> StateValidator:
    """Get global state validator instance
    
    Returns:
        StateValidator instance
    """
    global _state_validator
    if _state_validator is None:
        _state_validator = StateValidator()
    return _state_validator


def get_csrf_protection() -> CSRFProtection:
    """Get global CSRF protection instance
    
    Returns:
        CSRFProtection instance
    """
    global _csrf_protection
    if _csrf_protection is None:
        _csrf_protection = CSRFProtection()
    return _csrf_protection

