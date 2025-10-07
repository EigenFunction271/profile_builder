"""Gmail API email fetching with batch requests for efficiency"""
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from datetime import datetime
import base64


class EmailFetcher:
    """Fetches emails from Gmail API with optimizations"""
    
    def __init__(self, credentials: Credentials):
        """Initialize email fetcher
        
        Args:
            credentials: Valid Gmail credentials
        """
        self.service = build('gmail', 'v1', credentials=credentials)
        self.user_id = 'me'
    
    def get_user_email(self) -> str:
        """Get the authenticated user's email address
        
        Returns:
            User's email address
        """
        try:
            profile = self.service.users().getProfile(userId=self.user_id).execute()
            return profile.get('emailAddress', 'unknown@gmail.com')
        except HttpError as e:
            print(f"Error getting user profile: {e}")
            return 'unknown@gmail.com'
    
    def fetch_recent_emails(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent emails using metadata format for efficiency
        
        Fetches both received emails and newsletters.
        Uses format='metadata' to reduce data transfer.
        
        Args:
            max_results: Maximum number of emails to fetch
        
        Returns:
            List of email dictionaries with metadata
        """
        try:
            # Search for emails (inbox messages)
            results = self.service.users().messages().list(
                userId=self.user_id,
                maxResults=max_results,
                q='in:inbox OR in:sent'  # Get both inbox and sent for comprehensive analysis
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Fetch full metadata for each message
            emails = []
            for message in messages:
                email_data = self._fetch_email_metadata(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def fetch_sent_emails(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch only sent emails for communication style analysis
        
        Args:
            max_results: Maximum number of sent emails to fetch
        
        Returns:
            List of sent email dictionaries
        """
        try:
            # Search for sent emails only
            results = self.service.users().messages().list(
                userId=self.user_id,
                maxResults=max_results,
                q='in:sent'
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Fetch full metadata for each message
            emails = []
            for message in messages:
                email_data = self._fetch_email_metadata(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as e:
            print(f"Error fetching sent emails: {e}")
            return []
    
    def _fetch_email_metadata(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Fetch metadata for a single email
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            Email metadata dictionary
        """
        try:
            message = self.service.users().messages().get(
                userId=self.user_id,
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date', 'List-Unsubscribe', 'Reply-To']
            ).execute()
            
            # Extract headers
            headers = {
                header['name'].lower(): header['value']
                for header in message.get('payload', {}).get('headers', [])
            }
            
            # Parse date
            date_str = headers.get('date', '')
            timestamp = self._parse_date(date_str)
            
            return {
                'id': message['id'],
                'thread_id': message.get('threadId'),
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'subject': headers.get('subject', ''),
                'date': date_str,
                'timestamp': timestamp,
                'snippet': message.get('snippet', ''),
                'list_unsubscribe': headers.get('list-unsubscribe', ''),
                'reply_to': headers.get('reply-to', ''),
                'labels': message.get('labelIds', [])
            }
            
        except HttpError as e:
            print(f"Error fetching message {message_id}: {e}")
            return None
    
    def fetch_email_body(self, message_id: str) -> Optional[str]:
        """Fetch full email body (only when needed)
        
        This is a separate method to avoid fetching body unnecessarily.
        Only use for sent emails where we need to analyze writing style.
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            Email body as plain text
        """
        try:
            message = self.service.users().messages().get(
                userId=self.user_id,
                id=message_id,
                format='full'
            ).execute()
            
            # Extract body from payload
            body = self._extract_body_from_payload(message.get('payload', {}))
            return body
            
        except HttpError as e:
            print(f"Error fetching message body {message_id}: {e}")
            return None
    
    def _extract_body_from_payload(self, payload: Dict) -> str:
        """Extract plain text body from message payload
        
        Args:
            payload: Message payload from Gmail API
        
        Returns:
            Plain text body
        """
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        else:
            # Simple message
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse email date string to datetime
        
        Args:
            date_str: Date string from email header
        
        Returns:
            Parsed datetime or None
        """
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return None
    
    def get_email_count(self) -> Dict[str, int]:
        """Get email count statistics
        
        Returns:
            Dictionary with email counts by category
        """
        try:
            profile = self.service.users().getProfile(userId=self.user_id).execute()
            
            # Get counts for different categories
            inbox_count = self._get_label_count('INBOX')
            sent_count = self._get_label_count('SENT')
            
            return {
                'total': profile.get('messagesTotal', 0),
                'threads': profile.get('threadsTotal', 0),
                'inbox': inbox_count,
                'sent': sent_count
            }
            
        except HttpError as e:
            print(f"Error getting email counts: {e}")
            return {'total': 0, 'threads': 0, 'inbox': 0, 'sent': 0}
    
    def _get_label_count(self, label_id: str) -> int:
        """Get message count for a specific label
        
        Args:
            label_id: Gmail label ID (e.g., 'INBOX', 'SENT')
        
        Returns:
            Message count
        """
        try:
            results = self.service.users().messages().list(
                userId=self.user_id,
                labelIds=[label_id],
                maxResults=1
            ).execute()
            return results.get('resultSizeEstimate', 0)
        except HttpError:
            return 0

