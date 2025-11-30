import os
from dotenv import load_dotenv
from src.agent.simple_agent import SimpleAgent

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "BaHu-Git/Task_Manager"

def main():
    agent = SimpleAgent(TOKEN, REPO)
    agent.run()

if __name__ == "__main__":
    main()
