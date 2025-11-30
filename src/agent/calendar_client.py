from __future__ import print_function
import datetime

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "Google Calendar support requires the google-auth, "
        "google-auth-oauthlib, and google-api-python-client packages. "
        "Install them with "
        "`pip install google-auth google-auth-oauthlib "
        "google-api-python-client`."
    ) from exc

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class CalendarClient:
    def __init__(self):
        creds = None

        # 1) If token.json exists, load it
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except Exception:
            pass

        # 2) If no valid credentials, start OAuth flow
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

            # Save token.json
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        self.service = build("calendar", "v3", credentials=creds)

    def create_event(self, summary, start_time, duration_minutes):
        start_dt = start_time.isoformat()
        end_dt = (start_time + datetime.timedelta(minutes=duration_minutes)).isoformat()

        event = {
            "summary": summary,
            "start": {"dateTime": start_dt, "timeZone": "UTC"},
            "end": {"dateTime": end_dt, "timeZone": "UTC"},
        }

        created = self.service.events().insert(
            calendarId="primary", body=event
        ).execute()

        return created.get("id")

if __name__ == "__main__":
    print("Running CalendarClient test...")
    client = CalendarClient()
    print("OAuth successful. Calendar client created.")
