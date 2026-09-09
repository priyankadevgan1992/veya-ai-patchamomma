import os
import json
import datetime
from typing import List, Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")

class GoogleCalendarConnector:
    """
    Live Google Calendar Connector:
    Authenticates via OAuth 2.0 (supports Desktop app and Web Client with port 8080/fixed port or console prompt),
    reads live upcoming events, and creates focus/unwind blocks directly on the user's Google Calendar.
    """

    def __init__(self, prompt_if_missing: bool = False):
        self.creds = None
        self.service = None
        self.prompt_if_missing = prompt_if_missing
        self._authenticate()

    def _authenticate(self):
        if os.path.exists(TOKEN_PATH):
            try:
                self.creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = None
            
            if not self.creds and self.prompt_if_missing:
                if not os.path.exists(CREDENTIALS_PATH):
                    return

                # Read credentials file to see if it's "web" or "installed"
                with open(CREDENTIALS_PATH, "r") as f:
                    cred_data = json.load(f)

                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)

                # If the OAuth client type is "web", use fixed redirect uri on port 8080
                try:
                    # Attempt local server flow on port 8080 or random
                    self.creds = flow.run_local_server(port=8080, prompt="consent")
                except Exception as e:
                    print(f"Standard flow error, trying manual URL flow: {e}")
                    self.creds = flow.run_local_server(port=0)

                with open(TOKEN_PATH, 'w') as token_file:
                    token_file.write(self.creds.to_json())

        if self.creds and self.creds.valid:
            self.service = build('calendar', 'v3', credentials=self.creds)

    def is_connected(self) -> bool:
        return self.service is not None

    def fetch_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        if not self.service:
            return []

        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            items = events_result.get('items', [])
            formatted = []
            for item in items:
                start = item['start'].get('dateTime', item['start'].get('date'))
                end = item['end'].get('dateTime', item['end'].get('date'))
                formatted.append({
                    "id": item.get('id'),
                    "title": item.get('summary', 'Untitled Event'),
                    "start": start,
                    "end": end,
                    "status": item.get('status', 'confirmed'),
                    "attendees_count": len(item.get('attendees', [])),
                    "is_live_google_event": True
                })
            return formatted
        except Exception as error:
            print(f"An error occurred fetching events: {error}")
            return []

    def insert_calendar_block(self, title: str, start_iso: str, end_iso: str, description: str = "") -> Optional[Dict[str, Any]]:
        if not self.service:
            return None

        event_payload = {
            'summary': title,
            'description': f"{description}\n\n[Protected & Scheduled by VeyaAI Life Companion]",
            'start': {
                'dateTime': start_iso,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': 'Asia/Kolkata',
            },
            'colorId': '2'
        }

        try:
            created_event = self.service.events().insert(calendarId='primary', body=event_payload).execute()
            return {
                "id": created_event.get('id'),
                "link": created_event.get('htmlLink'),
                "title": title,
                "status": "CONFIRMED"
            }
        except Exception as error:
            print(f"An error occurred inserting event: {error}")
            return None

if __name__ == "__main__":
    print("Launching Google Calendar OAuth...")
    connector = GoogleCalendarConnector(prompt_if_missing=True)
    if connector.is_connected():
        print("Connected to Live Google Calendar successfully!")
        events = connector.fetch_upcoming_events(5)
        print(f"Upcoming {len(events)} events found:")
        for ev in events:
            print(f" - {ev['title']} ({ev['start']} to {ev['end']})")
    else:
        print("Could not connect to Live Google Calendar.")
