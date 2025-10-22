"""Token storage using SQLite for secure credential persistence"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class TokenStorage:
    """Manages OAuth token storage in SQLite database with encryption"""
    
    def __init__(self, db_path: str = "./data/tokens.db", encrypt: bool = True):
        """Initialize token storage
        
        Args:
            db_path: Path to SQLite database file
            encrypt: Whether to encrypt tokens (default: True)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.encrypt = encrypt
        
        # Initialize encryption if enabled
        if self.encrypt:
            from .security import get_token_encryption
            self.encryption = get_token_encryption()
        
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    email TEXT NOT NULL,
                    token_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(service, email)
                )
            """)
            conn.commit()
    
    def save_token(self, service: str, email: str, token_data: Dict[str, Any]) -> None:
        """Save or update token for a service and email
        
        Args:
            service: Service name (e.g., 'gmail')
            email: User email address
            token_data: Token data as dictionary
        """
        # Encrypt token data if encryption is enabled
        if self.encrypt:
            token_string = self.encryption.encrypt_token_data(token_data)
        else:
            token_string = json.dumps(token_data)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tokens (service, email, token_data, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(service, email) 
                DO UPDATE SET 
                    token_data = excluded.token_data,
                    updated_at = excluded.updated_at
            """, (service, email, token_string, datetime.now()))
            conn.commit()
    
    def load_token(self, service: str, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load token for a service
        
        Args:
            service: Service name (e.g., 'gmail')
            email: Optional email to filter by. If None, returns most recent token.
        
        Returns:
            Token data as dictionary, or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            if email:
                cursor = conn.execute(
                    "SELECT token_data FROM tokens WHERE service = ? AND email = ?",
                    (service, email)
                )
            else:
                cursor = conn.execute(
                    "SELECT token_data FROM tokens WHERE service = ? ORDER BY updated_at DESC LIMIT 1",
                    (service,)
                )
            
            row = cursor.fetchone()
            if row:
                token_string = row[0]
                
                # Decrypt token data if encryption is enabled
                if self.encrypt:
                    try:
                        return self.encryption.decrypt_token_data(token_string)
                    except ValueError:
                        # Try parsing as plain JSON (for backward compatibility)
                        try:
                            return json.loads(token_string)
                        except json.JSONDecodeError:
                            print(f"⚠️  Failed to decrypt/parse token for {service}")
                            return None
                else:
                    return json.loads(token_string)
            return None
    
    def delete_token(self, service: str, email: str) -> None:
        """Delete token for a service and email
        
        Args:
            service: Service name
            email: User email address
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM tokens WHERE service = ? AND email = ?",
                (service, email)
            )
            conn.commit()
    
    def list_stored_emails(self, service: str) -> list[str]:
        """List all emails with stored tokens for a service
        
        Args:
            service: Service name
        
        Returns:
            List of email addresses
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT email FROM tokens WHERE service = ? ORDER BY updated_at DESC",
                (service,)
            )
            return [row[0] for row in cursor.fetchall()]

