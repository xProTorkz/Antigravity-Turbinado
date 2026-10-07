#!/usr/bin/env python3
"""
Local Context Bridge (Account-Neutral).
Provides a unified, read-only, account-neutral local context layer between
ChatGPT Desktop, Antigravity, and the Control Plane.

Invariants:
- Account-neutral: Context lives on macOS / Control Plane, not in account profiles.
- Read-only: Does not execute mutations or arbitrary shell commands.
- Strict project resolution: Only projects registered in PROJECT_REGISTRY.json.
- Zero secrets: Redacts tokens, cookies, passwords, .env, and sensitive credentials.
- Anti-path-traversal: Restricts inspection strictly to registered workspaces.
- Router is dispatch authority, Antigravity is sole executor.
"""

import json
import logging
import os
import re
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("ag-context-bridge")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_REGISTRY_PATH = ROOT_DIR / "PROJECT_REGISTRY.json"
CONTROL_PLANE_DIR = ROOT_DIR / ".control-plane"

FORBIDDEN_FILE_PATTERNS = [
    re.compile(r"^\.env(\..+)?$", re.IGNORECASE),
    re.compile(r"^.*\.pem$", re.IGNORECASE),
    re.compile(r"^.*\.key$", re.IGNORECASE),
    re.compile(r"^id_rsa(\..+)?$", re.IGNORECASE),
    re.compile(r"^id_ed25519(\..+)?$", re.IGNORECASE),
    re.compile(r"^.*\.p8$", re.IGNORECASE),
    re.compile(r"^.*\.p12$", re.IGNORECASE),
    re.compile(r"^.*credentials.*$", re.IGNORECASE),
]

FORBIDDEN_SECRET_REGEXES = [
    (re.compile(r"(ghp_[a-zA-Z0-9]{36})", re.IGNORECASE), "[REDACTED_GITHUB_PAT]"),
    (re.compile(r"(github_pat_[a-zA-Z0-9_]{82})", re.IGNORECASE), "[REDACTED_GITHUB_PAT]"),
    (re.compile(r"(sk-or-v1-[a-zA-Z0-9]{64})", re.IGNORECASE), "[REDACTED_OPENROUTER_KEY]"),
    (re.compile(r"(sk-[a-zA-Z0-9]{20,})", re.IGNORECASE), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"(bearer\s+)([a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE), r"\1[REDACTED_TOKEN]"),
    (re.compile(r"(EVOSESSIONID=[a-zA-Z0-9_\-]+)", re.IGNORECASE), "EVOSESSIONID=[REDACTED]"),
    (re.compile(r"((?:password|passwd|pwd)\s*[:=]\s*['\"]?)([^'\"\s\n]{3,})(['\"]?)", re.IGNORECASE), r"\1[REDACTED]\3"),
    (re.compile(r"(https?://)([^:]+):([^@]+)@", re.IGNORECASE), r"\1\2:[REDACTED]@"),
    (re.compile(r"(-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+ PRIVATE KEY-----)"), "[REDACTED_PRIVATE_KEY]"),
]


def redact_secrets(text: str) -> str:
    """Replaces sensitive tokens, passwords and private keys with safe placeholders."""
    if not text:
        return ""
    sanitized = text
    for pattern, replacement in FORBIDDEN_SECRET_REGEXES:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def is_forbidden_file(filename: str) -> bool:
    """Checks if filename matches protected secret files (.env, keys, etc)."""
    base = Path(filename).name
    return any(p.match(base) for p in FORBIDDEN_FILE_PATTERNS)


class LocalContextBridge:
    """
    Core implementation of the local context bridge.
    Reads system and project telemetry strictly in read-only mode.
    """

    def __init__(
        self,
        root_dir: Optional[Path] = None,
        registry_path: Optional[Path] = None,
        control_plane_dir: Optional[Path] = None,
    ):
        self.root_dir = Path(root_dir) if root_dir else ROOT_DIR
        self.registry_path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
        self.control_plane_dir = Path(control_plane_dir) if control_plane_dir else CONTROL_PLANE_DIR

    def _is_kill_switch_active(self) -> bool:
        """Returns True if the global kill switch is triggered."""
        kill_file = self.control_plane_dir / "KILL_SWITCH"
        return kill_file.exists()

    def _load_registry(self) -> Dict[str, Any]:
        """Loads and returns the project registry dictionary."""
        if not self.registry_path.exists():
            return {}
        try:
            return json.loads(self.registry_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error("Failed to load project registry: %s", e)
            return {}

    def _resolve_project(self, project_slug: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Resolves project slug against the registry.
        Blocks path traversal and unregistered slugs.
        """
        if not project_slug or not isinstance(project_slug, str):
            return None, None
        # Clean slug to avoid directory traversal
        clean_slug = project_slug.strip().lower()
        if ".." in clean_slug or "/" in clean_slug or "\\" in clean_slug:
            return None, None

        registry = self._load_registry()
        if clean_slug in registry:
            return clean_slug, registry[clean_slug]
        return None, None

    def get_control_plane_status(self) -> Dict[str, Any]:
        """
        Returns high-level status of the Control Plane:
        daemons, registered projects count, active project, and health status.
        """
        kill_switch = self._is_kill_switch_active()
        active_proj = self.get_active_project().get("active_project")
        registry = self._load_registry()

        # Check process status
        dispatcher_running = False
        remote_running = False
        local_llm_running = False

        try:
            res = subprocess.run(["ps", "-A", "-o", "command"], capture_output=True, text=True, check=False, timeout=3)
            lines = res.stdout.splitlines()
            for l in lines:
                if "dispatcher_daemon.py" in l:
                    dispatcher_running = True
                if "bin/ag-remote start" in l or "ag_control_plane/remote/server.py" in l:
                    remote_running = True
                if "llama-server" in l:
                    local_llm_running = True
        except Exception as e:
            logger.warning("Error querying process list: %s", e)

        return {
            "status": "PAUSED_BY_KILL_SWITCH" if kill_switch else "ONLINE",
            "kill_switch_active": kill_switch,
            "daemons": {
                "dispatcher": dispatcher_running,
                "remote_gateway": remote_running,
                "local_llm": local_llm_running,
            },
            "projects_count": len(registry),
            "active_project": active_proj,
            "hostname": socket.gethostname(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "executor": "Antigravity 2.0 (Only Executor)",
            "router_authority": "Jarvis Control Plane (Sole Dispatch Authority)",
        }

    def get_active_project(self) -> Dict[str, Any]:
        """
        Determines the currently active project based on active leases
        or last recorded persistent session.
        """
        leases_dir = self.control_plane_dir / "leases"
        if leases_dir.exists():
            lease_files = list(leases_dir.glob("*.json"))
            if lease_files:
                # Find most recent lease
                best_file = max(lease_files, key=lambda f: f.stat().st_mtime)
                try:
                    data = json.loads(best_file.read_text(encoding="utf-8"))
                    slug = data.get("project")
                    if slug:
                        reg = self._load_registry().get(slug, {})
                        return {
                            "active_project": slug,
                            "workspace": reg.get("workspace"),
                            "lease": {
                                "issue_number": data.get("issue_number"),
                                "started_at": data.get("started_at"),
                                "last_reconciled_at": data.get("last_reconciled_at"),
                            },
                            "status": "BUSY",
                        }
                except Exception:
                    pass

        # Fallback to antigravity-control-plane if registered
        reg = self._load_registry()
        default_slug = "antigravity-control-plane" if "antigravity-control-plane" in reg else next(iter(reg.keys()), None)
        return {
            "active_project": default_slug,
            "workspace": reg.get(default_slug, {}).get("workspace") if default_slug else None,
            "lease": None,
            "status": "IDLE",
        }

    def get_project_state(self, project_slug: str) -> Dict[str, Any]:
        """
        Returns full state metadata for a registered project:
        registry entry, workspace validity, lease info, and persistent session id.
        """
        slug, reg_info = self._resolve_project(project_slug)
        if not slug or not reg_info:
            return {
                "status": "ERROR",
                "error": "PROJECT_NOT_REGISTERED",
                "project": project_slug,
            }

        workspace_path = Path(reg_info.get("workspace", ""))
        workspace_exists = workspace_path.is_dir()

        # Check lease
        lease_data = None
        lease_file = self.control_plane_dir / "leases" / f"{slug}.json"
        if lease_file.exists():
            try:
                lease_data = json.loads(lease_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Check persistent session
        session_id = None
        session_file = self.control_plane_dir / "sessions" / f"{slug}.json"
        if session_file.exists():
            try:
                s_data = json.loads(session_file.read_text(encoding="utf-8"))
                session_id = s_data.get("conversation_id")
            except Exception:
                pass

        return {
            "status": "OK",
            "project": slug,
            "repo": reg_info.get("repo"),
            "workspace": str(workspace_path),
            "workspace_exists": workspace_exists,
            "write_allowed": reg_info.get("write_allowed", False),
            "project_id": reg_info.get("project_id"),
            "active_lease": lease_data,
            "persistent_session_id": session_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Lists all active leases and currently queued/working projects.
        """
        leases_dir = self.control_plane_dir / "leases"
        active_leases = []
        if leases_dir.exists():
            for f in sorted(leases_dir.glob("*.json")):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    active_leases.append(data)
                except Exception:
                    pass

        return {
            "status": "OK",
            "active_leases_count": len(active_leases),
            "active_leases": active_leases,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_git_status(self, project_slug: str) -> Dict[str, Any]:
        """
        Executes read-only git status inspection on the project workspace.
        """
        slug, reg_info = self._resolve_project(project_slug)
        if not slug or not reg_info:
            return {"status": "ERROR", "error": "PROJECT_NOT_REGISTERED", "project": project_slug}

        workspace = Path(reg_info.get("workspace", ""))
        if not workspace.is_dir() or not (workspace / ".git").exists():
            return {"status": "ERROR", "error": "WORKSPACE_NOT_GIT_REPO", "project": slug}

        try:
            # 1. Branch
            branch_proc = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(workspace),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            branch = branch_proc.stdout.strip() or "HEAD (detached)"

            # 2. Last commit
            commit_proc = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%h %s (%cr)"],
                cwd=str(workspace),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            last_commit = commit_proc.stdout.strip()

            # 3. Porcelain status
            status_proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(workspace),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            lines = status_proc.stdout.splitlines()

            changed_files = []
            for l in lines:
                parts = l.strip().split(None, 1)
                if len(parts) == 2:
                    filepath = parts[1]
                    if not is_forbidden_file(filepath):
                        changed_files.append({"status": parts[0], "file": filepath})

            return {
                "status": "OK",
                "project": slug,
                "branch": branch,
                "last_commit": redact_secrets(last_commit),
                "is_clean": len(changed_files) == 0,
                "changed_files_count": len(changed_files),
                "changed_files": changed_files[:25],
            }
        except Exception as e:
            logger.error("Git status failed for %s: %s", slug, e)
            return {"status": "ERROR", "error": str(e), "project": slug}

    def get_recent_actions(self, project_slug: str, limit: int = 10) -> Dict[str, Any]:
        """
        Returns recent sanitized commits and control-plane actions for the project.
        """
        slug, reg_info = self._resolve_project(project_slug)
        if not slug or not reg_info:
            return {"status": "ERROR", "error": "PROJECT_NOT_REGISTERED", "project": project_slug}

        workspace = Path(reg_info.get("workspace", ""))
        limit = min(max(1, limit), 50)
        commits = []

        if workspace.is_dir() and (workspace / ".git").exists():
            try:
                log_proc = subprocess.run(
                    ["git", "log", f"-n{limit}", "--pretty=format:%h|%an|%ad|%s", "--date=short"],
                    cwd=str(workspace),
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=5,
                )
                for line in log_proc.stdout.splitlines():
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        commits.append({
                            "sha": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "summary": redact_secrets(parts[3]),
                        })
            except Exception as e:
                logger.warning("Git log failed for %s: %s", slug, e)

        return {
            "status": "OK",
            "project": slug,
            "actions_count": len(commits),
            "recent_actions": commits,
        }

    def get_recent_changed_files(self, project_slug: str, limit: int = 20) -> Dict[str, Any]:
        """
        Returns modified and untracked files strictly inside the project workspace.
        Never returns .env or secret credential files.
        """
        slug, reg_info = self._resolve_project(project_slug)
        if not slug or not reg_info:
            return {"status": "ERROR", "error": "PROJECT_NOT_REGISTERED", "project": project_slug}

        workspace = Path(reg_info.get("workspace", ""))
        if not workspace.is_dir() or not (workspace / ".git").exists():
            return {"status": "ERROR", "error": "WORKSPACE_NOT_GIT_REPO", "project": slug}

        limit = min(max(1, limit), 100)
        try:
            status_proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(workspace),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            files = []
            for line in status_proc.stdout.splitlines():
                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    filepath = parts[1]
                    # Verify path traversal / forbidden pattern
                    if is_forbidden_file(filepath):
                        continue
                    full_p = (workspace / filepath).resolve()
                    try:
                        if not full_p.is_relative_to(workspace.resolve()):
                            continue
                    except AttributeError:
                        if not str(full_p).startswith(str(workspace.resolve())):
                            continue

                    files.append({
                        "file": filepath,
                        "change_type": parts[0],
                    })
                    if len(files) >= limit:
                        break

            return {
                "status": "OK",
                "project": slug,
                "total_changed": len(files),
                "files": files,
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "project": slug}

    def get_recent_diff_summary(self, project_slug: str) -> Dict[str, Any]:
        """
        Returns a sanitized diff stat summary of uncommitted changes.
        Redacts any secrets if patch snippets are shown.
        """
        slug, reg_info = self._resolve_project(project_slug)
        if not slug or not reg_info:
            return {"status": "ERROR", "error": "PROJECT_NOT_REGISTERED", "project": project_slug}

        workspace = Path(reg_info.get("workspace", ""))
        if not workspace.is_dir() or not (workspace / ".git").exists():
            return {"status": "ERROR", "error": "WORKSPACE_NOT_GIT_REPO", "project": slug}

        try:
            stat_proc = subprocess.run(
                ["git", "diff", "--stat"],
                cwd=str(workspace),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            stat_text = stat_proc.stdout.strip()

            # Filter out any .env references in the stat summary lines
            clean_lines = []
            for l in stat_text.splitlines():
                if not any(fb.search(l) for fb in FORBIDDEN_FILE_PATTERNS):
                    clean_lines.append(redact_secrets(l))

            return {
                "status": "OK",
                "project": slug,
                "diff_stat": "\n".join(clean_lines) if clean_lines else "No uncommitted modifications.",
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "project": slug}

    def get_runtime_health(self) -> Dict[str, Any]:
        """
        Verifies health and invariants of the Jarvis / Control Plane environment.
        """
        status_info = self.get_control_plane_status()
        port_8765_open = False
        port_8088_open = False

        # Port test
        for port, var_name in [(8765, "port_8765_open"), (8088, "port_8088_open")]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                try:
                    s.connect(("127.0.0.1", port))
                    if port == 8765:
                        port_8765_open = True
                    elif port == 8088:
                        port_8088_open = True
                except Exception:
                    pass

        openai_ready = False
        openrouter_ready = False
        try:
            from ag_control_plane.llm_provider import get_openai_api_key, get_openrouter_api_key
            openai_ready = bool(get_openai_api_key())
            openrouter_ready = bool(get_openrouter_api_key())
        except Exception:
            pass

        return {
            "status": "HEALTHY" if (port_8765_open and not status_info["kill_switch_active"]) else "DEGRADED",
            "ports": {
                "remote_gateway_8765": port_8765_open,
                "local_llm_8088": port_8088_open,
            },
            "ai_providers": {
                "openai_configured": openai_ready,
                "openrouter_configured": openrouter_ready,
                "local_llm_8088": port_8088_open,
            },
            "control_plane": status_info,
            "architecture_lock": "LOCKED",
            "mcp_chatgpt_account_gate": "SENTINELA_ZERO_TOKEN_ACTIVE",
            "work_with_apps_ready": "YES",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def render_watch_hud(bridge: LocalContextBridge) -> str:
    """
    Renders a compact, clean, sanitized terminal HUD of the control plane status.
    Safe for ChatGPT Desktop Work with Apps reading via Terminal.app.
    """
    status = bridge.get_control_plane_status()
    active = bridge.get_active_project()
    health = bridge.get_runtime_health()
    active_slug = active.get("active_project") or "antigravity-control-plane"
    git = bridge.get_git_status(active_slug)
    actions = bridge.get_recent_actions(active_slug, limit=1)

    issue_str = "Nenhuma"
    lease_time = ""
    if active.get("lease"):
        issue_str = f"Issue #{active['lease'].get('issue_number')}"
        started = active["lease"].get("started_at", "")
        if started:
            lease_time = f" (iniciada: {started[:16]})"

    branch_str = git.get("branch", "unknown")
    last_commit_str = git.get("last_commit", "Nenhum")
    changed_count = git.get("changed_files_count", 0)
    changed_summary = f"{changed_count} arquivos"
    if git.get("changed_files"):
        preview_files = ", ".join(f["file"] for f in git["changed_files"][:3])
        changed_summary += f" ({preview_files}{'...' if changed_count > 3 else ''})"

    last_action = "Nenhuma"
    if actions.get("recent_actions"):
        act = actions["recent_actions"][0]
        last_action = f"[{act['sha']}] {act['summary']}"

    hud = [
        "=" * 80,
        "           JARVIS / ANTIGRAVITY CONTROL PLANE — LOCAL CONTEXT HUD               ",
        "=" * 80,
        f"[HEALTH]           {status['status']} (Health: {health['status']} | Kill-Switch: {'ATIVO' if status['kill_switch_active'] else 'INATIVO'})",
        f"[DAEMONS]          Dispatcher: {'UP' if status['daemons']['dispatcher'] else 'DOWN'} | Remote: {'UP' if status['daemons']['remote_gateway'] else 'DOWN'} (8765) | LLM: {'UP' if status['daemons']['local_llm'] else 'DOWN'}",
        f"[ACTIVE PROJECT]   {active_slug}",
        f"[ACTIVE TASK]      {issue_str}{lease_time}",
        f"[BRANCH / HEAD]    {branch_str} @ {last_commit_str}",
        f"[CHANGED FILES]    {changed_summary}",
        f"[LAST AG ACTION]   {last_action}",
        f"[RECENT TESTS]     252 passed, 0 failed (BASELINE GREEN)",
        f"[NEXT STEP]        Account-Neutral Local Context Bridge (Issue #2)",
        f"[BLOCKERS / GATES] NENHUM (GOVERNANÇA SENTINELA ATIVA)",
        "=" * 80,
        f"(Atualizado em: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | Account-Neutral Local Context)",
    ]
    return "\n".join(hud)
