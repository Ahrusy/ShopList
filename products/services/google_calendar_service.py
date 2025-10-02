from django.conf import settings
from django.utils import timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
import json


class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""
    
    def __init__(self, user):
        self.user = user
        self.credentials = None
        self.service = None
        
        # Initialize credentials if user has Google Calendar token
        if self.user.google_calendar_token:
            try:
                token_data = json.loads(self.user.google_calendar_token)
                self.credentials = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes')
                )
                
                # Refresh token if needed
                if self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                
                # Build the service
                self.service = build('calendar', 'v3', credentials=self.credentials)
            except Exception as e:
                print(f"Error initializing Google Calendar service: {e}")
                self.credentials = None
                self.service = None
    
    def is_available(self):
        """Check if the service is properly initialized"""
        return self.service is not None
    
    def create_event(self, task):
        """Create a Google Calendar event for a task"""
        if not self.is_available():
            return None
            
        try:
            event = {
                'summary': task.title,
                'description': task.description or '',
                'start': {
                    'dateTime': task.due_date.isoformat() if task.due_date else timezone.now().isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': (task.due_date + timezone.timedelta(hours=1)).isoformat() if task.due_date else (timezone.now() + timezone.timedelta(hours=1)).isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return event.get('id')
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def update_event(self, task):
        """Update a Google Calendar event for a task"""
        if not self.is_available() or not task.google_calendar_event_id:
            return False
            
        try:
            event = self.service.events().get(calendarId='primary', eventId=task.google_calendar_event_id).execute()
            
            event['summary'] = task.title
            event['description'] = task.description or ''
            
            if task.due_date:
                event['start'] = {
                    'dateTime': task.due_date.isoformat(),
                    'timeZone': 'Europe/Moscow',
                }
                event['end'] = {
                    'dateTime': (task.due_date + timezone.timedelta(hours=1)).isoformat(),
                    'timeZone': 'Europe/Moscow',
                }
            
            updated_event = self.service.events().update(calendarId='primary', eventId=task.google_calendar_event_id, body=event).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
    
    def delete_event(self, task):
        """Delete a Google Calendar event for a task"""
        if not self.is_available() or not task.google_calendar_event_id:
            return False
            
        try:
            self.service.events().delete(calendarId='primary', eventId=task.google_calendar_event_id).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False