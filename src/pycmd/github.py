from __future__ import annotations

import httpx

from pycmd.ui import PycmdError

API = "https://api.github.com"


class GitHubError(PycmdError):
    def __init__(self, message: str, status: int = 0) -> None:
        super().__init__(f"GitHub: {message}")
        self.status = status


def _message(r: httpx.Response) -> str:
    try:
        body = r.json()
    except ValueError:
        return f"HTTP {r.status_code}"
    msg = body.get("message", f"HTTP {r.status_code}")
    details = [
        e["message"] for e in body.get("errors", []) if isinstance(e, dict) and e.get("message")
    ]
    return msg + (": " + "; ".join(details) if details else "")


class GitHub:
    def __init__(self, token: str) -> None:
        if not token:
            raise PycmdError(
                "No GitHub token configured.",
                hint="Run `pycmd setup git` or set the GITHUB_TOKEN environment variable.",
            )
        self._client = httpx.Client(
            base_url=API,
            timeout=20,
            follow_redirects=True,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "pycmd",
            },
        )

    def __enter__(self) -> GitHub:
        return self

    def __exit__(self, *_exc) -> None:
        self._client.close()

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            r = self._client.request(method, url, **kwargs)
        except httpx.HTTPError as e:
            raise PycmdError(f"Could not reach GitHub: {e}") from e
        if r.status_code >= 400:
            raise GitHubError(_message(r), r.status_code)
        return r

    def user(self) -> dict:
        return self._request("GET", "/user").json()

    def create_repo(self, name: str, private: bool) -> dict:
        return self._request("POST", "/user/repos", json={"name": name, "private": private}).json()

    def delete_repo(self, owner: str, name: str) -> None:
        self._request("DELETE", f"/repos/{owner}/{name}")

    def list_repos(self) -> list[dict]:
        repos: list[dict] = []
        page = 1
        while True:
            batch = self._request(
                "GET", "/user/repos",
                params={"per_page": 100, "page": page, "affiliation": "owner", "sort": "updated"},
            ).json()
            repos.extend(batch)
            if len(batch) < 100:
                return repos
            page += 1