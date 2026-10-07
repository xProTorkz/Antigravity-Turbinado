"""Gerenciador de Execução em Background para tarefas assíncronas (Item 9).

Permite executar operações de longa duração sem bloquear o Coordinator:
- build, instalação, download, pytest longo, Playwright, CI, análise read-only.
Registra:
- BACKGROUND_TASK_ID
- STATUS (RUNNING, COMPLETED, FAILED)
- STARTED_AT
- COMPLETED_AT
- PID
- LOG_PATH
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ag-background-tasks")


@dataclass
class BackgroundTaskInfo:
    task_id: str
    name: str
    cmd: List[str]
    cwd: str
    status: str  # "RUNNING", "COMPLETED", "FAILED"
    pid: int
    started_at: str
    completed_at: Optional[str] = None
    exit_code: Optional[int] = None
    log_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BackgroundTaskManager:
    """Gerencia tarefas demoradas em processos isolados para manter o Coordinator responsivo."""

    SAFE_BACKGROUND_COMMANDS = {
        "pytest", "npm install", "pip install", "build", "playwright",
        "ci", "download", "analysis", "cargo build"
    }

    LONG_RUNNING_COMMANDS = {
        "pytest tests/", "pytest", "build", "playwright", "docker",
        "regressão", "regression", "cargo build", "npm run build"
    }

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent
        self.tasks_dir = self.root_dir / ".control-plane" / "background_tasks"
        self.logs_dir = self.root_dir / ".control-plane" / "logs" / "tasks"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self._active_processes: Dict[str, subprocess.Popen] = {}

    def is_safe_for_background(self, cmd: List[str]) -> bool:
        cmd_str = " ".join(cmd).lower()
        return any(safe in cmd_str for safe in self.SAFE_BACKGROUND_COMMANDS)

    def is_long_running(self, cmd: List[str] | str) -> bool:
        cmd_str = " ".join(cmd).lower() if isinstance(cmd, list) else cmd.lower()
        return any(term in cmd_str for term in self.LONG_RUNNING_COMMANDS)

    def start_task(
        self,
        name: str,
        cmd: List[str],
        cwd: Optional[Path] = None,
        force_background: bool = False,
    ) -> BackgroundTaskInfo:
        task_id = f"bg_{uuid.uuid4().hex[:8]}"
        task_cwd = str(cwd or self.root_dir)
        log_file = self.logs_dir / f"{task_id}.log"

        logger.info(f"[BACKGROUND] Iniciando tarefa '{name}' ({task_id}): {cmd}")

        log_fd = os.open(str(log_file), os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=task_cwd,
                stdin=subprocess.DEVNULL,
                stdout=log_fd,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
        finally:
            os.close(log_fd)
        self._active_processes[task_id] = proc

        info = BackgroundTaskInfo(
            task_id=task_id,
            name=name,
            cmd=cmd,
            cwd=task_cwd,
            status="RUNNING",
            pid=proc.pid,
            started_at=datetime.now(timezone.utc).isoformat(),
            log_path=str(log_file),
        )
        self._save_task_info(info)
        return info

    def check_task(self, task_id: str) -> Optional[BackgroundTaskInfo]:
        info = self.get_task(task_id)
        if not info:
            return None

        if info.status == "RUNNING":
            proc = self._active_processes.get(task_id)
            if proc:
                ret = proc.poll()
                if ret is not None:
                    info.status = "COMPLETED" if ret == 0 else "FAILED"
                    info.exit_code = ret
                    info.completed_at = datetime.now(timezone.utc).isoformat()
                    self._save_task_info(info)
                    self._active_processes.pop(task_id, None)
            else:
                # Checa por PID no SO
                try:
                    os.kill(info.pid, 0)
                except OSError:
                    info.status = "COMPLETED"
                    info.completed_at = datetime.now(timezone.utc).isoformat()
                    self._save_task_info(info)

        return info

    def get_task(self, task_id: str) -> Optional[BackgroundTaskInfo]:
        f = self.tasks_dir / f"{task_id}.json"
        if not f.exists():
            return None
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            return BackgroundTaskInfo(**data)
        except Exception:
            return None

    def list_active_tasks(self) -> List[BackgroundTaskInfo]:
        res = []
        for f in self.tasks_dir.glob("*.json"):
            task_id = f.stem
            info = self.check_task(task_id)
            if info and info.status == "RUNNING":
                res.append(info)
        return res

    def _save_task_info(self, info: BackgroundTaskInfo) -> None:
        f = self.tasks_dir / f"{info.task_id}.json"
        try:
            f.write_text(json.dumps(info.to_dict(), indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Erro ao salvar info da task {info.task_id}: {e}")

    def start_background_test(
        self,
        cmd: List[str],
        cwd: Optional[Path] = None,
        name: str = "pytest_suite",
    ) -> Dict[str, Any]:
        """Inicia teste longo em background e retorna imediatamente para manter o Coordinator READY."""
        task_info = self.start_task(name=name, cmd=cmd, cwd=cwd, force_background=True)
        return {
            "status": "READY",
            "coordinator_status": "READY",
            "coordinator_blocked": False,
            "background_task_id": task_info.task_id,
            "long_test_background": True,
            "cmd": cmd,
            "started_at": task_info.started_at,
            "log_path": task_info.log_path,
            "message": f"Teste longo em background iniciado ({task_info.task_id}). Coordinator imediatamente em estado READY.",
        }

    def attach_test_results(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Recupera e anexa o resultado do teste quando concluído."""
        info = self.check_task(task_id)
        if not info:
            return None

        output_snippet = ""
        if info.log_path and Path(info.log_path).exists():
            try:
                content = Path(info.log_path).read_text(encoding="utf-8")
                lines = content.splitlines()
                output_snippet = "\n".join(lines[-20:]) if len(lines) > 20 else content
            except Exception:
                pass

        return {
            "task_id": info.task_id,
            "status": info.status,
            "exit_code": info.exit_code,
            "completed_at": info.completed_at,
            "log_path": info.log_path,
            "output_snippet": output_snippet,
            "passed": (info.exit_code == 0) if info.exit_code is not None else False,
        }

