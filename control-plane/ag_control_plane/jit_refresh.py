"""JIT Refresh para tarefas preparadas previamente (Item 12).

Antes de iniciar uma tarefa preparada:
Compara BASELINE_HEAD vs CURRENT_HEAD.
- Se iguais: EXECUTE
- Se diferentes: analisa estritamente git diff BASELINE_HEAD..CURRENT_HEAD
  - Se os commits NÃO tocam o escopo da tarefa: FAST_REFRESH=PASS (atualiza baseline e prossegue)
  - Se tocam o escopo: MICRO_REFINEMENT (ajusta apenas os arquivos em conflito, sem full repo scan)
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("ag-jit-refresh")


@dataclass
class JITRefreshResult:
    status: str  # "EXECUTE", "MICRO_REFINEMENT", "BLOCKED"
    fast_refresh_passed: bool
    current_head: str
    baseline_head: str
    changed_files: List[str]
    conflicting_files: List[str]
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "fast_refresh_passed": self.fast_refresh_passed,
            "current_head": self.current_head,
            "baseline_head": self.baseline_head,
            "changed_files": self.changed_files,
            "conflicting_files": self.conflicting_files,
            "message": self.message,
        }


class JITRefreshManager:
    """Valida o delta entre a preparação da tarefa e o início da execução."""

    @classmethod
    def check_refresh(
        cls,
        workspace_path: Path,
        baseline_head: str,
        planned_files: List[str],
    ) -> JITRefreshResult:
        """Compara o HEAD atual do workspace com o BASELINE_HEAD da tarefa preparada."""
        if not workspace_path.exists() or not (workspace_path / ".git").exists():
            return JITRefreshResult(
                status="EXECUTE",
                fast_refresh_passed=True,
                current_head=baseline_head,
                baseline_head=baseline_head,
                changed_files=[],
                conflicting_files=[],
                message="Repositório não possui git local; prosseguindo com baseline informado.",
            )

        # 1. Obtém CURRENT_HEAD
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(workspace_path),
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            current_head = res.stdout.strip()
        except Exception as e:
            logger.warning(f"Erro ao obter HEAD atual para JIT Refresh: {e}")
            current_head = baseline_head

        # 2. Se HEAD não mudou: EXECUTE imediato
        if not baseline_head or baseline_head == current_head or baseline_head == "0000000":
            return JITRefreshResult(
                status="EXECUTE",
                fast_refresh_passed=True,
                current_head=current_head,
                baseline_head=baseline_head or current_head,
                changed_files=[],
                conflicting_files=[],
                message="HEAD inalterado desde a preparação. EXECUTE imediato.",
            )

        # 3. HEAD mudou: analisa git diff --name-only baseline_head..current_head
        try:
            diff_res = subprocess.run(
                ["git", "diff", "--name-only", f"{baseline_head}..{current_head}"],
                cwd=str(workspace_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if diff_res.returncode == 0:
                changed_files = [f.strip() for f in diff_res.stdout.splitlines() if f.strip()]
            else:
                changed_files = []
        except Exception as e:
            logger.warning(f"Erro ao executar git diff para JIT Refresh: {e}")
            changed_files = []

        # Compara com os arquivos planejados
        planned_set: Set[str] = {p.strip().lstrip("./") for p in planned_files}
        conflicting = [f for f in changed_files if f.strip().lstrip("./") in planned_set]

        if not conflicting:
            msg = (
                f"FAST_REFRESH=PASS: HEAD mudou de {baseline_head[:7]} para {current_head[:7]}, "
                f"mas nenhum arquivo do escopo foi alterado ({len(changed_files)} arquivos alterados fora do escopo)."
            )
            logger.info(f"[JIT_REFRESH] {msg}")
            return JITRefreshResult(
                status="EXECUTE",
                fast_refresh_passed=True,
                current_head=current_head,
                baseline_head=baseline_head,
                changed_files=changed_files,
                conflicting_files=[],
                message=msg,
            )

        # Conflito detectado: exige MICRO_REFINEMENT
        msg = (
            f"MICRO_REFINEMENT: Commits intermediários alteraram arquivos do escopo planejado: {conflicting}. "
            "Refinando cirurgicamente apenas os arquivos afetados."
        )
        logger.warning(f"[JIT_REFRESH] {msg}")
        return JITRefreshResult(
            status="MICRO_REFINEMENT",
            fast_refresh_passed=False,
            current_head=current_head,
            baseline_head=baseline_head,
            changed_files=changed_files,
            conflicting_files=conflicting,
            message=msg,
        )
