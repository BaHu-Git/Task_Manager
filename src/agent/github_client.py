import json
from typing import List, Dict
from urllib import request, error


class GitHubClient:
    def __init__(self, token: str, repo: str):
        if not token:
            raise ValueError("Missing GitHub token")
        if not repo:
            raise ValueError("Missing GitHub repo identifier")

        self.token = token
        self.repo = repo
        self.base_url = "https://api.github.com"

    def _build_request(self, path: str, query: str = "") -> request.Request:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{query}"

        req = request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        return req

    def _fetch_json(self, req: request.Request):
        try:
            with request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as http_err:
            detail = http_err.read().decode("utf-8")
            raise RuntimeError(f"GitHub API error ({http_err.code}): {detail}") from http_err
        except error.URLError as url_err:
            raise RuntimeError(f"Network error talking to GitHub: {url_err.reason}") from url_err

    def get_issues(self, state: str = "open") -> List[Dict[str, str]]:
        req = self._build_request(f"/repos/{self.repo}/issues", f"state={state}")
        issues = self._fetch_json(req)
        results = []
        for issue in issues:
            # GitHub returns pull requests in the same endpoint – skip them.
            if "pull_request" in issue:
                continue
            results.append(
                {
                    "title": issue.get("title", ""),
                    "body": issue.get("body") or "",
                    "number": issue.get("number"),
                }
            )
        return results

