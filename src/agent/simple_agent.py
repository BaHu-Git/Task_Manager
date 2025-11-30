import json
from datetime import datetime, timedelta

from src.agent.github_client import GitHubClient
from src.agent.calendar_client import CalendarClient
from src.agent.gemini_client import GeminiFlash


SYSTEM_PROMPT = """
Break the issue into small actionable tasks.
Each task must include:
- description (string)
- duration (integer minutes)
- depends_on (null or index of another task)

You MUST return ONLY valid JSON. No explanations.
Format example:

[
  {"description": "Task 1", "duration": 30, "depends_on": null},
  {"description": "Task 2", "duration": 20, "depends_on": 0}
]
"""


class SimpleAgent:
    def __init__(self, github_token, github_repo):
        self.github = GitHubClient(github_token, github_repo)
        self.calendar = CalendarClient()
        self.llm = GeminiFlash()

    def run(self):
        issues = self.github.get_issues()
        if not issues:
            print("No issues found.")
            return

        for issue in issues:
            print(f"\nProcessing issue: {issue['title']}")

            # --- 1) Break down with Gemini ---
            response = self.llm.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{issue['title']}\n\n{issue['body']}"}
            ])

            raw = response.choices[0].message.content
            print("Raw LLM output:", raw)   # Debug output

            # Parse JSON
            tasks = json.loads(raw)

            # --- 2) Simple scheduler with max 8 events ---
            start = datetime.utcnow()
            created_events = []
            max_events = 8

            for i, task in enumerate(tasks):
                if i >= max_events:
                    print(f"Reached max of {max_events} events for this issue. Skipping remaining tasks.")
                    break

                summary = task["description"]
                duration = task["duration"]

                print(f"Creating event: {summary} ({duration}m)")

                event_id = self.calendar.create_event(
                    summary=summary,
                    start_time=start,
                    duration_minutes=duration
                )

                created_events.append({
                    "summary": summary,
                    "duration": duration,
                    "start": start,
                    "event_id": event_id,
                })

                start += timedelta(minutes=duration)

            # --- 3) Summary report ---
            print("\nSummary of scheduled tasks:")
            for ev in created_events:
                print(
                    f"- {ev['summary']} ({ev['duration']} min) at {ev['start']} — ID: {ev['event_id']}"
                )
            print(f"Total events created: {len(created_events)}")
