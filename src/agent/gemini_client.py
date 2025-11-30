import os
import time
from openai import Client

# Google’s OpenAI-compatible endpoint
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Rate limiter (simple)
class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.delay = 60 / calls_per_minute
        self.last_call = 0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_call = time.time()


class GeminiFlash:
    def __init__(self, model="gemini-2.5-flash", rpm=10):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment")

        self.client = Client(
            api_key=api_key,
            base_url=GEMINI_BASE_URL
        )
        self.model = model
        self.limiter = RateLimiter(rpm)

    def chat(self, messages):
        self.limiter.wait()
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
