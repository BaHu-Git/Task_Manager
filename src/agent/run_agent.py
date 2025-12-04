# src/core/run_agent.py
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

HOST = "http://127.0.0.1:5000/mcp"


async def run_agent(repo: str):
    async with streamablehttp_client(HOST) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            issues_result = await session.call_tool(
                "github_get_issues",
                {"repo": repo},
            )
            issues_json = issues_result.content[0].text
            issues = json.loads(issues_json)
            print(f"Pulled {len(issues)} issues")

            for issue in issues:
                issue_text = issue["title"] + "\n" + issue.get("body", "")
                print("\nISSUE:", issue["title"])

                breakdown_result = await session.call_tool(
                    "tasks_breakdown",
                    {"issue_text": issue_text},
                )
                tasks_json = breakdown_result.content[0].text
                print("Raw tasks_json:", tasks_json)   # <<< debug
                tasks = json.loads(tasks_json)
                print(f"Parsed {len(tasks)} tasks")

                schedule_result = await session.call_tool(
                    "tasks_schedule",
                    {"tasks_json": json.dumps(tasks)},
                )
                schedule_json = schedule_result.content[0].text
                print("Raw schedule_json:", schedule_json)  # <<< debug
                schedule = json.loads(schedule_json)
                print(f"Scheduled {len(schedule)} tasks")

                for t in schedule:
                    print("Scheduling event:", t["task"], t["start"], "→", t["end"])
                    await session.call_tool(
                        "calendar_create_event",
                        {
                            "summary": t["task"],
                            "start": t["start"],
                            "end": t["end"],
                        },
                    )

            print("Done: issues scheduled into calendar.")


if __name__ == "__main__":
    asyncio.run(run_agent("BaHu-Git/Task_Manager"))
