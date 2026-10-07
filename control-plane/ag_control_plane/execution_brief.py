from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import yaml


@dataclass
class FilePlanItem:
    path: str
    operation: str = "MODIFY"  # MODIFY, CREATE, DELETE, READ_ONLY, RENAME
    symbols: List[str] = field(default_factory=list)
    instruction: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "operation": self.operation.upper(),
            "symbols": self.symbols,
            "instruction": self.instruction,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FilePlanItem:
        return cls(
            path=str(data.get("path", "")).strip(),
            operation=str(data.get("operation", "MODIFY")).strip().upper(),
            symbols=[str(s).strip() for s in data.get("symbols", []) if s],
            instruction=str(data.get("instruction", "")).strip(),
        )


@dataclass
class ReadOnlyContextItem:
    path: str
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReadOnlyContextItem:
        return cls(
            path=str(data.get("path", "")).strip(),
            reason=str(data.get("reason", "")).strip(),
        )


def normalize_path(path: str) -> str:
    """Normaliza caminhos relativos ao workspace e bloqueia escapes com '../'."""
    clean = str(path).strip().replace("\\", "/")

    # Bloqueia escape traversal
    parts = clean.split("/")
    if ".." in parts:
        raise ValueError(f"PATH_TRAVERSAL_BLOCKED: '{path}' tenta escapar do workspace via '../'")

    # Remove leading ./
    while clean.startswith("./"):
        clean = clean[2:]

    # Remove leading slashes
    while clean.startswith("/"):
        clean = clean[1:]

    # Remove redundant slashes //
    clean = re.sub(r"/+", "/", clean)

    # Remove trailing slash
    if clean.endswith("/") and len(clean) > 1:
        clean = clean.rstrip("/")

    return clean


def paths_overlap(path_a: str, path_b: str) -> bool:
    """Verifica se dois caminhos coincidem ou possuem relação ancestral pai-filho."""
    norm_a = normalize_path(path_a)
    norm_b = normalize_path(path_b)

    if norm_a == norm_b:
        return True

    # Verifica se A é pai/diretório de B
    if norm_b.startswith(norm_a + "/"):
        return True

    # Verifica se B é pai/diretório de A
    if norm_a.startswith(norm_b + "/"):
        return True

    return False


def access_conflicts(mode_a: str, mode_b: str) -> bool:
    """
    READ + READ = SAFE (False)
    READ + WRITE = CONFLICT (True)
    WRITE + READ = CONFLICT (True)
    WRITE + WRITE = CONFLICT (True)
    """
    m_a = mode_a.upper()
    m_b = mode_b.upper()
    if m_a == "READ" and m_b == "READ":
        return False
    return True


def normalize_symbol(symbol: str) -> str:
    """Normaliza identificador simbólico para comparação determinística.

    Remove:
    - espaços nas pontas e ao redor de delimitadores
    - separadores redundantes
    - prefixos de arquivo (ex: src/auth.py::, auth.py:, auth.ts::)
    - unifica '::' em '.'
    """
    s = str(symbol).strip()
    if not s:
        return ""
    # Remove prefixo de arquivo quando presente (ex: 'path/file.py::' ou 'path/file.ts:')
    s = re.sub(r"^(?:[\w\.\-/]+\.(?:py|ts|js|jsx|tsx|go|rs|java|rb|cpp|c|h))::?", "", s).strip()
    # Unifica separadores '::' em '.'
    s = s.replace("::", ".")
    # Remove espaços ao redor de '.'
    s = re.sub(r"\s*\.\s*", ".", s)
    # Remove múltiplos '.' consecutivos
    s = re.sub(r"\.+", ".", s)
    # Remove pontos nas extremidades
    s = s.strip(".")
    return s


def symbols_overlap(sym_a: str, sym_b: str) -> bool:
    """Verifica se dois identificadores de símbolos são equivalentes após normalização."""
    norm_a = normalize_symbol(sym_a)
    norm_b = normalize_symbol(sym_b)
    if not norm_a or not norm_b:
        return False
    return norm_a == norm_b


def normalize_semantic_resource(resource: str) -> str:
    """Normaliza recurso semântico hierárquico.

    Remove:
    - espaços nas extremidades
    - barras repetidas
    - barras iniciais e finais
    - uniformiza para lowercase determinístico
    """
    s = str(resource).strip().lower()
    s = re.sub(r"/+", "/", s)
    s = s.strip("/")
    return s


def semantic_resources_overlap(res_a: str, res_b: str) -> bool:
    """Verifica se recursos semânticos coincidem ou possuem relação hierárquica pai-filho.

    Recursos irmãos (ex: oauth/google vs oauth/microsoft) não coincidem (retornam False).
    """
    norm_a = normalize_semantic_resource(res_a)
    norm_b = normalize_semantic_resource(res_b)
    if not norm_a or not norm_b:
        return False
    if norm_a == norm_b:
        return True
    if norm_b.startswith(norm_a + "/"):
        return True
    if norm_a.startswith(norm_b + "/"):
        return True
    return False


@dataclass
class ImpactSet:
    read_files: List[str] = field(default_factory=list)
    write_files: List[str] = field(default_factory=list)
    read_symbols: List[str] = field(default_factory=list)
    write_symbols: List[str] = field(default_factory=list)
    read_semantic_resources: List[str] = field(default_factory=list)
    write_semantic_resources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "read_files": self.read_files,
            "write_files": self.write_files,
            "read_symbols": self.read_symbols,
            "write_symbols": self.write_symbols,
            "read_semantic_resources": self.read_semantic_resources,
            "write_semantic_resources": self.write_semantic_resources,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ImpactSet:
        return cls(
            read_files=[normalize_path(str(f)) for f in data.get("read_files", []) if f],
            write_files=[normalize_path(str(f)) for f in data.get("write_files", []) if f],
            read_symbols=[normalize_symbol(str(s)) for s in data.get("read_symbols", []) if s and normalize_symbol(str(s))],
            write_symbols=[normalize_symbol(str(s)) for s in data.get("write_symbols", []) if s and normalize_symbol(str(s))],
            read_semantic_resources=[normalize_semantic_resource(str(r)) for r in data.get("read_semantic_resources", []) if r and normalize_semantic_resource(str(r))],
            write_semantic_resources=[normalize_semantic_resource(str(r)) for r in data.get("write_semantic_resources", []) if r and normalize_semantic_resource(str(r))],
        )


@dataclass
class ConflictDetail:
    conflict_type: str = "PATH"  # PATH, SYMBOL, SEMANTIC_RESOURCE
    resource: str = ""
    current_issue: Optional[int] = None
    conflicting_issue: Optional[int] = None
    access_a: str = "WRITE"
    access_b: str = "WRITE"
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_type": self.conflict_type,
            "resource": self.resource,
            "current_issue": self.current_issue,
            "conflicting_issue": self.conflicting_issue,
            "access_a": self.access_a,
            "access_b": self.access_b,
            "reason": self.reason or f"Conflito de {self.conflict_type} no recurso '{self.resource}' ({self.access_a} vs {self.access_b})",
        }

    def to_reason_string(self) -> str:
        r = self.reason or f"Conflito de {self.conflict_type} no recurso '{self.resource}' ({self.access_a} vs {self.access_b})"
        return (
            f"CONFLICT_TYPE={self.conflict_type}\n"
            f"RESOURCE={self.resource}\n"
            f"CURRENT_ISSUE={self.current_issue}\n"
            f"CONFLICTING_ISSUE={self.conflicting_issue}\n"
            f"ACCESS_A={self.access_a}\n"
            f"ACCESS_B={self.access_b}\n"
            f"REASON={r}"
        )


# Alias para retrocompatibilidade total com PATCH 2A.1
PathConflictDetail = ConflictDetail


def detect_path_conflicts(
    current_brief: ExecutionBrief,
    current_issue_id: Optional[int],
    other_brief: ExecutionBrief,
    other_issue_id: Optional[int],
) -> List[ConflictDetail]:
    """Detecta conflitos de caminho entre dois ExecutionBriefs conforme as regras de acesso."""
    conflicts: List[ConflictDetail] = []
    c_impact = current_brief.effective_impact_set
    o_impact = other_brief.effective_impact_set

    # 1. WRITE x WRITE
    for cw in c_impact.write_files:
        for ow in o_impact.write_files:
            if paths_overlap(cw, ow):
                conflicts.append(ConflictDetail(
                    conflict_type="PATH",
                    resource=cw,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="WRITE",
                    access_b="WRITE",
                    reason=f"Conflito de escrita simultânea no caminho '{cw}'",
                ))

    # 2. WRITE x READ
    for cw in c_impact.write_files:
        for or_ in o_impact.read_files:
            if paths_overlap(cw, or_):
                conflicts.append(ConflictDetail(
                    conflict_type="PATH",
                    resource=cw,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="WRITE",
                    access_b="READ",
                    reason=f"Conflito WRITE/READ no caminho '{cw}'",
                ))

    # 3. READ x WRITE
    for cr in c_impact.read_files:
        for ow in o_impact.write_files:
            if paths_overlap(cr, ow):
                conflicts.append(ConflictDetail(
                    conflict_type="PATH",
                    resource=cr,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="READ",
                    access_b="WRITE",
                    reason=f"Conflito READ/WRITE no caminho '{cr}'",
                ))

    # 4. READ x READ -> SAFE (não gera conflito)
    return conflicts


def detect_symbol_conflicts(
    current_brief: ExecutionBrief,
    current_issue_id: Optional[int],
    other_brief: ExecutionBrief,
    other_issue_id: Optional[int],
) -> List[ConflictDetail]:
    """Detecta conflitos de símbolos entre dois ExecutionBriefs conforme a matriz de acesso."""
    conflicts: List[ConflictDetail] = []
    c_impact = current_brief.effective_impact_set
    o_impact = other_brief.effective_impact_set

    # 1. WRITE x WRITE
    for cw in c_impact.write_symbols:
        for ow in o_impact.write_symbols:
            if symbols_overlap(cw, ow):
                conflicts.append(ConflictDetail(
                    conflict_type="SYMBOL",
                    resource=cw,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="WRITE",
                    access_b="WRITE",
                    reason=f"Conflito de escrita simultânea no símbolo '{cw}'",
                ))

    # 2. WRITE x READ
    for cw in c_impact.write_symbols:
        for or_ in o_impact.read_symbols:
            if symbols_overlap(cw, or_):
                conflicts.append(ConflictDetail(
                    conflict_type="SYMBOL",
                    resource=cw,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="WRITE",
                    access_b="READ",
                    reason=f"Conflito WRITE/READ no símbolo '{cw}'",
                ))

    # 3. READ x WRITE
    for cr in c_impact.read_symbols:
        for ow in o_impact.write_symbols:
            if symbols_overlap(cr, ow):
                conflicts.append(ConflictDetail(
                    conflict_type="SYMBOL",
                    resource=cr,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="READ",
                    access_b="WRITE",
                    reason=f"Conflito READ/WRITE no símbolo '{cr}'",
                ))

    # 4. READ x READ -> SAFE
    return conflicts


def detect_semantic_conflicts(
    current_brief: ExecutionBrief,
    current_issue_id: Optional[int],
    other_brief: ExecutionBrief,
    other_issue_id: Optional[int],
) -> List[ConflictDetail]:
    """Detecta conflitos de recursos semânticos hierárquicos conforme a matriz de acesso."""
    conflicts: List[ConflictDetail] = []
    c_impact = current_brief.effective_impact_set
    o_impact = other_brief.effective_impact_set

    # 1. WRITE x WRITE
    for cw in c_impact.write_semantic_resources:
        for ow in o_impact.write_semantic_resources:
            if semantic_resources_overlap(cw, ow):
                conflicts.append(ConflictDetail(
                    conflict_type="SEMANTIC_RESOURCE",
                    resource=cw,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="WRITE",
                    access_b="WRITE",
                    reason=f"Conflito de escrita simultânea no recurso semântico '{cw}' (overlap com '{ow}')",
                ))

    # 2. WRITE x READ
    for cw in c_impact.write_semantic_resources:
        for or_ in o_impact.read_semantic_resources:
            if semantic_resources_overlap(cw, or_):
                conflicts.append(ConflictDetail(
                    conflict_type="SEMANTIC_RESOURCE",
                    resource=cw,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="WRITE",
                    access_b="READ",
                    reason=f"Conflito WRITE/READ no recurso semântico '{cw}' (overlap com '{or_}')",
                ))

    # 3. READ x WRITE
    for cr in c_impact.read_semantic_resources:
        for ow in o_impact.write_semantic_resources:
            if semantic_resources_overlap(cr, ow):
                conflicts.append(ConflictDetail(
                    conflict_type="SEMANTIC_RESOURCE",
                    resource=cr,
                    current_issue=current_issue_id,
                    conflicting_issue=other_issue_id,
                    access_a="READ",
                    access_b="WRITE",
                    reason=f"Conflito READ/WRITE no recurso semântico '{cr}' (overlap com '{ow}')",
                ))

    # 4. READ x READ -> SAFE
    return conflicts


def detect_impact_conflicts(
    current_brief: ExecutionBrief,
    current_issue_id: Optional[int],
    other_brief: ExecutionBrief,
    other_issue_id: Optional[int],
) -> List[ConflictDetail]:
    """Avalia conflitos rigorosamente na ordem canônica do ImpactGuard:
    1. PATH
    2. SYMBOL
    3. SEMANTIC_RESOURCE
    """
    conflicts: List[ConflictDetail] = []
    conflicts.extend(detect_path_conflicts(current_brief, current_issue_id, other_brief, other_issue_id))
    conflicts.extend(detect_symbol_conflicts(current_brief, current_issue_id, other_brief, other_issue_id))
    conflicts.extend(detect_semantic_conflicts(current_brief, current_issue_id, other_brief, other_issue_id))
    return conflicts


@dataclass
class ExecutionBrief:
    refinement_status: str = "PASS"  # PASS, BLOCKED, NEEDS_INFO
    project: str = ""
    workstream: str = "system"  # system, sharkbot, general
    objective: str = ""
    baseline_sha: str = ""
    skill_primary: str = ""
    skill_support: Optional[str] = None
    files: List[FilePlanItem] = field(default_factory=list)
    impact_set: Optional[ImpactSet] = None
    read_only_context: List[ReadOnlyContextItem] = field(default_factory=list)
    do_not_touch: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    acceptance: List[str] = field(default_factory=list)
    conflicts_checked: bool = True
    architecture_summary: List[str] = field(default_factory=list)
    known_risks: List[str] = field(default_factory=list)
    rollback: str = ""
    ai_metadata: Optional[Dict[str, Any]] = None

    def validate(self) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if self.refinement_status not in {"PASS", "BLOCKED", "NEEDS_INFO"}:
            errors.append(f"Invalid refinement_status: {self.refinement_status}")
        if not self.project:
            errors.append("project cannot be empty")
        if self.workstream not in {"system", "sharkbot", "general"}:
            errors.append(f"Invalid workstream: {self.workstream}")
        if not self.objective:
            errors.append("objective cannot be empty")
        if not self.baseline_sha or len(self.baseline_sha) < 7:
            errors.append("baseline_sha must be at least 7 characters")
        if not self.skill_primary or not self.skill_primary.startswith("@"):
            errors.append(f"skill_primary must start with '@': {self.skill_primary}")
        if not self.files:
            errors.append("files list cannot be empty")
        for f in self.files:
            if not f.path:
                errors.append("FilePlanItem path cannot be empty")
            if f.operation not in {"MODIFY", "CREATE", "DELETE", "READ_ONLY", "RENAME"}:
                errors.append(f"Invalid operation {f.operation} on file {f.path}")
        if not self.conflicts_checked:
            errors.append("conflicts_checked must be True")
        return len(errors) == 0, errors

    def validate_fast_path(
        self,
        registry: Dict[str, Any],
        target_repo: Optional[str] = None,
        head_commit: Optional[str] = None,
        dependencies: Optional[List[int]] = None,
    ) -> Tuple[bool, List[str]]:
        """Validação cirúrgica do Fast Path (Item 4).

        Valida estritamente:
        - PROJECT: presente no registry e write_allowed=True
        - REPOSITORY: confere com o repositório configurado
        - HEAD / BASELINE: baseline_sha presente e consistente
        - FILES: arquivos especificados sem path traversal
        - SCOPE: operações permitidas dentro do escopo
        - CONFLICTS: conflicts_checked=True
        - DEPENDENCIES: sem dependências bloqueantes não resolvidas
        - SENTINELA: skill primária @ com conformidade Sentinela
        """
        errors: List[str] = []

        # 1. Validação básica de campos obrigatórios
        ok_basic, basic_errs = self.validate()
        if not ok_basic:
            errors.extend(basic_errs)

        # 2. PROJECT
        lower_reg = {k.lower(): (k, v) for k, v in registry.items()}
        proj_key = self.project.lower()
        if proj_key not in lower_reg:
            errors.append(f"PROJECT_NOT_IN_REGISTRY: '{self.project}'")
        else:
            orig_k, proj_data = lower_reg[proj_key]
            if not proj_data.get("write_allowed", False):
                errors.append(f"PROJECT_WRITE_DISALLOWED: '{self.project}'")

            # 3. REPOSITORY
            expected_repo = proj_data.get("repo", "")
            if target_repo and expected_repo and target_repo.lower() != expected_repo.lower():
                errors.append(f"REPOSITORY_MISMATCH: esperado '{expected_repo}', obtido '{target_repo}'")

        # 4. HEAD / BASELINE
        if not self.baseline_sha or len(self.baseline_sha) < 7:
            errors.append(f"INVALID_BASELINE_SHA: '{self.baseline_sha}'")

        # 5. FILES & SCOPE (Path traversal e integridade)
        for f in self.files:
            if ".." in f.path or f.path.startswith("/"):
                errors.append(f"UNSAFE_FILE_PATH: '{f.path}'")

        # 6. CONFLICTS
        if not self.conflicts_checked:
            errors.append("CONFLICTS_NOT_CHECKED: conflicts_checked deve ser True")

        # 7. DEPENDENCIES
        # Se dependencies forem passadas, checar se não estão vazias/pendentes
        # (gerenciado externamente no dispatcher)

        # 8. SENTINELA (Skill não genérica)
        generic_skills = {
            "@developer", "@desenvolvedor", "@programador", "@generic",
            "@coder", "@software-engineer", "@assistant", "@assistente"
        }
        if self.skill_primary.lower() in generic_skills:
            errors.append(f"SENTINELA_GENERIC_SKILL_FORBIDDEN: '{self.skill_primary}'")

        return len(errors) == 0, errors

    @property
    def effective_impact_set(self) -> ImpactSet:
        """Deriva ou normaliza o ImpactSet de arquivos, símbolos e recursos semânticos."""
        read_f: List[str] = []
        write_f: List[str] = []
        read_s: List[str] = []
        write_s: List[str] = []
        read_r: List[str] = []
        write_r: List[str] = []

        if self.impact_set is not None:
            read_f.extend(self.impact_set.read_files)
            write_f.extend(self.impact_set.write_files)
            read_s.extend(self.impact_set.read_symbols)
            write_s.extend(self.impact_set.write_symbols)
            read_r.extend(self.impact_set.read_semantic_resources)
            write_r.extend(self.impact_set.write_semantic_resources)

        # 1. Arquivos: se não foram fornecidos no impact_set, deriva de files e read_only_context
        if not read_f and not write_f:
            for f in self.files:
                op = f.operation.upper()
                try:
                    norm = normalize_path(f.path)
                except ValueError:
                    norm = f.path
                if op in ("MODIFY", "CREATE", "DELETE", "RENAME"):
                    write_f.append(norm)
                elif op == "READ_ONLY":
                    read_f.append(norm)
                else:
                    write_f.append(norm)

            for ro in self.read_only_context:
                try:
                    read_f.append(normalize_path(ro.path))
                except ValueError:
                    read_f.append(ro.path)

        # 2. Símbolos: se não foram fornecidos no impact_set, deriva dos FilePlanItems
        if not read_s and not write_s:
            for f in self.files:
                if f.symbols:
                    op = f.operation.upper()
                    for sym in f.symbols:
                        norm_sym = normalize_symbol(sym)
                        if norm_sym:
                            if op in ("MODIFY", "CREATE", "DELETE", "RENAME"):
                                write_s.append(norm_sym)
                            elif op == "READ_ONLY":
                                read_s.append(norm_sym)
                            else:
                                write_s.append(norm_sym)

        # 3. Recursos Semânticos: se não foram fornecidos no impact_set, obtém de ai_metadata se presente
        if not read_r and not write_r and self.ai_metadata:
            sem_meta = self.ai_metadata.get("semantic_resources")
            if isinstance(sem_meta, dict):
                read_r.extend([normalize_semantic_resource(r) for r in sem_meta.get("read", []) if r])
                write_r.extend([normalize_semantic_resource(r) for r in sem_meta.get("write", []) if r])

        return ImpactSet(
            read_files=list(dict.fromkeys(normalize_path(p) for p in read_f if p)),
            write_files=list(dict.fromkeys(normalize_path(p) for p in write_f if p)),
            read_symbols=list(dict.fromkeys(normalize_symbol(s) for s in read_s if normalize_symbol(s))),
            write_symbols=list(dict.fromkeys(normalize_symbol(s) for s in write_s if normalize_symbol(s))),
            read_semantic_resources=list(dict.fromkeys(normalize_semantic_resource(r) for r in read_r if normalize_semantic_resource(r))),
            write_semantic_resources=list(dict.fromkeys(normalize_semantic_resource(r) for r in write_r if normalize_semantic_resource(r))),
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "refinement_status": self.refinement_status,
            "project": self.project,
            "workstream": self.workstream,
            "objective": self.objective,
            "baseline_sha": self.baseline_sha,
            "skill_primary": self.skill_primary,
            "skill_support": self.skill_support,
            "files": [f.to_dict() for f in self.files],
            "impact_set": self.effective_impact_set.to_dict(),
            "read_only_context": [r.to_dict() for r in self.read_only_context],
            "do_not_touch": self.do_not_touch,
            "tests": self.tests,
            "acceptance": self.acceptance,
            "conflicts_checked": self.conflicts_checked,
        }
        if self.architecture_summary:
            data["architecture_summary"] = self.architecture_summary
        if self.known_risks:
            data["known_risks"] = self.known_risks
        if self.rollback:
            data["rollback"] = self.rollback
        if self.ai_metadata:
            data["ai_metadata"] = self.ai_metadata
        return {"execution_brief": data}

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict(), sort_keys=False, allow_unicode=True)

    @classmethod
    def from_dict(cls, raw_data: Dict[str, Any]) -> ExecutionBrief:
        data = raw_data.get("execution_brief", raw_data)
        files = [
            FilePlanItem.from_dict(item) if isinstance(item, dict) else FilePlanItem(path=str(item))
            for item in data.get("files", [])
        ]
        read_only = [
            ReadOnlyContextItem.from_dict(item) if isinstance(item, dict) else ReadOnlyContextItem(path=str(item))
            for item in data.get("read_only_context", [])
        ]
        raw_impact = data.get("impact_set")
        parsed_impact = None
        if isinstance(raw_impact, dict):
            try:
                parsed_impact = ImpactSet.from_dict(raw_impact)
            except Exception:
                parsed_impact = None

        return cls(
            refinement_status=str(data.get("refinement_status", "PASS")).strip().upper(),
            project=str(data.get("project", "")).strip(),
            workstream=str(data.get("workstream", "system")).strip().lower(),
            objective=str(data.get("objective", "")).strip(),
            baseline_sha=str(data.get("baseline_sha", "")).strip(),
            skill_primary=str(data.get("skill_primary", "")).strip(),
            skill_support=str(data.get("skill_support", "")).strip() if data.get("skill_support") else None,
            files=files,
            impact_set=parsed_impact,
            read_only_context=read_only,
            do_not_touch=[str(d).strip() for d in data.get("do_not_touch", []) if d],
            tests=[str(t).strip() for t in data.get("tests", []) if t],
            acceptance=[str(a).strip() for a in data.get("acceptance", []) if a],
            conflicts_checked=bool(data.get("conflicts_checked", False)),
            architecture_summary=[str(s).strip() for s in data.get("architecture_summary", []) if s],
            known_risks=[str(k).strip() for k in data.get("known_risks", []) if k],
            rollback=str(data.get("rollback", "")).strip(),
            ai_metadata=data.get("ai_metadata") if isinstance(data.get("ai_metadata"), dict) else None,
        )

    @classmethod
    def from_yaml(cls, yaml_str: str) -> ExecutionBrief:
        parsed = yaml.safe_load(yaml_str)
        if not isinstance(parsed, dict):
            raise ValueError("YAML content did not parse to a dictionary")
        return cls.from_dict(parsed)
