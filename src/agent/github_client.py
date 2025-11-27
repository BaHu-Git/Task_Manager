from github import Github

class GitHubClient:
    def __init__(self, token: str, repo: str):
        self.client = Github(token)
        self.repo = self.client.get_repo(repo)

    def get_issues(self, state="open"):
        issues = self.repo.get_issues(state=state)
        return [
            {
                "title": issue.title,
                "body": issue.body if issue.body else "",
                "number": issue.number
            }
            for issue in issues
        ]
