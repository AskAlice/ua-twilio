from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from halo import Halo

@Halo(text='Loading Calendar Service', spinner='dots')
def calendarClient():
    creds = None
    scopes = ['https://www.googleapis.com/auth/calendar']
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("credentials.json file not found for calendar integration. Please download it from the Google Cloud Console and save it in the root directory of this project.")
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("refreshing credentials")
            creds.refresh(Request())
        else:
            print("reading credentials from file")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes
            )
            print("running local server")
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        print("saving credentials")
        with open("token.json", "w") as token:
            token.write(creds.to_json())


    service = build("calendar", "v3", credentials=creds)
    return service
from datetime import datetime, timedelta
import pytz  # Make sure to install pytz

def createEvent(needsTesting, error=None):
    service = calendarClient()
    now = datetime.utcnow().replace(tzinfo=pytz.utc)  # Ensuring the 'now' is timezone-aware
    
    event_summary = "Get tested" if needsTesting else "No test needed" if not error else f"Error: {error}"

    # Adjust to cover the whole day in UTC
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events_list = events_result.get('items', [])

    # More robust check considering only the date part and summary
    existing_event = next((event for event in events_list if
                           event['summary'] == event_summary and
                           datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date'))).date() == now.date()), None)

    if existing_event:
        print("Event already exists today:", existing_event['htmlLink'])
        return

    timezone = 'UTC'  # Change this as needed
    event_time = now.astimezone().replace(hour=17,minute=30)  # Assuming you want to use the current date but a fixed time
    reminders = [] if not needsTesting else [
                {'method': 'email', 'minutes': 240},
                {'method': 'popup', 'minutes': 30},
                {'method': 'popup', 'minutes': 60},
                {'method': 'popup', 'minutes': 90},
                {'method': 'popup', 'minutes': 120},
            ]
    # Create a new event
    event = {
        'summary': event_summary,
        'location': os.getenv('TEST_LOCATION', 'Default Location'),
        'description': os.getenv('TEST_EVENT_DESCRIPTION', 'Please attend the testing session.'),
        'start': {
            'dateTime': event_time.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': (event_time + timedelta(hours=5)).isoformat(),
            'timeZone': timezone,
        },
        'reminders': {
            'useDefault': False,
            'overrides': reminders,
        },
    }

    # Insert the event
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print("Event created:", created_event['htmlLink'])
