from dotenv import load_dotenv
load_dotenv()

from src.agent.gemini_client import GeminiFlash

def main():
    gem = GeminiFlash()
    resp = gem.chat([
        {"role": "user", "content": "Say 'Gemini is working'."}
    ])
    print(resp.choices[0].message.content)

if __name__ == "__main__":
    main()
