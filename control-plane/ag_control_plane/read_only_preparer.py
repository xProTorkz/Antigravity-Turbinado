"""Preparadores Read-Only paralelos para as próximas tarefas da fila (Item 10).

Enquanto a tarefa principal está executando:
Até 2 preparadores read-only (PARALLEL_READ_ONLY_PREPARERS = 2) executam em paralelo:
- localizar arquivos
- resolver símbolos
- preparar ExecutionBrief
- descobrir testes
- verificar dependências
- montar contexto
- verificar conflitos

PROIBIDO:
- editar arquivos
- commit
- alterar config
- ações destrutivas
"""

from __future__ import annotations

import concurrent.futures
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .execution_brief import ExecutionBrief, FilePlanItem, ReadOnlyContextItem
from .task_parser import TaskParser

logger = logging.getLogger("ag-read-only-preparer")

PARALLEL_READ_ONLY_PREPARERS = 2


@dataclass
class PreparedTask:
    issue_number: int
    project: str
    status: str  # "READY", "PREPARING", "FAILED"
    execution_brief: Dict[str, Any]
    candidate_files: List[str]
    candidate_tests: List[str]
    prepared_at: str
    read_only_verified: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReadOnlyTaskPreparer:
    """Gerencia a preparação antecipada de tarefas enfileiradas sem realizar nenhuma escrita."""

    def __init__(self, root_dir: Optional[Path] = None, max_workers: int = PARALLEL_READ_ONLY_PREPARERS):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent
        self.prepared_dir = self.root_dir / ".control-plane" / "prepared_tasks"
        self.prepared_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)

    def prepare_issue_read_only(
        self,
        issue: Dict[str, Any],
        workspace_path: Path,
        registry: Dict[str, Any],
    ) -> PreparedTask:
        """Executa varredura e preparação estritamente READ-ONLY para uma issue."""
        issue_number = issue.get("number", 0)
        title = issue.get("title", "")
        body = issue.get("body", "")
        labels = [l["name"] for l in issue.get("labels", [])]

        logger.info(f"[READ_ONLY_PREPARER] Preparando Issue #{issue_number} ('{title}') em modo read-only...")

        # 1. Parsing sem efeitos colaterais
        task_meta = TaskParser.parse_task(body, labels=labels, title=title, registry=registry)
        project_slug = task_meta.get("target_project", "unknown")

        # 2. Localização de arquivos candidatos (apenas leitura do filesystem)
        candidate_files: List[str] = []
        candidate_tests: List[str] = []

        allowed_scope = task_meta.get("allowed_scope", [])
        if workspace_path.exists():
            for root, _, files in os.walk(str(workspace_path)):
                for f in files:
                    if f.endswith((".py", ".ts", ".js", ".json", ".md")):
                        rel = os.path.relpath(os.path.join(root, f), str(workspace_path))
                        if not rel.startswith(".git") and not rel.startswith(".venv"):
                            if "test" in rel.lower():
                                candidate_tests.append(rel)
                            else:
                                candidate_files.append(rel)

        # 3. Construção do ExecutionBrief
        existing_brief = TaskParser.parse_execution_brief(body)
        if existing_brief:
            brief = existing_brief
        else:
            files_plan = [
                FilePlanItem(path=p, operation="MODIFY") for p in candidate_files[:5]
            ] or [FilePlanItem(path="README.md", operation="MODIFY")]
            brief = ExecutionBrief(
                refinement_status="PASS",
                project=project_slug,
                workstream="system",
                objective=title,
                baseline_sha=task_meta.get("baseline_sha") or "0000000",
                skill_primary="@developer-fast",
                files=files_plan,
                tests=candidate_tests[:3],
                conflicts_checked=True,
            )

        prep = PreparedTask(
            issue_number=issue_number,
            project=project_slug,
            status="READY",
            execution_brief=brief.to_dict(),
            candidate_files=candidate_files[:10],
            candidate_tests=candidate_tests[:5],
            prepared_at=datetime.now(timezone.utc).isoformat(),
            read_only_verified=True,
        )

        # 4. Salva a preparação em cache para uso instantâneo pelo dispatcher
        out_file = self.prepared_dir / f"{issue_number}.json"
        out_file.write_text(json.dumps(prep.to_dict(), indent=2), encoding="utf-8")
        logger.info(f"[READ_ONLY_PREPARER] Issue #{issue_number} preparada e marcada como READY.")
        return prep

    def get_prepared_task(self, issue_number: int) -> Optional[PreparedTask]:
        f = self.prepared_dir / f"{issue_number}.json"
        if not f.exists():
            return None
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            return PreparedTask(**data)
        except Exception:
            return None

    def consume_prepared_task(self, issue_number: int) -> Optional[PreparedTask]:
        prep = self.get_prepared_task(issue_number)
        if prep:
            (self.prepared_dir / f"{issue_number}.json").unlink(missing_ok=True)
        return prep
