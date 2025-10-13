import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']
ASA_CALENDAR = "d3b6eb598f0111b1330b8ac24b471c133808d236292b8835fdb432c4f7dd087a@group.calendar.google.com"
service = None

creds = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json")

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

try:
    service = build("calendar", "v3", credentials=creds) if not service else None

    currentTime = dt.datetime.now(tz=dt.timezone.utc).isoformat()

    event_result = service.events().list(calendarId="d3b6eb598f0111b1330b8ac24b471c133808d236292b8835fdb432c4f7dd087a@group.calendar.google.com", maxResults=3, timeMin=currentTime, orderBy="startTime", singleEvents=True, timeZone='UTC').execute()
    events = event_result.get("items", [])

    if events:
        print("Success connecting to Google Calendar API; ready to run.")

    
except HttpError as e:
    print(f"An error occurred: {e}")


def get_next_event():
    now = dt.datetime.now(tz=dt.timezone.utc)

    upcoming_events = service.events().list(
        calendarId = ASA_CALENDAR,
        maxResults = 5,
        timeMin = now.isoformat(),
        singleEvents = True,
        orderBy = "startTime",
        timeZone = 'UTC'
    ).execute()

    events = upcoming_events.get("items", [])

    if not events:
        print("No upcoming events found")
        return
    
    for event in events:
        event_name = event['summary']
        event_name_lower = event_name.lower()

        if "week" not in event_name_lower and "meeting" not in event_name_lower and 'equipment' not in event_name_lower:
            start = dt.datetime.fromisoformat(event["start"].get("dateTime", event["start"].get("date")))

            delta = start - now
            if ("birthday" in event_name_lower and start.day == now.day) or 0 < delta.days <= 4:
                return event_name, delta.days


if __name__ == '__main__':
    print(get_next_event())