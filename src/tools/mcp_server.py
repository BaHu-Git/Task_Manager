# src/tools/mcp_server.py
import os
import sys
import json
from typing import List, Dict, Any

# Make `src` importable when running this file directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import requests
from mcp.server import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.core.task_breakdown import TaskBreakdown
from src.core.scheduler import Scheduler

# One MCP server with all tools
MCP = FastMCP(
    "task-manager-mcp",
    host="127.0.0.1",
    port=5000,
)

breaker = TaskBreakdown()
scheduler = Scheduler()


@MCP.tool()
def github_get_issues(repo: str) -> str:
    """
    Return all non-PR issues from a GitHub repo as JSON string.
    repo: 'owner/repo'
    """
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    resp = requests.get(
        f"https://api.github.com/repos/{repo}/issues",
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()

    issues = [
        {"title": i.get("title", ""), "body": i.get("body", "")}
        for i in resp.json()
        if "pull_request" not in i
    ]

    # Return as JSON string so tools stay simple
    return json.dumps(issues)


@MCP.tool()
def tasks_breakdown(issue_text: str) -> str:
    """
    Use Jinja + Gemini (LLMClient) to break an issue into tasks.
    Returns a JSON string list of tasks.
    """
    tasks = breaker.breakdown(issue_text)
    return json.dumps(tasks)


@MCP.tool()
def tasks_schedule(tasks_json: str) -> str:
    """
    Take a JSON string of tasks and return a scheduled list (also JSON string).
    """
    tasks: List[Dict[str, Any]] = json.loads(tasks_json)
    scheduled = scheduler.schedule(tasks)
    return json.dumps(scheduled)


@MCP.tool()
def calendar_create_event(summary: str, start: str, end: str) -> str:
    from googleapiclient.errors import HttpError

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    token_path = os.path.join(root, "token.json")

    creds = Credentials.from_authorized_user_file(token_path)
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": summary,
        "start": {
            "dateTime": start,
            "timeZone": "Europe/Zurich",
        },
        "end": {
            "dateTime": end,
            "timeZone": "Europe/Zurich",
        },
    }

    try:
        created = service.events().insert(calendarId="primary", body=event).execute()
        print("Created event:", created.get("summary"))
        print("Start:", created.get("start"))
        print("End:", created.get("end"))
        print("Link:", created.get("htmlLink"))
        return "ok"
    except HttpError as e:
        print("Calendar API error:", e)
        return f"error: {e}"

if __name__ == "__main__":
    # HTTP MCP server on http://127.0.0.1:5000/mcp
    MCP.run(transport="streamable-http", mount_path="/mcp")
