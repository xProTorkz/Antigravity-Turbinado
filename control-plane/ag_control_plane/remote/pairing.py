import hmac
import hashlib
import json
import logging
import os
import secrets
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("ag-remote-pairing")

FORBIDDEN_SECRET_MARKERS = [
    "ghp_",
    "github_pat_",
    "sk-",
    "csrf_token",
    "cookie",
    "session_token",
    "client_secret",
]


@dataclass
class PairedDevice:
    device_id: str
    name: str
    token: str
    secret_key: str
    created_at: float
    last_used_at: float
    status: str = "active"  # "active" | "revoked"

    def sanitize(self) -> Dict[str, Any]:
        """Returns safe representation without the shared HMAC secret key."""
        d = asdict(self)
        d.pop("secret_key", None)
        return d


class PairingManager:
    """
    Manages cryptographic pairing between Mac and iPhone companion/Shortcuts.
    Guarantees:
    - HMAC-SHA256 authenticated requests
    - Replay protection via nonces and timestamp drift checks
    - Zero leaks of host credentials (NO_SECRETS_ON_PHONE)
    - Instant revocation and kill-switch
    """

    MAX_TIMESTAMP_SKEW_SECONDS = 60.0
    MAX_NONCE_AGE_SECONDS = 300.0

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path(__file__).resolve().parent.parent.parent / ".control-plane" / "remote"
        self.storage_dir = Path(storage_dir)
        self.storage_file = self.storage_dir / "paired_devices.json"
        self._seen_nonces: Dict[str, float] = {}  # nonce -> seen_at_epoch
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.storage_dir, 0o700)
        except Exception:
            pass

        if not self.storage_file.exists():
            self._save_devices({})
        else:
            try:
                os.chmod(self.storage_file, 0o600)
            except Exception:
                pass

    def _load_devices(self) -> Dict[str, PairedDevice]:
        if not self.storage_file.exists():
            return {}
        try:
            raw = json.loads(self.storage_file.read_text(encoding="utf-8"))
            devices = {}
            for dev_id, item in raw.items():
                devices[dev_id] = PairedDevice(**item)
            return devices
        except Exception as e:
            logger.error(f"Erro ao carregar dispositivos pareados: {e}")
            return {}

    def _save_devices(self, devices: Dict[str, PairedDevice]) -> None:
        data = {dev_id: asdict(dev) for dev_id, dev in devices.items()}
        # Security invariant: assert no host secrets are written to pairing storage
        raw_str = json.dumps(data)
        for marker in FORBIDDEN_SECRET_MARKERS:
            if marker in raw_str:
                raise ValueError(f"CRITICAL: Attempted to store host credential '{marker}' in pairing storage!")

        temp = self.storage_file.with_suffix(".tmp")
        temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        try:
            os.chmod(temp, 0o600)
        except Exception:
            pass
        temp.replace(self.storage_file)

    def register_device(self, name: str) -> PairedDevice:
        """
        Creates a new pairing entry for a companion device (e.g. iPhone).
        Generates high-entropy device_id, bearer token, and HMAC secret key.
        """
        devices = self._load_devices()
        device_id = f"iphone_{secrets.token_hex(6)}"
        token = secrets.token_urlsafe(32)
        secret_key = secrets.token_hex(32)
        now = time.time()

        dev = PairedDevice(
            device_id=device_id,
            name=name,
            token=token,
            secret_key=secret_key,
            created_at=now,
            last_used_at=now,
            status="active",
        )
        devices[device_id] = dev
        self._save_devices(devices)
        logger.info(f"Dispositivo registrado com sucesso: {name} (ID: {device_id})")
        return dev

    def get_device(self, device_id: str) -> Optional[PairedDevice]:
        devices = self._load_devices()
        return devices.get(device_id)

    def list_devices(self, include_revoked: bool = False) -> List[Dict[str, Any]]:
        """Returns list of registered devices without secrets."""
        devices = self._load_devices()
        results = []
        for dev in devices.values():
            if dev.status == "active" or include_revoked:
                results.append(dev.sanitize())
        return results

    def revoke_device(self, device_id: str) -> bool:
        """Immediately revokes an iPhone's access."""
        devices = self._load_devices()
        if device_id in devices:
            devices[device_id].status = "revoked"
            self._save_devices(devices)
            logger.info(f"Dispositivo revogado: {device_id}")
            return True
        return False

    def revoke_all(self) -> int:
        """Kill switch: revokes all paired devices immediately."""
        devices = self._load_devices()
        count = 0
        for dev in devices.values():
            if dev.status == "active":
                dev.status = "revoked"
                count += 1
        self._save_devices(devices)
        logger.warning(f"KILL-SWITCH acionado: {count} dispositivos revogados.")
        return count

    @staticmethod
    def compute_signature(secret_key: str, timestamp: int, nonce: str, path: str, body: str = "") -> str:
        """Computes HMAC-SHA256 over timestamp, nonce, path, and body."""
        message = f"{timestamp}:{nonce}:{path}:{body}".encode("utf-8")
        return hmac.new(secret_key.encode("utf-8"), message, hashlib.sha256).hexdigest()

    def verify_request(
        self,
        device_id: str,
        timestamp: int,
        nonce: str,
        path: str,
        body: str,
        signature: str,
    ) -> Tuple[bool, str]:
        """
        Verifies request authenticity, timestamp freshness, and nonce uniqueness.
        """
        dev = self.get_device(device_id)
        if not dev:
            return False, "DEVICE_NOT_FOUND"

        if dev.status != "active":
            return False, "DEVICE_REVOKED"

        now = time.time()
        # 1. Timestamp freshness check
        if abs(now - float(timestamp)) > self.MAX_TIMESTAMP_SKEW_SECONDS:
            return False, "TIMESTAMP_EXPIRED"

        # 2. Replay check (nonce)
        self._prune_nonces(now)
        if nonce in self._seen_nonces:
            return False, "NONCE_REPLAYED"

        # 3. Signature check
        expected_sig = self.compute_signature(dev.secret_key, timestamp, nonce, path, body)
        if not hmac.compare_digest(expected_sig, signature):
            return False, "INVALID_SIGNATURE"

        # Record nonce and update device activity
        self._seen_nonces[nonce] = now
        devices = self._load_devices()
        if device_id in devices:
            devices[device_id].last_used_at = now
            self._save_devices(devices)

        return True, "OK"

    def _prune_nonces(self, now: float) -> None:
        cutoff = now - self.MAX_NONCE_AGE_SECONDS
        expired = [n for n, ts in self._seen_nonces.items() if ts < cutoff]
        for n in expired:
            del self._seen_nonces[n]

    @staticmethod
    def audit_zero_secrets(data: Dict[str, Any]) -> bool:
        """
        Strict audit tool ensuring payload sent to iPhone never contains host tokens.
        """
        raw = json.dumps(data)
        for marker in FORBIDDEN_SECRET_MARKERS:
            if marker in raw.lower():
                return False
        return True
