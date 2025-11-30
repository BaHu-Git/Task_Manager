import openai
from path.to.llm_backends import Gemini2p5Flash

SYSTEM_PROMPT = """
You are an assistant who breaks down GitHub issues into small actionable tasks.
For each task, estimate:
- description
- dependency (which task must come before)
- duration estimate in minutes
Produce a JSON list.
"""



class TaskBreakdown:
    def __init__(self):
        cfg = Gemini2p5Flash()          # ← Step 3 happens here
        self.backend = cfg.get_backend()

    def breakdown(self, issue):
        prompt = f"Issue: {issue['title']}\n{issue['body']}"
        response = self.backend(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message["content"]
