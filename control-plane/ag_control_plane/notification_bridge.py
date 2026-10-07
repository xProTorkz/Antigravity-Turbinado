"""Notification Bridge for Control Plane Status Events.

Decoupled bridge that formats and emits canonical STATUS_EVENT envelopes
across Control Plane transitions (WORKING, BLOCKED, REVIEW, DONE, REFINEMENT_PASS, REFINEMENT_BLOCKED).

Invariants:
- Sanitizes all secrets, tokens, private endpoints, and localhost ports.
- Provides an optional external sink (e.g. webhook) that is DISABLED by default.
- Fail-safe: failures in alert channels/sinks never disrupt canonical task execution or state.
- Idempotent comment formatting: avoids duplicate STATUS_EVENT blocks.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("notification-bridge")


def sanitize_status_text(val: Any) -> Any:
    """Recursively redacts sensitive tokens, API keys, passwords, and private ports/endpoints."""
    if isinstance(val, str):
        # GitHub tokens
        val = re.sub(r"(ghp_[a-zA-Z0-9]+|github_pat_[a-zA-Z0-9_]+)", "[REDACTED_GITHUB_TOKEN]", val)
        # OpenAI keys
        val = re.sub(r"sk-[a-zA-Z0-9_\-]+", "[REDACTED_OPENAI_KEY]", val)
        # Bearer tokens
        val = re.sub(r"(Bearer\s+)[a-zA-Z0-9_\-\.]+", r"\1[REDACTED_TOKEN]", val)
        # Passwords / secrets
        val = re.sub(r"(?i)(senha|password|secret|token)\s*[:=]\s*\S+", r"\1=[REDACTED]", val)
        # Localhost endpoints & ports
        val = re.sub(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?(?:/\S*)?", "[REDACTED_LOCAL_ENDPOINT]", val)
        val = re.sub(r"(?:localhost|127\.0\.0\.1):\d+", "[REDACTED_LOCAL_ENDPOINT]", val)
        return val
    elif isinstance(val, dict):
        return {k: sanitize_status_text(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_status_text(item) for item in val]
    return val


@dataclass
class StatusEvent:
    """Canonical representation of a Control Plane status event."""

    status: str  # WORKING, BLOCKED, REVIEW, DONE, REFINEMENT_PASS, REFINEMENT_BLOCKED
    project: str
    issue_number: int
    repo: str
    reason: Optional[str] = None
    labels: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    comment: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.labels is None:
            self.labels = []
        if self.metadata is None:
            self.metadata = {}

    def sanitize(self) -> StatusEvent:
        """Returns a sanitized copy with zero secrets or private endpoints."""
        clean_reason = sanitize_status_text(self.reason) if self.reason else None
        clean_metadata = sanitize_status_text(self.metadata) if self.metadata else {}
        clean_project = sanitize_status_text(self.project)
        clean_repo = sanitize_status_text(self.repo)
        clean_comment = sanitize_status_text(self.comment) if self.comment else None

        return StatusEvent(
            status=self.status,
            project=clean_project,
            issue_number=self.issue_number,
            repo=clean_repo,
            reason=clean_reason,
            labels=list(self.labels) if self.labels else [],
            metadata=clean_metadata,
            timestamp=self.timestamp,
            comment=clean_comment,
        )

    def to_envelope_text(self) -> str:
        """Serializes the canonical STATUS_EVENT block for GitHub comments and logs."""
        clean = self.sanitize()
        lines = [
            "STATUS_EVENT",
            f"STATUS_EVENT={clean.status}",
            f"STATUS={clean.status}",
            f"PROJECT={clean.project}",
            f"ISSUE={clean.issue_number}",
            f"REPO={clean.repo}",
            f"TIMESTAMP={clean.timestamp}",
        ]
        if clean.labels:
            lines.append(f"LABELS={', '.join(clean.labels)}")
        if clean.reason:
            # Single-line or trimmed summary in envelope header
            reason_line = clean.reason.replace("\n", " ").strip()
            if len(reason_line) > 160:
                reason_line = reason_line[:157] + "..."
            lines.append(f"REASON={reason_line}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Returns a serializable dictionary representation."""
        clean = self.sanitize()
        return {
            "event": "STATUS_EVENT",
            "status_event": clean.status,
            "status": clean.status,
            "project": clean.project,
            "issue_number": clean.issue_number,
            "repo": clean.repo,
            "timestamp": clean.timestamp,
            "reason": clean.reason,
            "labels": clean.labels,
            "metadata": clean.metadata,
            "comment": clean.comment,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """Returns a JSON string representation."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class NotificationSink:
    """Base interface for status notification sinks."""

    def handle_event(self, event: StatusEvent) -> None:
        raise NotImplementedError


class InMemoryNotificationSink(NotificationSink):
    """Stores status events in memory (ideal for testing and in-process inspection)."""

    def __init__(self) -> None:
        self.events: List[StatusEvent] = []

    def handle_event(self, event: StatusEvent) -> None:
        self.events.append(event)

    def clear(self) -> None:
        self.events.clear()


class ExternalWebhookSink(NotificationSink):
    """Optional external HTTP webhook sink, DISABLED by default."""

    def __init__(
        self,
        enabled: bool = False,
        endpoint_url: Optional[str] = None,
        timeout: float = 2.0,
        http_client: Optional[Callable[[str, Dict[str, Any], float], Any]] = None,
    ) -> None:
        self.enabled = enabled
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self._http_client = http_client

    def handle_event(self, event: StatusEvent) -> None:
        if not self.enabled or not self.endpoint_url:
            return

        payload = event.to_dict()

        if self._http_client:
            self._http_client(self.endpoint_url, payload, self.timeout)
            return

        # Default standard urllib POST
        import urllib.request
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            pass


class TelegramNotificationSink(NotificationSink):
    """Sends formatted status notifications to Telegram chats/groups.

    Invariants:
    - Fail-safe: failures never disrupt control plane execution.
    - Sanitizes all secrets and endpoints before delivery.
    - Supports multiple chat IDs (delivered independently).
    """

    def __init__(
        self,
        enabled: bool = False,
        bot_token: Optional[str] = None,
        chat_ids: Optional[List[Any]] = None,
        timeout: float = 4.0,
        http_client: Optional[Callable[[str, Dict[str, Any], float], Any]] = None,
    ) -> None:
        self.enabled = enabled
        self.bot_token = bot_token
        self.chat_ids = chat_ids or []
        self.timeout = timeout
        self._http_client = http_client

    def handle_event(self, event: StatusEvent) -> None:
        if not self.enabled or not self.bot_token or not self.chat_ids:
            return

        clean = event.sanitize()

        status_emojis = {
            "WORKING": "🚀",
            "DONE": "✅",
            "REVIEW": "👀",
            "BLOCKED": "⛔",
            "QUEUED": "⏳",
            "REFINEMENT_PASS": "📋",
            "REFINEMENT_BLOCKED": "⚠️",
        }
        emoji = status_emojis.get(clean.status, "📌")

        lines = [
            f"{emoji} <b>[Antigravity Control Plane]</b>",
            f"<b>Status:</b> <code>{clean.status}</code>",
            f"<b>Projeto:</b> <code>{clean.project}</code>",
            f"<b>Issue:</b> #{clean.issue_number} ({clean.repo})",
        ]
        if clean.reason:
            lines.append(f"<b>Info:</b> {clean.reason}")
        if clean.labels:
            lines.append(f"<b>Labels:</b> {', '.join(clean.labels)}")
        lines.append(f"<b>Timestamp:</b> <code>{clean.timestamp}</code>")

        text = "\n".join(lines)
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        import urllib.error
        import urllib.request

        for cid in self.chat_ids:
            payload = {
                "chat_id": str(cid),
                "text": text,
                "parse_mode": "HTML",
            }
            if self._http_client:
                try:
                    self._http_client(url, payload, self.timeout)
                except Exception as err:
                    logger.warning(f"[TELEGRAM_SINK] Falha ao enviar para chat {cid}: {err}")
                continue

            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    pass
            except Exception as err:
                logger.warning(f"[TELEGRAM_SINK] Falha ao enviar para chat {cid}: {err}")


class NotificationBridge:
    """Coordinates STATUS_EVENT serialization, sanitization, and dispatch to sinks."""

    def __init__(
        self,
        sinks: Optional[List[NotificationSink]] = None,
        external_sink: Optional[ExternalWebhookSink] = None,
        telegram_sink: Optional[TelegramNotificationSink] = None,
    ) -> None:
        self.sinks: List[NotificationSink] = sinks if sinks is not None else []
        self.external_sink = external_sink or ExternalWebhookSink(enabled=False)
        if self.external_sink not in self.sinks:
            self.sinks.append(self.external_sink)

        self.telegram_sink = telegram_sink
        if self.telegram_sink is None:
            # Auto-carrega configuração local segura em .control-plane/telegram_config.json
            from pathlib import Path
            cfg_file = Path(__file__).resolve().parent.parent / ".control-plane" / "telegram_config.json"
            if cfg_file.exists():
                try:
                    cfg_data = json.loads(cfg_file.read_text(encoding="utf-8"))
                    if cfg_data.get("enabled"):
                        self.telegram_sink = TelegramNotificationSink(
                            enabled=True,
                            bot_token=cfg_data.get("token"),
                            chat_ids=cfg_data.get("chat_ids", []),
                        )
                except Exception as e:
                    logger.warning(f"Erro ao carregar telegram_config.json: {e}")

        if self.telegram_sink and self.telegram_sink not in self.sinks:
            self.sinks.append(self.telegram_sink)

    def emit(self, event: StatusEvent) -> StatusEvent:
        """Sanitizes and dispatches a StatusEvent to all sinks.

        Fail-safe invariant: sink failures NEVER bubble up to interrupt control plane execution.
        """
        sanitized = event.sanitize()

        for sink in self.sinks:
            try:
                sink.handle_event(sanitized)
            except Exception as exc:
                logger.warning(
                    f"[NOTIFICATION_BRIDGE] Falha ao processar evento no sink {type(sink).__name__}: {exc}"
                )

        return sanitized

    def format_comment(
        self,
        event: Optional[StatusEvent] = None,
        body: Optional[str] = None,
        *,
        status: Optional[str] = None,
        project: Optional[str] = None,
        issue_number: Optional[int] = None,
        repo: Optional[str] = None,
        comment: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Formats a comment incorporating the STATUS_EVENT envelope idempotently."""
        if event is None:
            if status is None:
                raise ValueError("Must provide either event or status to format_comment")
            event = StatusEvent(
                status=status,
                project=project or "unknown",
                issue_number=issue_number or 0,
                repo=repo or "unknown",
                comment=comment or body or "",
                reason=reason,
                labels=labels or [],
                metadata=metadata or {},
            )

        target_body = body or comment or event.comment
        envelope = event.to_envelope_text()
        clean_body = (target_body or "").strip()

        # If body already starts with or contains STATUS_EVENT, do not duplicate
        if "STATUS_EVENT=" in clean_body:
            return clean_body

        if clean_body:
            return f"{envelope}\n---\n{clean_body}"
        return envelope


_GLOBAL_BRIDGE: Optional[NotificationBridge] = None


def get_notification_bridge() -> NotificationBridge:
    """Returns the default global NotificationBridge instance."""
    global _GLOBAL_BRIDGE
    if _GLOBAL_BRIDGE is None:
        _GLOBAL_BRIDGE = NotificationBridge()
    return _GLOBAL_BRIDGE


def set_notification_bridge(bridge: Optional[NotificationBridge]) -> None:
    """Overrides the global NotificationBridge instance (useful for testing)."""
    global _GLOBAL_BRIDGE
    _GLOBAL_BRIDGE = bridge
