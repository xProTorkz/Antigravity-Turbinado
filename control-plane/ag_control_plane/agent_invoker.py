import json
import logging
import os
import plistlib
import re
import subprocess
import time
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("ag-invoker")

ANTIGRAVITY_2_APP_PATH = Path("/Applications/Antigravity.app")
ANTIGRAVITY_2_BUNDLE_ID = "com.google.antigravity"
ANTIGRAVITY_2_MIN_MAJOR_VERSION = 2
ANTIGRAVITY_2_EXECUTABLE = Path("/Applications/Antigravity.app/Contents/MacOS/Antigravity")
ANTIGRAVITY_2_CLI = Path.home() / ".gemini" / "antigravity" / "bin" / "agentapi"

BLOCKED_LEGACY_PATTERNS = [
    "com.google.antigravity" + "-ide",
    "/Applications/Antigravity" + " IDE.app",
    "antigravity" + "-ide",
    ".antigravity" + "-ide"
]

class Antigravity2InvocationError(Exception):
    pass

class AgentInvoker:
    def __init__(
        self,
        app_path: Optional[Path] = None,
        cli_bin: Optional[Path] = None,
        bundle_id: Optional[str] = None
    ):
        self.app_path = app_path or ANTIGRAVITY_2_APP_PATH
        self.cli_bin = cli_bin or ANTIGRAVITY_2_CLI
        self.bundle_id = bundle_id or ANTIGRAVITY_2_BUNDLE_ID

    def validate_antigravity_2_identity(self) -> Dict[str, Any]:
        """
        Valida de forma estrita que o aplicativo é o Antigravity 2.0 real,
        rejeitando terminantemente qualquer bundle legado.
        """
        # 1. Checagem de caminhos e bloqueio explícito de legados
        app_str = str(self.app_path)
        cli_str = str(self.cli_bin)
        for blocked in BLOCKED_LEGACY_PATTERNS:
            if blocked in app_str or blocked in cli_str:
                raise Antigravity2InvocationError(
                    f"Tentativa de uso de bundle/binário legado bloqueado: '{blocked}'."
                )

        if not self.app_path.exists():
            raise Antigravity2InvocationError(
                f"Antigravity 2.0 não encontrado no caminho esperado: {self.app_path}"
            )

        # 2. Leitura e validação de Info.plist
        plist_path = self.app_path / "Contents" / "Info.plist"
        if not plist_path.exists():
            raise Antigravity2InvocationError(
                f"Info.plist não encontrado em {plist_path}"
            )

        try:
            with open(plist_path, "rb") as f:
                pl = plistlib.load(f)
        except Exception as e:
            raise Antigravity2InvocationError(f"Erro ao ler Info.plist do Antigravity 2.0: {e}")

        found_bundle_id = pl.get("CFBundleIdentifier")
        if found_bundle_id != self.bundle_id:
            raise Antigravity2InvocationError(
                f"Bundle ID incorreto: esperado '{self.bundle_id}', encontrado '{found_bundle_id}'."
            )

        version = pl.get("CFBundleShortVersionString") or pl.get("CFBundleVersion") or ""
        try:
            major_version = int(version.split(".")[0])
            if major_version < ANTIGRAVITY_2_MIN_MAJOR_VERSION:
                raise Antigravity2InvocationError(
                    f"Versão inválida: esperado 2.x+, encontrado '{version}'."
                )
        except Exception:
            raise Antigravity2InvocationError(f"Não foi possível validar versão 2.0 a partir de '{version}'.")

        # 3. Executável nativo
        executable = self.app_path / "Contents" / "MacOS" / pl.get("CFBundleExecutable", "Antigravity")
        if not executable.exists() or not os.access(executable, os.X_OK):
            raise Antigravity2InvocationError(f"Executável do Antigravity 2.0 inacessível: {executable}")

        # 4. CLI do Antigravity 2.0 (agentapi)
        if not self.cli_bin.exists() or not os.access(self.cli_bin, os.X_OK):
            raise Antigravity2InvocationError(f"CLI agentapi do Antigravity 2.0 não encontrada em {self.cli_bin}")

        return {
            "app_path": str(self.app_path),
            "bundle_id": found_bundle_id,
            "version": version,
            "executable": str(executable),
            "cli": str(self.cli_bin)
        }

    def is_app_running(self) -> bool:
        """Verifica se o Antigravity 2.0 ou seu language_server está em execução."""
        try:
            res = subprocess.run(["ps", "-eo", "pid,command"], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if ("Antigravity.app/Contents/MacOS/Antigravity" in line) or ("language_server" in line and "--subclient_type hub" in line):
                    return True
        except Exception:
            pass
        return False

    def ensure_app_running(self, workspace_path: Optional[Path] = None, timeout: int = 30) -> bool:
        """Garante que o Antigravity 2.0 está aberto e seu Language Server inicializado."""
        if not self.is_app_running():
            logger.info("Antigravity 2.0 não está em execução. Abrindo aplicativo...")
            open_cmd = ["open", "-b", self.bundle_id]
            if workspace_path:
                open_cmd.append(str(workspace_path))
            try:
                subprocess.run(open_cmd, capture_output=True, text=True, timeout=10)
            except Exception as e:
                logger.warning(f"Aviso ao abrir Antigravity 2.0: {e}")

        # Aguarda a prontidão do Language Server via autodescoberta
        start_t = time.time()
        while time.time() - start_t < timeout:
            try:
                creds = self.discover_ls_credentials(timeout=2)
                if creds:
                    return True
            except Exception:
                pass
            time.sleep(1)

        raise Antigravity2InvocationError(
            f"Timeout ({timeout}s) aguardando inicialização do Language Server do Antigravity 2.0."
        )

    def discover_ls_credentials(self, timeout: int = 15) -> Dict[str, Any]:
        """
        Descobre automaticamente o PID, porta/endereço gRPC e CSRF token do
        Language Server ativo do Antigravity 2.0.
        """
        start_t = time.time()
        while time.time() - start_t < timeout:
            hub_pid = None
            csrf_token = None

            # 1. Localiza processo hub
            try:
                res = subprocess.run(["ps", "-eo", "pid,command"], capture_output=True, text=True)
                for line in res.stdout.splitlines():
                    if "language_server" in line and "--subclient_type hub" in line and "grep" not in line:
                        parts = line.strip().split(None, 1)
                        try:
                            hub_pid = int(parts[0])
                        except ValueError:
                            continue
                        m = re.search(r"--csrf_token\s+([a-zA-Z0-9\-]+)", line)
                        if m:
                            csrf_token = m.group(1)
                        break
            except Exception as e:
                logger.warning(f"Erro ao inspecionar processos para LS: {e}")

            if hub_pid and csrf_token:
                # 2. Localiza portas TCP em LISTEN
                try:
                    lsof_res = subprocess.run(
                        ["lsof", "-anP", "-p", str(hub_pid), "-iTCP", "-sTCP:LISTEN"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    ports = re.findall(r":(\d+)\s+\(LISTEN\)", lsof_res.stdout)
                    ports = list(dict.fromkeys(ports))
                except Exception as e:
                    logger.warning(f"Erro ao executar lsof para PID {hub_pid}: {e}")
                    ports = []

                # 3. Testa portas para confirmar a porta gRPC válida do Language Server
                for port in ports:
                    env = {
                        "ANTIGRAVITY_LS_ADDRESS": f"localhost:{port}",
                        "ANTIGRAVITY_CSRF_TOKEN": csrf_token,
                        "ANTIGRAVITY_PROJECT_ID": "outside-of-project",
                        "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin")
                    }
                    try:
                        probe = subprocess.run(
                            [str(self.cli_bin), "get-conversation-metadata", "probe"],
                            env=env,
                            capture_output=True,
                            text=True,
                            timeout=3
                        )
                        # Se não der erro de preface/conexão recusada, encontramos o endpoint gRPC
                        if probe.returncode == 0 or "trajectory not found" in probe.stdout or "conversation" in probe.stdout:
                            return {
                                "address": f"localhost:{port}",
                                "csrf_token": csrf_token,
                                "pid": hub_pid
                            }
                    except Exception:
                        continue

            time.sleep(1)

        raise Antigravity2InvocationError(
            "Não foi possível descobrir automaticamente o LS address e CSRF token do Antigravity 2.0."
        )

    def open_workspace(self, workspace_path: Path) -> bool:
        """Abre/foca o workspace exclusivamente no Antigravity 2.0."""
        self.validate_antigravity_2_identity()

        resolved_ws = Path(workspace_path).resolve()
        if not resolved_ws.exists() or not resolved_ws.is_dir():
            raise Antigravity2InvocationError(
                f"Workspace path does not exist or is not a directory: {workspace_path}"
            )

        # Tentativa primária por Bundle ID
        try:
            res = subprocess.run(
                ["open", "-b", self.bundle_id, str(resolved_ws)],
                capture_output=True,
                text=True,
                timeout=15,
                check=False
            )
            if res.returncode == 0:
                logger.info(f"Workspace {resolved_ws} focado via bundle ID {self.bundle_id}")
                return True
        except Exception as e:
            logger.warning(f"Aviso ao abrir via bundle id {self.bundle_id}: {e}")

        # Fallback por caminho explícito do Antigravity 2.0
        try:
            res = subprocess.run(
                ["open", "-a", str(self.app_path), str(resolved_ws)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            if res.returncode == 0:
                logger.info(f"Workspace {resolved_ws} focado via app path {self.app_path}")
                return True
        except Exception as e:
            logger.error(f"Erro ao focar via app path: {e}")

        raise Antigravity2InvocationError("Falha ao abrir workspace no Antigravity 2.0.")

    def validate_conversation(
        self,
        candidate_id: Optional[str],
        workspace_path: Path,
        env: Optional[Dict[str, str]] = None,
        target_project_id: Optional[str] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Valida que a conversa indicada existe no runtime Antigravity,
        não está marcada como outside-of-project, e pertence ao workspace correto.
        """
        if not candidate_id or candidate_id in ("unknown", "github_discovered"):
            return False, "ID de conversa vazio ou desconhecido", {}
        try:
            probe = subprocess.run(
                [str(self.cli_bin), "get-conversation-metadata", candidate_id],
                cwd=str(workspace_path),
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            output = (probe.stdout or "") + "\n" + (probe.stderr or "")
            lower = output.lower()
            if probe.returncode != 0 or "not found" in lower or "trajectory not found" in lower:
                return False, f"Conversa {candidate_id} não encontrada no runtime Antigravity", {}

            try:
                meta = json.loads(probe.stdout) if (probe.stdout or "").strip() else {}
            except Exception:
                meta = {}
            metadata = (
                meta.get("response", {})
                .get("conversationMetadata", {})
                .get("metadata", {})
            )
            if not metadata and isinstance(meta, dict):
                metadata = meta.get("metadata", meta)

            actual_project_id = metadata.get("projectId")
            is_outside = False
            if actual_project_id == "outside-of-project":
                is_outside = True
            elif metadata.get("outside-of-project") is True or metadata.get("outside_of_project") is True:
                is_outside = True
            elif not metadata and "outside-of-project" in lower:
                is_outside = True

            if is_outside:
                logger.warning(
                    "Rejeitando conversa %s: metadata indica outside-of-project; workspace esperado=%s",
                    candidate_id,
                    workspace_path,
                )
                return False, "Metadata indica outside-of-project", {
                    "outside_of_project": "YES",
                    "project_id": actual_project_id
                }

            if target_project_id and actual_project_id and actual_project_id != target_project_id:
                logger.warning(
                    "Rejeitando conversa %s: projectId divergente (esperado=%s, obtido=%s)",
                    candidate_id,
                    target_project_id,
                    actual_project_id,
                )
                return False, f"projectId divergente (esperado={target_project_id}, obtido={actual_project_id})", {
                    "outside_of_project": "NO",
                    "project_id": actual_project_id
                }

            expected_resolved = str(workspace_path.resolve())
            workspaces = metadata.get("workspaces", [])
            workspace_uris = metadata.get("workspaceUris", [])
            matched_workspace = False
            metadata_workspace = None

            for ws in workspaces:
                folder = ""
                if isinstance(ws, dict):
                    folder = ws.get("workspaceFolderAbsoluteUri") or ws.get("gitRootAbsoluteUri") or ""
                elif isinstance(ws, str):
                    folder = ws
                unquoted = urllib.parse.unquote(folder).replace("file://", "")
                if unquoted and (unquoted == expected_resolved or expected_resolved in unquoted):
                    matched_workspace = True
                    metadata_workspace = unquoted
                    break

            if not matched_workspace and workspace_uris:
                for uri in workspace_uris:
                    unquoted = urllib.parse.unquote(uri).replace("file://", "")
                    if unquoted and (unquoted == expected_resolved or expected_resolved in unquoted):
                        matched_workspace = True
                        metadata_workspace = unquoted
                        break

            has_workspace_declaration = bool(workspaces or workspace_uris)
            if not matched_workspace:
                meta_text = urllib.parse.unquote(json.dumps(metadata, ensure_ascii=False))
                home_prefix = str(Path.home())
                path_tokens = re.findall(rf"{re.escape(home_prefix)}/[^\"\n]+", meta_text)
                if path_tokens:
                    has_workspace_declaration = True
                    if expected_resolved in meta_text:
                        matched_workspace = True
                        metadata_workspace = expected_resolved
                    else:
                        metadata_workspace = path_tokens[0]

            if has_workspace_declaration and not matched_workspace:
                if not metadata_workspace:
                    if workspaces:
                        first_ws = workspaces[0]
                        first_folder = first_ws.get("workspaceFolderAbsoluteUri") if isinstance(first_ws, dict) else str(first_ws)
                        metadata_workspace = urllib.parse.unquote(first_folder or "").replace("file://", "")
                    elif workspace_uris:
                        metadata_workspace = urllib.parse.unquote(workspace_uris[0]).replace("file://", "")

                return (
                    False,
                    f"Metadados da sessão indicam workspace divergente ({metadata_workspace or 'desconhecido'})",
                    {
                        "outside_of_project": "NO",
                        "project_id": actual_project_id,
                        "metadata_workspace": metadata_workspace or "N/A"
                    }
                )

            if env is not None and actual_project_id and actual_project_id != "outside-of-project":
                env["ANTIGRAVITY_PROJECT_ID"] = str(actual_project_id)

            return (
                True,
                "VERIFIED",
                {
                    "outside_of_project": "NO",
                    "project_id": actual_project_id,
                    "metadata_workspace": metadata_workspace or expected_resolved
                }
            )
        except Exception as exc:
            return False, f"Exceção ao validar conversa {candidate_id}: {exc}", {}

    def trigger_agent(
        self,
        workspace_path: Path,
        issue_number: int,
        title: str,
        instructions: str,
        model: str = "flash",
        conversation_id: Optional[str] = None,
        allow_bootstrap: bool = True,
        target_project_id: Optional[str] = None,
        execution_brief: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Entrega uma tarefa ao Antigravity 2.0 usando a CLI oficial agentapi.
        Reutiliza a conversation_id persistente quando válida via send-message.
        new-conversation é permitido somente como bootstrap quando expressamente autorizado (allow_bootstrap=True).
        Fail Closed: Se a conversa existente for inválida ou o send-message falhar, suspende com BLOCKED e PROJECT_SESSION_REPAIR_REQUIRED.
        """
        # 0. Verifica integridade dos arquivos arquiteturais
        architecture_lock_path = Path(__file__).resolve().parent.parent / "JARVIS_ARCHITECTURE_LOCK.md"
        if not architecture_lock_path.exists():
            return {
                "invoker": "agentapi",
                "app": "Antigravity 2.0",
                "bundle_id": self.bundle_id,
                "workspace": str(workspace_path),
                "status": "BLOCKED",
                "error": "ARCHITECTURE_LOCK_MISSING",
                "new_conversation_created": 0
            }

        # 1. Valida identidade estrita do 2.0
        try:
            identity = self.validate_antigravity_2_identity()
        except Antigravity2InvocationError as e:
            logger.error(f"Fail Closed: Identidade do Antigravity 2.0 não confirmada: {e}")
            return {
                "invoker": "agentapi",
                "app": "Antigravity 2.0",
                "bundle_id": self.bundle_id,
                "workspace": str(workspace_path),
                "status": "BLOCKED",
                "error": f"ANTIGRAVITY_2_NOT_CONFIRMED: {e}",
                "new_conversation_created": 0
            }

        # 2. Garante que o Antigravity 2.0 está em execução e descobre o LS address automaticamente
        try:
            self.ensure_app_running(workspace_path)
            ls_creds = self.discover_ls_credentials()
            ls_address = ls_creds["address"]
            csrf_token = ls_creds["csrf_token"]
            logger.info(f"LS address descoberto automaticamente: {ls_address} (PID: {ls_creds['pid']})")
        except Antigravity2InvocationError as e:
            logger.error(f"Fail Closed: LS address do Antigravity 2.0 não disponível: {e}")
            return {
                "invoker": "agentapi",
                "app": "Antigravity 2.0",
                "bundle_id": self.bundle_id,
                "workspace": str(workspace_path),
                "status": "BLOCKED",
                "error": f"ANTIGRAVITY_2_LS_UNAVAILABLE: {e}",
                "new_conversation_created": 0
            }

        # 3. Foca o workspace no Antigravity 2.0 (fail-closed se o caminho for inválido)
        try:
            self.open_workspace(workspace_path)
        except Exception as e:
            logger.error(f"Falha ao focar workspace no Antigravity 2.0: {e}")
            return {
                "invoker": "agentapi",
                "app": "Antigravity 2.0",
                "bundle_id": self.bundle_id,
                "workspace": str(workspace_path),
                "status": "BLOCKED",
                "error": "WORKSPACE_SWITCH_FAILED",
                "human_gate": "WORKSPACE_SWITCH_FAILED",
                "reason": f"Não foi possível abrir/focar o workspace {workspace_path}: {e}",
                "new_conversation_created": 0
            }

        # Resolução cirúrgica do ExecutionBrief
        brief = execution_brief
        if brief is None:
            from .task_parser import TaskParser
            brief = TaskParser.parse_execution_brief(instructions)

        is_control_plane = (
            "antigravity-control-plane" in str(workspace_path).lower()
            or "jarvis assistente" in str(workspace_path).lower()
        )

        architecture_fingerprint = ""
        if is_control_plane:
            architecture_fingerprint = (
                "[ARCHITECTURE FINGERPRINT — CONTROL PLANE]\n"
                "[ARCHITECTURE LOCK — HIGHEST PRECEDENCE]\n"
                "- Router tem autoridade de despacho exclusiva; Antigravity 2.0 é o único executor em sessão persistente.\n"
                "- Modificações proibidas em TASK_PROTOCOL.md e JARVIS_ARCHITECTURE_LOCK.md.\n"
                "- Em caso de conflito, interrompa e reporte ARCHITECTURE_CONFLICT.\n"
                "- Preservar isolamento estrito por projeto e single source of truth.\n\n"
            )

        if brief:
            file_plan_lines = []
            for f in brief.files:
                syms = f", símbolos: {', '.join(f.symbols)}" if f.symbols else ""
                inst = f" -> {f.instruction}" if f.instruction else ""
                file_plan_lines.append(f"- [{f.operation}] {f.path}{syms}{inst}")
            files_formatted = "\n".join(file_plan_lines) if file_plan_lines else "Nenhum arquivo especificado"

            read_only_lines = [f"- {r.path} ({r.reason})" for r in brief.read_only_context]
            read_only_formatted = "\n".join(read_only_lines) if read_only_lines else "Nenhum"
            do_not_touch_formatted = ", ".join(brief.do_not_touch) if brief.do_not_touch else "Nenhum adicional"
            tests_formatted = "\n".join(f"- {t}" for t in brief.tests) if brief.tests else "Testes padrão do projeto"
            acceptance_formatted = "\n".join(f"- {a}" for a in brief.acceptance) if brief.acceptance else "Critérios de aceite padrão"

            arch_sum_formatted = "\n".join(f"- {s}" for s in getattr(brief, "architecture_summary", [])) if getattr(brief, "architecture_summary", None) else ""
            arch_sum_block = f"\nRESUMO ARQUITETURAL (CONTEXT PACKET):\n{arch_sum_formatted}\n" if arch_sum_formatted else ""

            risks_formatted = "\n".join(f"- {r}" for r in getattr(brief, "known_risks", [])) if getattr(brief, "known_risks", None) else ""
            risks_block = f"\nRISCOS CONHECIDOS:\n{risks_formatted}\n" if risks_formatted else ""

            rollback_block = f"\nPLANO DE ROLLBACK:\n{getattr(brief, 'rollback', '')}\n" if getattr(brief, "rollback", None) else ""

            prompt = (
                f"{architecture_fingerprint}"
                f"[AGENT TASK #{issue_number}] {title}\n\n"
                f"Projeto: {brief.project}\n"
                f"Workstream: {brief.workstream}\n"
                f"Workspace: {workspace_path}\n"
                f"Objetivo: {brief.objective}\n"
                f"Baseline SHA: {brief.baseline_sha}\n"
                f"Skill Primária: {brief.skill_primary}\n\n"
                f"REGRAS OPERACIONAIS OBRIGATÓRIAS (SURGICAL EXECUTOR MODE):\n"
                f"EXECUTOR_MODE = SURGICAL\n"
                f"PROJECT_DISCOVERY = FORBIDDEN\n"
                f"FULL_REPO_AUDIT = FORBIDDEN\n"
                f"SKILL_RESELECTION = FORBIDDEN\n"
                f"TOOL_PRIORITY = 1:API > 2:MCP > 3:CLI > 4:SDK > 5:SCRIPT > 6:HTTP > 7:BROWSER > 8:APPLESCRIPT\n"
                f"BROWSER_AND_APPLESCRIPT = LAST_RESORT (Search API/CLI/MCP first)\n"
                f"ANTI_LOOP_MAX_RETRIES = 3\n"
                f"IF_NO_PROGRESS_IN_3_STEPS = STOP_APPROACH_AND_SWITCH_STRATEGY\n"
                f"VERIFIABLE_PROGRESS_REQUIRED = true (command execution without state change != progress)\n"
                f"READ_ALLOWED = file_plan + read_only_context\n"
                f"IF_CONTEXT_INSUFFICIENT = RETURN NEEDS_REFINEMENT\n"
                f"DO_NOT_EXPAND_SCOPE = true\n"
                f"{arch_sum_block}"
                f"\nARQUIVOS DO FILE PLAN (PERMITIDOS PARA LEITURA/ESCRITA):\n"
                f"{files_formatted}\n\n"
                f"CONTEXTO READ-ONLY RESTRITO:\n"
                f"{read_only_formatted}\n\n"
                f"ARQUIVOS PROIBIDOS (DO NOT TOUCH):\n"
                f"{do_not_touch_formatted}\n\n"
                f"TESTES OBRIGATÓRIOS:\n"
                f"{tests_formatted}\n\n"
                f"CRITÉRIOS DE ACEITE:\n"
                f"{acceptance_formatted}\n"
                f"{risks_block}"
                f"{rollback_block}\n"
                f"Ao finalizar, realize commits limpos no repositório local e relate arquivos alterados e testes comprovados."
            )

            issue_body_chars = len(instructions or "")
            execution_brief_chars = len(brief.to_yaml()) if hasattr(brief, "to_yaml") else len(str(brief))
            prompt_sent_chars = len(prompt)
            files_allowed_count = len(brief.files)
            read_only_context_count = len(brief.read_only_context)
            legacy_estimated_chars = issue_body_chars + 25000
            reduction_percent = round((1.0 - (prompt_sent_chars / max(legacy_estimated_chars, prompt_sent_chars))) * 100, 2)

            context_budget = {
                "ISSUE_BODY_CHARS": issue_body_chars,
                "EXECUTION_BRIEF_CHARS": execution_brief_chars,
                "PROMPT_SENT_CHARS": prompt_sent_chars,
                "FILES_ALLOWED_COUNT": files_allowed_count,
                "READ_ONLY_CONTEXT_COUNT": read_only_context_count,
                "CONTEXT_REDUCTION_PERCENT": reduction_percent,
            }
            logger.info(
                f"[CONTEXT_BUDGET] Issue #{issue_number}: body_chars={issue_body_chars}, "
                f"brief_chars={execution_brief_chars}, prompt_chars={prompt_sent_chars}, "
                f"reduction={reduction_percent}%"
            )
        else:
            prompt = (
                f"{architecture_fingerprint}"
                f"[AGENT TASK #{issue_number}] {title}\n\n"
                f"Workspace: {workspace_path}\n\n"
                f"INSTRUÇÕES OBRIGATÓRIAS:\n"
                f"{instructions}\n\n"
                f"Ao finalizar, realize commits limpos no repositório local e relate arquivos alterados e testes."
            )
            context_budget = {
                "ISSUE_BODY_CHARS": len(instructions or ""),
                "EXECUTION_BRIEF_CHARS": 0,
                "PROMPT_SENT_CHARS": len(prompt),
                "FILES_ALLOWED_COUNT": 0,
                "READ_ONLY_CONTEXT_COUNT": 0,
                "CONTEXT_REDUCTION_PERCENT": 0.0,
            }

        # 4. Injeta credenciais descobertas no ambiente
        env = os.environ.copy()
        env["ANTIGRAVITY_LS_ADDRESS"] = ls_address
        env["ANTIGRAVITY_CSRF_TOKEN"] = csrf_token
        for k in ["ANTIGRAVITY_SOURCE_METADATA", "ANTIGRAVITY_CONVERSATION_ID", "ANTIGRAVITY_AGENT", "ANTIGRAVITY_TRAJECTORY_ID"]:
            env.pop(k, None)
        if env.get("ANTIGRAVITY_PROJECT_ID") == "outside-of-project":
            env.pop("ANTIGRAVITY_PROJECT_ID", None)
        if target_project_id:
            env["ANTIGRAVITY_PROJECT_ID"] = str(target_project_id)
        env["JARVIS_CANONICAL_WORKSPACE"] = str(workspace_path)

        def _validate_conversation(candidate_id: Optional[str]) -> Tuple[bool, str, Dict[str, Any]]:
            return self.validate_conversation(candidate_id, workspace_path, env, target_project_id)

        def _conversation_is_valid(candidate_id: Optional[str]) -> bool:
            valid, _, _ = _validate_conversation(candidate_id)
            return valid

        try:
            # 5. Caminho canônico: reutilizar sessão persistente do projeto.
            if conversation_id:
                valid, reason, meta_info = _validate_conversation(conversation_id)
                if not valid:
                    logger.warning(
                        f"Conversa existente {conversation_id} inválida: {reason}. "
                        "Fail-closed: new-conversation bloqueado."
                    )
                    return {
                        "status": "BLOCKED",
                        "error": "PROJECT_SESSION_REPAIR_REQUIRED",
                        "human_gate": "PROJECT_SESSION_REPAIR_REQUIRED",
                        "reason": f"Canonical session {conversation_id} failed binding verification ({reason}). Manual repair required.",
                        "conversation_id": conversation_id,
                        "new_conversation_created": 0,
                        "workspace_binding": "FAILED",
                        "outside_of_project": meta_info.get("outside_of_project", "UNKNOWN"),
                        "project_id": meta_info.get("project_id", "N/A"),
                        "metadata_workspace": meta_info.get("metadata_workspace", str(workspace_path)),
                    }

                logger.info(
                    f"Reutilizando conversa persistente {conversation_id} para Issue #{issue_number}."
                )
                res = subprocess.run(
                    [str(self.cli_bin), "send-message", conversation_id, prompt],
                    cwd=str(workspace_path),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                output = (res.stdout or "") + ("\n" + res.stderr if res.stderr else "")
                if res.returncode == 0:
                    return {
                        "invoker": "agentapi",
                        "app": "Antigravity 2.0",
                        "bundle_id": identity["bundle_id"],
                        "version": identity["version"],
                        "conversation_id": conversation_id,
                        "session_mode": "REUSED",
                        "ls_address": ls_address,
                        "workspace": str(workspace_path),
                        "workspace_binding": "VERIFIED",
                        "status": "STARTED",
                        "output": output,
                        "new_conversation_created": 0,
                        "outside_of_project": "NO",
                        "project_id": meta_info.get("project_id"),
                        "metadata_workspace": meta_info.get("metadata_workspace", str(workspace_path)),
                        "context_budget": context_budget
                    }
                logger.error(
                    f"send-message falhou para {conversation_id}: {output}. "
                    "Fail-closed: new-conversation bloqueado."
                )
                return {
                    "status": "BLOCKED",
                    "error": "PROJECT_SESSION_REPAIR_REQUIRED",
                    "human_gate": "PROJECT_SESSION_REPAIR_REQUIRED",
                    "reason": f"Falha ao enviar mensagem para sessão canônica ({conversation_id}): {output}. Manual repair required.",
                    "conversation_id": conversation_id,
                    "new_conversation_created": 0,
                    "workspace_binding": "VERIFIED",
                }

            # 6. Bootstrap somente quando expressamente autorizado (nenhuma sessão prévia ou reparo autorizado).
            if not allow_bootstrap:
                logger.error(
                    f"Bootstrap desautorizado para Issue #{issue_number}: projeto já possui histórico de sessão ou requer reparo manual."
                )
                return {
                    "status": "BLOCKED",
                    "error": "PROJECT_SESSION_REPAIR_REQUIRED",
                    "human_gate": "PROJECT_SESSION_REPAIR_REQUIRED",
                    "reason": "Bootstrap desautorizado: o projeto requer reparo manual da sessão canônica existente.",
                    "new_conversation_created": 0,
                    "workspace_binding": "FAILED",
                }

            logger.info(
                f"Bootstrap autorizado de conversa Antigravity para Issue #{issue_number}; "
                "new-conversation não será usado novamente enquanto esta sessão permanecer válida."
            )
            cmd = [
                str(self.cli_bin),
                "new-conversation",
                f"--model={model}",
                f"--title=[PROJECT SESSION] {workspace_path.name}",
                prompt
            ]
            res = subprocess.run(
                cmd,
                cwd=str(workspace_path),
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
            output = (res.stdout or "") + ("\n" + res.stderr if res.stderr else "")
            conversation_id_new = None
            if res.returncode == 0:
                try:
                    parsed_json = json.loads(res.stdout)
                    conversation_id_new = (
                        parsed_json.get("response", {})
                        .get("newConversation", {})
                        .get("conversationId")
                    )
                except Exception as parse_err:
                    logger.warning(f"Erro ao interpretar JSON de agentapi: {parse_err}")

                if not conversation_id_new:
                    return {
                        "invoker": "agentapi",
                        "app": "Antigravity 2.0",
                        "bundle_id": identity["bundle_id"],
                        "workspace": str(workspace_path),
                        "status": "FAILED",
                        "error": f"NO_CONVERSATION_ID_RETURNED: {output}",
                        "new_conversation_created": 0,
                    }

                valid, reason, meta_info = _validate_conversation(conversation_id_new)
                if not valid:
                    return {
                        "invoker": "agentapi",
                        "app": "Antigravity 2.0",
                        "bundle_id": identity["bundle_id"],
                        "workspace": str(workspace_path),
                        "conversation_id": conversation_id_new,
                        "status": "BLOCKED",
                        "error": "ANTIGRAVITY_CONVERSATION_WORKSPACE_UNVERIFIED",
                        "human_gate": "PROJECT_SESSION_REPAIR_REQUIRED",
                        "reason": reason,
                        "output": output,
                        "new_conversation_created": 1,
                        "workspace_binding": "FAILED"
                    }

                return {
                    "invoker": "agentapi",
                    "app": "Antigravity 2.0",
                    "bundle_id": identity["bundle_id"],
                    "version": identity["version"],
                    "conversation_id": conversation_id_new,
                    "session_mode": "CREATED_BOOTSTRAP",
                    "ls_address": ls_address,
                    "workspace": str(workspace_path),
                    "workspace_binding": "VERIFIED",
                    "status": "STARTED",
                    "output": output,
                    "new_conversation_created": 1,
                    "outside_of_project": "NO",
                    "project_id": meta_info.get("project_id"),
                    "metadata_workspace": meta_info.get("metadata_workspace", str(workspace_path)),
                    "context_budget": context_budget
                }

            return {
                "invoker": "agentapi",
                "app": "Antigravity 2.0",
                "bundle_id": identity["bundle_id"],
                "workspace": str(workspace_path),
                "status": "FAILED",
                "error": output,
                "new_conversation_created": 0,
            }
        except Exception as e:
            logger.error(f"Exceção ao invocar Antigravity 2.0 agentapi: {e}")
            return {
                "invoker": "agentapi",
                "app": "Antigravity 2.0",
                "bundle_id": identity["bundle_id"],
                "workspace": str(workspace_path),
                "status": "FAILED",
                "error": str(e),
                "new_conversation_created": 0,
            }
