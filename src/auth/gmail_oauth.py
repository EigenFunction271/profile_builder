"""Gmail OAuth 2.0 authentication implementation"""
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from ..utils.config import Config
from ..utils.storage import TokenStorage


class GmailAuthenticator:
    """Handles Gmail OAuth authentication flow"""
    
    def __init__(self, config: Config, storage: Optional[TokenStorage] = None):
        """Initialize authenticator
        
        Args:
            config: Application configuration
            storage: Token storage instance (creates new if None)
        """
        self.config = config
        self.storage = storage or TokenStorage(config.database_path)
        self.scopes = config.gmail_scopes
    
    def get_oauth_flow(self) -> InstalledAppFlow:
        """Initialize OAuth flow with correct scopes
        
        Returns:
            Configured OAuth flow
        """
        client_config = {
            "installed": {
                "client_id": self.config.google_client_id,
                "client_secret": self.config.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }
        
        return InstalledAppFlow.from_client_config(
            client_config,
            scopes=self.scopes
        )
    
    def authenticate_user(self) -> Credentials:
        """Run OAuth flow and save tokens
        
        Returns:
            Valid credentials
        
        Raises:
            Exception: If authentication fails
        """
        flow = self.get_oauth_flow()
        
        # Run local server for OAuth callback
        credentials = flow.run_local_server(
            port=0,
            authorization_prompt_message='Please visit this URL to authorize: {url}',
            success_message='Authentication successful! You can close this window.',
            open_browser=True
        )
        
        # Get user email to use as storage key
        user_email = self._get_user_email(credentials)
        
        # Save credentials
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        self.storage.save_token('gmail', user_email, token_data)
        
        return credentials
    
    def load_credentials(self, email: Optional[str] = None) -> Optional[Credentials]:
        """Load existing credentials from storage
        
        Args:
            email: Optional email to load credentials for
        
        Returns:
            Credentials if found and valid, None otherwise
        """
        token_data = self.storage.load_token('gmail', email)
        if not token_data:
            return None
        
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )
        
        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            credentials = self.refresh_token(credentials, email)
        
        return credentials if credentials.valid else None
    
    def refresh_token(self, credentials: Credentials, email: Optional[str] = None) -> Credentials:
        """Refresh expired token
        
        Args:
            credentials: Expired credentials
            email: Optional email for saving refreshed token
        
        Returns:
            Refreshed credentials
        """
        credentials.refresh(Request())
        
        # Save refreshed token
        if email:
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            self.storage.save_token('gmail', email, token_data)
        
        return credentials
    
    def _get_user_email(self, credentials: Credentials) -> str:
        """Get user's email address from credentials
        
        Args:
            credentials: Valid credentials
        
        Returns:
            User's email address
        """
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info.get('email', 'unknown@gmail.com')
    
    def get_stored_emails(self) -> list[str]:
        """Get list of emails with stored credentials
        
        Returns:
            List of email addresses
        """
        return self.storage.list_stored_emails('gmail')

