"""Context Firewall & Scope Isolation (Patch 0C).

Regras fundamentais:
1. CLASSIFICAR TODA SOLICITAÇÃO ANTES DE CARREGAR CONTEXTO:
   SCOPE_TYPE = GLOBAL_CONTROL_PLANE | PROJECT | DIRECT
   - GLOBAL_CONTROL_PLANE: performance do Antigravity, dispatcher, browser manager, scheduler,
     agentes, GitHub orchestration, infraestrutura geral e governança global.
   - PROJECT: somente tarefas pertencentes explicitamente a um projeto de produto.
   - DIRECT: operações simples do sistema operacional (abrir Chrome, site, volume, aplicativo, etc.).

2. CONTEXT FIREWALL:
   - GLOBAL_CONTROL_PLANE: somente antigravity-control-plane e skills necessárias.
     CROSS_PROJECT_DISCOVERY=FORBIDDEN (não buscar DerivBot, Sharkbot, Minha Agenda, etc.).
   - PROJECT: somente workspace e repo daquele projeto.
     CROSS_PROJECT_DISCOVERY=FORBIDDEN (não inspecionar outros projetos).
   - DIRECT: não carregar repository nem executar project discovery.

3. CONTEXTO PESSOAL:
   - PERSONAL_CONTEXT_DEFAULT = OFF para tarefas técnicas.
   - Não pesquisar contatos, amigos, histórico social ou memórias pessoais irrelevantes.

4. PROTEÇÃO DE ESCRITA:
   - Se arquivo estiver fora do workspace autorizado: BLOCK (WRONG_PROJECT_WRITES=0).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("ag-context-firewall")


class ScopeType(str, Enum):
    GLOBAL_CONTROL_PLANE = "GLOBAL_CONTROL_PLANE"
    PROJECT = "PROJECT"
    DIRECT = "DIRECT"


@dataclass
class ScopeClassification:
    scope: ScopeType
    target_project: Optional[str] = None
    authorized_workspace: Optional[str] = None
    authorized_repo: Optional[str] = None
    personal_context_enabled: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Padrões e palavras-chave de escopo global do Control Plane
GLOBAL_CONTROL_PLANE_KEYWORDS = {
    "control-plane", "control plane", "control_plane", "antigravity",
    "dispatcher", "browser manager", "browser_session", "scheduler",
    "orchestrator", "orchestration", "agentes", "subagente", "router",
    "execution_brief", "execution brief", "patch 0c", "fast mode",
    "fast_mode", "anti-loop", "tool priority", "sentinela", "guardiao",
    "infraestrutura", "gateway", "lease", "conflictguard", "session_hardlock"
}

# Padrões de operações diretas cotidianas
DIRECT_OPERATIONS_PATTERNS = [
    r"^(?:por\s+favor\s+)?(?:abrir|abre|abra|fechar|fecha|feche)\s+(?:o\s+|a\s+)?(?:google\s+)?chrome\b",
    r"^(?:por\s+favor\s+)?(?:abrir|abre|abra|fechar|fecha|feche)\s+(?:o\s+|a\s+)?(?:safari|spotify|terminal|finder|slack|discord|notas|calend[aá]rio)\b",
    r"\b(?:aumenta|diminui|muda|ajusta|silencia|muta)\s+(?:o\s+)?volume\b",
    r"\b(?:bateria|status\s+da\s+bateria|disco|espa[cç]o\s+em\s+disco)\b",
    r"\b(?:bloquear|bloqueia|trava)\s+(?:a\s+)?tela\b",
]

# Tópicos pessoais irrelevantes para tarefas técnicas
PERSONAL_TOPICS = {
    "amigo", "amigos", "contato", "contatos", "social", "relacionamento",
    "pessoas antigas", "família", "familia", "aniversário", "aniversario",
    "memórias pessoais", "fotos pessoais", "conversas pessoais"
}


def classify_scope(
    prompt: str,
    project_hint: Optional[str] = None,
    registry: Optional[Dict[str, Any]] = None,
    root_dir: Optional[Path] = None,
) -> ScopeClassification:
    """Classifica toda solicitação ANTES de carregar qualquer contexto de projeto ou repositório."""
    text_clean = prompt.strip()
    text_lower = text_clean.lower()

    # 1. Carrega registry se não fornecido
    if registry is None:
        p_root = root_dir or Path(__file__).resolve().parent.parent
        reg_file = p_root / "PROJECT_REGISTRY.json"
        if reg_file.exists():
            try:
                registry = json.loads(reg_file.read_text(encoding="utf-8"))
            except Exception:
                registry = {}
        else:
            registry = {}

    # 2. Verifica se é comando DIRECT puro (abrir app, volume, etc. sem contexto de dev)
    is_direct = False
    for pat in DIRECT_OPERATIONS_PATTERNS:
        if re.search(pat, text_lower):
            is_direct = True
            break

    # Se parecer direct e não mencionar explicitamente repositório/código/projeto
    if is_direct and not any(w in text_lower for w in ["repositório", "repositorio", "projeto", "commit", "branch", "code"]):
        return ScopeClassification(
            scope=ScopeType.DIRECT,
            target_project=None,
            authorized_workspace=None,
            authorized_repo=None,
            personal_context_enabled=False,
            reason="Comando operacional direto do sistema operacional / desktop.",
        )

    # 3. Verifica menção explícita a projeto de produto
    # Hint explícito
    if project_hint and project_hint.lower() in registry:
        p_slug = project_hint.lower()
        info = registry[p_slug]
        return ScopeClassification(
            scope=ScopeType.PROJECT,
            target_project=p_slug,
            authorized_workspace=info.get("workspace"),
            authorized_repo=info.get("repo"),
            personal_context_enabled=False,
            reason=f"Projeto explícito via hint: {p_slug}",
        )

    # Menção a projeto via @projeto ou no texto
    matched_project = None
    for slug, p_data in registry.items():
        # Ignora antigravity-control-plane aqui, pois ele cai em GLOBAL_CONTROL_PLANE
        if slug in ("antigravity-control-plane", "jarvis-assistant", "jarvis"):
            continue

        aliases = [slug] + [a.lower() for a in p_data.get("aliases", [])]
        for alias in aliases:
            pat = r"(?:@|\b)" + re.escape(alias) + r"\b"
            if re.search(pat, text_lower):
                matched_project = (slug, p_data)
                break
        if matched_project:
            break

    if matched_project:
        slug, p_data = matched_project
        return ScopeClassification(
            scope=ScopeType.PROJECT,
            target_project=slug,
            authorized_workspace=p_data.get("workspace"),
            authorized_repo=p_data.get("repo"),
            personal_context_enabled=False,
            reason=f"Projeto identificado no prompt: {slug}",
        )

    # 4. Verifica se é GLOBAL_CONTROL_PLANE
    is_control_plane = any(kw in text_lower for kw in GLOBAL_CONTROL_PLANE_KEYWORDS)
    if is_control_plane or "patch 0c" in text_lower or "control plane" in text_lower:
        cp_info = registry.get("antigravity-control-plane", {})
        return ScopeClassification(
            scope=ScopeType.GLOBAL_CONTROL_PLANE,
            target_project="antigravity-control-plane",
            authorized_workspace=cp_info.get("workspace", str(Path(__file__).resolve().parent.parent)),
            authorized_repo=cp_info.get("repo", "xProTorkz/antigravity-control-plane"),
            personal_context_enabled=False,
            reason="Tarefa de arquitetura, governança, performance ou dispatcher do Control Plane.",
        )

    # 5. Default para GLOBAL_CONTROL_PLANE nesta sessão canônica
    return ScopeClassification(
        scope=ScopeType.GLOBAL_CONTROL_PLANE,
        target_project="antigravity-control-plane",
        authorized_workspace=str(Path(__file__).resolve().parent.parent),
        authorized_repo="xProTorkz/antigravity-control-plane",
        personal_context_enabled=False,
        reason="Contexto canônico default da sessão: Control Plane.",
    )


class ContextFirewall:
    """Firewall de contexto para isolamento rigoroso entre projetos, Control Plane e operações diretas."""

    def __init__(self, root_dir: Optional[Path] = None, registry_file: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent
        self.registry_file = registry_file or (self.root_dir / "PROJECT_REGISTRY.json")
        self.registry = self._load_registry()

        self.telemetry = {
            "CROSS_PROJECT_DISCOVERY_BLOCKED": 0,
            "WRONG_PROJECT_WRITES_BLOCKED": 0,
            "DIRECT_REPO_READS_BLOCKED": 0,
            "IRRELEVANT_PERSONAL_CONTEXT_FILTERED": 0,
        }

    def _load_registry(self) -> Dict[str, Any]:
        if self.registry_file.exists():
            try:
                return json.loads(self.registry_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def validate_access(
        self,
        scope: ScopeType,
        target_project: Optional[str],
        requested_path: Path | str,
        operation: str = "read",  # "read" | "write" | "discover"
    ) -> Tuple[bool, str]:
        """Valida se o acesso ao arquivo/diretório é permitido pelo firewall de contexto."""
        req_p = Path(requested_path).resolve()
        op_upper = operation.upper()

        # 1. ESCOPO DIRECT: Proibido carregar repositórios ou executar discovery de projeto
        if scope == ScopeType.DIRECT:
            # Permite apenas arquivos temporários do gateway ou configs locais do sistema
            if any(p in str(req_p).lower() for p in ["/projetos/", ".git", "repo"]):
                self.telemetry["DIRECT_REPO_READS_BLOCKED"] += 1
                msg = "FIREWALL_BLOCK: Escopo DIRECT não autoriza carregamento de repositório ou descoberta de projeto."
                logger.warning(msg)
                return False, msg
            return True, "DIRECT_ACCESS_ALLOWED"

        # 2. ESCOPO GLOBAL_CONTROL_PLANE:
        # Só pode acessar o workspace do control plane e catálogo de skills global.
        # Proibido tocar ou inspecionar DerivBot, Sharkbot, Minha Agenda, etc.
        if scope == ScopeType.GLOBAL_CONTROL_PLANE:
            # Lista de workspaces de projetos de produto proibidos
            for slug, p_data in self.registry.items():
                if slug in ("antigravity-control-plane", "jarvis-assistant", "jarvis"):
                    continue
                wk = p_data.get("workspace")
                if wk and Path(wk).resolve() in req_p.parents or req_p == Path(wk).resolve():
                    self.telemetry["CROSS_PROJECT_DISCOVERY_BLOCKED"] += 1
                    msg = (
                        f"FIREWALL_BLOCK: Escopo GLOBAL_CONTROL_PLANE proibido de acessar projeto de produto '{slug}' ({req_p}). "
                        "CROSS_PROJECT_DISCOVERY=FORBIDDEN."
                    )
                    logger.error(msg)
                    return False, msg

            return True, "GLOBAL_CONTROL_PLANE_ACCESS_ALLOWED"

        # 3. ESCOPO PROJECT:
        # Acesso estritamente restrito ao workspace autorizado daquele projeto.
        if scope == ScopeType.PROJECT:
            if not target_project or target_project not in self.registry:
                msg = f"FIREWALL_BLOCK: Projeto alvo '{target_project}' não encontrado no registro canônico."
                logger.error(msg)
                return False, msg

            authorized_ws = self.registry[target_project].get("workspace")
            if not authorized_ws:
                msg = f"FIREWALL_BLOCK: Projeto '{target_project}' sem workspace autorizado cadastrado."
                return False, msg

            auth_path = Path(authorized_ws).resolve()

            # Checa se o arquivo requisitado pertence a OUTRO projeto de produto
            for other_slug, other_data in self.registry.items():
                if other_slug == target_project:
                    continue
                other_ws = other_data.get("workspace")
                if other_ws and (Path(other_ws).resolve() in req_p.parents or req_p == Path(other_ws).resolve()):
                    self.telemetry["CROSS_PROJECT_DISCOVERY_BLOCKED"] += 1
                    msg = (
                        f"FIREWALL_BLOCK: Projeto '{target_project}' tentou acessar '{other_slug}' ({req_p}). "
                        "CROSS_PROJECT_DISCOVERY=FORBIDDEN."
                    )
                    logger.error(msg)
                    return False, msg

            # Para operações de ESCRITA: o arquivo DEVE estar estritamente dentro do workspace autorizado
            if op_upper == "WRITE":
                if not (auth_path in req_p.parents or req_p == auth_path):
                    self.telemetry["WRONG_PROJECT_WRITES_BLOCKED"] += 1
                    msg = (
                        f"FIREWALL_BLOCK: Escrita proibida em '{req_p}'. "
                        f"Arquivo está fora do workspace autorizado '{auth_path}'. WRONG_PROJECT_WRITES=0 violado."
                    )
                    logger.error(msg)
                    return False, msg

            return True, "PROJECT_ACCESS_ALLOWED"

        return False, "UNKNOWN_SCOPE"

    def filter_personal_context(
        self,
        is_technical_task: bool = True,
        query_items: Optional[List[str]] = None,
    ) -> List[str]:
        """Remove tópicos pessoais desnecessários quando a tarefa for técnica."""
        if not query_items:
            return []

        if not is_technical_task:
            return query_items

        filtered = []
        for item in query_items:
            lower = item.lower()
            if any(p_topic in lower for p_topic in PERSONAL_TOPICS):
                self.telemetry["IRRELEVANT_PERSONAL_CONTEXT_FILTERED"] += 1
                logger.info(f"[CONTEXT_FIREWALL] Contexto pessoal irrelevante descartado: '{item}'")
            else:
                filtered.append(item)

        return filtered
