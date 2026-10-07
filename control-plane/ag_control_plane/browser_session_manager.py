"""Browser Session Manager & Desktop/Browser Routing (Background First & Session Reuse).

Diretrizes:
- BACKGROUND_BY_DEFAULT = YES
- ACTIVATE_BROWSER_BY_DEFAULT = NO
- FOREGROUND_ONLY_FOR_HUMAN_GATE = YES
- REUSE_RUNNING_BROWSER = YES
- REUSE_EXISTING_TAB = YES
- PRESERVE_LOGIN_SESSION = YES (Usa perfil normal existente, nunca perfis temporários/incógnito)
- DO_NOT_EXPORT_COOKIES / TOKENS / PASSWORDS = YES
- Deduplicação de abas: prioridade URL exata > domínio+path > domínio > título > criar nova.
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger("ag-browser-session-mgr")

KNOWN_SERVICES: Dict[str, Dict[str, Any]] = {
    "cloudflare": {
        "domains": ["dash.cloudflare.com", "cloudflare.com"],
        "default_url": "https://dash.cloudflare.com",
        "login_markers": ["/login", "/sign-in", "auth"],
    },
    "github": {
        "domains": ["github.com"],
        "default_url": "https://github.com",
        "login_markers": ["/login", "/session"],
    },
    "google_flow": {
        "domains": ["flow.google.com"],
        "default_url": "https://flow.google.com",
        "login_markers": ["accounts.google.com"],
    },
    "openai": {
        "domains": ["chatgpt.com", "chat.openai.com", "platform.openai.com"],
        "default_url": "https://chatgpt.com",
        "login_markers": ["/auth/login", "/login"],
    },
    "chatgpt": {
        "domains": ["chatgpt.com", "chat.openai.com"],
        "default_url": "https://chatgpt.com",
        "login_markers": ["/auth/login", "/login"],
    },
    "youtube": {
        "domains": ["youtube.com"],
        "default_url": "https://www.youtube.com",
        "login_markers": ["accounts.google.com"],
    },
    "google": {
        "domains": ["google.com"],
        "default_url": "https://www.google.com",
        "login_markers": ["accounts.google.com"],
    },
    "netflix": {
        "domains": ["netflix.com"],
        "default_url": "https://www.netflix.com",
        "login_markers": ["/login"],
    },
    "aws": {
        "domains": ["console.aws.amazon.com", "aws.amazon.com"],
        "default_url": "https://console.aws.amazon.com",
        "login_markers": ["/signin"],
    },
}



@dataclass
class BrowserTab:
    window_id: str
    tab_id: str
    url: str
    title: str
    browser: str = "Google Chrome"
    is_authenticated: bool = True
    created_by_worker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrowserTabResult:
    status: str  # "REUSED", "CREATED", "ALREADY_OPEN", "FAILED"
    tab: Optional[BrowserTab]
    reused: bool
    created: bool
    browser_reused: bool
    message: str


@dataclass
class Checkpoint:
    task_id: str
    worker_id: str
    service: str
    browser: str
    window_id: str
    tab_id: str
    current_url: str
    operation: str
    step: int
    expected_next_state: str
    foreground_app_before: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BrowserSessionManager:
    """Gerenciador unificado de sessões de navegador com reuso de abas e execução em background."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent
        self.sessions_meta_file = self.root_dir / ".control-plane" / "browser_sessions.json"
        self.checkpoints_dir = self.root_dir / ".control-plane" / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

        # Telemetria leve
        self.metrics: Dict[str, int] = {
            "BROWSER_REUSE_COUNT": 0,
            "TAB_REUSE_COUNT": 0,
            "TAB_CREATE_COUNT": 0,
            "DUPLICATE_TAB_PREVENTED": 0,
            "LOGIN_SESSION_REUSED": 0,
            "LOGIN_GATE_COUNT": 0,
            "CAPTCHA_GATE_COUNT": 0,
            "MFA_GATE_COUNT": 0,
            "FOREGROUND_ACTIVATION_COUNT": 0,
            "APPLE_SCRIPT_CALLS": 0,
            "BROWSER_TOOL_CALLS": 0,
            "API_CALLS": 0,
            "CLI_CALLS": 0,
            "NO_PROGRESS_ABORTS": 0,
            "ALTERNATIVE_PATH_SWITCHES": 0,
            "BACKGROUND_BROWSER_TASKS": 0,
        }

    def is_browser_running(self, browser: str = "Google Chrome") -> bool:
        """Verifica se o navegador está ativo sem interagir com a interface gráfica."""
        try:
            res = subprocess.run(["pgrep", "-f", browser], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    def list_tabs(self, browser: str = "Google Chrome") -> List[BrowserTab]:
        """Lista todas as abas abertas em background sem ativar a janela."""
        if not self.is_browser_running(browser):
            return []

        self.metrics["APPLE_SCRIPT_CALLS"] += 1
        script = f"""
        tell application "{browser}"
            set output to ""
            repeat with w in windows
                set wid to id of w
                repeat with t in tabs of w
                    set tid to id of t
                    set turl to URL of t
                    set ttitle to title of t
                    set output to output & (wid as text) & "\\t" & (tid as text) & "\\t" & turl & "\\t" & ttitle & "\\n"
                end repeat
            end repeat
            return output
        end tell
        """
        try:
            res = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode != 0:
                return []

            tabs = []
            for line in res.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    wid = parts[0].strip()
                    tid = parts[1].strip()
                    url = parts[2].strip()
                    title = parts[3].strip() if len(parts) > 3 else ""

                    # Detecta marcadores de login para saber se a aba está autenticada
                    is_auth = not any(
                        m in url.lower() for svc in KNOWN_SERVICES.values() for m in svc["login_markers"]
                    )
                    tabs.append(BrowserTab(
                        window_id=wid,
                        tab_id=tid,
                        url=url,
                        title=title,
                        browser=browser,
                        is_authenticated=is_auth,
                    ))
            return tabs
        except Exception as e:
            logger.debug(f"Falha ao listar abas de {browser}: {e}")
            return []

    def find_tab(
        self,
        browser: str = "Google Chrome",
        domain: Optional[str] = None,
        url_prefix: Optional[str] = None,
        title_contains: Optional[str] = None,
        exact_url: Optional[str] = None,
        prefer_authenticated: bool = True,
    ) -> Optional[BrowserTab]:
        """Encontra uma aba existente respeitando a prioridade estrita de seleção.

        Prioridade:
        1. URL exata
        2. Domínio + path relevante
        3. Domínio (preferindo aba autenticada se houver)
        4. Título da página
        """
        tabs = self.list_tabs(browser)
        if not tabs:
            return None

        # 1. URL exata
        if exact_url:
            for t in tabs:
                if t.url == exact_url:
                    return t

        # 2. Domínio + path relevante (url_prefix)
        if url_prefix:
            matches = [t for t in tabs if t.url.startswith(url_prefix)]
            if matches:
                if prefer_authenticated:
                    auth_matches = [m for m in matches if m.is_authenticated]
                    if auth_matches:
                        return auth_matches[0]
                return matches[0]

        # 3. Domínio
        if domain:
            dom_lower = domain.lower().strip()
            matches = []
            for t in tabs:
                parsed = urlparse(t.url)
                netloc = (parsed.netloc or "").lower()
                if dom_lower in netloc or (netloc and netloc in dom_lower):
                    matches.append(t)
            if matches:
                if prefer_authenticated:
                    auth_matches = [m for m in matches if m.is_authenticated]
                    if auth_matches:
                        return auth_matches[0]
                return matches[0]

        # 4. Título
        if title_contains:
            tit_lower = title_contains.lower().strip()
            matches = [t for t in tabs if tit_lower in t.title.lower()]
            if matches:
                return matches[0]

        return None

    def reuse_or_create_tab(
        self,
        target: str,
        browser: str = "Google Chrome",
        explicit_new_tab: bool = False,
        background: bool = True,
    ) -> BrowserTabResult:
        """Reutiliza aba compatível existente ou cria UMA nova em background se necessário."""
        # Mapeamento de serviço conhecido
        service_key = target.lower().strip()
        svc_info = KNOWN_SERVICES.get(service_key)

        target_url = svc_info["default_url"] if svc_info else target
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = f"https://{target_url}"

        domain = svc_info["domains"][0] if svc_info else urlparse(target_url).netloc
        browser_was_running = self.is_browser_running(browser)

        # Se não há pedido explícito de nova aba, procura aba existente
        if not explicit_new_tab:
            found = self.find_tab(browser=browser, domain=domain, exact_url=target_url)
            if found:
                self.metrics["TAB_REUSE_COUNT"] += 1
                if browser_was_running:
                    self.metrics["BROWSER_REUSE_COUNT"] += 1
                if found.is_authenticated:
                    self.metrics["LOGIN_SESSION_REUSED"] += 1

                logger.info(f"[BROWSER_REUSE] Aba existente reutilizada: {found.url} (ID: {found.tab_id})")
                return BrowserTabResult(
                    status="REUSED",
                    tab=found,
                    reused=True,
                    created=False,
                    browser_reused=browser_was_running,
                    message=f"Reutilizando aba existente para {domain}.",
                )

        # Se chegou aqui, precisamos abrir/criar a aba
        if not browser_was_running:
            # Abre o browser em background (-g) com o perfil real
            cmd = ["open", "-g", "-a", browser, target_url]
            try:
                subprocess.run(cmd, check=False, timeout=5)
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"Erro ao abrir {browser}: {e}")
        else:
            # Browser já rodando: abre aba em background sem ativar o aplicativo
            self.metrics["APPLE_SCRIPT_CALLS"] += 1
            script = f"""
            tell application "{browser}"
                if (count of windows) is 0 then
                    make new window
                    set URL of active tab of front window to "{target_url}"
                else
                    tell front window to make new tab with properties {{URL:"{target_url}"}}
                end if
            end tell
            """
            try:
                subprocess.run(["osascript", "-e", script], check=False, timeout=5)
            except Exception as e:
                logger.warning(f"Erro ao criar aba em {browser}: {e}")

        self.metrics["TAB_CREATE_COUNT"] += 1
        new_tab = BrowserTab(
            window_id="new",
            tab_id="new",
            url=target_url,
            title=target,
            browser=browser,
            is_authenticated=True,
            created_by_worker=True,
        )
        return BrowserTabResult(
            status="CREATED",
            tab=new_tab,
            reused=False,
            created=True,
            browser_reused=browser_was_running,
            message=f"Nova aba aberta em background para {target_url}.",
        )

    def handle_command(self, text: str) -> Dict[str, Any]:
        """Interpreta semântica de abertura de desktop/browser com preservação rigorosa de foco."""
        clean = text.lower().strip()

        # 1. Abertura explícita de NOVA aba
        is_explicit_new = bool(re.search(r"\b(?:nova\s+aba|outra\s+aba|crie\s+uma\s+aba|cria\s+uma\s+aba|abre\s+uma\s+nova\s+aba)\b", clean))

        # 2. Comando apenas de abrir o Chrome (ex: "abre o Chrome", "abrir Chrome")
        is_open_browser_only = bool(re.search(r"^(?:por\s+favor\s+)?(?:abrir|abre|abra|iniciar|inicia)\s+(?:o\s+)?(?:google\s+)?chrome$", clean))
        if is_open_browser_only and not is_explicit_new:
            running = self.is_browser_running("Google Chrome")
            if running:
                self.metrics["BROWSER_REUSE_COUNT"] += 1
                return {
                    "action": "BROWSER_REUSE",
                    "browser": "Google Chrome",
                    "existing_browser_reused": True,
                    "new_tab_created": False,
                    "status": "DONE",
                    "message": "Google Chrome já está em execução. Nenhuma aba duplicada criada.",
                    "speech": "O Google Chrome já está aberto, Lucas.",
                }
            else:
                subprocess.run(["open", "-a", "Google Chrome"], check=False, timeout=5)
                return {
                    "action": "BROWSER_OPENED",
                    "browser": "Google Chrome",
                    "existing_browser_reused": False,
                    "new_tab_created": False,
                    "status": "DONE",
                    "message": "Google Chrome aberto com o perfil padrão do usuário.",
                    "speech": "Abrindo o Google Chrome para você, Lucas.",
                }

        # 3. Comando para abrir serviço (ex: "abre o Cloudflare", "abre o GitHub")
        for svc_name, svc_data in KNOWN_SERVICES.items():
            if svc_name in clean or any(d in clean for d in svc_data["domains"]):
                res = self.reuse_or_create_tab(
                    target=svc_name,
                    browser="Google Chrome",
                    explicit_new_tab=is_explicit_new,
                    background=True,
                )
                if res.reused:
                    self.metrics["DUPLICATE_TAB_PREVENTED"] += 1
                    return {
                        "action": "TAB_REUSE",
                        "service": svc_name,
                        "tab_reused": True,
                        "new_tab_created": False,
                        "status": "DONE",
                        "message": f"Aba existente do {svc_name.title()} reutilizada em segundo plano.",
                        "speech": f"A aba do {svc_name.title()} já estava aberta e pronta, Lucas.",
                    }
                else:
                    return {
                        "action": "TAB_CREATED",
                        "service": svc_name,
                        "tab_reused": False,
                        "new_tab_created": True,
                        "status": "DONE",
                        "message": f"Aba do {svc_name.title()} criada em background.",
                        "speech": f"Abri o {svc_name.title()} em segundo plano para você, Lucas.",
                    }

        # 4. Fallback para comando genérico de nova aba se explícito
        if is_explicit_new:
            res = self.reuse_or_create_tab(
                target="https://chrome.google.com",
                browser="Google Chrome",
                explicit_new_tab=True,
                background=True,
            )
            return {
                "action": "TAB_CREATED",
                "tab_reused": False,
                "new_tab_created": True,
                "status": "DONE",
                "message": "Nova aba criada no Google Chrome.",
                "speech": "Abri uma nova aba para você, Lucas.",
            }

        return {"action": "NO_OP", "status": "SKIPPED", "message": "Nenhuma ação de browser identificada."}

    # =========================================================================
    # Focus Ownership & Human Gates
    # =========================================================================

    def get_frontmost_app(self) -> Optional[str]:
        """Identifica o aplicativo em primeiro plano antes de qualquer intervenção humana."""
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        try:
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def restore_focus(self, app_name: str) -> bool:
        """Restaura o foco ao aplicativo que o usuário estava usando antes do Human Gate."""
        if not app_name:
            return False
        try:
            subprocess.run(["open", "-a", app_name], check=False, timeout=3)
            return True
        except Exception:
            return False

    def trigger_human_gate(
        self,
        gate_type: str,
        tab: BrowserTab,
        task_id: str,
        reason: str,
        expected_state: str,
    ) -> Checkpoint:
        """Aciona Human Gate de forma segura salvando checkpoint sem expor credenciais."""
        prev_app = self.get_frontmost_app()
        self.metrics["FOREGROUND_ACTIVATION_COUNT"] += 1

        if "captcha" in gate_type.lower():
            self.metrics["CAPTCHA_GATE_COUNT"] += 1
        elif "mfa" in gate_type.lower():
            self.metrics["MFA_GATE_COUNT"] += 1
        elif "login" in gate_type.lower():
            self.metrics["LOGIN_GATE_COUNT"] += 1

        cp = Checkpoint(
            task_id=task_id,
            worker_id=f"worker_{task_id}",
            service=tab.title or "web_service",
            browser=tab.browser,
            window_id=tab.window_id,
            tab_id=tab.tab_id,
            current_url=tab.url,
            operation="HUMAN_GATE",
            step=1,
            expected_next_state=expected_state,
            foreground_app_before=prev_app,
        )

        cp_file = self.checkpoints_dir / f"{task_id}.json"
        cp_file.write_text(json.dumps(cp.to_dict(), indent=2), encoding="utf-8")

        # Traz SOMENTE esta aba para a frente para o usuário resolver o gate
        self.metrics["APPLE_SCRIPT_CALLS"] += 1
        script = f"""
        tell application "{tab.browser}"
            activate
            tell window id {tab.window_id}
                set index to 1
            end tell
        end tell
        """
        try:
            subprocess.run(["osascript", "-e", script], check=False, timeout=3)
        except Exception:
            pass

        logger.info(f"[HUMAN_GATE] Acionado {gate_type} para task {task_id}. App anterior: {prev_app}")
        return cp

    def resume_from_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        """Retoma execução a partir do checkpoint salvo, sem reiniciar do início."""
        cp_file = self.checkpoints_dir / f"{task_id}.json"
        if not cp_file.exists():
            return None
        try:
            data = json.loads(cp_file.read_text(encoding="utf-8"))
            cp = Checkpoint(**data)
            # Remove checkpoint após consumo seguro
            cp_file.unlink(missing_ok=True)

            # Restaura foco se havia app anterior gravado
            if cp.foreground_app_before:
                self.restore_focus(cp.foreground_app_before)

            logger.info(f"[RESUME_CHECKPOINT] Tarefa {task_id} resumida do passo {cp.step}. Foco restaurado para {cp.foreground_app_before}.")
            return cp
        except Exception as e:
            logger.warning(f"Erro ao resumir checkpoint {task_id}: {e}")
            return None

    def check_session_health(self, tab: BrowserTab) -> Dict[str, Any]:
        """Verifica se a aba está autenticada ou se precisa de login/captcha/mfa."""
        url_lower = tab.url.lower()
        title_lower = tab.title.lower()

        # 1. Detecção de CAPTCHA
        if any(c in url_lower or c in title_lower for c in ["captcha", "challenge", "cf-chl-widget", "turnstile", "recaptcha"]):
            return {
                "health": "CAPTCHA_DETECTED",
                "gate_required": True,
                "gate_type": "HUMAN_GATE_CAPTCHA_REQUIRED",
                "reason": "Desafio CAPTCHA/Turnstile detectado na página.",
            }

        # 2. Detecção de MFA / 2FA
        if any(m in url_lower or m in title_lower for m in ["/mfa", "/2fa", "two-factor", "authenticator", "passkey"]):
            return {
                "health": "MFA_DETECTED",
                "gate_required": True,
                "gate_type": "HUMAN_GATE_MFA_REQUIRED",
                "reason": "Verificação em duas etapas (MFA/Passkey) requerida.",
            }

        # 3. Detecção de Login Expirado / Necessário
        is_login = any(
            marker in url_lower
            for svc in KNOWN_SERVICES.values()
            for marker in svc.get("login_markers", [])
        )
        if is_login or "login" in url_lower or "sign-in" in url_lower:
            return {
                "health": "LOGIN_REQUIRED",
                "gate_required": True,
                "gate_type": "HUMAN_GATE_LOGIN_REQUIRED",
                "reason": "Sessão não autenticada ou expirada. Login manual necessário.",
            }

        return {
            "health": "AUTHENTICATED",
            "gate_required": False,
            "gate_type": None,
            "reason": "Sessão válida e ativa.",
        }

    def should_use_browser(self, available_tools: List[str]) -> Tuple[bool, str]:
        """Avalia se o browser deve ser utilizado com base na prioridade estrita de ferramentas."""
        try:
            from ag_control_plane.tool_priority import ToolPriorityPolicy
            allowed, msg, best = ToolPriorityPolicy.enforce_priority("browser", available_tools)
            if not allowed:
                return False, msg
        except Exception:
            pass
        return True, "Nenhuma alternativa de API/CLI disponível. Browser autorizado como fallback."

