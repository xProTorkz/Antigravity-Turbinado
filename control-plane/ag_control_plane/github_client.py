import base64
import json
import subprocess
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or self._get_token_from_keychain()
        if not self.token:
            raise RuntimeError("Não foi possível obter o token do GitHub pelo macOS Keychain.")

    @staticmethod
    def _get_token_from_keychain() -> Optional[str]:
        try:
            proc = subprocess.run(
                ["git", "credential-osxkeychain", "get"],
                input="protocol=https\nhost=github.com\n",
                text=True,
                capture_output=True,
                check=False
            )
            for line in proc.stdout.splitlines():
                if line.startswith("password="):
                    return line.split("=", 1)[1].strip()
        except Exception:
            pass
        return None

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"https://api.github.com{path}" if path.startswith("/") else path
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Antigravity-Control-Plane/1.0"
        }
        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        import ssl
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                status = resp.getcode()
                raw = resp.read()
                if not raw:
                    return None
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API Error {e.code} on {method} {url}: {err_msg}") from e

    def get_user(self) -> Dict[str, Any]:
        return self._request("GET", "/user")

    def get_file_text(
        self,
        repo: str,
        path: str,
        ref: str = "main"
    ) -> str:
        """Lê um arquivo UTF-8 diretamente do repositório canônico via GitHub API."""
        payload = self._request("GET", f"/repos/{repo}/contents/{path}?ref={ref}")
        if not isinstance(payload, dict):
            raise RuntimeError(f"Resposta inválida ao ler {repo}/{path}@{ref}.")
        if payload.get("encoding") != "base64" or not payload.get("content"):
            raise RuntimeError(f"Conteúdo de {repo}/{path}@{ref} não veio em base64.")
        try:
            raw = base64.b64decode(payload["content"])
            return raw.decode("utf-8")
        except Exception as exc:
            raise RuntimeError(f"Falha ao decodificar {repo}/{path}@{ref}: {exc}") from exc

    def list_queued_issues(self, repo: str = "xProTorkz/project-blueprint") -> List[Dict[str, Any]]:
        return self._request("GET", f"/repos/{repo}/issues?labels=ag:queued&state=open") or []

    def list_issues_by_label(self, repo: str = "xProTorkz/project-blueprint", label: str = "ag:working") -> List[Dict[str, Any]]:
        return self._request("GET", f"/repos/{repo}/issues?labels={label}&state=open") or []

    def get_issue(self, repo: str, issue_number: int) -> Dict[str, Any]:
        return self._request("GET", f"/repos/{repo}/issues/{issue_number}")

    def add_comment(self, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
        return self._request("POST", f"/repos/{repo}/issues/{issue_number}/comments", {"body": body})

    def get_issue_comments(self, repo: str, issue_number: int) -> List[Dict[str, Any]]:
        return self._request("GET", f"/repos/{repo}/issues/{issue_number}/comments") or []

    def set_issue_labels(self, repo: str, issue_number: int, labels: List[str]) -> List[Dict[str, Any]]:
        return self._request("PUT", f"/repos/{repo}/issues/{issue_number}/labels", {"labels": labels})

    def update_issue_labels(
        self,
        repo: str,
        issue_number: int,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None
    ) -> List[str]:
        issue = self.get_issue(repo, issue_number)
        current = {l["name"] for l in issue.get("labels", [])}
        if remove_labels:
            for rl in remove_labels:
                current.discard(rl)
        if add_labels:
            for al in add_labels:
                current.add(al)
        final_list = sorted(list(current))
        self.set_issue_labels(repo, issue_number, final_list)
        return final_list

    def create_issue(
        self,
        repo: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "title": title,
            "body": body,
        }
        if labels:
            payload["labels"] = labels
        return self._request("POST", f"/repos/{repo}/issues", payload)

    def close_issue(self, repo: str, issue_number: int) -> Dict[str, Any]:
        return self._request("PATCH", f"/repos/{repo}/issues/{issue_number}", {"state": "closed"})

    def update_issue(
        self,
        repo: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if state is not None:
            payload["state"] = state
        return self._request("PATCH", f"/repos/{repo}/issues/{issue_number}", payload)

    def list_open_issues(self, repo: str) -> List[Dict[str, Any]]:
        return self._request("GET", f"/repos/{repo}/issues?state=open") or []

    def get_tree(self, repo: str, tree_sha: str = "main", recursive: bool = True) -> Dict[str, Any]:
        rec_param = "?recursive=1" if recursive else ""
        return self._request("GET", f"/repos/{repo}/git/trees/{tree_sha}{rec_param}") or {}

    def search_code(self, repo: str, query: str) -> List[Dict[str, Any]]:
        import urllib.parse
        q = urllib.parse.quote(f"{query} repo:{repo}")
        res = self._request("GET", f"/search/code?q={q}") or {}
        return res.get("items", [])
