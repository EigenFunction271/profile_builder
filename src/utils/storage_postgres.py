"""Token storage using PostgreSQL (Supabase) for production deployment"""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime


class TokenStoragePostgres:
    """Manages OAuth token storage in PostgreSQL (Supabase) with encryption"""
    
    def __init__(self, database_url: Optional[str] = None, encrypt: bool = True):
        """Initialize token storage with PostgreSQL
        
        Args:
            database_url: PostgreSQL connection URL (from DATABASE_URL env var if not provided)
            encrypt: Whether to encrypt tokens (default: True)
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.encrypt = encrypt
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required for PostgreSQL storage")
        
        # Import psycopg2 here (only needed for production)
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            self.psycopg2 = psycopg2
            self.RealDictCursor = RealDictCursor
        except ImportError:
            raise ImportError(
                "psycopg2 is required for PostgreSQL storage. "
                "Install it with: pip install psycopg2-binary"
            )
        
        # Initialize encryption if enabled
        if self.encrypt:
            from .security import get_token_encryption
            self.encryption = get_token_encryption()
        
        self._init_db()
    
    def _get_connection(self):
        """Get database connection"""
        return self.psycopg2.connect(self.database_url)
    
    def _init_db(self) -> None:
        """Initialize database schema"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tokens (
                        id SERIAL PRIMARY KEY,
                        service TEXT NOT NULL,
                        email TEXT NOT NULL,
                        token_data JSONB NOT NULL,
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
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tokens (service, email, token_data, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (service, email) 
                    DO UPDATE SET 
                        token_data = EXCLUDED.token_data,
                        updated_at = EXCLUDED.updated_at
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
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=self.RealDictCursor) as cur:
                if email:
                    cur.execute(
                        "SELECT token_data FROM tokens WHERE service = %s AND email = %s",
                        (service, email)
                    )
                else:
                    cur.execute(
                        "SELECT token_data FROM tokens WHERE service = %s ORDER BY updated_at DESC LIMIT 1",
                        (service,)
                    )
                
                row = cur.fetchone()
                if row:
                    token_data = row['token_data']
                    
                    # Handle different storage formats
                    if isinstance(token_data, str):
                        # It's a string - could be encrypted or plain JSON
                        if self.encrypt:
                            try:
                                return self.encryption.decrypt_token_data(token_data)
                            except ValueError:
                                # Try parsing as plain JSON (backward compatibility)
                                try:
                                    return json.loads(token_data)
                                except json.JSONDecodeError:
                                    print(f"⚠️  Failed to decrypt/parse token for {service}")
                                    return None
                        else:
                            return json.loads(token_data)
                    else:
                        # It's already a dict (JSONB type)
                        return token_data
                return None
    
    def delete_token(self, service: str, email: str) -> None:
        """Delete token for a service and email
        
        Args:
            service: Service name
            email: User email address
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tokens WHERE service = %s AND email = %s",
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
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT email FROM tokens WHERE service = %s ORDER BY updated_at DESC",
                    (service,)
                )
                return [row[0] for row in cur.fetchall()]


# Auto-select storage based on environment
def get_token_storage(config=None):
    """Factory function to get appropriate token storage
    
    Uses PostgreSQL (Supabase) if DATABASE_URL is set, otherwise SQLite
    
    Args:
        config: Optional config object (for SQLite path)
    
    Returns:
        TokenStorage instance (either PostgreSQL or SQLite)
    """
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Production: Use PostgreSQL (Supabase)
        print("🗄️  Using PostgreSQL storage (Supabase)")
        return TokenStoragePostgres(database_url)
    else:
        # Local development: Use SQLite
        print("🗄️  Using SQLite storage (local)")
        from .storage import TokenStorage
        db_path = config.database_path if config else "./data/tokens.db"
        return TokenStorage(db_path)

