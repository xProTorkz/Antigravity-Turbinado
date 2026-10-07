import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

class LockError(Exception):
    pass

class LockManager:
    def __init__(self, lock_dir: Optional[str] = None):
        if lock_dir:
            self.lock_dir = Path(lock_dir)
        else:
            self.lock_dir = Path(__file__).resolve().parent.parent / ".control-plane" / "locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)

    def _get_lock_path(self, project: str) -> Path:
        safe_project = "".join(c for c in project if c.isalnum() or c in ("-", "_"))
        return self.lock_dir / f"{safe_project}.lock"

    def _get_lease_path(self, project: str) -> Path:
        safe_project = "".join(c for c in project if c.isalnum() or c in ("-", "_"))
        return self.lock_dir / f"{safe_project}.lease.json"

    @staticmethod
    def _is_pid_alive(pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True # process exists but owned by someone else

    def is_locked(self, project: str) -> bool:
        lock_path = self._get_lock_path(project)
        if not lock_path.exists():
            return False
        try:
            data = json.loads(lock_path.read_text(encoding="utf-8"))
            pid = data.get("pid")
            if pid and self._is_pid_alive(pid):
                return True
            else:
                # Stale lock: process is dead
                self.release(project, force=True)
                return False
        except Exception:
            return False

    def acquire(self, project: str, issue_number: int, timeout_sec: int = 5) -> bool:
        lock_path = self._get_lock_path(project)
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            if not self.is_locked(project):
                payload = {
                    "project": project,
                    "issue_number": issue_number,
                    "pid": os.getpid(),
                    "acquired_at": datetime.now(timezone.utc).isoformat()
                }
                try:
                    # Write exclusively
                    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                    fd = os.open(str(lock_path), flags, 0o644)
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        json.dump(payload, f, indent=2)
                    return True
                except FileExistsError:
                    pass
            time.sleep(0.5)
        return False

    def release(self, project: str, force: bool = False) -> None:
        lock_path = self._get_lock_path(project)
        if not lock_path.exists():
            return
        if not force:
            try:
                data = json.loads(lock_path.read_text(encoding="utf-8"))
                if data.get("pid") != os.getpid():
                    raise LockError(f"Lock para '{project}' pertence ao PID {data.get('pid')}, não a este processo ({os.getpid()}).")
            except Exception as e:
                if not isinstance(e, LockError):
                    pass
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass

    def create_lease(self, project: str, issue_number: int, conversation_id: str) -> Path:
        lease_path = self._get_lease_path(project)
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "project": project,
            "issue_number": issue_number,
            "conversation_id": conversation_id,
            "status": "working",
            "acquired_at": now_iso,
            "updated_at": now_iso
        }
        lease_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return lease_path

    def get_lease(self, project: str) -> Optional[Dict[str, Any]]:
        lease_path = self._get_lease_path(project)
        if not lease_path.exists():
            return None
        try:
            return json.loads(lease_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def release_lease(self, project: str) -> None:
        lease_path = self._get_lease_path(project)
        try:
            lease_path.unlink(missing_ok=True)
        except Exception:
            pass

    def list_leases(self) -> List[Dict[str, Any]]:
        leases = []
        for p in self.lock_dir.glob("*.lease.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                leases.append(data)
            except Exception:
                continue
        return leases

    def __call__(self, project: str, issue_number: int):
        return _LockContext(self, project, issue_number)

class _LockContext:
    def __init__(self, manager: LockManager, project: str, issue_number: int):
        self.manager = manager
        self.project = project
        self.issue_number = issue_number

    def __enter__(self):
        acquired = self.manager.acquire(self.project, self.issue_number)
        if not acquired:
            raise LockError(f"Não foi possível obter lock exclusivo para o projeto '{self.project}' (Issue #{self.issue_number}).")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.manager.release(self.project)
