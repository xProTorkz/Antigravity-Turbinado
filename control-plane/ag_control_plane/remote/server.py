import json
import logging
import os
import subprocess
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import socket

from urllib.parse import parse_qs, urlparse
import re

from .pairing import PairingManager
from .context_bridge import LocalContextBridge

logger = logging.getLogger("ag-remote-server")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_PORT = 8765
DEFAULT_ALEXA_SKILL_ID = "amzn1.ask.skill.b5215356-dc43-4d42-9d2b-803f42191188"


class JarvisRemoteHandler(BaseHTTPRequestHandler):
    """
    HTTP Request Handler for the Jarvis Remote Bridge.
    Enforces authentication, executes authorized macOS system controls,
    and reports live telemetry and Orb state to the paired iPhone.
    """

    server_version = "JarvisRemoteControl/1.0"

    @property
    def pairing_manager(self) -> PairingManager:
        return self.server.pairing_manager  # type: ignore

    @property
    def context_bridge(self) -> LocalContextBridge:
        if not hasattr(self.server, "context_bridge"):
            setattr(self.server, "context_bridge", LocalContextBridge(root_dir=ROOT_DIR))
        return getattr(self.server, "context_bridge")

    def _is_loopback(self) -> bool:
        client_ip = self.client_address[0] if self.client_address else ""
        return client_ip in ("127.0.0.1", "::1", "localhost", "testclient")

    def _send_json(self, status_code: int, data: Dict[str, Any]) -> None:
        # Audit invariant: ensure no host secrets are leaked in any outgoing response
        assert self.pairing_manager.audit_zero_secrets(data), "CRITICAL: Secret leak detected in response!"
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Device-Id, X-Timestamp, X-Nonce, X-Signature")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status_code: int, html_content: str) -> None:
        body = html_content.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Device-Id, X-Timestamp, X-Nonce, X-Signature")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def _authenticate(self, body_str: str = "") -> Tuple[bool, str, Optional[str]]:
        """
        Validates request using either:
        1. Cryptographic HMAC-SHA256 headers (X-Device-Id, X-Timestamp, X-Nonce, X-Signature)
        2. Bearer Token in Authorization header (matches active device token)
        Returns: (is_authenticated, error_reason, device_id)
        """
        device_id = self.headers.get("X-Device-Id")
        timestamp = self.headers.get("X-Timestamp")
        nonce = self.headers.get("X-Nonce")
        signature = self.headers.get("X-Signature")

        # 1. HMAC Signature path
        if device_id and timestamp and nonce and signature:
            try:
                ts_int = int(timestamp)
            except ValueError:
                return False, "INVALID_TIMESTAMP_FORMAT", None

            valid, reason = self.pairing_manager.verify_request(
                device_id=device_id,
                timestamp=ts_int,
                nonce=nonce,
                path=self.path.split("?")[0],
                body=body_str,
                signature=signature,
            )
            return valid, reason, device_id if valid else None

        # 2. Bearer Token path (Apple Shortcuts convenience)
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            devices = self.pairing_manager._load_devices()
            for dev in devices.values():
                if dev.token == token:
                    if dev.status != "active":
                        return False, "DEVICE_REVOKED", dev.device_id
                    dev.last_used_at = time.time()
                    devices[dev.device_id] = dev
                    self.pairing_manager._save_devices(devices)
                    return True, "OK", dev.device_id

        return False, "MISSING_OR_INVALID_AUTHENTICATION", None

    def _get_orb_state(self) -> Dict[str, Any]:
        state_file = ROOT_DIR / ".control-plane" / "jarvis" / "ui_state.json"
        if state_file.exists():
            try:
                return json.loads(state_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"state": "IDLE", "updated_at": datetime.now(timezone.utc).isoformat()}

    def _set_orb_state(self, new_state: str, **kwargs) -> None:
        state_file = ROOT_DIR / ".control-plane" / "jarvis" / "ui_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "state": new_state,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        temp = state_file.with_suffix(".tmp")
        temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temp.replace(state_file)

    def _is_audio_muted(self) -> bool:
        try:
            res = subprocess.run(
                ["osascript", "-e", "output muted of (get volume settings)"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2.0,
            )
            return "true" in res.stdout.strip().lower()
        except Exception:
            return False

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        if path in ("/health", "/api/health"):
            self._send_json(200, {
                "status": "PASS",
                "service": "Jarvis Remote Bridge",
                "timestamp": time.time(),
                "node": socket.gethostname(),
            })
            return

        if path in ("/v1/ingress/alexa", "/api/alexa"):
            self._send_json(200, {
                "status": "PASS",
                "service": "Jarvis Alexa Ingress",
                "skill_id": DEFAULT_ALEXA_SKILL_ID,
                "timestamp": time.time(),
            })
            return

        if path == "/api/status":
            orb = self._get_orb_state()
            muted = self._is_audio_muted()
            signal_file = ROOT_DIR / ".control-plane" / "remote" / "iphone_signal.json"
            pending_signal = None
            if signal_file.exists():
                try:
                    pending_signal = json.loads(signal_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

            self._send_json(200, {
                "status": "OK",
                "orb": orb,
                "audio": {"muted": muted},
                "server_time": time.time(),
                "hostname": socket.gethostname(),
                "pending_signal": pending_signal,
            })
            return

        if path == "/api/companion" or path == "/":
            companion_file = ROOT_DIR / "jarvis_remote" / "web" / "index.html"
            if companion_file.exists():
                self._send_html(200, companion_file.read_text(encoding="utf-8"))
            else:
                self._send_html(200, "<h1>Jarvis Remote Companion</h1><p>Em breve.</p>")
            return

        # Context Bridge routes (Account-neutral local context)
        if path.startswith("/api/context"):
            # Require authentication if request is not from loopback
            if not self._is_loopback():
                is_auth, reason, _ = self._authenticate()
                if not is_auth:
                    self._send_json(401, {"error": "UNAUTHORIZED", "reason": reason})
                    return

            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            if path in ("/api/context/status", "/api/context"):
                self._send_json(200, self.context_bridge.get_control_plane_status())
                return

            if path == "/api/context/active_project":
                self._send_json(200, self.context_bridge.get_active_project())
                return

            if path == "/api/context/queue":
                self._send_json(200, self.context_bridge.get_queue_status())
                return

            if path == "/api/context/health":
                self._send_json(200, self.context_bridge.get_runtime_health())
                return

            m_sub = re.match(r"^/api/context/project/([^/]+)/(state|git|actions|files|diff)$", path)
            if m_sub:
                slug = m_sub.group(1)
                sub = m_sub.group(2)
                if sub == "state":
                    res = self.context_bridge.get_project_state(slug)
                elif sub == "git":
                    res = self.context_bridge.get_git_status(slug)
                elif sub == "actions":
                    try:
                        limit = int(query_params.get("limit", [10])[0])
                    except (ValueError, IndexError):
                        limit = 10
                    res = self.context_bridge.get_recent_actions(slug, limit=limit)
                elif sub == "files":
                    try:
                        limit = int(query_params.get("limit", [20])[0])
                    except (ValueError, IndexError):
                        limit = 20
                    res = self.context_bridge.get_recent_changed_files(slug, limit=limit)
                elif sub == "diff":
                    res = self.context_bridge.get_recent_diff_summary(slug)
                else:
                    res = {"status": "ERROR", "error": "UNKNOWN_ACTION"}

                status_code = 404 if res.get("status") == "ERROR" and res.get("error") == "PROJECT_NOT_REGISTERED" else 200
                self._send_json(status_code, res)
                return

            m_proj = re.match(r"^/api/context/project/([^/]+)$", path)
            if m_proj:
                slug = m_proj.group(1)
                res = self.context_bridge.get_project_state(slug)
                status_code = 404 if res.get("status") == "ERROR" and res.get("error") == "PROJECT_NOT_REGISTERED" else 200
                self._send_json(status_code, res)
                return

            self._send_json(404, {"error": "NOT_FOUND", "path": path})
            return

        self._send_json(404, {"error": "NOT_FOUND", "path": path})

    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        content_length = int(self.headers.get("Content-Length", 0))
        body_str = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""

        # Enforce Authentication on mutative POST endpoints
        if path == "/v1/ingress/alexa":
            logger.debug("Ingress Alexa POST received with %d bytes", len(body_str))
            # Allow authenticated device token or verified Alexa Skill ID
            is_auth, reason, dev_id = self._authenticate(body_str)
            if not is_auth and body_str:
                try:
                    payload = json.loads(body_str)
                    app_id = (
                        payload.get("session", {}).get("application", {}).get("applicationId")
                        or payload.get("context", {}).get("System", {}).get("application", {}).get("applicationId")
                    )
                    expected_id = os.environ.get("ALEXA_SKILL_ID", DEFAULT_ALEXA_SKILL_ID)
                    if app_id and app_id == expected_id:
                        is_auth = True
                        reason = "OK"
                        dev_id = (
                            payload.get("context", {})
                            .get("System", {})
                            .get("device", {})
                            .get("deviceId")
                            or "alexa_device"
                        )
                    else:
                        reason = "INVALID_ALEXA_SKILL_ID"
                except Exception:
                    reason = "INVALID_JSON_FOR_ALEXA_AUTH"
        else:
            is_auth, reason, dev_id = self._authenticate(body_str)

        if not is_auth:
            self._send_json(401, {"error": "UNAUTHORIZED", "reason": reason})
            return

        if path == "/api/activate":
            # Wake up Jarvis Orb on Mac
            self._set_orb_state("WAKE", triggered_by=f"remote_{dev_id}")
            # Ensure Antigravity is prewarmed on Mac (fail-soft)
            try:
                subprocess.run(
                    ["open", "-g", "-b", "com.google.antigravity"],
                    capture_output=True,
                    check=False,
                    timeout=2,
                )
            except Exception:
                pass
            self._send_json(200, {
                "status": "SUCCESS",
                "action": "WAKE",
                "orb_state": "WAKE",
                "device_id": dev_id,
            })
            return

        if path == "/v1/ingress/siri":
            try:
                payload = json.loads(body_str) if body_str else {}
            except Exception:
                self._send_json(400, {"error": "INVALID_JSON_BODY"})
                return

            if not payload.get("device_id") and dev_id:
                payload["device_id"] = dev_id

            from siri_bridge.adapter import SiriShortcutAdapter
            from jarvis_remote.ingress import RemoteIngressHandler

            ingress_handler = getattr(self.server, "ingress_handler", None)
            if not ingress_handler:
                ingress_handler = RemoteIngressHandler()
                setattr(self.server, "ingress_handler", ingress_handler)

            adapter = SiriShortcutAdapter(ingress_handler=ingress_handler.handle_envelope)
            res = adapter.handle_request(payload)
            self._send_json(200, res)
            return

        if path == "/v1/ingress/alexa":
            try:
                payload = json.loads(body_str) if body_str else {}
            except Exception:
                self._send_json(400, {"error": "INVALID_JSON_BODY"})
                return

            from alexa.adapter import AlexaSkillAdapter
            from jarvis_remote.ingress import RemoteIngressHandler

            ingress_handler = getattr(self.server, "ingress_handler", None)
            if not ingress_handler:
                ingress_handler = RemoteIngressHandler()
                setattr(self.server, "ingress_handler", ingress_handler)

            adapter = AlexaSkillAdapter(ingress_handler=ingress_handler.handle_envelope)
            res = adapter.handle_request(payload)
            self._send_json(200, res)
        if path == "/api/antigravity/voice/start":
            try:
                payload = json.loads(body_str) if body_str else {}
            except Exception:
                payload = {}
            from .antigravity_voice import start_voice_recording
            new_conv = payload.get("new_conversation", True)
            res = start_voice_recording(new_conversation=new_conv)
            self._send_json(200, res)
            return

        if path == "/api/antigravity/voice/stop":
            from .antigravity_voice import stop_voice_recording_and_send
            res = stop_voice_recording_and_send()
            self._send_json(200, res)
            return

        if path == "/api/antigravity/voice/toggle":
            try:
                payload = json.loads(body_str) if body_str else {}
            except Exception:
                payload = {}
            from .antigravity_voice import toggle_voice_recording
            new_conv = payload.get("new_conversation", True)
            res = toggle_voice_recording(new_conversation_on_start=new_conv)
            self._send_json(200, res)
            return

        if path == "/api/voice/command":
            try:
                payload = json.loads(body_str) if body_str else {}
            except Exception:
                self._send_json(400, {"error": "INVALID_JSON_BODY"})
                return

            text = str(payload.get("text", "")).strip()
            source = str(payload.get("source", "voice")).strip()

            if not text:
                self._send_json(400, {"error": "EMPTY_TEXT"})
                return

            # Comandos explícitos de controle de gravação nativa no Antigravity (⌃ Control + M)
            text_lower = text.lower().strip()
            if text_lower in {"gravar", "gravar audio", "gravar áudio", "gravar no antigravity", "iniciar gravação", "inicie a gravação", "ativar microfone"}:
                from .antigravity_voice import start_voice_recording
                res = start_voice_recording(new_conversation=True)
                self._send_json(200, res)
                return

            if text_lower in {"pronto", "encerrar", "parar", "finalizei", "concluído", "concluido", "parar gravação", "encerrar gravação"}:
                from .antigravity_voice import is_currently_recording, stop_voice_recording_and_send
                if is_currently_recording() or text_lower in {"parar gravação", "encerrar gravação", "finalizei"}:
                    res = stop_voice_recording_and_send()
                    self._send_json(200, res)
                    return

            # Processamento de gatilhos vocais (despertar Antigravity e limpeza de 'pronto', 'execute', 'é isso')
            from .voice_trigger import clean_voice_triggers
            trigger_res = clean_voice_triggers(text)

            if trigger_res.is_wake_only:
                self._send_json(200, {
                    "status": "SUCCESS",
                    "action": "WAKE_ANTIGRAVITY",
                    "message": "Antigravity ativado no Mac. Aguardando sua solicitação.",
                    "speech": "Antigravity ativado no Mac.",
                    "source": source,
                    "timestamp": time.time(),
                })
                return

            effective_prompt = trigger_res.cleaned_prompt or text

            # 1. Injeção no ChatGPT normal chat no Mac (Desativada por padrão em produção)
            inject_res = {"status": "SKIPPED"}
            if payload.get("inject_chatgpt", False) and os.environ.get("JARVIS_ALLOW_MANUAL_CHATGPT_INJECTION") == "1":
                try:
                    from voice_gateway.chatgpt_normal_injector import ChatGPTNormalInjector
                    injector = ChatGPTNormalInjector()
                    inject_res = injector.inject_prompt(effective_prompt)
                except Exception as inj_exc:
                    logger.debug("Falha na injeção manual ChatGPT: %s", inj_exc)
                    inject_res = {"status": "ERROR", "error": str(inj_exc)}

            # 2. Roteamento de projeto e compilação de tarefa
            from chatgpt_voice.prompt_compiler import PromptCompiler, TranscriptTurn
            from chatgpt_voice.router import JarvisTextRouter

            compiler = PromptCompiler(ROOT_DIR / "PROJECT_REGISTRY.json")
            turn = TranscriptTurn(
                key=f"voice_{int(time.time()*1000)}",
                role="user",
                text=effective_prompt,
                source_id=source,
            )
            compiled = compiler.compile_turn(turn)

            route_status = "NO_ACTION"
            issue_num = None
            project_resolved = None

            if compiled:
                project_resolved = compiled.project
                router = JarvisTextRouter(root_dir=ROOT_DIR)
                route_res = router.route(compiled)
                route_status = route_res.status
                issue_num = route_res.issue_number

            self._send_json(200, {
                "status": "SUCCESS",
                "message": f"Comando enviado para o Antigravity{' no projeto ' + project_resolved if project_resolved else ''}.",
                "chatgpt_injection": inject_res.get("status"),
                "project": project_resolved,
                "route_status": route_status,
                "issue_number": issue_num,
                "cleaned_prompt": effective_prompt,
                "trigger_detected": trigger_res.trigger_word,
                "source": source,
                "timestamp": time.time(),
            })
            return

        if path == "/api/mute":
            res = subprocess.run(
                ["osascript", "-e", "set volume with output muted"],
                capture_output=True,
                text=True,
                check=False,
            )
            self._send_json(200, {
                "status": "SUCCESS",
                "action": "mute",
                "device_id": dev_id,
            })
            return

        if path == "/api/unmute":
            res = subprocess.run(
                ["osascript", "-e", "set volume without output muted"],
                capture_output=True,
                text=True,
                check=False,
            )
            self._send_json(200, {
                "status": "SUCCESS",
                "action": "unmute",
                "device_id": dev_id,
            })
            return

        if path == "/api/stop":
            # Resets Orb to IDLE
            self._set_orb_state("IDLE", stopped_by=f"remote_{dev_id}")
            self._send_json(200, {
                "status": "SUCCESS",
                "action": "stop",
                "orb_state": "IDLE",
                "device_id": dev_id,
            })
            return

        if path == "/api/trigger_iphone":
            # Mac signaling iPhone to open ChatGPT Voice
            signal_file = ROOT_DIR / ".control-plane" / "remote" / "iphone_signal.json"
            signal_file.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "action": "OPEN_CHATGPT_VOICE",
                "url": "chatgpt://voice",
                "timestamp": time.time(),
                "from_mac": socket.gethostname(),
            }
            signal_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self._send_json(200, {
                "status": "SIGNAL_DISPATCHED",
                "signal": payload,
            })
            return

        if path == "/api/dispatch":
            # Receives prompt from iPhone, routes via PromptCompiler / Router
            try:
                payload = json.loads(body_str) if body_str else {}
            except Exception:
                self._send_json(400, {"error": "INVALID_JSON_BODY"})
                return

            prompt = payload.get("prompt", "").strip()
            if not prompt:
                self._send_json(400, {"error": "EMPTY_PROMPT"})
                return

            from chatgpt_voice.router import VoiceRouter
            router = VoiceRouter()
            dispatch_result = router.route_prompt(prompt, source=f"remote_{dev_id}")

            self._send_json(200, {
                "status": "DISPATCHED",
                "prompt": prompt,
                "route": dispatch_result.get("route"),
                "result": dispatch_result,
            })
            return

        self._send_json(404, {"error": "ENDPOINT_NOT_FOUND", "path": path})


class JarvisRemoteServer(HTTPServer):
    def __init__(self, host: str = "0.0.0.0", port: int = DEFAULT_PORT, pairing_manager: Optional[PairingManager] = None):
        self.pairing_manager = pairing_manager or PairingManager()
        super().__init__((host, port), JarvisRemoteHandler)
        logger.info(f"JarvisRemoteServer pronto em {host}:{port}")


def run_server(host: str = "0.0.0.0", port: int = DEFAULT_PORT) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    server = JarvisRemoteServer(host, port)
    print(f"[Jarvis Remote] Servidor escutando em http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Jarvis Remote] Encerrando servidor.")
        server.server_close()
