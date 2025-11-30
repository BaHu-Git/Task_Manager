import os
from agent.agent import Agent

def main():
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO")  # e.g. "username/my-fork"
    agent = Agent(token, repo)
    agent.run()

if __name__ == "__main__":
    main()



