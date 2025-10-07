"""Token storage using SQLite for secure credential persistence"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class TokenStorage:
    """Manages OAuth token storage in SQLite database"""
    
    def __init__(self, db_path: str = "./data/tokens.db"):
        """Initialize token storage
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
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
        token_json = json.dumps(token_data)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tokens (service, email, token_data, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(service, email) 
                DO UPDATE SET 
                    token_data = excluded.token_data,
                    updated_at = excluded.updated_at
            """, (service, email, token_json, datetime.now()))
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
                return json.loads(row[0])
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

