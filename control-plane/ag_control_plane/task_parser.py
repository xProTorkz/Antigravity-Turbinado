import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

PROTECTED_ARCHITECTURE_FILES = {
    "JARVIS_ARCHITECTURE_LOCK.md",
    "JARVIS_ARCHITECTURE_LOCK.json",
    "CANONICAL_RULES.md",
    "PROJECT_STATE.md",
    "ANTIGRAVITY_PROJECT_WORKFLOW.md",
    "ISSUE_TAXONOMY.md",
    "TASK_PROTOCOL.md",
    "ANTIGRAVITY_INVOCATION.md",
    ".github/CODEOWNERS",
}

class TaskValidationError(Exception):
    pass

class TaskParser:
    @staticmethod
    def extract_yaml_block(body: str) -> Optional[str]:
        if not body:
            return None
        # Look for ```yaml ... ``` or ```agent_task ... ```
        pattern = r"```(?:yaml|agent_task)?\s*(agent_task:[\s\S]*?)```"
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Or look for agent_task: at start of line
        pattern_raw = r"(agent_task:\s*\n(?:[ \t]+[^\n]+\n*)+)"
        match_raw = re.search(pattern_raw, body)
        if match_raw:
            return match_raw.group(1).strip()
        return None

    @staticmethod
    def extract_execution_brief_yaml(body: str) -> Optional[str]:
        if not body:
            return None
        # Look for ```yaml ... execution_brief: ... ``` or ```execution_brief ... ```
        pattern = r"```(?:yaml|execution_brief)?\s*(execution_brief:[\s\S]*?)```"
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        pattern_raw = r"(execution_brief:\s*\n(?:[ \t]+[^\n]+\n*)+)"
        match_raw = re.search(pattern_raw, body)
        if match_raw:
            return match_raw.group(1).strip()
        return None

    @classmethod
    def parse_execution_brief(cls, body: str) -> Optional[Any]:
        yaml_text = cls.extract_execution_brief_yaml(body)
        if not yaml_text:
            return None
        from .execution_brief import ExecutionBrief
        try:
            return ExecutionBrief.from_yaml(yaml_text)
        except Exception:
            return None

    @classmethod
    def parse_yaml_str(cls, yaml_text: str) -> Dict[str, Any]:
        """Robust YAML parser for agent_task schema supporting nested blocks and fallback."""
        try:
            import yaml
            parsed = yaml.safe_load(yaml_text)
            if isinstance(parsed, dict):
                task_dict = parsed.get("agent_task", parsed)
                if isinstance(task_dict, dict):
                    return dict(task_dict)
        except Exception:
            pass

        lines = yaml_text.splitlines()
        data: Dict[str, Any] = {}
        current_list_key: Optional[str] = None

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Check if root agent_task:
            if line == "agent_task:" or line.startswith("agent_task:"):
                current_list_key = None
                continue

            # List item
            if line.startswith("- "):
                val = line[2:].strip().strip("\"'")
                if current_list_key and current_list_key in data:
                    if isinstance(data[current_list_key], list):
                        if val.isdigit():
                            data[current_list_key].append(int(val))
                        else:
                            data[current_list_key].append(val)
                continue

            # Key-value pair
            if ":" in line:
                key, rest = line.split(":", 1)
                key = key.strip()
                rest = rest.strip()
                current_list_key = None

                if not rest:
                    data[key] = []
                    current_list_key = key
                    continue

                if rest.startswith("[") and rest.endswith("]"):
                    inner = rest[1:-1].strip()
                    if not inner:
                        data[key] = []
                    else:
                        items = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
                        converted = [int(x) if x.isdigit() else x for x in items]
                        data[key] = converted
                    current_list_key = None
                    continue

                if rest.lower() in ("true", "yes"):
                    data[key] = True
                elif rest.lower() in ("false", "no"):
                    data[key] = False
                elif rest.isdigit():
                    data[key] = int(rest)
                else:
                    data[key] = rest.strip("\"'")

        return data

    @classmethod
    def load_default_registry(cls, registry_path: Optional[Path] = None) -> Dict[str, Any]:
        if registry_path and registry_path.exists():
            try:
                return json.loads(registry_path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        root_reg = Path(__file__).resolve().parent.parent / "PROJECT_REGISTRY.json"
        if root_reg.exists():
            try:
                return json.loads(root_reg.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    @classmethod
    def validate_taxonomy(cls, labels: List[str]) -> None:
        """Validate label taxonomy, rejecting conflicting priorities, states, or projects."""
        priorities = [l.lower() for l in labels if l.lower().startswith("priority:")]
        if len(set(priorities)) > 1:
            raise TaskValidationError(
                f"Conflito de labels de prioridade detectado: {priorities}. Exatamente uma prioridade permitida."
            )

        ag_states = [l.lower() for l in labels if l.lower().startswith("ag:")]
        if len(set(ag_states)) > 1:
            raise TaskValidationError(
                f"Conflito de labels de ciclo de vida ag:* detectado: {ag_states}. Exatamente um estado ag:* permitido."
            )

        projects = [l.lower() for l in labels if l.lower().startswith("project:")]
        if len(set(projects)) > 1:
            raise TaskValidationError(
                f"Conflito de labels de projeto detectado: {projects}. Exatamente um projeto permitido."
            )

    @classmethod
    def normalize_labels(cls, labels: List[str]) -> List[str]:
        """Normalize labels by resolving conflicting priorities and lifecycle states."""
        cleaned = list(labels)
        priorities = [l for l in cleaned if l.lower().startswith("priority:")]
        if len(set(p.lower() for p in priorities)) > 1:
            p_order = {"priority:p0": 0, "priority:p1": 1, "priority:p2": 2, "priority:p3": 3}
            best_p = min(priorities, key=lambda p: p_order.get(p.lower(), 99))
            cleaned = [l for l in cleaned if not l.lower().startswith("priority:") or l.lower() == best_p.lower()]

        ag_states = [l for l in cleaned if l.lower().startswith("ag:")]
        if len(set(s.lower() for s in ag_states)) > 1:
            state_order = {"ag:working": 0, "ag:queued": 1, "ag:blocked": 2, "ag:done": 3, "ag:cancelled": 4}
            best_s = min(ag_states, key=lambda s: state_order.get(s.lower(), 99))
            cleaned = [l for l in cleaned if not l.lower().startswith("ag:") or l.lower() == best_s.lower()]

        return sorted(list(dict.fromkeys(cleaned)))

    @classmethod
    def parse_task(
        cls,
        body: str,
        labels: Optional[List[str]] = None,
        title: str = "",
        registry: Optional[Dict[str, Any]] = None,
        is_auto: Optional[bool] = None,
    ) -> Dict[str, Any]:
        lbl_list = labels or []
        cls.validate_taxonomy(lbl_list)

        auto_mode = is_auto if is_auto is not None else any("execution:auto" == l.lower() for l in lbl_list)
        yaml_block = cls.extract_yaml_block(body)

        if auto_mode:
            if not yaml_block:
                raise TaskValidationError(
                    "AUTO_TASK_YAML_REQUIRED: Bloco 'agent_task' em YAML é estritamente obrigatório para tarefas com execution:auto."
                )
            data = cls.parse_yaml_str(yaml_block)
            if not data.get("user_execution_confirmed", False):
                raise TaskValidationError(
                    "HUMAN_GATE=EXECUTION_INTENT_UNCONFIRMED: user_execution_confirmed=true é obrigatório para execução autônoma."
                )
        elif yaml_block:
            data = cls.parse_yaml_str(yaml_block)
        else:
            raise TaskValidationError(
                "TITLE_ROUTING_AUTHORITY=0: O projeto de destino não pode ser inferido pelo título/labels sem bloco 'agent_task'."
            )

        cls.validate_task(data, registry=registry)
        return data

    @classmethod
    def validate_task(cls, data: Dict[str, Any], registry: Optional[Dict[str, Any]] = None) -> None:
        if registry is None:
            registry = cls.load_default_registry()

        if "target_project" not in data or not str(data["target_project"]).strip():
            raise TaskValidationError("Campo obrigatório ausente ou vazio: 'target_project'")

        project = str(data["target_project"]).strip()
        if ".." in project or "/" in project or "\\" in project:
            raise TaskValidationError(f"target_project inválido ou inseguro: '{project}'")

        if registry is not None and project not in registry:
            raise TaskValidationError(
                f"target_project '{project}' não consta no PROJECT_REGISTRY allowlisted."
            )

        target_repo = str(data.get("target_repo", "")).strip()

        # Resolução estrita e segura do target_repo através do registry allowlisted
        if not target_repo:
            if not registry or project not in registry:
                raise TaskValidationError(
                    f"target_repo ausente e target_project '{project}' não consta no PROJECT_REGISTRY allowlisted."
                )
            reg_repo = str(registry[project].get("repo", "")).strip()
            if not reg_repo:
                raise TaskValidationError(
                    f"target_project '{project}' no registry não possui repositório configurado."
                )
            data["target_repo"] = reg_repo
            repo = reg_repo
        else:
            repo = target_repo
            if not re.match(r"^[\w\-\.]+/[ \w\-\.]+$", repo):
                raise TaskValidationError(f"target_repo inválido: '{repo}'")
            if registry and project in registry:
                reg_repo = str(registry[project].get("repo", "")).strip()
                if reg_repo and repo != reg_repo:
                    raise TaskValidationError(
                        f"target_repo divergente: '{repo}' não coincide com o repositório allowlisted '{reg_repo}' do projeto '{project}'."
                    )

        # Verificação 1 (Planejamento & Despacho): Validação estrita de project_id quando fornecido
        project_id = str(data.get("project_id", "")).strip()
        if project_id and registry and project in registry:
            expected_pid = str(registry[project].get("project_id", "")).strip()
            if expected_pid and project_id != expected_pid:
                raise TaskValidationError(
                    f"PROJECT_ID_MISMATCH: project_id '{project_id}' diverge do cadastrado no PROJECT_REGISTRY ('{expected_pid}') para o projeto '{project}'."
                )

        priority = str(data.get("priority", "P2")).upper()
        if priority not in ("P0", "P1", "P2", "P3"):
            priority = "P2"
        data["priority"] = priority

        allowed_scope = data.get("allowed_scope", [])
        if isinstance(allowed_scope, list):
            for scope in allowed_scope:
                if ".." in str(scope) or str(scope).startswith("/"):
                    raise TaskValidationError(f"allowed_scope inválido ou inseguro: '{scope}'")
                normalized_scope = str(scope).strip()
                if normalized_scope.startswith("./"):
                    normalized_scope = normalized_scope[2:].strip()
                if normalized_scope in PROTECTED_ARCHITECTURE_FILES:
                    raise TaskValidationError(
                        f"Arquivo de arquitetura protegido não pode entrar em allowed_scope: '{normalized_scope}'. "
                        "Mudanças arquiteturais exigem decisão manual explícita do proprietário fora do fluxo autônomo."
                    )
                if project == "antigravity-control-plane" and normalized_scope in {"*", "**", "."}:
                    raise TaskValidationError(
                        "allowed_scope amplo é proibido no antigravity-control-plane porque poderia incluir os arquivos de architecture lock."
                    )
        else:
            data["allowed_scope"] = []

        if bool(data.get("architecture_override", False)):
            raise TaskValidationError(
                "architecture_override não é aceito pelo fluxo autônomo. O JARVIS_ARCHITECTURE_LOCK só pode ser alterado manualmente pelo proprietário."
            )

        for list_key in ("depends_on", "supersedes"):
            if list_key not in data or not isinstance(data[list_key], list):
                data[list_key] = []

        repair_mode = str(data.get("repair_mode", "normal")).lower()
        data["repair_mode"] = "surgical" if repair_mode == "surgical" else "normal"

        data["destructive_changes"] = bool(data.get("destructive_changes", False))
        data["requires_human_approval"] = bool(data.get("requires_human_approval", False))
        data["baseline_sha"] = str(data.get("baseline_sha", "")).strip()

        # Suporte opcional retrocompatível ao bloco de inteligência cloud-first (Multi-AI)
        if "ai" in data and isinstance(data["ai"], dict):
            ai_data = data["ai"]
            workload = str(ai_data.get("workload", "engineering")).strip().lower()
            provider = str(ai_data.get("provider", "auto")).strip().lower()
            model = str(ai_data.get("model", "")).strip() if ai_data.get("model") else None
            data["ai"] = {
                "workload": workload,
                "provider": provider,
                "model": model,
            }
