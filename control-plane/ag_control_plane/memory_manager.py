import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ag-memory")

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent.parent / ".control-plane" / "memory"

class MemoryManager:
    """
    Gerenciador de Memória em 4 Camadas para o Jarvis:
    1. SHARED_MEMORY: Preferências globais do usuário e contexto permanente do sistema.
    2. PROJECT_MEMORY: Decisões, convenções e histórico por projeto Git.
    3. PERSONA_MEMORY: Ajustes de tom, estilo e memórias específicas de cada persona.
    4. SESSION_MEMORY: Contexto transitório da sessão ativa (comandos recentes, estado).
    """

    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or DEFAULT_MEMORY_DIR
        self.shared_file = self.memory_dir / "shared_memory.json"
        self.project_file = self.memory_dir / "project_memory.json"
        self.personas_dir = self.memory_dir / "personas"
        self.session_file = self.memory_dir / "session_memory.json"
        self.personal_file = self.memory_dir / "personal_memory.json"

        self._ensure_structures()

    def _ensure_structures(self) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.personas_dir.mkdir(parents=True, exist_ok=True)

        # 1. SHARED_MEMORY inicial
        if not self.shared_file.exists():
            default_shared = {
                "owner": "Lucas Vinícius",
                "os": "macOS (Apple Silicon arm64)",
                "locale": "pt-BR",
                "wake_word": "E aí, Jarvis",
                "rules": [
                    "Zero robotic local TTS (apenas voz oficial ChatGPT)",
                    "Fail-closed em operações destrutivas ou de alto risco",
                    "Evitar chuva de chats no Antigravity reutilizando sessões",
                    "Manter janelas em segundo plano de forma não intrusiva"
                ],
                "preferences": {
                    "auto_open_browser": False,
                    "default_persona": "jarvis",
                    "notifications": True
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self._write_json(self.shared_file, default_shared)

        # 2. PROJECT_MEMORY inicial
        if not self.project_file.exists():
            default_projects = {
                "antigravity-control-plane": {
                    "slug": "antigravity-control-plane",
                    "path": "/Users/lucasvinicius/projetos/Jarvis Assistente",
                    "description": "Jarvis Control Plane e Voice Gateway",
                    "frameworks": ["Python 3.14", "AppKit", "Cocoa/Swift 6.4", "GitHub API"],
                    "notes": ["Symlink: /Users/lucasvinicius/projetos/antigravity-control-plane"]
                }
            }
            self._write_json(self.project_file, default_projects)

        # 3. SESSION_MEMORY inicial
        if not self.session_file.exists():
            default_session = {
                "session_id": f"sess_{int(time.time())}",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "last_active": datetime.now(timezone.utc).isoformat(),
                "current_persona": "jarvis",
                "recent_utterances": [],
                "recent_tasks": []
            }
            self._write_json(self.session_file, default_session)

        # 4. PERSONAL_MEMORY inicial
        if not self.personal_file.exists():
            default_personal = {
                "facts": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            self._write_json(self.personal_file, default_personal)

    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        try:
            if not file_path.exists():
                return {}
            content = file_path.read_text(encoding="utf-8").strip()
            return json.loads(content) if content else {}
        except Exception as e:
            logger.error(f"Erro ao ler {file_path.name}: {e}")
            return {}

    def _write_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        try:
            tmp = file_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(file_path)
        except Exception as e:
            logger.error(f"Erro ao gravar {file_path.name}: {e}")

    # --- CAMADA 1: SHARED MEMORY ---
    def get_shared_memory(self) -> Dict[str, Any]:
        return self._read_json(self.shared_file)

    def update_shared_memory(self, key: str, value: Any) -> None:
        data = self.get_shared_memory()
        data[key] = value
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._write_json(self.shared_file, data)

    # --- CAMADA 2: PROJECT MEMORY ---
    def get_project_memory(self, project_slug: Optional[str] = None) -> Any:
        data = self._read_json(self.project_file)
        if project_slug:
            return data.get(project_slug, {})
        return data

    def record_project_decision(self, project_slug: str, decision: str, context: Optional[Dict] = None) -> None:
        data = self._read_json(self.project_file)
        if project_slug not in data:
            data[project_slug] = {"decisions": [], "updated_at": datetime.now(timezone.utc).isoformat()}
        proj = data[project_slug]
        decisions = proj.setdefault("decisions", [])
        decisions.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "context": context or {}
        })
        proj["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._write_json(self.project_file, data)

    # --- CAMADA 3: PERSONA MEMORY ---
    def get_persona_memory(self, persona_id: str) -> Dict[str, Any]:
        p_file = self.personas_dir / f"{persona_id.lower()}.json"
        return self._read_json(p_file)

    def save_persona_memory(self, persona_id: str, updates: Dict[str, Any]) -> None:
        p_file = self.personas_dir / f"{persona_id.lower()}.json"
        data = self._read_json(p_file)
        data.update(updates)
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._write_json(p_file, data)

    # --- CAMADA 4: SESSION MEMORY ---
    def get_session_memory(self) -> Dict[str, Any]:
        return self._read_json(self.session_file)

    def append_session_interaction(self, user_utterance: str, intent: Optional[str] = None, response: Optional[str] = None) -> None:
        data = self.get_session_memory()
        history = data.setdefault("recent_utterances", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "utterance": user_utterance,
            "intent": intent,
            "response": response
        })
        # Mantém histórico nos últimos 30 itens
        if len(history) > 30:
            data["recent_utterances"] = history[-30:]
        data["last_active"] = datetime.now(timezone.utc).isoformat()
        self._write_json(self.session_file, data)

    def record_session_task(self, task_info: Dict[str, Any]) -> None:
        data = self.get_session_memory()
        tasks = data.setdefault("recent_tasks", [])
        tasks.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **task_info
        })
        if len(tasks) > 20:
            data["recent_tasks"] = tasks[-20:]
        data["last_active"] = datetime.now(timezone.utc).isoformat()
        self._write_json(self.session_file, data)

    @staticmethod
    def _sanitize_text(text: str) -> str:
        if not text:
            return ""
        import re
        clean = re.sub(r"ghp_[a-zA-Z0-9]{20,}", "[REDACTED_GITHUB_TOKEN]", text)
        clean = re.sub(r"github_pat_[a-zA-Z0-9_]{20,}", "[REDACTED_GITHUB_TOKEN]", clean)
        clean = re.sub(r"sk-[a-zA-Z0-9_\-]{20,}", "[REDACTED_API_KEY]", clean)
        clean = re.sub(r"(?i)(senha|password|secret|token)\s*[:=]\s*\S+", r"\1=[REDACTED]", clean)
        clean = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED_PAYMENT_CREDENTIAL]", clean)
        return clean

    # --- CAMADA 5: PERSONAL MEMORY (SUPER AGENTE) ---
    def remember_fact(
        self,
        fact: str,
        category: str = "general",
        source: str = "alexa",
        confidence: str = "user_stated",
        ttl_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        clean_fact = self._sanitize_text(fact.strip())
        if not clean_fact:
            return {}
        import hashlib
        data = self._read_json(self.personal_file)
        facts = data.setdefault("facts", [])
        norm = clean_fact.lower()

        # Deduplicação: se o fato já existe, atualiza metadados
        for item in facts:
            if item.get("fact", "").lower() == norm or (len(norm) > 10 and norm in item.get("fact", "").lower()):
                item["source"] = source
                item["category"] = category
                item["confidence"] = confidence
                item["last_used"] = datetime.now(timezone.utc).isoformat()
                item["updated_at"] = datetime.now(timezone.utc).isoformat()
                if ttl_seconds is not None:
                    item["ttl_seconds"] = ttl_seconds
                data["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._write_json(self.personal_file, data)
                return item

        fact_id = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]
        new_item = {
            "id": fact_id,
            "fact": clean_fact,
            "category": category,
            "source": source,
            "confidence": confidence,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_used": datetime.now(timezone.utc).isoformat(),
        }
        if ttl_seconds is not None:
            new_item["ttl_seconds"] = ttl_seconds

        facts.append(new_item)
        if len(facts) > 100:
            data["facts"] = facts[-100:]
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._write_json(self.personal_file, data)
        return new_item

    def correct_fact(
        self,
        target_keyword: str,
        new_fact: str,
        category: Optional[str] = None,
        source: str = "alexa",
    ) -> Optional[Dict[str, Any]]:
        clean_kw = target_keyword.strip().lower()
        clean_new = self._sanitize_text(new_fact.strip())
        if not clean_kw or not clean_new:
            return None
        data = self._read_json(self.personal_file)
        facts = data.setdefault("facts", [])
        for item in facts:
            if clean_kw in item.get("fact", "").lower() or clean_kw in item.get("category", "").lower():
                item["fact"] = clean_new
                if category:
                    item["category"] = category
                item["source"] = source
                item["confidence"] = "user_stated"
                item["updated_at"] = datetime.now(timezone.utc).isoformat()
                item["last_used"] = datetime.now(timezone.utc).isoformat()
                data["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._write_json(self.personal_file, data)
                return item
        # If not found, add as new fact
        return self.remember_fact(clean_new, category=category or "general", source=source)

    def forget_fact(self, keyword: str) -> List[str]:
        clean_kw = keyword.strip().lower()
        if not clean_kw:
            return []
        data = self._read_json(self.personal_file)
        facts = data.setdefault("facts", [])
        kept = []
        removed = []
        for item in facts:
            if clean_kw in item.get("fact", "").lower() or clean_kw in item.get("category", "").lower():
                removed.append(item.get("fact", ""))
            else:
                kept.append(item)
        if removed:
            data["facts"] = kept
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._write_json(self.personal_file, data)
        return removed

    def query_memories(self, query: str = "") -> List[Dict[str, Any]]:
        data = self._read_json(self.personal_file)
        facts = data.get("facts", [])
        clean_q = query.strip().lower()
        now_ts = datetime.now(timezone.utc)

        valid_facts = []
        for f in facts:
            ttl = f.get("ttl_seconds")
            if ttl:
                try:
                    created = datetime.fromisoformat(f.get("created_at", "").replace("Z", "+00:00"))
                    if (now_ts - created).total_seconds() > ttl:
                        continue
                except Exception:
                    pass
            valid_facts.append(f)

        if not clean_q or clean_q == "*":
            return valid_facts
        return [
            f for f in valid_facts
            if clean_q in f.get("fact", "").lower() or clean_q in f.get("category", "").lower()
        ]

    def audit_memories(self) -> Dict[str, Any]:
        data = self._read_json(self.personal_file)
        facts = data.get("facts", [])
        categories = list({f.get("category", "general") for f in facts})
        sources = list({f.get("source", "alexa") for f in facts})
        return {
            "total_facts": len(facts),
            "categories": categories,
            "sources": sources,
            "facts": [
                {
                    "id": f.get("id"),
                    "fact": f.get("fact"),
                    "category": f.get("category"),
                    "source": f.get("source"),
                    "confidence": f.get("confidence", "user_stated"),
                    "updated_at": f.get("updated_at"),
                }
                for f in facts
            ],
        }

    def export_memories(self) -> Dict[str, Any]:
        return {
            "personal_profile": self.get_personal_profile(),
            "project_context": self.get_project_memory(),
            "conversation_context": self.get_conversation_context(),
            "device_context": self.get_device_context(),
            "task_context": self.get_task_context(),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_personal_profile(self) -> Dict[str, Any]:
        shared = self.get_shared_memory()
        personal = self._read_json(self.personal_file)
        return {
            "owner": shared.get("owner", "Lucas Vinícius"),
            "os": shared.get("os", "macOS"),
            "locale": shared.get("locale", "pt-BR"),
            "preferences": shared.get("preferences", {}),
            "facts": personal.get("facts", []),
            "updated_at": personal.get("updated_at") or shared.get("updated_at"),
        }

    # --- CROSS-DEVICE CONTEXT & TOPIC CONTINUITY ---
    def set_active_topic(self, topic: str, device: str = "alexa") -> None:
        clean = self._sanitize_text(topic.strip())
        if not clean:
            return
        data = self.get_session_memory()
        data["active_topic"] = {
            "topic": clean,
            "device": device,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        data["last_active"] = datetime.now(timezone.utc).isoformat()
        self._write_json(self.session_file, data)

    def get_active_topic(self) -> Optional[Dict[str, Any]]:
        data = self.get_session_memory()
        return data.get("active_topic")

    def resolve_topic_continuation(self) -> Optional[str]:
        active = self.get_active_topic()
        if active and active.get("topic"):
            return active["topic"]
        sess = self.get_session_memory()
        tasks = sess.get("recent_tasks", [])
        if tasks:
            return tasks[-1].get("title") or tasks[-1].get("task")
        utterances = sess.get("recent_utterances", [])
        if utterances:
            for u in reversed(utterances):
                if u.get("utterance"):
                    return u["utterance"]
        return None

    def update_device_context(self, device_id: str, platform: str, last_action: Optional[str] = None) -> None:
        data = self.get_session_memory()
        devices = data.setdefault("devices", {})
        devices[device_id] = {
            "platform": platform,
            "last_action": last_action,
            "last_seen": datetime.now(timezone.utc).isoformat(),
        }
        data["last_active"] = datetime.now(timezone.utc).isoformat()
        self._write_json(self.session_file, data)

    def get_device_context(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        data = self.get_session_memory()
        devices = data.get("devices", {})
        if device_id:
            return devices.get(device_id, {})
        return devices

    def get_conversation_context(self) -> Dict[str, Any]:
        data = self.get_session_memory()
        return {
            "session_id": data.get("session_id"),
            "active_topic": data.get("active_topic"),
            "recent_utterances": data.get("recent_utterances", [])[-5:],
            "last_active": data.get("last_active"),
        }

    def get_task_context(self) -> Dict[str, Any]:
        data = self.get_session_memory()
        return {
            "recent_tasks": data.get("recent_tasks", [])[-5:],
            "last_active": data.get("last_active"),
        }

