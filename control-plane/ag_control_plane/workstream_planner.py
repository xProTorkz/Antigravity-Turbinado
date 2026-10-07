"""Workstream Planner — Decomposição de tarefas grandes em workstreams verificáveis (Task #24).

Diretrizes:
- Não dividir tarefas pequenas ou triviais (heurística de fan-out);
- Não criar subagentes por quantidade artificial;
- Workstream só é parallel_safe=True quando o ConflictGuard comprovar ausência de sobreposição;
- Um workstream deve possuir um único objetivo e role especializado;
- Integrator único é sempre obrigatório e consolida o fan-in final.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from .execution_brief import (
    ExecutionBrief,
    FilePlanItem,
    ImpactSet,
    ReadOnlyContextItem,
    access_conflicts,
    normalize_path,
    normalize_semantic_resource,
    normalize_symbol,
    paths_overlap,
    semantic_resources_overlap,
    symbols_overlap,
)

logger = logging.getLogger("ag-workstream-planner")


class WorkstreamMode(str, Enum):
    READ_ONLY = "READ_ONLY"
    WRITE = "WRITE"
    REVIEW = "REVIEW"
    TEST = "TEST"


class WorkstreamRole(str, Enum):
    DISCOVERY = "DISCOVERY"
    DEPENDENCY = "DEPENDENCY"
    IMPLEMENTATION = "IMPLEMENTATION"
    TEST = "TEST"
    SECURITY_REVIEW = "SECURITY_REVIEW"
    DOCS_SYNC = "DOCS_SYNC"
    INTEGRATOR = "INTEGRATOR"


class WorkstreamRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ExecutionProfile(str, Enum):
    FAST = "FAST"
    STANDARD = "STANDARD"
    PARALLEL = "PARALLEL"
    DEEP = "DEEP"


@dataclass
class Workstream:
    id: str
    role: WorkstreamRole
    objective: str
    mode: WorkstreamMode
    dependencies: List[str] = field(default_factory=list)
    allowed_files: List[str] = field(default_factory=list)
    read_only_context: List[str] = field(default_factory=list)
    write_symbols: List[str] = field(default_factory=list)
    read_symbols: List[str] = field(default_factory=list)
    semantic_resources: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    risk: WorkstreamRisk = WorkstreamRisk.LOW
    estimated_effort: str = "S"  # S, M, L
    parallel_safe: bool = False
    project: str = ""
    status: str = "PENDING"  # PENDING, READY, RUNNING, REVIEW, DONE, BLOCKED, FAILED, CANCELLED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["role"] = self.role.value if isinstance(self.role, WorkstreamRole) else str(self.role)
        d["mode"] = self.mode.value if isinstance(self.mode, WorkstreamMode) else str(self.mode)
        d["risk"] = self.risk.value if isinstance(self.risk, WorkstreamRisk) else str(self.risk)
        return d

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), sort_keys=False, allow_unicode=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Workstream:
        raw_role = data.get("role", "IMPLEMENTATION")
        raw_mode = data.get("mode", "WRITE")
        raw_risk = data.get("risk", "LOW")

        role = WorkstreamRole(raw_role) if raw_role in WorkstreamRole.__members__ else WorkstreamRole.IMPLEMENTATION
        mode = WorkstreamMode(raw_mode) if raw_mode in WorkstreamMode.__members__ else WorkstreamMode.WRITE
        risk = WorkstreamRisk(raw_risk) if raw_risk in WorkstreamRisk.__members__ else WorkstreamRisk.LOW

        return cls(
            id=str(data.get("id", "")).strip(),
            role=role,
            objective=str(data.get("objective", "")).strip(),
            mode=mode,
            dependencies=[str(d).strip() for d in data.get("dependencies", []) if d],
            allowed_files=[normalize_path(str(f)) for f in data.get("allowed_files", []) if f],
            read_only_context=[normalize_path(str(f)) for f in data.get("read_only_context", []) if f],
            write_symbols=[normalize_symbol(str(s)) for s in data.get("write_symbols", []) if s],
            read_symbols=[normalize_symbol(str(s)) for s in data.get("read_symbols", []) if s],
            semantic_resources=[normalize_semantic_resource(str(r)) for r in data.get("semantic_resources", []) if r],
            expected_outputs=[str(o).strip() for o in data.get("expected_outputs", []) if o],
            risk=risk,
            estimated_effort=str(data.get("estimated_effort", "S")),
            parallel_safe=bool(data.get("parallel_safe", False)),
            project=str(data.get("project", "")).strip(),
            status=str(data.get("status", "PENDING")),
            result=data.get("result"),
            error=data.get("error"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
        )


class WorkstreamPlanner:
    """Planeja e decompõe tarefas de ExecutionBrief em workstreams governados."""

    def __init__(self, root_dir: Optional[Path] = None, registry: Optional[Dict[str, Any]] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent
        self.registry = registry or {}

    def determine_profile(self, brief: ExecutionBrief) -> ExecutionProfile:
        """Determina perfil de execução automático (FAST, STANDARD, PARALLEL, DEEP)."""
        files = brief.files or []
        read_only = brief.read_only_context or []
        tests = brief.tests or []

        # Quantidade de áreas de arquivos distintas (pastas de primeiro nível)
        areas: Set[str] = set()
        for f in files:
            parts = f.path.split("/")
            if len(parts) > 1:
                areas.add(parts[0])
            else:
                areas.add(".")

        # Identifica risco
        is_high_risk = any(
            any(w in f.path.lower() for w in ["auth", "security", "permission", "lock", "gateway", "token", "crypto"])
            for f in files
        ) or any(
            any(w in s.lower() for w in ["auth", "security", "token", "password", "key"])
            for f in files for s in f.symbols
        )

        total_files_count = len(files)

        if is_high_risk or total_files_count >= 5 or len(areas) >= 3:
            return ExecutionProfile.DEEP

        if total_files_count >= 2 and len(areas) >= 2:
            return ExecutionProfile.PARALLEL

        if total_files_count == 1 and not read_only and len(tests) <= 1:
            return ExecutionProfile.FAST

        return ExecutionProfile.STANDARD

    def check_workstream_conflict(self, ws_a: Workstream, ws_b: Workstream) -> bool:
        """Verifica se há conflito de recursos entre dois workstreams.

        Retorna True se houver conflito (não podem rodar em paralelo), False se forem seguros/disjuntos.
        """
        # Se ambos forem puramente READ_ONLY, TEST ou REVIEW sem escrita: SAFE
        is_write_a = (ws_a.mode == WorkstreamMode.WRITE)
        is_write_b = (ws_b.mode == WorkstreamMode.WRITE)

        if not is_write_a and not is_write_b:
            return False

        # 1. PATH conflict
        all_paths_a = [(p, "WRITE" if is_write_a else "READ") for p in ws_a.allowed_files]
        all_paths_a.extend([(p, "READ") for p in ws_a.read_only_context])

        all_paths_b = [(p, "WRITE" if is_write_b else "READ") for p in ws_b.allowed_files]
        all_paths_b.extend([(p, "READ") for p in ws_b.read_only_context])

        for path_a, mode_a in all_paths_a:
            for path_b, mode_b in all_paths_b:
                if paths_overlap(path_a, path_b) and access_conflicts(mode_a, mode_b):
                    return True

        # 2. SYMBOL conflict
        symbols_a = [(s, "WRITE") for s in ws_a.write_symbols] + [(s, "READ") for s in ws_a.read_symbols]
        symbols_b = [(s, "WRITE") for s in ws_b.write_symbols] + [(s, "READ") for s in ws_b.read_symbols]

        for sym_a, mode_a in symbols_a:
            for sym_b, mode_b in symbols_b:
                if symbols_overlap(sym_a, sym_b) and access_conflicts(mode_a, mode_b):
                    return True

        # 3. SEMANTIC_RESOURCE conflict
        for res_a in ws_a.semantic_resources:
            for res_b in ws_b.semantic_resources:
                if semantic_resources_overlap(res_a, res_b):
                    # Se pelo menos um for write, conflita
                    if is_write_a or is_write_b:
                        return True

        return False

    def plan_workstreams(
        self,
        brief: ExecutionBrief,
        profile: Optional[ExecutionProfile] = None,
    ) -> List[Workstream]:
        """Decompõe o ExecutionBrief em workstreams governados."""
        if profile is None:
            profile = self.determine_profile(brief)

        project = brief.project or "antigravity-control-plane"
        workstreams: List[Workstream] = []

        files = brief.files or []
        read_only = [r.path for r in (brief.read_only_context or [])]
        tests = brief.tests or []

        # Extrai símbolos e semantic resources do brief/impact_set se presentes
        all_symbols = []
        all_semantic = []
        if brief.impact_set:
            all_symbols = [s.name for s in brief.impact_set.symbols]
            all_semantic = [r.name for r in brief.impact_set.semantic_resources]

        # 1. Caso FAST ou mono-arquivo trivial: NÃO cria subagentes artificiais
        if profile == ExecutionProfile.FAST or len(files) <= 1:
            allowed = [f.path for f in files]
            syms = [s for f in files for s in f.symbols] or all_symbols
            ws_single = Workstream(
                id="ws_impl_core",
                role=WorkstreamRole.IMPLEMENTATION,
                objective=brief.objective or "Executar implementação direcionada",
                mode=WorkstreamMode.WRITE,
                dependencies=[],
                allowed_files=allowed,
                read_only_context=read_only,
                write_symbols=syms,
                semantic_resources=all_semantic,
                expected_outputs=["Arquivos modificados e testes validados"],
                risk=WorkstreamRisk.LOW,
                estimated_effort="S",
                parallel_safe=False,
                project=project,
            )
            ws_integ = Workstream(
                id="ws_integrator",
                role=WorkstreamRole.INTEGRATOR,
                objective="Consolidação e validação final Sentinela",
                mode=WorkstreamMode.REVIEW,
                dependencies=["ws_impl_core"],
                allowed_files=[],
                read_only_context=allowed + read_only,
                risk=WorkstreamRisk.LOW,
                estimated_effort="S",
                parallel_safe=False,
                project=project,
            )
            return [ws_single, ws_integ]

        # 2. Caso PARALLEL ou DEEP: Decomposição estruturada em workstreams especializados
        dep_ids: List[str] = []

        # 2.1 Discovery (Read-only) se houver contexto amplo para analisar
        if read_only or len(files) >= 3:
            ws_disc = Workstream(
                id="ws_discovery",
                role=WorkstreamRole.DISCOVERY,
                objective="Mapear arquitetura, estado de arquivos e pontos de modificação",
                mode=WorkstreamMode.READ_ONLY,
                dependencies=[],
                allowed_files=[],
                read_only_context=read_only + [f.path for f in files],
                read_symbols=all_symbols,
                semantic_resources=all_semantic,
                risk=WorkstreamRisk.LOW,
                estimated_effort="S",
                parallel_safe=True,
                project=project,
            )
            workstreams.append(ws_disc)
            dep_ids.append("ws_discovery")

        # 2.2 Dependency workstream se profile for DEEP
        if profile == ExecutionProfile.DEEP:
            ws_dep = Workstream(
                id="ws_dependency",
                role=WorkstreamRole.DEPENDENCY,
                objective="Verificar dependências, imports cruzados e contratos de interface",
                mode=WorkstreamMode.READ_ONLY,
                dependencies=[],
                allowed_files=[],
                read_only_context=read_only + [f.path for f in files],
                read_symbols=all_symbols,
                risk=WorkstreamRisk.LOW,
                estimated_effort="S",
                parallel_safe=True,
                project=project,
            )
            workstreams.append(ws_dep)
            dep_ids.append("ws_dependency")

        # 2.3 Implementation workstreams agrupados por arquivo ou módulo
        impl_ids: List[str] = []
        for idx, f_item in enumerate(files, start=1):
            w_id = f"ws_impl_{idx}"
            syms_write = f_item.symbols or []
            ws_impl = Workstream(
                id=w_id,
                role=WorkstreamRole.IMPLEMENTATION,
                objective=f_item.instruction or f"Implementar alterações em {f_item.path}",
                mode=WorkstreamMode.WRITE,
                dependencies=list(dep_ids),
                allowed_files=[f_item.path],
                read_only_context=list(read_only),
                write_symbols=syms_write,
                semantic_resources=[r for r in all_semantic if any(part in f_item.path for part in r.split("/"))],
                risk=WorkstreamRisk.MEDIUM if profile == ExecutionProfile.DEEP else WorkstreamRisk.LOW,
                estimated_effort="M",
                parallel_safe=False,  # Será calculado abaixo contra outros writers
                project=project,
            )
            workstreams.append(ws_impl)
            impl_ids.append(w_id)

        # 2.4 Test Planner / Runner workstream
        ws_test = Workstream(
            id="ws_test",
            role=WorkstreamRole.TEST,
            objective="Planejar e validar suíte de testes unitários e de integração",
            mode=WorkstreamMode.TEST,
            dependencies=list(impl_ids),
            allowed_files=[t for t in tests if "test" in t.lower() and not t.startswith("tests/test_fast_mode")],
            read_only_context=[f.path for f in files],
            risk=WorkstreamRisk.LOW,
            estimated_effort="S",
            parallel_safe=True,
            project=project,
        )
        workstreams.append(ws_test)

        # 2.5 Security Reviewer se profile for DEEP
        if profile == ExecutionProfile.DEEP:
            ws_sec = Workstream(
                id="ws_security_review",
                role=WorkstreamRole.SECURITY_REVIEW,
                objective="Auditar segredos, permissões, sanitização e políticas fail-closed",
                mode=WorkstreamMode.REVIEW,
                dependencies=list(impl_ids),
                allowed_files=[],
                read_only_context=[f.path for f in files],
                risk=WorkstreamRisk.HIGH,
                estimated_effort="S",
                parallel_safe=True,
                project=project,
            )
            workstreams.append(ws_sec)

        # 2.6 Integrator Final Obrigatório (Fan-in)
        all_previous_ids = [ws.id for ws in workstreams]
        ws_integrator = Workstream(
            id="ws_integrator",
            role=WorkstreamRole.INTEGRATOR,
            objective="Consolidação final com fan-in, verificação de diffs e validação Sentinela",
            mode=WorkstreamMode.REVIEW,
            dependencies=all_previous_ids,
            allowed_files=[],
            read_only_context=[f.path for f in files] + read_only,
            risk=WorkstreamRisk.LOW,
            estimated_effort="S",
            parallel_safe=False,
            project=project,
        )
        workstreams.append(ws_integrator)

        # 3. Calcula `parallel_safe` determinístico entre writers e readers
        # Para cada writer, compara com outros writers simultâneos
        writers = [ws for ws in workstreams if ws.mode == WorkstreamMode.WRITE]
        for w in writers:
            has_conflict = False
            for other_w in writers:
                if w.id == other_w.id:
                    continue
                if self.check_workstream_conflict(w, other_w):
                    has_conflict = True
                    break
            # Se for disjunto de todos os outros writers, é parallel_safe
            w.parallel_safe = not has_conflict

        return workstreams
