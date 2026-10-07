import json
import logging
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .github_client import GitHubClient
from .task_parser import TaskParser, TaskValidationError
from .lock_manager import LockManager, LockError
from .anti_stale import AntiStaleChecker, AntiStaleStatus
from .agent_invoker import AgentInvoker
from .audit import PreFlightAuditor, PostFlightAuditor
from .notification_bridge import NotificationBridge, StatusEvent, get_notification_bridge

logger = logging.getLogger("ag-dispatcher")

class WorkspaceMismatchError(Exception):
    pass

class Dispatcher:
    def __init__(
        self,
        root_dir: Optional[Path] = None,
        github_client: Optional[Any] = None,
        invoker: Optional[Any] = None,
        notification_bridge: Optional[Any] = None,
    ):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent
        self.registry_file = self.root_dir / "PROJECT_REGISTRY.json"
        self.state_dir = self.root_dir / ".control-plane" / "state"
        self.locks_dir = self.root_dir / ".control-plane" / "locks"
        self.leases_dir = self.root_dir / ".control-plane" / "leases"
        self.sessions_dir = self.root_dir / ".control-plane" / "sessions"
        self.repair_tokens_dir = self.root_dir / ".control-plane" / "repair_tokens"
        self.kill_switch_file = self.root_dir / ".control-plane" / "KILL_SWITCH"

        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        self.leases_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.repair_tokens_dir.mkdir(parents=True, exist_ok=True)

        self.events_dir = self.root_dir / ".control-plane" / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.wake_event_file = self.events_dir / "wake.trigger"

        self.github = github_client or GitHubClient()
        self.lock_mgr = LockManager(str(self.locks_dir))
        self.invoker = invoker or AgentInvoker()
        self.registry = self._load_registry()
        self.notification_bridge = notification_bridge or get_notification_bridge()

    def _emit_status(
        self,
        status: str,
        project: Optional[str] = None,
        issue_number: int = 0,
        repo: Optional[str] = None,
        comment: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        project_slug: Optional[str] = None,
        queue_repo: Optional[str] = None,
    ) -> StatusEvent:
        """Emite evento canônico de status pelo NotificationBridge."""
        actual_project = project or project_slug or "unknown"
        actual_repo = repo or queue_repo or "unknown"
        event = StatusEvent(
            status=status,
            project=actual_project,
            issue_number=issue_number,
            repo=actual_repo,
            reason=reason,
            labels=labels or [],
            metadata=metadata or {},
            comment=comment,
        )
        return self.notification_bridge.emit(event)

    def wake(self) -> None:
        """Acorda imediatamente o scheduler do dispatcher (Event-Driven Dispatch)."""
        try:
            self.wake_event_file.touch()
            logger.debug("[FAST_DISPATCH] Sinal de wakeup emitido.")
        except Exception as e:
            logger.warning(f"Erro ao emitir sinal de wake: {e}")

    def wait_for_event(self, timeout: float = 5.0) -> bool:
        """Aguarda um sinal de wake ou timeout de fallback (default 5s).

        Retorna True se acordado por evento, False por timeout. Zero busy-loop.
        """
        deadline = time.time() + max(0.05, timeout)
        while time.time() < deadline:
            if self.wake_event_file.exists():
                try:
                    self.wake_event_file.unlink(missing_ok=True)
                except Exception:
                    pass
                return True
            time.sleep(0.05)
        return False

    def create_repair_token(self, project_slug: str) -> str:
        """Gera e armazena um token descartável para permitir exatamente uma rotação/reparo de sessão canônica."""
        token = str(uuid.uuid4())
        token_file = self.repair_tokens_dir / f"{project_slug}.token"
        token_file.write_text(token, encoding="utf-8")
        logger.info(f"Repair token gerado para '{project_slug}': {token}")
        return token

    def has_repair_token(self, project_slug: str) -> bool:
        return (self.repair_tokens_dir / f"{project_slug}.token").exists()

    def consume_repair_token(self, project_slug: str, token: Optional[str] = None) -> bool:
        """Consome o repair token. Se válido, remove o arquivo para impedir reuso."""
        token_file = self.repair_tokens_dir / f"{project_slug}.token"
        if not token_file.exists():
            return False
        try:
            stored = token_file.read_text(encoding="utf-8").strip()
            if token is None or token.strip() == stored:
                token_file.unlink(missing_ok=True)
                return True
        except Exception:
            pass
        return False

    def get_project_session(self, project_slug: str) -> Optional[Dict[str, Any]]:
        """
        Retorna a sessão canônica exclusiva de um projeto a partir de .control-plane/sessions/<project>.json.
        Fonte única da verdade (Single Source of Truth). Fallback de lease removido.
        """
        session_file = self.sessions_dir / f"{project_slug}.json"
        if session_file.exists():
            try:
                data = json.loads(session_file.read_text(encoding="utf-8"))
                expected_workspace = str(
                    Path(self.registry.get(project_slug, {}).get("workspace", self.root_dir)).resolve()
                )
                saved_workspace = str(Path(str(data.get("workspace", ""))).expanduser().resolve()) if data.get("workspace") else ""
                if (
                    data.get("project") == project_slug
                    and data.get("conversation_id")
                    and saved_workspace == expected_workspace
                ):
                    return data
                if data.get("conversation_id"):
                    logger.warning(
                        "Sessão persistente rejeitada por workspace divergente: "
                        "project=%s saved=%s expected=%s conversation=%s",
                        project_slug,
                        saved_workspace or "<missing>",
                        expected_workspace,
                        data.get("conversation_id"),
                    )
            except Exception:
                pass
        return None

    def set_project_session(
        self,
        project_slug: str,
        conversation_id: str,
        workspace: Path,
        allow_rotation: bool = False,
        repair_token: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> None:
        """
        Define ou atualiza a sessão canônica do projeto.
        Bloqueia rotações acidentais: se uma sessão canônica diferente já existir, exige allow_rotation=True
        ou repair_token válido para autorizar a substituição.
        """
        session_file = self.sessions_dir / f"{project_slug}.json"
        existing_data = None
        if session_file.exists():
            try:
                existing_data = json.loads(session_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        if existing_data and existing_data.get("conversation_id"):
            existing_id = existing_data.get("conversation_id")
            if existing_id != conversation_id:
                authorized = False
                if allow_rotation:
                    authorized = True
                elif repair_token and self.consume_repair_token(project_slug, repair_token):
                    authorized = True

                if not authorized:
                    raise RuntimeError(
                        f"CANONICAL_SESSION_ROTATION_BLOCKED: Project '{project_slug}' already has "
                        f"canonical session '{existing_id}'. Cannot overwrite with '{conversation_id}' "
                        "without explicit authorization or repair token."
                    )
                logger.info(
                    f"Canonical session rotation authorized for '{project_slug}': {existing_id} -> {conversation_id}"
                )

        retired = []
        if existing_data:
            retired = list(existing_data.get("retired_conversation_ids", []))
            old_id = existing_data.get("conversation_id")
            if old_id and old_id != conversation_id and old_id not in retired:
                retired.append(old_id)

        data = {
            "project": project_slug,
            "conversation_id": conversation_id,
            "workspace": str(workspace),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "retired_conversation_ids": retired
        }
        if project_id:
            data["project_id"] = project_id
        elif existing_data and existing_data.get("project_id"):
            data["project_id"] = existing_data.get("project_id")

        if existing_data:
            data["created_at"] = existing_data.get("created_at") or existing_data.get("updated_at")
        data.setdefault("created_at", datetime.now(timezone.utc).isoformat())

        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._sync_current_state_session(
            project_slug,
            conversation_id,
            str(workspace),
            retired,
            data.get("project_id")
        )

    def repair_project_session(
        self,
        project_slug: str,
        new_conversation_id: str,
        workspace: Optional[Path] = None,
        project_id: Optional[str] = None
    ) -> None:
        """Comando administrativo para reparar e rotacionar a sessão canônica de forma explícita."""
        ws = workspace or Path(self.registry.get(project_slug, {}).get("workspace", self.root_dir))
        self.set_project_session(
            project_slug=project_slug,
            conversation_id=new_conversation_id,
            workspace=ws,
            allow_rotation=True,
            project_id=project_id
        )
        logger.info(f"Sessão canônica do projeto '{project_slug}' reparada manualmente para '{new_conversation_id}'.")

    def _sync_current_state_session(
        self,
        project_slug: str,
        conversation_id: str,
        workspace: str,
        retired_ids: List[str],
        project_id: Optional[str] = None
    ) -> None:
        """Mantém CURRENT_STATE.json sincronizado como mirror/doc da sessão canônica."""
        current_state_path = self.root_dir / "CURRENT_STATE.json"
        if not current_state_path.exists():
            return
        try:
            state = json.loads(current_state_path.read_text(encoding="utf-8"))
            if project_slug in ("antigravity-control-plane", "jarvis"):
                state.setdefault("status", {})["jarvis_canonical_session"] = conversation_id
                state.setdefault("antigravity_sessions", {})
                entry = {
                    "canonical_conversation_id": conversation_id,
                    "retired_conversation_ids": retired_ids,
                    "workspace": workspace,
                    "workspace_binding": "VERIFIED",
                    "status": "HARDLOCKED"
                }
                if project_id:
                    entry["project_id"] = project_id
                state["antigravity_sessions"]["jarvis"] = entry
                state["antigravity_sessions"]["antigravity-control-plane"] = entry

                state.setdefault("workspace_binding_audit", {})
                state["workspace_binding_audit"]["canonical_conversation_id"] = conversation_id
                state["workspace_binding_audit"]["expected_workspace"] = workspace
                state["workspace_binding_audit"]["retired_conversation_ids"] = retired_ids
                if project_id:
                    state["workspace_binding_audit"]["project_id"] = project_id
            else:
                state.setdefault("antigravity_sessions", {})
                entry = {
                    "canonical_conversation_id": conversation_id,
                    "retired_conversation_ids": retired_ids,
                    "workspace": workspace,
                    "workspace_binding": "VERIFIED",
                    "status": "HARDLOCKED"
                }
                if project_id:
                    entry["project_id"] = project_id
                state["antigravity_sessions"][project_slug] = entry

            current_state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Aviso ao sincronizar CURRENT_STATE.json para {project_slug}: {e}")

    def audit_current_state_consistency(self) -> Tuple[bool, List[str]]:
        """
        Audita se CURRENT_STATE.json e .control-plane/sessions concordam estritamente.
        Retorna (is_consistent, issues).
        """
        issues = []
        current_state_path = self.root_dir / "CURRENT_STATE.json"
        if not current_state_path.exists():
            return True, []
        try:
            state = json.loads(current_state_path.read_text(encoding="utf-8"))
        except Exception as e:
            return False, [f"Erro ao ler CURRENT_STATE.json: {e}"]

        jarvis_canon = state.get("status", {}).get("jarvis_canonical_session")
        sessions_map = state.get("antigravity_sessions", {})
        jarvis_session_obj = sessions_map.get("jarvis", {})
        jarvis_obj_id = jarvis_session_obj.get("canonical_conversation_id")
        acp_session_obj = sessions_map.get("antigravity-control-plane", {})
        acp_obj_id = acp_session_obj.get("canonical_conversation_id")
        audit_id = state.get("workspace_binding_audit", {}).get("canonical_conversation_id")

        all_ids = set()
        for ref_name, cid in [
            ("status.jarvis_canonical_session", jarvis_canon),
            ("antigravity_sessions.jarvis.canonical_conversation_id", jarvis_obj_id),
            ("antigravity_sessions.antigravity-control-plane.canonical_conversation_id", acp_obj_id),
            ("workspace_binding_audit.canonical_conversation_id", audit_id),
        ]:
            if cid:
                all_ids.add(cid)

        if len(all_ids) > 1:
            issues.append(
                f"Contradição em CURRENT_STATE.json: múltiplos IDs canônicos encontrados: {list(all_ids)}"
            )

        acp_file = self.sessions_dir / "antigravity-control-plane.json"
        if acp_file.exists():
            try:
                acp_data = json.loads(acp_file.read_text(encoding="utf-8"))
                file_cid = acp_data.get("conversation_id")
                if file_cid and all_ids and file_cid not in all_ids:
                    issues.append(
                        f"Divergência entre .control-plane/sessions/antigravity-control-plane.json ({file_cid}) "
                        f"e CURRENT_STATE.json ({list(all_ids)})"
                    )
            except Exception as e:
                issues.append(f"Erro ao ler antigravity-control-plane.json: {e}")

        return (len(issues) == 0, issues)


    def get_project_lease(self, project_slug: str) -> Optional[Dict[str, Any]]:
        lease_file = self.leases_dir / f"{project_slug}.json"
        if not lease_file.exists():
            return None
        try:
            return json.loads(lease_file.read_text(encoding="utf-8"))
        except Exception:
            return None

    def set_project_lease(
        self,
        project_slug: str,
        issue_number: int,
        conversation_id: str,
        queue_repo: str = "xProTorkz/project-blueprint",
    ) -> None:
        lease_file = self.leases_dir / f"{project_slug}.json"
        data = {
            "project": project_slug,
            "issue_number": issue_number,
            "conversation_id": conversation_id,
            "queue_repo": queue_repo,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "last_reconciled_at": datetime.now(timezone.utc).isoformat()
        }
        lease_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def release_project_lease(self, project_slug: str) -> None:
        lease_file = self.leases_dir / f"{project_slug}.json"
        if lease_file.exists():
            lease_file.unlink(missing_ok=True)
            self.wake()

    def reconcile_project_leases(self, default_queue_repo: str = "xProTorkz/project-blueprint") -> None:
        """
        Reconcilia leases locais com o estado real no GitHub.
        Se a issue gravada no lease não estiver mais em ag:working (ou foi fechada/concluída),
        libera o lease local. Suporta leases com queue_repo dedicado e fallback legado.
        """
        for lease_file in list(self.leases_dir.glob("*.json")):
            try:
                data = json.loads(lease_file.read_text(encoding="utf-8"))
                issue_num = data.get("issue_number")
                if not issue_num:
                    lease_file.unlink(missing_ok=True)
                    self.wake()
                    continue

                queue_repo = data.get("queue_repo") or default_queue_repo
                issue = self.github.get_issue(queue_repo, int(issue_num))
                labels = [l["name"] for l in issue.get("labels", [])]
                state = issue.get("state", "open")

                if state == "closed" or "ag:working" not in labels:
                    logger.info(f"Reconciliando lease do projeto '{data.get('project')}': Issue #{issue_num} em {queue_repo} não está mais em execução (labels: {labels}). Liberando lease.")
                    lease_file.unlink(missing_ok=True)
                    self.wake()
                else:
                    data["last_reconciled_at"] = datetime.now(timezone.utc).isoformat()
                    lease_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception as e:
                logger.warning(f"Erro ao reconciliar lease {lease_file.name}: {e}")

    def is_project_busy(self, project_slug: str, current_issue_number: int, queue_repo: str) -> Optional[int]:
        """
        Verifica se o projeto já possui uma issue em execução (ag:working).
        Checa tanto o lease local reconciliado quanto issues ativas no GitHub.
        Retorna o issue_number que está executando, ou None se livre.
        """
        # 1. Checagem do lease local
        lease = self.get_project_lease(project_slug)
        if lease:
            lease_queue_repo = lease.get("queue_repo") or "xProTorkz/project-blueprint"
            active_num = lease.get("issue_number")
            # Se for a mesma issue no mesmo repositório, não está ocupado por outra
            if active_num and (active_num != current_issue_number or lease_queue_repo != queue_repo):
                try:
                    issue = self.github.get_issue(lease_queue_repo, int(active_num))
                    labels = [l["name"] for l in issue.get("labels", [])]
                    if issue.get("state") == "open" and "ag:working" in labels:
                        return int(active_num)
                    else:
                        self.release_project_lease(project_slug)
                except Exception:
                    return int(active_num)

        # 2. Checagem direta no GitHub por issues com ag:working para o projeto
        try:
            working_issues = self.github.list_issues_by_label(queue_repo, "ag:working")
            for w_issue in working_issues:
                w_num = w_issue.get("number")
                if not w_num or int(w_num) == current_issue_number:
                    continue
                try:
                    w_task = TaskParser.parse_task(
                        w_issue.get("body", ""),
                        [l["name"] for l in w_issue.get("labels", [])],
                        w_issue.get("title", ""),
                        registry=self.registry
                    )
                    if w_task.get("target_project") == project_slug:
                        self.set_project_lease(project_slug, int(w_num), "github_discovered", queue_repo=queue_repo)
                        return int(w_num)
                except Exception:
                    w_labels = [l["name"].lower() for l in w_issue.get("labels", [])]
                    if f"project:{project_slug}" in w_labels or any(project_slug in l for l in w_labels):
                        return int(w_num)
        except Exception as e:
            logger.warning(f"Aviso ao verificar issues ag:working no GitHub: {e}")

        return None

    def _load_registry(self) -> Dict[str, Any]:
        if not self.registry_file.exists():
            return {}
        try:
            data = json.loads(self.registry_file.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(f"Erro ao carregar {self.registry_file}: {e}")
            return {}

    def _refresh_registry(self) -> Dict[str, Any]:
        """
        Atualiza o registry em memória a partir da fonte canônica no GitHub.
        Em qualquer falha transitória, preserva o último registry válido e usa
        o arquivo local apenas como fallback seguro.
        """
        last_valid = self.registry if isinstance(getattr(self, "registry", None), dict) else {}

        try:
            remote_text = self.github.get_file_text(
                "xProTorkz/antigravity-control-plane",
                "PROJECT_REGISTRY.json",
                "main",
            )
            if isinstance(remote_text, str):
                remote_data = json.loads(remote_text)
                if isinstance(remote_data, dict):
                    self.registry = remote_data
                    return self.registry
                logger.error("PROJECT_REGISTRY remoto não é um objeto JSON.")
        except Exception as e:
            logger.warning(f"Falha ao atualizar PROJECT_REGISTRY remoto: {e}")

        local_data = self._load_registry()
        if local_data:
            self.registry = local_data
            return self.registry

        if last_valid:
            self.registry = last_valid
            logger.warning("Usando último PROJECT_REGISTRY válido em memória.")
            return self.registry

        self.registry = {}
        return self.registry

    def is_kill_switched(self) -> bool:
        return self.kill_switch_file.exists()

    def update_heartbeat(self) -> None:
        hb_file = self.state_dir / "heartbeat.json"
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "kill_switched": self.is_kill_switched()
        }
        try:
            hb_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def validate_workspace(
        self,
        project_slug: str,
        expected_repo_or_workspace: Any,
        expected_workspace: Optional[Path] = None,
    ) -> Path:
        self._refresh_registry()
        if project_slug not in self.registry:
            raise WorkspaceMismatchError(
                f"WORKSPACE_BINDING_MISMATCH: Projeto '{project_slug}' não consta na allowlist ({self.registry_file.name})."
            )

        entry = self.registry[project_slug]
        if not entry.get("write_allowed", False):
            raise PermissionError(f"Escrita não autorizada para '{project_slug}' em {self.registry_file.name}.")

        if isinstance(expected_repo_or_workspace, Path):
            expected_ws = expected_repo_or_workspace
            expected_repo = entry.get("repo", "")
        else:
            expected_repo = str(expected_repo_or_workspace)
            expected_ws = expected_workspace

        if entry.get("repo") != expected_repo:
            raise WorkspaceMismatchError(
                f"WORKSPACE_BINDING_MISMATCH: Repositório '{expected_repo}' diverge do configurado para '{project_slug}': '{entry.get('repo')}'."
            )

        workspace_path = Path(entry.get("workspace", ""))
        # Path traversal guard
        try:
            resolved = workspace_path.resolve()
            allowed_roots = ("/Users/lucasvinicius/projetos", str(self.root_dir.resolve()))
            if not any(str(resolved).startswith(r) for r in allowed_roots):
                raise PermissionError(f"Workspace {resolved} está fora da raiz autorizada de projetos.")
        except Exception as e:
            raise PermissionError(f"Falha na validação de caminho seguro para {workspace_path}: {e}")

        if expected_ws is not None and resolved != Path(expected_ws).resolve():
            raise WorkspaceMismatchError(
                f"WORKSPACE_BINDING_MISMATCH: Workspace configurado '{resolved}' diverge do esperado '{expected_ws}'."
            )

        # Verificação 2 (Antes da Escrita): Existência física prévia do workspace e repositório Git
        if not workspace_path.exists():
            raise WorkspaceMismatchError(
                f"WORKSPACE_BINDING_MISMATCH: Workspace físico '{workspace_path}' não existe no disco. "
                "Auto-criação de diretório desativada (Fail-Closed Obrigatório)."
            )

        # Git check
        git_dir = workspace_path / ".git"
        if not git_dir.exists():
            raise WorkspaceMismatchError(
                f"WORKSPACE_BINDING_MISMATCH: Diretório '{workspace_path}' não é um repositório Git (.git inexistente)."
            )

        # Git top-level check
        top_res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(resolved),
            capture_output=True,
            text=True
        )
        if top_res.returncode == 0:
            top_level = Path(top_res.stdout.strip()).resolve()
            if top_level != resolved:
                raise WorkspaceMismatchError(
                    f"WORKSPACE_BINDING_MISMATCH: Git toplevel '{top_level}' diverge do workspace configurado '{resolved}'."
                )

        # Remote check
        res = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(workspace_path),
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            remote_url = res.stdout.strip()
            if expected_repo.lower() not in remote_url.lower():
                raise WorkspaceMismatchError(
                    f"WORKSPACE_BINDING_MISMATCH: Remote origin '{remote_url}' diverge do esperado '{expected_repo}'."
                )

        return workspace_path

    def process_issue(self, issue: Dict[str, Any], queue_repo: str = "xProTorkz/project-blueprint") -> bool:
        issue_number = issue["number"]
        title = issue.get("title", "")
        body = issue.get("body", "")
        author = issue.get("user", {}).get("login", "")
        labels = [l["name"] for l in issue.get("labels", [])]

        logger.info(f"Analisando Issue #{issue_number}: '{title}' (autor: {author})")

        # 1. Check emergency status
        if "ag:cancelled" in labels:
            logger.info(f"Issue #{issue_number} está marcada com ag:cancelled. Ignorando.")
            self.github.update_issue_labels(queue_repo, issue_number, remove_labels=["ag:queued"])
            return False

        # 2. Author check
        if author != "xProTorkz" and not issue.get("performed_via_github_app"):
            logger.warning(f"Autor não autorizado '{author}' na Issue #{issue_number}.")
            comment_body = f"AGENT_RESULT\nSTATUS=BLOCKED\nHUMAN_GATE=Autor '{author}' não autorizado no Control Plane."
            formatted_comment = self.notification_bridge.format_comment(
                status="BLOCKED",
                project="unknown",
                issue_number=issue_number,
                repo=queue_repo,
                comment=comment_body,
                reason="UNAUTHORIZED_AUTHOR",
                labels=["ag:blocked"],
            )
            self._emit_status(
                status="BLOCKED",
                project="unknown",
                issue_number=issue_number,
                repo=queue_repo,
                comment=formatted_comment,
                reason="UNAUTHORIZED_AUTHOR",
                labels=["ag:blocked"],
            )
            self.github.add_comment(queue_repo, issue_number, formatted_comment)
            self.github.update_issue_labels(queue_repo, issue_number, add_labels=["ag:blocked"], remove_labels=["ag:queued"])
            return False

        # 3. Parse task YAML
        try:
            is_auto = any("execution:auto" == l.lower() for l in labels)
            task_meta = TaskParser.parse_task(body, labels=labels, title=title, registry=self.registry, is_auto=is_auto)
        except TaskValidationError as e:
            logger.error(f"Erro de validação do protocolo na Issue #{issue_number}: {e}")
            comment_body = f"AGENT_RESULT\nSTATUS=BLOCKED\nHUMAN_GATE=Erro no protocolo da tarefa: {e}"
            formatted_comment = self.notification_bridge.format_comment(
                status="BLOCKED",
                project="unknown",
                issue_number=issue_number,
                repo=queue_repo,
                comment=comment_body,
                reason="PROTOCOL_VALIDATION_ERROR",
                labels=["ag:blocked"],
            )
            self._emit_status(
                status="BLOCKED",
                project="unknown",
                issue_number=issue_number,
                repo=queue_repo,
                comment=formatted_comment,
                reason="PROTOCOL_VALIDATION_ERROR",
                labels=["ag:blocked"],
            )
            self.github.add_comment(queue_repo, issue_number, formatted_comment)
            self.github.update_issue_labels(queue_repo, issue_number, add_labels=["ag:blocked"], remove_labels=["ag:queued"])
            return False

        project_slug = task_meta["target_project"]
        target_repo = task_meta["target_repo"]
        baseline_sha = task_meta.get("baseline_sha")
        allowed_scope = task_meta.get("allowed_scope", [])
        repair_mode = task_meta.get("repair_mode", "normal")
        requires_human_approval = task_meta.get("requires_human_approval", False)

        # 4. Handle supersedes
        supersedes = task_meta.get("supersedes", [])
        for sup_num in supersedes:
            try:
                sup_issue = self.github.get_issue(queue_repo, int(sup_num))
                sup_labels = [l["name"] for l in sup_issue.get("labels", [])]
                if "ag:done" not in sup_labels and "ag:cancelled" not in sup_labels:
                    logger.info(f"Cancelando Issue #{sup_num} superada pela Issue #{issue_number}...")
                    self.github.add_comment(
                        queue_repo,
                        int(sup_num),
                        f"Tarefa superada e cancelada cirurgicamente pela Issue #{issue_number}."
                    )
                    self.github.update_issue_labels(
                        queue_repo,
                        int(sup_num),
                        add_labels=["ag:cancelled"],
                        remove_labels=["ag:queued", "ag:working"]
                    )
            except Exception as e:
                logger.warning(f"Não foi possível processar supersedes #{sup_num}: {e}")

        # 5. Check dependencies
        depends_on = task_meta.get("depends_on", [])
        for dep_num in depends_on:
            try:
                dep_issue = self.github.get_issue(queue_repo, int(dep_num))
                dep_labels = [l["name"] for l in dep_issue.get("labels", [])]
                if "ag:done" not in dep_labels and dep_issue.get("state") != "closed":
                    logger.info(f"Issue #{issue_number} aguardando dependência não concluída #{dep_num}.")
                    return False
            except Exception as e:
                logger.warning(f"Erro ao verificar dependência #{dep_num}: {e}")

        # 6. Validate workspace and allowlist
        try:
            workspace_path = self.validate_workspace(project_slug, target_repo)
        except Exception as e:
            logger.error(f"Validação de workspace falhou para Issue #{issue_number}: {e}")
            comment_body = f"AGENT_RESULT\nSTATUS=BLOCKED\nPROJECT={project_slug}\nHUMAN_GATE=Falha de validação de workspace: {e}"
            formatted_comment = self.notification_bridge.format_comment(
                status="BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=queue_repo,
                comment=comment_body,
                reason="WORKSPACE_VALIDATION_FAILED",
                labels=["ag:blocked"],
            )
            self._emit_status(
                status="BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=queue_repo,
                comment=formatted_comment,
                reason="WORKSPACE_VALIDATION_FAILED",
                labels=["ag:blocked"],
            )
            self.github.add_comment(queue_repo, issue_number, formatted_comment)
            self.github.update_issue_labels(queue_repo, issue_number, add_labels=["ag:blocked"], remove_labels=["ag:queued"])
            return False

        # 7. Check if project is busy with an active execution (ag:working)
        busy_issue = self.is_project_busy(project_slug, issue_number, queue_repo)
        if busy_issue:
            logger.info(f"WAITING_FOR_PROJECT_LOCK: Projeto '{project_slug}' já possui a Issue #{busy_issue} em execução (ag:working). Mantendo Issue #{issue_number} em ag:queued.")
            return False

        if self.lock_mgr.is_locked(project_slug):
            logger.info(f"Workspace '{project_slug}' está travado por outra execução em andamento. Aguardando...")
            return False

        # 8. Acquire project lock for dispatch cycle
        try:
            with self.lock_mgr(project_slug, issue_number):
                # Fetch latest git state in workspace
                try:
                    subprocess.run(["git", "fetch", "--all"], cwd=str(workspace_path), capture_output=True, timeout=20)
                except Exception:
                    pass

                head_before = AntiStaleChecker.get_current_head(workspace_path) or "unknown"

                # Anti-stale evaluation
                stale_status, stale_msg, stale_details = AntiStaleChecker.evaluate(
                    workspace_path,
                    baseline_sha,
                    allowed_scope,
                    task_title=title,
                    task_body=body
                )

                logger.info(f"AntiStale check para Issue #{issue_number}: {stale_status} - {stale_msg}")

                if stale_status == AntiStaleStatus.NOOP:
                    result_comment = (
                        f"AGENT_RESULT\n"
                        f"STATUS=NOOP\n"
                        f"PROJECT={project_slug}\n"
                        f"BASELINE_SHA={baseline_sha or 'none'}\n"
                        f"FINAL_SHA={head_before}\n"
                        f"BRANCH=main\n"
                        f"FILES_CHANGED=0\n"
                        f"TESTS=Nenhum teste necessário (solicitação já atendida)\n"
                        f"REGRESSION=NOT_RUN\n"
                        f"HUMAN_GATE=none\n"
                        f"NEXT_ACTION=Nenhuma ação necessária. {stale_msg}"
                    )
                    formatted_comment = self.notification_bridge.format_comment(
                        status="DONE",
                        project=project_slug,
                        issue_number=issue_number,
                        repo=queue_repo,
                        comment=result_comment,
                        reason="ANTI_STALE_NOOP",
                        labels=["ag:done"],
                    )
                    self._emit_status(
                        status="DONE",
                        project=project_slug,
                        issue_number=issue_number,
                        repo=queue_repo,
                        comment=formatted_comment,
                        reason="ANTI_STALE_NOOP",
                        labels=["ag:done"],
                    )
                    self.github.add_comment(queue_repo, issue_number, formatted_comment)
                    self.github.update_issue_labels(
                        queue_repo,
                        issue_number,
                        add_labels=["ag:done"],
                        remove_labels=["ag:queued", "ag:working"]
                    )
                    return True

                if stale_status == AntiStaleStatus.BLOCKED:
                    result_comment = (
                        f"AGENT_RESULT\n"
                        f"STATUS=BLOCKED\n"
                        f"PROJECT={project_slug}\n"
                        f"BASELINE_SHA={baseline_sha or 'none'}\n"
                        f"FINAL_SHA={head_before}\n"
                        f"BRANCH=main\n"
                        f"FILES_CHANGED=0\n"
                        f"TESTS=Não executado devido a conflito de arquitetura\n"
                        f"REGRESSION=NOT_RUN\n"
                        f"HUMAN_GATE=Decisão humana requerida para conflito arquitetural\n"
                        f"NEXT_ACTION={stale_msg}"
                    )
                    formatted_comment = self.notification_bridge.format_comment(
                        status="BLOCKED",
                        project=project_slug,
                        issue_number=issue_number,
                        repo=queue_repo,
                        comment=result_comment,
                        reason="ANTI_STALE_BLOCKED",
                        labels=["ag:blocked"],
                    )
                    self._emit_status(
                        status="BLOCKED",
                        project=project_slug,
                        issue_number=issue_number,
                        repo=queue_repo,
                        comment=formatted_comment,
                        reason="ANTI_STALE_BLOCKED",
                        labels=["ag:blocked"],
                    )
                    self.github.add_comment(queue_repo, issue_number, formatted_comment)
                    self.github.update_issue_labels(
                        queue_repo,
                        issue_number,
                        add_labels=["ag:blocked"],
                        remove_labels=["ag:queued", "ag:working"]
                    )
                    return True

                # Record task in state (PREPARING)
                task_state_file = self.state_dir / "current_task.json"
                task_state = {
                    "issue_number": issue_number,
                    "title": title,
                    "project": project_slug,
                    "status": "preparing",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "baseline_sha": baseline_sha or head_before,
                    "pid": os.getpid()
                }
                task_state_file.write_text(json.dumps(task_state, indent=2), encoding="utf-8")

                # Mandatory Pre-Flight Audit before mutation
                persistent_session = self.get_project_session(project_slug)
                persistent_conversation_id = (
                    persistent_session.get("conversation_id")
                    if persistent_session
                    else None
                )
                target_project_id = (
                    (persistent_session.get("project_id") if persistent_session else None)
                    or self.registry.get(project_slug, {}).get("project_id")
                )

                # Bootstrap is ONLY allowed if project has never had a session file or has a valid repair token
                session_file_exists = (self.sessions_dir / f"{project_slug}.json").exists()
                has_repair = self.has_repair_token(project_slug)
                allow_bootstrap = (not session_file_exists) or has_repair

                pre_flight = PreFlightAuditor.audit(
                    issue_number=issue_number,
                    task_meta=task_meta,
                    expected_workspace=workspace_path,
                    session_id=persistent_conversation_id,
                    session_binding_verified=True,
                    architecture_lock_path=self.root_dir / "JARVIS_ARCHITECTURE_LOCK.md" if project_slug == "antigravity-control-plane" else None,
                )
                logger.info(f"Pre-flight audit para Issue #{issue_number}: {pre_flight.passed}")

                if not pre_flight.passed:
                    logger.warning(f"Pre-flight audit FALHOU para Issue #{issue_number}:\n{pre_flight.report}")
                    comment_body = (
                        f"AGENT_RESULT\nSTATUS=BLOCKED\nPROJECT={project_slug}\n"
                        f"HUMAN_GATE=Falha na auditoria prévia (PRE_FLIGHT_AUDIT)\n\n"
                        f"```text\n{pre_flight.report}\n```"
                    )
                    formatted_comment = self.notification_bridge.format_comment(
                        status="BLOCKED",
                        project=project_slug,
                        issue_number=issue_number,
                        repo=queue_repo,
                        comment=comment_body,
                        reason="PRE_FLIGHT_FAILED",
                        labels=["ag:blocked"],
                    )
                    self._emit_status(
                        status="BLOCKED",
                        project=project_slug,
                        issue_number=issue_number,
                        repo=queue_repo,
                        comment=formatted_comment,
                        reason="PRE_FLIGHT_FAILED",
                        labels=["ag:blocked"],
                    )
                    self.github.add_comment(queue_repo, issue_number, formatted_comment)
                    self.github.update_issue_labels(
                        queue_repo,
                        issue_number,
                        add_labels=["ag:blocked"],
                        remove_labels=["ag:queued", "ag:working"]
                    )
                    if task_state_file.exists():
                        task_state_file.unlink(missing_ok=True)
                    return False

                # Trigger Antigravity Agent via Antigravity 2.0 exclusively.
                # A sessão é persistente por projeto e não pertence ao lease da Issue.
                brief = TaskParser.parse_execution_brief(body)
                fast_path_status = "NONE"
                jit_status = "N/A"

                if brief:
                    ok_fp, fp_errs = brief.validate_fast_path(
                        registry=self.registry,
                        target_repo=target_repo,
                        head_commit=head_before,
                    )
                    if ok_fp:
                        fast_path_status = "PASS"
                        logger.info(f"[FAST_PATH] FAST_PATH=PASS para Issue #{issue_number}. Envio cirúrgico imediato.")
                        try:
                            from .jit_refresh import JITRefreshManager
                            jit_res = JITRefreshManager.check_refresh(
                                workspace_path=workspace_path,
                                baseline_head=brief.baseline_sha,
                                planned_files=[f.path for f in brief.files],
                            )
                            jit_status = jit_res.status
                            logger.info(f"[JIT_REFRESH] Issue #{issue_number}: {jit_res.status} ({jit_res.message})")
                        except Exception as e:
                            logger.warning(f"Aviso no JIT Refresh para Issue #{issue_number}: {e}")
                    else:
                        logger.info(f"[FAST_PATH] Fast path não ativado para Issue #{issue_number}: {fp_errs}")

                inv_res = self.invoker.trigger_agent(
                    workspace_path,
                    issue_number,
                    title,
                    body,
                    conversation_id=persistent_conversation_id,
                    allow_bootstrap=allow_bootstrap,
                    target_project_id=target_project_id,
                    execution_brief=brief
                )
                inv_status = inv_res.get("status", "FAILED")
                inv_error = inv_res.get("error", "ANTIGRAVITY_2_NOT_CONFIRMED")
                inv_reason = inv_res.get("reason", inv_res.get("error", "Erro ao acionar Antigravity 2.0"))
                conv_id = inv_res.get("conversation_id")
                workspace_binding = inv_res.get("workspace_binding")
                new_conv_count = inv_res.get("new_conversation_created", 0)

                if (
                    inv_status != "STARTED"
                    or not conv_id
                    or conv_id == "unknown"
                    or workspace_binding != "VERIFIED"
                ):
                    if inv_status == "STARTED" and workspace_binding != "VERIFIED":
                        inv_error = "ANTIGRAVITY_CONVERSATION_WORKSPACE_UNVERIFIED"
                        inv_reason = f"Metadados da sessão indicam workspace divergente ou fora do projeto ({inv_res.get('metadata_workspace')})"
                    logger.error(f"Invocação do Antigravity 2.0 falhou/bloqueada para Issue #{issue_number}: {inv_error}")
                    blocked_comment = (
                        f"AGENT_RESULT\n"
                        f"STATUS=BLOCKED\n"
                        f"PROJECT={project_slug}\n"
                        f"HUMAN_GATE=PROJECT_SESSION_REPAIR_REQUIRED\n"
                        f"REASON={inv_reason}\n"
                        f"CANONICAL_CONVERSATION_ID={persistent_conversation_id or 'NONE'}\n"
                        f"NEW_CONVERSATION_COUNT={new_conv_count}\n"
                        f"WORKSPACE={workspace_path}\n"
                        f"METADATA_WORKSPACE={inv_res.get('metadata_workspace', 'N/A')}\n"
                        f"OUTSIDE_OF_PROJECT={inv_res.get('outside_of_project', 'UNKNOWN')}\n"
                        f"PROJECT_ID={inv_res.get('project_id', target_project_id or 'N/A')}\n"
                        f"NEXT_ACTION=Resolve session binding with repair command or confirm clean project bootstrap."
                    )
                    formatted_comment = self.notification_bridge.format_comment(
                        status="BLOCKED",
                        project=project_slug,
                        issue_number=issue_number,
                        repo=queue_repo,
                        comment=blocked_comment,
                        reason=inv_error,
                        labels=["ag:blocked"],
                    )
                    self._emit_status(
                        status="BLOCKED",
                        project=project_slug,
                        issue_number=issue_number,
                        repo=queue_repo,
                        comment=formatted_comment,
                        reason=inv_error,
                        labels=["ag:blocked"],
                    )
                    self.github.add_comment(queue_repo, issue_number, formatted_comment)
                    self.github.update_issue_labels(
                        queue_repo,
                        issue_number,
                        add_labels=["ag:blocked"],
                        remove_labels=["ag:queued"]
                    )
                    if task_state_file.exists():
                        task_state_file.unlink(missing_ok=True)
                    return False

                # Se usamos repair token no bootstrap, consome
                if has_repair:
                    self.consume_repair_token(project_slug)

                # Persiste a sessão do projeto independentemente da vida útil da Issue.
                self.set_project_session(
                    project_slug,
                    conv_id,
                    workspace_path,
                    allow_rotation=has_repair,
                    project_id=inv_res.get("project_id", target_project_id)
                )

                # Lease continua sendo apenas o lock temporário da tarefa atual.
                self.set_project_lease(project_slug, issue_number, conv_id, queue_repo=queue_repo)
                logger.info(
                    f"Antigravity 2.0 acionado com sucesso para Issue #{issue_number} "
                    f"(conv: {conv_id}, mode: {inv_res.get('session_mode', 'UNKNOWN')})"
                )

                # Atualiza estado local para working com conversation_id confirmado
                task_state["status"] = "working"
                task_state["conversation_id"] = conv_id
                task_state["context_budget"] = inv_res.get("context_budget")
                task_state["updated_at"] = datetime.now(timezone.utc).isoformat()
                task_state_file.write_text(json.dumps(task_state, indent=2), encoding="utf-8")

                # SOMENTE APÓS CONFIRMAÇÃO DE STARTED E CONVERSATION_ID: transiciona para ag:working
                self.github.update_issue_labels(
                    queue_repo,
                    issue_number,
                    add_labels=["ag:working"],
                    remove_labels=["ag:queued"]
                )

                session_mode = inv_res.get("session_mode", "UNKNOWN")
                cb = inv_res.get("context_budget") or {}
                cb_line = f"CONTEXT_BUDGET=REDUCTION_{cb.get('CONTEXT_REDUCTION_PERCENT', 0)}% (body:{cb.get('ISSUE_BODY_CHARS', 0)} -> prompt:{cb.get('PROMPT_SENT_CHARS', 0)})\n" if cb else ""
                dispatch_comment = (
                    f"AGENT_DISPATCHED\n"
                    f"STATUS=WORKING\n"
                    f"APP=Antigravity 2.0\n"
                    f"BUNDLE_ID=com.google.antigravity\n"
                    f"CONVERSATION_ID={conv_id}\n"
                    f"RUNTIME_ENDPOINT=CONFIRMED\n"
                    f"PROJECT={project_slug}\n"
                    f"WORKSPACE={workspace_path}\n"
                    f"WORKSPACE_BINDING={workspace_binding}\n"
                    f"INVOKER=agentapi\n"
                    f"SESSION_MODE={session_mode}\n"
                    f"FAST_PATH={fast_path_status}\n"
                    f"JIT_REFRESH={jit_status}\n"
                    f"{cb_line}"
                    f"NEW_CONVERSATION_COUNT={new_conv_count}\n"
                    f"OUTSIDE_OF_PROJECT={inv_res.get('outside_of_project', 'NO')}\n"
                    f"PROJECT_ID={inv_res.get('project_id', target_project_id or 'N/A')}\n"
                    f"METADATA_WORKSPACE={inv_res.get('metadata_workspace', str(workspace_path))}\n"
                    f"NEXT_ACTION=Tarefa entregue à sessão persistente do projeto.\n\n"
                    f"```text\n{pre_flight.report}\n```"
                )
                formatted_dispatch = self.notification_bridge.format_comment(
                    status="WORKING",
                    project=project_slug,
                    issue_number=issue_number,
                    repo=queue_repo,
                    comment=dispatch_comment,
                    reason="AGENT_DISPATCHED",
                    labels=["ag:working"],
                )
                self._emit_status(
                    status="WORKING",
                    project=project_slug,
                    issue_number=issue_number,
                    repo=queue_repo,
                    comment=formatted_dispatch,
                    reason="AGENT_DISPATCHED",
                    labels=["ag:working"],
                    metadata={
                        "conversation_id": conv_id,
                        "session_mode": session_mode,
                        "fast_path": fast_path_status,
                    },
                )
                self.github.add_comment(queue_repo, issue_number, formatted_dispatch)
                return True

        except LockError as e:
            logger.info(f"Lock indisponível para {project_slug}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro fatal executando Issue #{issue_number}: {e}", exc_info=True)
            comment_body = f"AGENT_RESULT\nSTATUS=BLOCKED\nPROJECT={project_slug}\nHUMAN_GATE=Erro fatal no Dispatcher: {e}"
            formatted_comment = self.notification_bridge.format_comment(
                status="BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=queue_repo,
                comment=comment_body,
                reason="FATAL_DISPATCHER_ERROR",
                labels=["ag:blocked"],
            )
            self._emit_status(
                status="BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=queue_repo,
                comment=formatted_comment,
                reason="FATAL_DISPATCHER_ERROR",
                labels=["ag:blocked"],
            )
            self.github.add_comment(queue_repo, issue_number, formatted_comment)
            self.github.update_issue_labels(
                queue_repo,
                issue_number,
                add_labels=["ag:blocked"],
                remove_labels=["ag:working"]
            )
            return False

    def complete_issue(
        self,
        queue_repo: str,
        issue_number: int,
        project_slug: str,
        head_before: str,
        allowed_scope: Optional[List[str]] = None,
        run_tests_cmd: Optional[List[str]] = None,
        requires_human_approval: bool = False,
    ) -> bool:
        """Run post-flight audit and finalize task with ag:done (or ag:review) only if audit passes."""
        workspace_path = Path(self.registry.get(project_slug, {}).get("workspace", self.root_dir))
        post_flight = PostFlightAuditor.audit(
            issue_number=issue_number,
            target_project=project_slug,
            workspace_path=workspace_path,
            head_before=head_before,
            allowed_scope=allowed_scope,
            session_binding_verified=True,
            run_tests_cmd=run_tests_cmd,
        )
        if not post_flight.passed:
            logger.error(f"Post-flight audit falhou para Issue #{issue_number}. ag:done PROIBIDO:\n{post_flight.report}")
            comment_body = (
                f"AGENT_RESULT\nSTATUS=BLOCKED\nPROJECT={project_slug}\n"
                f"HUMAN_GATE=Falha na auditoria pós-execução (POST_FLIGHT_AUDIT)\n\n"
                f"```text\n{post_flight.report}\n```"
            )
            formatted_comment = self.notification_bridge.format_comment(
                status="BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=queue_repo,
                comment=comment_body,
                reason="POST_FLIGHT_FAILED",
                labels=["ag:blocked"],
            )
            self._emit_status(
                status="BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=queue_repo,
                comment=formatted_comment,
                reason="POST_FLIGHT_FAILED",
                labels=["ag:blocked"],
            )
            self.github.add_comment(queue_repo, issue_number, formatted_comment)
            self.github.update_issue_labels(
                queue_repo,
                issue_number,
                add_labels=["ag:blocked"],
                remove_labels=["ag:working", "ag:queued"]
            )
            return False

        # Post-flight aprovado
        self.release_project_lease(project_slug)

        if requires_human_approval:
            final_status = "REVIEW"
            final_label = "ag:review"
            final_reason = "EXECUTION_REVIEW"
        else:
            final_status = "DONE"
            final_label = "ag:done"
            final_reason = "EXECUTION_DONE"

        comment_body = (
            f"AGENT_RESULT\nSTATUS={final_status}\nPROJECT={project_slug}\n\n"
            f"```text\n{post_flight.report}\n```"
        )
        formatted_comment = self.notification_bridge.format_comment(
            status=final_status,
            project=project_slug,
            issue_number=issue_number,
            repo=queue_repo,
            comment=comment_body,
            reason=final_reason,
            labels=[final_label],
        )
        self._emit_status(
            status=final_status,
            project=project_slug,
            issue_number=issue_number,
            repo=queue_repo,
            comment=formatted_comment,
            reason=final_reason,
            labels=[final_label],
        )
        self.github.add_comment(queue_repo, issue_number, formatted_comment)
        self.github.update_issue_labels(
            queue_repo,
            issue_number,
            add_labels=[final_label],
            remove_labels=["ag:working", "ag:queued"]
        )
        self.wake()
        return True

    def get_queue_repos(self, default_queue_repo: str = "xProTorkz/project-blueprint") -> List[str]:
        """Retorna a lista de repositórios de fila: central + filas próprias registradas."""
        self._refresh_registry()
        repos = [default_queue_repo]
        for proj_data in self.registry.values():
            if isinstance(proj_data, dict):
                q_repo = proj_data.get("queue_repo")
                if q_repo and q_repo not in repos:
                    repos.append(q_repo)
        return repos

    def run_cycle(self, queue_repo: Optional[str] = None) -> int:
        self.update_heartbeat()
        self._refresh_registry()

        if self.is_kill_switched():
            logger.warning("KILL_SWITCH ativo. Polling pausado.")
            return 0

        # Executa refinamento automático em issues com refinement:pending
        try:
            from .task_refiner import GitHubTaskRefiner
            refiner = GitHubTaskRefiner(root_dir=self.root_dir, github_client=self.github, registry=self.registry)
            refined_count = refiner.process_all_pending()
            if refined_count and refined_count > 0:
                self.wake()
        except Exception as e:
            logger.warning(f"Aviso no processamento de refinamento de issues: {e}")

        # Se especificado explicitamente, usa apenas o repositório solicitado (compatibilidade)
        # Caso contrário, escaneia a fila central + todas as filas próprias registradas
        repos_to_scan = [queue_repo] if queue_repo else self.get_queue_repos()

        # Reconcilia todos os leases ativos primeiro com fallback de compatibilidade
        self.reconcile_project_leases()

        processed_count = 0
        dispatched_projects_in_cycle: set[str] = set()

        for current_repo in repos_to_scan:
            if self.is_kill_switched():
                break

            issues = self.github.list_queued_issues(current_repo)
            if not issues:
                continue

            # Sort issues by priority: P0 (0), P1 (1), P2 (2), P3 (3), then issue number
            def priority_weight(it: Dict[str, Any]) -> int:
                lbls = [l["name"].lower() for l in it.get("labels", [])]
                if "priority:p0" in lbls:
                    return 0
                if "priority:p1" in lbls:
                    return 1
                if "priority:p2" in lbls:
                    return 2
                if "priority:p3" in lbls:
                    return 3
                return 2

            sorted_issues = sorted(issues, key=lambda x: (priority_weight(x), x["number"]))

            for issue in sorted_issues:
                if self.is_kill_switched():
                    break
                # Do not process Issue #2 itself in project-blueprint
                if current_repo == "xProTorkz/project-blueprint" and issue["number"] == 2:
                    continue

                # Identifica projeto alvo para garantir MAX_WRITER_PER_PROJECT = 1 nesta fase
                target_proj = None
                try:
                    meta = TaskParser.parse_task(
                        issue.get("body", ""),
                        labels=[l["name"] for l in issue.get("labels", [])],
                        title=issue.get("title", ""),
                        registry=self.registry,
                    )
                    target_proj = meta.get("target_project")
                except Exception:
                    pass

                # Se este projeto já recebeu despacho no ciclo atual, aguarda próximo ciclo
                if target_proj and target_proj in dispatched_projects_in_cycle:
                    logger.info(
                        f"MAX_WRITER_PER_PROJECT=1: Projeto '{target_proj}' já despachado neste ciclo. "
                        f"Postergando Issue #{issue['number']}."
                    )
                    continue

                if self.process_issue(issue, current_repo):
                    processed_count += 1
                    if target_proj:
                        dispatched_projects_in_cycle.add(target_proj)
                    # NÃO encerra o ciclo: continua avaliando outras tarefas de projetos diferentes!

        return processed_count


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Antigravity Control Plane Dispatcher")
    parser.add_argument(
        "--repair-session",
        nargs=2,
        metavar=("PROJECT", "CONVERSATION_ID"),
        help="Repair and rotate canonical session for a project",
    )
    parser.add_argument(
        "--create-repair-token",
        metavar="PROJECT",
        help="Create a one-time repair token for a project",
    )
    parser.add_argument(
        "--audit-consistency",
        action="store_true",
        help="Audit consistency between CURRENT_STATE.json and sessions",
    )
    args = parser.parse_args()

    disp = Dispatcher()
    if args.repair_session:
        proj, cid = args.repair_session
        disp.repair_project_session(proj, cid)
        print(f"Repaired project '{proj}' canonical session to '{cid}'.")
    elif args.create_repair_token:
        proj = args.create_repair_token
        tok = disp.create_repair_token(proj)
        print(f"Created repair token for '{proj}': {tok}")
    elif args.audit_consistency:
        ok, issues = disp.audit_current_state_consistency()
        if ok:
            print("CURRENT_STATE.json and session files are consistent.")
        else:
            print("Consistency audit FAILED:")
            for iss in issues:
                print(f"  - {iss}")
            sys.exit(1)
