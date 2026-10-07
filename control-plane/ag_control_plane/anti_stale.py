import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class AntiStaleStatus:
    APPLY = "APPLY"
    RECONCILE = "RECONCILE"
    NOOP = "NOOP"
    BLOCKED = "BLOCKED"

class AntiStaleChecker:
    @staticmethod
    def get_current_head(workspace_path: Path) -> Optional[str]:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(workspace_path),
                capture_output=True,
                text=True,
                check=True
            )
            return res.stdout.strip()
        except Exception:
            return None

    @classmethod
    def evaluate(
        cls,
        workspace_path: Path,
        baseline_sha: Optional[str],
        allowed_scope: Optional[List[str]] = None,
        task_title: str = "",
        task_body: str = ""
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Retorna:
          (status, rationale, details_dict)
          status: APPLY | RECONCILE | NOOP | BLOCKED
        """
        head_sha = cls.get_current_head(workspace_path)
        if not head_sha:
            return (
                AntiStaleStatus.APPLY,
                "Repositório local sem commits anteriores ou git HEAD inacessível; prosseguindo com APPLY.",
                {"baseline_sha": baseline_sha, "head_sha": None, "commits_ahead": 0}
            )

        if not baseline_sha or baseline_sha == head_sha:
            return (
                AntiStaleStatus.APPLY,
                f"HEAD atual ({head_sha[:8]}) coincide com o baseline_sha informado ou nenhum baseline foi exigido.",
                {"baseline_sha": baseline_sha, "head_sha": head_sha, "commits_ahead": 0}
            )

        # Check if baseline_sha exists in history
        check_rev = subprocess.run(
            ["git", "cat-file", "-t", baseline_sha],
            cwd=str(workspace_path),
            capture_output=True,
            text=True
        )
        if check_rev.returncode != 0:
            # baseline_sha is unknown in local repo
            return (
                AntiStaleStatus.RECONCILE,
                f"baseline_sha ({baseline_sha[:8]}) não encontrado no histórico local; projeto avançou de base desconhecida. Reconciliando com HEAD ({head_sha[:8]}).",
                {"baseline_sha": baseline_sha, "head_sha": head_sha, "commits_ahead": -1}
            )

        # Count commits ahead: git rev-list --count baseline_sha..HEAD
        commits_ahead_proc = subprocess.run(
            ["git", "rev-list", "--count", f"{baseline_sha}..{head_sha}"],
            cwd=str(workspace_path),
            capture_output=True,
            text=True
        )
        commits_ahead = int(commits_ahead_proc.stdout.strip()) if commits_ahead_proc.returncode == 0 else 0

        if commits_ahead == 0:
            return (
                AntiStaleStatus.APPLY,
                "Nenhum commit novo detectado após o baseline_sha.",
                {"baseline_sha": baseline_sha, "head_sha": head_sha, "commits_ahead": 0}
            )

        # Check files modified since baseline
        diff_files_proc = subprocess.run(
            ["git", "diff", "--name-only", baseline_sha, head_sha],
            cwd=str(workspace_path),
            capture_output=True,
            text=True
        )
        files_modified = [f.strip() for f in diff_files_proc.stdout.splitlines() if f.strip()]

        # Check if commits since baseline mention this task title or issue number
        log_proc = subprocess.run(
            ["git", "log", f"{baseline_sha}..{head_sha}", "--oneline"],
            cwd=str(workspace_path),
            capture_output=True,
            text=True
        )
        recent_log = log_proc.stdout

        details = {
            "baseline_sha": baseline_sha,
            "head_sha": head_sha,
            "commits_ahead": commits_ahead,
            "files_modified": files_modified,
            "recent_commits": [l.strip() for l in recent_log.splitlines()[:5]]
        }

        # Check NOOP condition: if recent commits already implemented this exact task
        clean_title = task_title.lower()
        for kw in ["sharkbot", "catalogador", "control-plane"]:
            clean_title = clean_title.replace(f"[{kw}]", "").replace(kw, "")
        clean_title = clean_title.strip().lower()

        if clean_title and len(clean_title) > 8 and clean_title in recent_log.lower():
            return (
                AntiStaleStatus.NOOP,
                f"A funcionalidade ou correção solicitada já consta no histórico de commits posteriores ({commits_ahead} commits à frente).",
                details
            )

        # Check scope conflicts
        scope_conflict = False
        if allowed_scope:
            for modified in files_modified:
                for scope in allowed_scope:
                    if modified.startswith(scope) or scope.startswith(modified):
                        scope_conflict = True
                        break

        if scope_conflict:
            return (
                AntiStaleStatus.RECONCILE,
                f"O projeto avançou {commits_ahead} commits e modificou arquivos dentro do escopo permitido. Aplicando com reconciliação sobre o código atual.",
                details
            )

        return (
            AntiStaleStatus.APPLY,
            f"O projeto avançou {commits_ahead} commits, mas sem conflito com o escopo da tarefa. Seguro para prosseguir.",
            details
        )
