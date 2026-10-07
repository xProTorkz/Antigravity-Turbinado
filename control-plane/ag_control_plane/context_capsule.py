"""Context Capsule para encapsulamento cirúrgico de contexto (Item 11).

Garante que o executor receba o contexto exato e estruturado sem ruído:
- PROJECT
- REPO
- BRANCH
- HEAD
- BASELINE_SHA
- OBJECTIVE
- CURRENT_STATE
- FILES_TO_WRITE
- FILES_READ_ONLY
- SYMBOLS
- DEPENDENCIES
- RELATED_ISSUES
- RECENT_RELEVANT_COMMITS
- DO_NOT_TOUCH
- TESTS
- ACCEPTANCE
"""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .execution_brief import ExecutionBrief


@dataclass
class ContextCapsule:
    project: str
    repo: str
    branch: str
    head: str
    baseline_sha: str
    objective: str
    current_state: str
    files_to_write: List[str]
    files_read_only: List[str]
    symbols: List[str]
    dependencies: List[int]
    related_issues: List[int]
    recent_relevant_commits: List[str]
    do_not_touch: List[str]
    tests: List[str]
    acceptance: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_prompt(self, issue_number: int) -> str:
        """Formata a cápsula em prompt cirúrgico de alta densidade informativa."""
        files_write_str = "\n".join(f"- {f}" for f in self.files_to_write) or "Nenhum"
        files_ro_str = "\n".join(f"- {f}" for f in self.files_read_only) or "Nenhum"
        symbols_str = ", ".join(self.symbols) if self.symbols else "Nenhum específico"
        deps_str = ", ".join(f"#{d}" for d in self.dependencies) if self.dependencies else "Nenhuma"
        related_str = ", ".join(f"#{r}" for r in self.related_issues) if self.related_issues else "Nenhuma"
        commits_str = "\n".join(f"- {c}" for c in self.recent_relevant_commits) or "Nenhum"
        dnt_str = ", ".join(self.do_not_touch) if self.do_not_touch else "Padrão do projeto"
        tests_str = "\n".join(f"- {t}" for t in self.tests) or "Testes unitários afetados"
        acc_str = "\n".join(f"- {a}" for a in self.acceptance) or "Critérios de aceite padrão"

        return (
            f"[CONTEXT CAPSULE — TASK #{issue_number}]\n"
            f"PROJECT: {self.project}\n"
            f"REPO: {self.repo}\n"
            f"BRANCH: {self.branch}\n"
            f"HEAD: {self.head}\n"
            f"BASELINE_SHA: {self.baseline_sha}\n"
            f"OBJECTIVE: {self.objective}\n"
            f"CURRENT_STATE: {self.current_state}\n\n"
            f"FILES_TO_WRITE:\n{files_write_str}\n\n"
            f"FILES_READ_ONLY:\n{files_ro_str}\n\n"
            f"SYMBOLS: {symbols_str}\n"
            f"DEPENDENCIES: {deps_str}\n"
            f"RELATED_ISSUES: {related_str}\n\n"
            f"RECENT_RELEVANT_COMMITS:\n{commits_str}\n\n"
            f"DO_NOT_TOUCH: {dnt_str}\n\n"
            f"TESTS:\n{tests_str}\n\n"
            f"ACCEPTANCE:\n{acc_str}\n"
        )

    @classmethod
    def from_brief(
        cls,
        brief: ExecutionBrief,
        workspace_path: Path,
        repo: str,
        branch: str = "main",
        dependencies: Optional[List[int]] = None,
        related_issues: Optional[List[int]] = None,
        current_state: str = "STABLE",
    ) -> ContextCapsule:
        """Monta a cápsula cirúrgica inspecionando o repositório local sem sobrecarga."""
        head = brief.baseline_sha or "0000000"
        recent_commits: List[str] = []

        if workspace_path.exists() and (workspace_path / ".git").exists():
            try:
                res_head = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(workspace_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if res_head.returncode == 0 and res_head.stdout.strip():
                    head = res_head.stdout.strip()

                res_log = subprocess.run(
                    ["git", "log", "-n", "3", "--oneline"],
                    cwd=str(workspace_path),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if res_log.returncode == 0:
                    recent_commits = [c.strip() for c in res_log.stdout.splitlines() if c.strip()]
            except Exception:
                pass

        files_to_write = [
            f.path for f in brief.files if f.operation in {"MODIFY", "CREATE", "DELETE", "RENAME"}
        ]
        files_read_only = [
            f.path for f in brief.files if f.operation == "READ_ONLY"
        ] + [r.path for r in brief.read_only_context]

        symbols: List[str] = []
        for f in brief.files:
            symbols.extend(f.symbols)

        return cls(
            project=brief.project,
            repo=repo,
            branch=branch,
            head=head,
            baseline_sha=brief.baseline_sha or head,
            objective=brief.objective,
            current_state=current_state,
            files_to_write=files_to_write,
            files_read_only=files_read_only,
            symbols=symbols,
            dependencies=dependencies or [],
            related_issues=related_issues or [],
            recent_relevant_commits=recent_commits,
            do_not_touch=brief.do_not_touch or [],
            tests=brief.tests or [],
            acceptance=brief.acceptance or [],
        )
