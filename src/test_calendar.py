from datetime import datetime
from src.agent.calendar_client import CalendarClient

def main():
    client = CalendarClient()

    event_id = client.create_event(
        summary="Test Event from agent",
        start_time=datetime.utcnow(),
        duration_minutes=30,
    )

    print("Created event with ID:", event_id)

if __name__ == "__main__":
    main()
