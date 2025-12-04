# src/core/task_breakdown.py
import os
import json
import re
from jinja2 import Environment, FileSystemLoader

from .llm import LLMClient


class TaskBreakdown:
    def __init__(self):
        templates_path = os.path.join(
            os.path.dirname(__file__), "..", "templates"
        )
        self.env = Environment(loader=FileSystemLoader(templates_path))
        self.template = self.env.get_template("breakdown_prompt.j2")
        self.llm = LLMClient()

    def breakdown(self, issue_text: str):
        """Return a list of task dicts from an issue text."""
        prompt = self.template.render(issue=issue_text)
        raw = self.llm.run(prompt)

        cleaned = self._extract_json(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Last resort: try first [ ... ] slice
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start != -1 and end != -1:
                snippet = cleaned[start:end + 1]
                return json.loads(snippet)
            # If still failing, show raw output for debugging
            print("LLM output was not valid JSON:\n", raw)
            raise

    @staticmethod
    def _extract_json(text: str) -> str:
        """Strip code fences / extra text, keep JSON part."""
        t = text.strip()

        # Remove ```json ... ``` fences if present
        if t.startswith("```"):
            # drop opening fence
            t = re.sub(r"^```[a-zA-Z0-9_]*", "", t).strip()
            # drop trailing fence
            if "```" in t:
                t = t.split("```", 1)[0].strip()

        return t
