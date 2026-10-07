#!/usr/bin/env python3
"""
Motor Semântico Composicional de Automação SRE (Antigravity 2.0 / Sentinela v5.0)
Local: /Users/lucasvinicius/projetos/estruturas/semantic_resolver.py
Escopo: Compreensão linguística profunda, decomposição de intenções, ranking determinístico,
        resolução de contexto, preservação de negações, planos em DAG e governança Sentinela.
"""

import json
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

BASE_DIR = Path(__file__).resolve().parent

REGISTRY_PATH = BASE_DIR / "semantic_registry.json"
SETS_PATH = BASE_DIR / "semantic_sets.json"
RULES_PATH = BASE_DIR / "semantic_rules.json"
INDEXES_PATH = BASE_DIR / "semantic_indexes.json"
SECURITY_REF_PATH = BASE_DIR / "security_reference_index.json"
MISSIONS_PATH = BASE_DIR / "semantic_missions.json"

@dataclass
class RouteReceipt:
    INPUT_SOURCE: str
    INTENT_ID: str
    EXECUTION_PROFILE: str
    EXECUTION_SURFACE: str
    PROJECT: str
    TARGET: str
    RISK: str
    POLICY: str
    AGY_USED: bool
    ANTIGRAVITY_USED: bool
    SUBAGENTS_USED: int
    BACKGROUND: bool
    UI_FOCUS: bool
    STEPS: List[str]
    PARALLEL_GROUPS: List[Any]
    SESSION_REUSED: bool
    DURATION_MS: float
    RESULT: str

@dataclass
class ResolvedIntent:
    intent_id: str
    action: str
    object: str
    scope: str
    depth: str
    intensity: str
    target: Optional[str]
    context: Dict[str, Any]
    parameters: Dict[str, Any]
    constraints: Dict[str, Any]
    negations: List[str]
    excluded_actions: List[str]
    output: str
    mode: str
    risk: str
    execution_policy: str
    confidence_score: int
    matched_by: str
    canonical_phrase: str
    command_target: str
    command_template: str
    destructive: bool = False
    sensitive: bool = False
    requires_confirmation: bool = False
    requires_human_gate: bool = False
    is_compound: bool = False
    plan_steps: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    phases: List[Dict[str, Any]] = field(default_factory=list)
    discreet_policy: Dict[str, Any] = field(default_factory=dict)
    resolution_time_ms: float = 0.0
    execution_surface: str = "AUTO"
    resolved_surface: str = "AGY_BACKGROUND"
    execution_profile: str = "STANDARD"
    surface_scores: Dict[str, int] = field(default_factory=dict)
    surface_reasons: Dict[str, List[str]] = field(default_factory=dict)
    execution_plan: Dict[str, Any] = field(default_factory=dict)
    route_receipt: Dict[str, Any] = field(default_factory=dict)
    is_mission: bool = False
    mission_id: Optional[str] = None
    mission_phases: List[Dict[str, Any]] = field(default_factory=list)
    parallel_groups: List[Any] = field(default_factory=list)
    completion_conditions: List[str] = field(default_factory=list)
    modifiers_applied: List[str] = field(default_factory=list)
    mission_pipeline: List[str] = field(default_factory=list)
    sub_missions: List[Any] = field(default_factory=list)
    total_layers: List[str] = field(default_factory=list)
    global_domains: List[Dict[str, Any]] = field(default_factory=list)

    def generate_route_receipt(self) -> Dict[str, Any]:
        return self.route_receipt

    def route_receipt_formatted(self) -> str:
        lines = []
        for k, v in self.route_receipt.items():
            lines.append(f"{k}={v}")
        return "\n".join(lines)

    def to_github_issue(self, raw_query: str = "", repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Converte a intenção resolvida em uma especificação estruturada de GitHub Issue.
        Gera título, corpo em Markdown, labels e comando determinístico 'gh issue create'.
        """
        title = f"[TASK/{self.action}]: {self.intent_id} ({self.object})"
        if self.intent_id == "project-save-sync":
            title = "[SRE/GOVERNANCE]: Salvar e Sincronizar Projeto com GitHub"
        elif "audit" in self.intent_id:
            title = f"[AUDIT/SRE]: Inspeção Forense {self.scope} ({self.depth})"
        elif "unlock" in self.intent_id:
            title = f"[SRE/OPS]: Destravamento Operacional {self.object}"

        plan_block = self.command_template
        if self.is_compound and self.plan_steps:
            plan_block = " && ".join([f"agy_cmd {step}" for step in self.plan_steps])

        body_parts = [
            "## 🎯 Objetivo da Tarefa",
            f"Executar a operação técnica `{self.action}` sobre `{self.object}` no escopo `{self.scope}`.",
            "",
            "## 🧭 Rastreabilidade & Contexto Semântico",
            f"- **Intenção Original:** \"{raw_query or self.canonical_phrase}\"",
            f"- **Intent ID:** `{self.intent_id}`",
            f"- **Superfície:** `{self.resolved_surface}` (`{self.execution_profile}`)",
            f"- **Confiança do Roteamento:** `{self.confidence_score}%` via `{self.matched_by}`",
            "- **Workspace Canônico:** `/Users/lucasvinicius/projetos/`",
            "",
            "## ⚡ Plano de Execução Canônico (Idempotente)",
            "```bash",
            plan_block,
            "```",
            "",
            "## 🛡️ Governança & Restrições (Sentinela Guardião)",
            "- **Zero-Token Guard:** Ativo (execução local sem consumo de tokens de API externa).",
            "- **Scope Lock:** Minimal Necessary Diff (proibida refatoração oportunista).",
            f"- **Política de Execução:** `{self.execution_policy}`",
            f"- **Mutação Autorizada:** `{'Sim' if self.constraints.get('mutation_allowed', True) and not self.constraints.get('read_only', False) else 'Não (Read-Only)'}`",
            f"- **Requer Confirmação/Gate:** `{'Sim' if self.requires_human_gate or self.destructive else 'Não'}`",
            "",
            "## 📋 Critérios de Aceitação (DoD)",
            "- [ ] Execução determinística dos comandos canônicos com código de saída 0.",
            "- [ ] Verificação de integridade pós-execução (baseline preservada, sem regressões).",
            "- [ ] Sincronização verificável do estado sem vazamento de segredos."
        ]
        body = "\n".join(body_parts)

        labels = ["ops", "sentinela", self.action.lower(), self.scope.lower().replace("_", "-")]
        if self.destructive:
            labels.append("high-risk")

        escaped_title = title.replace('"', '\\"')
        escaped_body = body.replace('"', '\\"')
        gh_cmd = f'gh issue create --title "{escaped_title}" --body "{escaped_body}"'
        if repo:
            gh_cmd += f' --repo "{repo}"'

        return {
            "title": title,
            "body": body,
            "labels": labels,
            "command": gh_cmd
        }

    def to_llm_prompt(self, raw_query: str = "") -> str:
        """
        Gera um prompt de engenharia de software ultra-estruturado e desprovido de termos
        ambíguos ou gatilhos de moderação para LLMs externas ou locais (ChatGPT, Claude, Ollama).
        """
        plan_block = self.command_template
        if self.is_compound and self.plan_steps:
            plan_block = " && ".join([f"agy_cmd {step}" for step in self.plan_steps])

        prompt_parts = [
            "### ROLE & SYSTEM DIRECTIVE",
            "Atue como Engenheiro de Confiabilidade de Sistemas (SRE) e Guardião de Projetos.",
            "Sua responsabilidade é executar a tarefa técnica abaixo com precisão cirúrgica, segurança e determinismo.",
            "",
            "### TASK SPECIFICATION",
            f"- **Objetivo:** Execução da operação técnica `{self.action}` em `{self.object}`.",
            f"- **Solicitação Original:** \"{raw_query or self.canonical_phrase}\"",
            f"- **Identificador Canônico:** `{self.intent_id}`",
            f"- **Perfil de Execução:** `{self.resolved_surface}` / `{self.execution_profile}`",
            "- **Diretório de Trabalho (Cwd):** `/Users/lucasvinicius/projetos/`",
            "",
            "### DETERMINISTIC COMMAND (SHELL / AGY_CMD)",
            "Execute exatamente o comando no terminal:",
            "```bash",
            plan_block,
            "```",
            "",
            "### OPERATIONAL CONSTRAINTS (INVARIANTS)",
            "1. **Zero-Token Guard:** Execução estritamente em ambiente local, sem consumo de APIs pagas por token.",
            "2. **Minimal Necessary Diff:** Modifique estritamente os arquivos necessários para cumprir o escopo.",
            "3. **Zero Refatoração Oportunista:** Não altere arquivos ou lógicas fora da tarefa autorizada.",
            "4. **Validação Obrigatória:** Execute testes antes de declarar a tarefa como concluída.",
            "5. **Segurança de Credenciais:** Proibido comitar chaves, senhas, tokens ou arquivos `.env`.",
            "",
            "### EXPECTED OUTPUT & RECEIPT",
            "Retorne um recibo conciso de conclusão no formato:",
            "- STATUS: [IMPLEMENTADO / VALIDADO / SINCRONIZADO / DONE]",
            f"- COMANDO_EXECUTADO: `{plan_block}`",
            "- EVIDÊNCIAS: [Resultados dos testes ou diff verificado]",
            "- PENDÊNCIAS: [Nenhuma ou bloqueios identificados]"
        ]
        return "\n".join(prompt_parts)


class SurfaceRouter:
    """
    Surface Router Canônico SRE (v5.1).
    Roteia planos de execução determinísticos para AGY_BACKGROUND,
    tarefas de raciocínio e código para ANTIGRAVITY_VISUAL,
    e pipelines compostos multi-etapa para HYBRID.
    """
    @classmethod
    def calculate_scores(cls, intent: ResolvedIntent, raw_query: str = "") -> Tuple[Dict[str, int], Dict[str, List[str]]]:
        query_lower = raw_query.lower()
        scores = {"AGY_BACKGROUND": 0, "ANTIGRAVITY_VISUAL": 0, "HYBRID": 0}
        reasons = {"AGY_BACKGROUND": [], "ANTIGRAVITY_VISUAL": [], "HYBRID": []}

        # 1. AGY_SCORE
        # +40 deterministic
        if intent.command_target in ["agy_cmd", "shell", "sqlite3"] and intent.action not in ["REPAIR", "REFACTOR"]:
            scores["AGY_BACKGROUND"] += 40
            reasons["AGY_BACKGROUND"].append("+40 deterministic")
        # +30 shell_adapter
        if intent.command_target == "agy_cmd" or "agy_cmd" in intent.command_template or "sqlite3" in intent.command_template:
            scores["AGY_BACKGROUND"] += 30
            reasons["AGY_BACKGROUND"].append("+30 shell_adapter")
        # +20 read_only
        if intent.constraints.get("read_only", False) or intent.action in ["AUDIT", "RECON", "MAP", "STATUS", "CHECK", "LIST"]:
            scores["AGY_BACKGROUND"] += 20
            reasons["AGY_BACKGROUND"].append("+20 read_only")
        # +20 short_duration
        if not (intent.depth in ["HARD", "FORENSIC"] or intent.is_compound):
            scores["AGY_BACKGROUND"] += 20
            reasons["AGY_BACKGROUND"].append("+20 short_duration")
        # +20 background_capable
        if intent.discreet_policy.get("EXECUTION_VISIBILITY") == "BACKGROUND" or intent.mode == "discreet_background":
            scores["AGY_BACKGROUND"] += 20
            reasons["AGY_BACKGROUND"].append("+20 background_capable")

        # 2. ANTIGRAVITY_SCORE
        # +40 code_change
        if intent.action in ["REPAIR", "FIX", "REFACTOR", "IMPLEMENT"] or any(w in query_lower for w in ["corrija", "conserta", "refatore", "backend", "codigo", "código", "autenticação", "autenticacao"]):
            scores["ANTIGRAVITY_VISUAL"] += 40
            reasons["ANTIGRAVITY_VISUAL"].append("+40 code_change")
        # +30 multi_file
        if any(w in query_lower for w in ["projeto", "arquitetura", "backend", "auth", "autenticacao", "tudo"]) and intent.action in ["REPAIR", "REFACTOR"]:
            scores["ANTIGRAVITY_VISUAL"] += 30
            reasons["ANTIGRAVITY_VISUAL"].append("+30 multi_file")
        # +30 reasoning_required
        if intent.action in ["REPAIR", "REFACTOR", "ARCHITECT", "DEBUG"]:
            scores["ANTIGRAVITY_VISUAL"] += 30
            reasons["ANTIGRAVITY_VISUAL"].append("+30 reasoning_required")
        # +20 visual_review
        if intent.requires_confirmation or intent.action in ["REPAIR", "REFACTOR"]:
            scores["ANTIGRAVITY_VISUAL"] += 20
            reasons["ANTIGRAVITY_VISUAL"].append("+20 visual_review")
        # +20 long_context
        if intent.action in ["REPAIR", "REFACTOR"]:
            scores["ANTIGRAVITY_VISUAL"] += 20
            reasons["ANTIGRAVITY_VISUAL"].append("+20 long_context")

        # 3. HYBRID_SCORE
        # +50 multi_stage
        if intent.is_compound or bool(intent.execution_plan.get("steps")) or intent.intent_id in ["audit.project.hard", "recon.project.hard", "map.project.general"]:
            scores["HYBRID"] += 50
            reasons["HYBRID"].append("+50 multi_stage")
        # +30 audit_then_repair
        has_audit = ("audit" in intent.intent_id or intent.action in ["AUDIT", "RECON"] or any("audit" in s or "recon" in s for s in intent.plan_steps))
        has_repair = any(x in query_lower or x in s for x in ["corrija", "repair", "conserta", "refatore", "valide", "valida"] for s in intent.plan_steps + [query_lower])
        if has_audit and has_repair:
            scores["HYBRID"] += 30
            reasons["HYBRID"].append("+30 audit_then_repair")
        # +30 parallelizable
        if bool(intent.execution_plan.get("parallel_groups")) or (intent.is_compound and len(intent.plan_steps) > 1):
            scores["HYBRID"] += 30
            reasons["HYBRID"].append("+30 parallelizable")
        # +20 validation_required
        if (intent.is_compound and any(x in query_lower for x in ["valide", "validação", "teste", "corrija"])) or ("audit" in intent.intent_id and any(x in query_lower for x in ["corrija", "repare", "valide"])):
            scores["HYBRID"] += 20
            reasons["HYBRID"].append("+20 validation_required")

        # 4. MISSION_SCORE
        if getattr(intent, "is_mission", False):
            default_surf = intent.execution_plan.get("default_surface") or getattr(intent, "execution_surface", "AUTO")
            if default_surf == "HYBRID":
                scores["HYBRID"] += 60
                reasons["HYBRID"].append("+60 mission_default_hybrid")
            elif default_surf == "ANTIGRAVITY_VISUAL":
                scores["ANTIGRAVITY_VISUAL"] += 60
                reasons["ANTIGRAVITY_VISUAL"].append("+60 mission_default_visual")
            elif default_surf == "AGY_BACKGROUND":
                scores["AGY_BACKGROUND"] += 60
                reasons["AGY_BACKGROUND"].append("+60 mission_default_background")

        # Modifiers impact
        if "EXECUTION.DISCREET" in getattr(intent, "modifiers_applied", []):
            scores["AGY_BACKGROUND"] += 40
            reasons["AGY_BACKGROUND"].append("+40 modifier_discreet")

        return scores, reasons

    @classmethod
    def route(cls, intent: ResolvedIntent, raw_query: str = "", context: Optional[Dict[str, Any]] = None,
              requested_surface: str = "AUTO", input_source: str = "CHATGPT") -> Tuple[str, str, Dict[str, int], Dict[str, List[str]], Dict[str, Any]]:
        scores, reasons = cls.calculate_scores(intent, raw_query)

        if requested_surface in ["AGY_BACKGROUND", "ANTIGRAVITY_VISUAL", "HYBRID"]:
            winning_surface = requested_surface
        else:
            h_score = scores["HYBRID"]
            a_score = scores["ANTIGRAVITY_VISUAL"]
            b_score = scores["AGY_BACKGROUND"]

            if h_score > a_score and h_score > b_score:
                winning_surface = "HYBRID"
            elif a_score > b_score and a_score >= h_score:
                winning_surface = "ANTIGRAVITY_VISUAL"
            elif b_score >= a_score and b_score >= h_score:
                winning_surface = "AGY_BACKGROUND"
            else:
                winning_surface = "HYBRID" if h_score >= a_score else "ANTIGRAVITY_VISUAL"

        query_lower = raw_query.lower()
        if "EXECUTION.ADVANCED" in getattr(intent, "modifiers_applied", []):
            profile = "DEEP"
        elif (intent.intent_id in ["audit.project.hard", "recon.project.hard", "map.project.general"] or 
            (getattr(intent, "is_mission", False) and intent.depth in ["HARD", "FORENSIC"]) or
            "audite e corrija" in query_lower or intent.depth in ["HARD", "FORENSIC"] or 
            intent.execution_policy in ["HUMAN_GATE", "DENIED_BY_POLICY"]):
            profile = "DEEP"
        elif intent.is_compound or len(intent.plan_steps) > 2 or bool(intent.execution_plan.get("parallel_groups")):
            profile = "PARALLEL"
        elif winning_surface == "AGY_BACKGROUND" and not intent.destructive and intent.confidence_score >= 800:
            profile = "FAST"
        else:
            profile = "STANDARD"

        project_name = "THIS_PROJECT"
        if context and isinstance(context, dict):
            project_name = context.get("project") or context.get("active_project") or "THIS_PROJECT"
        elif intent.target:
            project_name = intent.target

        steps_list = []
        if getattr(intent, "mission_pipeline", None) and len(intent.mission_pipeline) > 1:
            steps_list = intent.mission_pipeline
        elif intent.is_compound and intent.plan_steps:
            steps_list = intent.plan_steps
        elif intent.execution_plan and intent.execution_plan.get("steps"):
            steps_list = [s["id"] if isinstance(s, dict) else str(s) for s in intent.execution_plan.get("steps")]
        else:
            steps_list = [intent.intent_id]

        parallel_grps = intent.execution_plan.get("parallel_groups", []) if intent.execution_plan else []
        subagents = 0
        if parallel_grps:
            subagents = sum(len(g) for g in parallel_grps)
        elif getattr(intent, "mission_pipeline", None) and len(intent.mission_pipeline) > 1:
            subagents = len(intent.mission_pipeline)
        elif intent.is_compound:
            subagents = len(intent.plan_steps)

        is_discreet = (
            "EXECUTION.DISCREET" in getattr(intent, "modifiers_applied", []) or
            intent.discreet_policy.get("EXECUTION_VISIBILITY") == "BACKGROUND" or
            intent.mode == "discreet_background"
        )
        bg_used = (winning_surface in ["AGY_BACKGROUND", "HYBRID"] or is_discreet)
        ui_focus_used = (winning_surface == "ANTIGRAVITY_VISUAL" and not is_discreet)

        receipt = RouteReceipt(
            INPUT_SOURCE=input_source,
            INTENT_ID=intent.intent_id,
            EXECUTION_PROFILE=profile,
            EXECUTION_SURFACE=winning_surface,
            PROJECT=project_name,
            TARGET=intent.target or intent.object,
            RISK=intent.risk.upper(),
            POLICY=intent.execution_policy,
            AGY_USED=(winning_surface in ["AGY_BACKGROUND", "HYBRID"]),
            ANTIGRAVITY_USED=(winning_surface in ["ANTIGRAVITY_VISUAL", "HYBRID"]),
            SUBAGENTS_USED=subagents,
            BACKGROUND=bg_used,
            UI_FOCUS=ui_focus_used,
            STEPS=steps_list,
            PARALLEL_GROUPS=parallel_grps,
            SESSION_REUSED=True,
            DURATION_MS=intent.resolution_time_ms,
            RESULT="ROUTED"
        )

        return winning_surface, profile, scores, reasons, asdict(receipt)

MISSION_CANONICAL_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "AUDIT.HARD": {
        "intent_id": "audit.project.hard",
        "action": "AUDIT",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "VISIT.GENERAL": {
        "intent_id": "recon.project.hard",
        "action": "VISIT",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "REPORT.GENERAL": {
        "intent_id": "report.problems",
        "action": "REPORT",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "FIND.SMART": {
        "intent_id": "report.problems",
        "action": "FIND",
        "default_depth": "DEEP",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "EXECUTION.DISCREET": {
        "intent_id": "execution.discreet.background",
        "action": "CONFIGURE",
        "default_depth": "NORMAL",
        "default_surface": "AGY_BACKGROUND",
        "default_profile": "FAST",
        "read_only": True,
        "mutation_allowed": False
    },
    "EXECUTION.ADVANCED": {
        "intent_id": "mode-advanced",
        "action": "CONFIGURE",
        "default_depth": "HARD",
        "default_surface": "AGY_BACKGROUND",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "CONNECT.SMART": {
        "intent_id": "conectar",
        "action": "CONNECT",
        "default_depth": "NORMAL",
        "default_surface": "AGY_BACKGROUND",
        "default_profile": "FAST",
        "read_only": True,
        "mutation_allowed": False
    },
    "ACTIVATE.SMART": {
        "intent_id": "conectar",
        "action": "ACTIVATE",
        "default_depth": "NORMAL",
        "default_surface": "AGY_BACKGROUND",
        "default_profile": "FAST",
        "read_only": False,
        "mutation_allowed": True
    },
    "ORGANIZE.SYSTEM": {
        "intent_id": "deep-clean",
        "action": "ORGANIZE",
        "default_depth": "NORMAL",
        "default_surface": "HYBRID",
        "default_profile": "STANDARD",
        "read_only": False,
        "mutation_allowed": True
    },
    "MAKE_IT_WORK": {
        "intent_id": "repair-project",
        "action": "REPAIR",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": False,
        "mutation_allowed": True
    },
    "RECON.HARD": {
        "intent_id": "recon.project.hard",
        "action": "RECON",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "MAP.GENERAL": {
        "intent_id": "map.project.general",
        "action": "MAP",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "REPAIR.SMART": {
        "intent_id": "repair-project",
        "action": "REPAIR",
        "default_depth": "HARD",
        "default_surface": "ANTIGRAVITY_VISUAL",
        "default_profile": "DEEP",
        "read_only": False,
        "mutation_allowed": True
    },
    "OPTIMIZE.SMART": {
        "intent_id": "bench-endpoint",
        "action": "OPTIMIZE",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": False,
        "mutation_allowed": True
    },
    "VALIDATE.COMPLETE": {
        "intent_id": "test-project",
        "action": "TEST",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "SYNC.SMART": {
        "intent_id": "config-sync",
        "action": "SYNC",
        "default_depth": "NORMAL",
        "default_surface": "AGY_BACKGROUND",
        "default_profile": "STANDARD",
        "read_only": False,
        "mutation_allowed": True
    },
    "INTEGRATE.SMART": {
        "intent_id": "conectar",
        "action": "INTEGRATE",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": False,
        "mutation_allowed": True
    },
    "PREPARE.SMART": {
        "intent_id": "test-project",
        "action": "PREPARE",
        "default_depth": "NORMAL",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": False,
        "mutation_allowed": True
    },
    "REVIEW.DEEP": {
        "intent_id": "audit.project.hard",
        "action": "AUDIT",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": True,
        "mutation_allowed": False
    },
    "STABILIZE.SYSTEM": {
        "intent_id": "repair-project",
        "action": "STABILIZE",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": False,
        "mutation_allowed": True
    },
    "COMPLETE.WORK": {
        "intent_id": "test-project",
        "action": "COMPLETE",
        "default_depth": "HARD",
        "default_surface": "HYBRID",
        "default_profile": "DEEP",
        "read_only": False,
        "mutation_allowed": True
    }
}

class MissionResolver:
    """
    Resolvedor Canônico de Missões e Modificadores SRE (Antigravity v5.2).
    Orquestra DAGs completas, dependências, subagentes e roteamento de superfície:
    PHRASE -> MODIFIERS -> MISSIONS / INTENTS -> CONTEXT -> DAG -> SURFACE ROUTER -> RESULT
    """
    def __init__(self, resolver: "SemanticResolver"):
        self.resolver = resolver
        self.missions = resolver.missions
        self.modifiers = resolver.modifiers
        self.composition_rules = resolver.composition_rules
        self.context_rules = resolver.context_rules
        self._build_alias_maps()

    def _build_alias_maps(self):
        self.mission_alias_map: Dict[str, str] = {}
        for mid, m in self.missions.items():
            for al in m.get("aliases", []):
                norm = self.resolver.normalize(al)
                unacc = self.resolver.strip_accents(norm)
                self.mission_alias_map[norm] = mid
                self.mission_alias_map[unacc] = mid

        self.modifier_alias_map: Dict[str, str] = {}
        for modid, mod in self.modifiers.items():
            for al in mod.get("aliases", []):
                norm = self.resolver.normalize(al)
                unacc = self.resolver.strip_accents(norm)
                self.modifier_alias_map[norm] = modid
                self.modifier_alias_map[unacc] = modid

    def extract_modifiers(self, text: str) -> Tuple[str, List[str], Dict[str, Any]]:
        norm = self.resolver.normalize(text)
        unacc = self.resolver.strip_accents(norm)

        # Se a frase inteira for estritamente um modifier alias, trata como comando isolado
        if norm in self.modifier_alias_map or unacc in self.modifier_alias_map:
            return text, [], {}

        extracted_mods: List[str] = []
        mod_settings: Dict[str, Any] = {}
        remainder = norm

        # Ordem decrescente de tamanho para capturar compostos mais específicos primeiro
        sorted_aliases = sorted(self.modifier_alias_map.keys(), key=len, reverse=True)
        for alias in sorted_aliases:
            mod_id = self.modifier_alias_map[alias]
            pattern = r"^(?:" + re.escape(alias) + r")\s*(?:,\s*|\s+e\s+|\s+depois\s+|\s+)(.+)$"
            match = re.match(pattern, remainder)
            if match:
                if mod_id not in extracted_mods:
                    extracted_mods.append(mod_id)
                mod_data = self.modifiers.get(mod_id, {})
                mod_settings.update(mod_data.get("settings", {}))
                remainder = match.group(1).strip()

        # Variante 'ativa/ative modo avançado ...'
        match_act = re.match(r"^(?:ativ(?:a|e)\s+modo\s+avançado|ativ(?:a|e)\s+avançado)\s*(?:,\s*|\s+e\s+|\s+depois\s+|\s+)(.+)$", remainder)
        if match_act:
            if "EXECUTION.ADVANCED" not in extracted_mods:
                extracted_mods.append("EXECUTION.ADVANCED")
            remainder = match_act.group(1).strip()

        return remainder, extracted_mods, mod_settings

    def resolve_candidate(self, phrase: str, context: Any) -> Optional[Tuple[str, Dict[str, Any], Dict[str, Any]]]:
        norm = self.resolver.normalize(phrase)
        unacc = self.resolver.strip_accents(norm)

        core = norm
        core = re.sub(r"\s+mas\s+(?:não|nao|só|so|apenas)\b.*$", "", core).strip()
        core = re.sub(r"\s+sem\s+.*$", "", core).strip()
        core = re.sub(r"\s+(?:nesse|no)\s+projeto$", "", core).strip()
        core_unacc = self.resolver.strip_accents(core)

        matched_id = self.mission_alias_map.get(core) or self.mission_alias_map.get(core_unacc) or \
                     self.mission_alias_map.get(norm) or self.mission_alias_map.get(unacc)

        extra_attrs: Dict[str, Any] = {}

        # 1. Especialização FIND.SMART
        if (matched_id == "FIND.SMART" or (matched_id is None and re.search(r"\b(?:encontre|acha|ache|procura|descubra|localiza)\b", norm))):
            if re.search(r"\berro(?:s)?\b", norm):
                matched_id = "FIND.ROOT_CAUSE_CANDIDATES"
                extra_attrs["target"] = "error"
                extra_attrs["parent_mission"] = "FIND.SMART"
            elif re.search(r"\barquivo(?:s)?\b", norm):
                matched_id = "FIND.FILE"
                extra_attrs["target"] = "file"
                extra_attrs["parent_mission"] = "FIND.SMART"
            elif re.search(r"\b(?:fun[cç][aã]o|funcoes|c[oó]digo|codigo)\b", norm):
                matched_id = "FIND.CODE_ORIGIN"
                extra_attrs["target"] = "code_origin"
                extra_attrs["parent_mission"] = "FIND.SMART"
            elif re.search(r"\bproblema(?:s)?\b", norm):
                matched_id = "FIND.PROBLEM"
                extra_attrs["target"] = "problem"
                extra_attrs["parent_mission"] = "FIND.SMART"
            elif re.search(r"\brelacionad[oa]s?\b", norm):
                matched_id = "FIND.RELATED_RESOURCES"
                extra_attrs["target"] = "related_resources"
                extra_attrs["parent_mission"] = "FIND.SMART"
            elif not matched_id:
                matched_id = "FIND.SMART"

        # 2. Especialização ACTIVATE.SMART
        if matched_id == "ACTIVATE.SMART" or (matched_id is None and re.match(r"^(?:ativ(?:e|a))\b", norm)):
            if "modo avançado" in norm or "avancado" in norm:
                matched_id = "EXECUTION.ADVANCED"
            elif re.search(r"\bprojeto\b", norm):
                matched_id = "ACTIVATE.PROJECT_CONTEXT"
                extra_attrs["target"] = "project"
            elif re.search(r"\bbot\b", norm):
                matched_id = "ACTIVATE.SERVICE"
                extra_attrs["target"] = "bot"
            elif context and (context == "DISPATCHER" or (isinstance(context, dict) and context.get("service") == "dispatcher")):
                matched_id = "ACTIVATE.SERVICE"
                extra_attrs["target"] = "dispatcher"
            elif not matched_id:
                matched_id = "ACTIVATE.SMART"

        # 3. Especialização CONNECT.SMART
        if matched_id == "CONNECT.SMART" or (matched_id is None and norm in ["se conecte", "conecta", "conecte", "entra la", "entra lá", "abre conexao", "abre conexão"]):
            ctx_str = str(context).lower() if context else ""
            if "github" in norm or "github" in ctx_str:
                matched_id = "CONNECT.GITHUB"
                extra_attrs["target"] = "github"
            elif "vps" in norm or "vps" in ctx_str:
                matched_id = "CONNECT.VPS"
                extra_attrs["target"] = "vps"
            elif any(d in norm or d in ctx_str for d in ["database", "banco", "sqlite"]):
                matched_id = "CONNECT.DATABASE"
                extra_attrs["target"] = "database"
            elif not matched_id:
                matched_id = "CONNECT.SMART"

        # 4. Especialização PREPARE.SMART
        if matched_id == "PREPARE.SMART" or (matched_id is None and any(norm.startswith(p) for p in ["prepare", "prepara", "deixa pronto"])):
            if re.search(r"\bprodu[cç][aã]o\b", norm):
                matched_id = "PREPARE.PRODUCTION"
                extra_attrs["target"] = "production"
            elif re.search(r"\bdev\b", norm):
                matched_id = "PREPARE.DEV"
                extra_attrs["target"] = "development"
            elif re.search(r"\btest(?:e)?s?\b", norm):
                matched_id = "PREPARE.TEST"
                extra_attrs["target"] = "testing"
            elif re.search(r"\bdeploy\b", norm):
                matched_id = "PREPARE.DEPLOY"
                extra_attrs["target"] = "deploy"
            elif not matched_id:
                matched_id = "PREPARE.SMART"

        # 5. VISIT.GENERAL com reparo
        if matched_id == "VISIT.GENERAL" or re.search(r"\b(?:visita|visitar)\b", norm):
            matched_id = "VISIT.GENERAL"
            if re.search(r"\b(?:arrumar|arruma|consertar|conserta|corrigir|corrige)\b", norm):
                extra_attrs["extra_phases"] = [
                    {"phase_id": "DIAGNOSE", "name": "DIAGNOSE", "objective": "Diagnosticar causas raízes"},
                    {"phase_id": "REPAIR", "name": "REPAIR", "objective": "Executar correções cirúrgicas"},
                    {"phase_id": "TEST", "name": "TEST", "objective": "Executar testes focados"},
                    {"phase_id": "VALIDATE", "name": "VALIDATE", "objective": "Validar ausência de regressões"}
                ]

        if not matched_id:
            return None

        parent_id = extra_attrs.get("parent_mission") or matched_id.split(".")[0]
        mission_data = self.missions.get(matched_id)
        if not mission_data:
            for k, v in self.missions.items():
                if k.startswith(parent_id) or k == parent_id:
                    mission_data = v
                    break

        if not mission_data:
            return None

        return matched_id, mission_data, extra_attrs

    def resolve(self, utterance: str, context: Any, modifiers: List[str],
                neg_tokens: List[str], excluded_actions: List[str], constraints: Dict[str, Any],
                params: Dict[str, Any], inferred_object: str, resolved_scope: str,
                execution_surface: str, input_source: str, raw_query: str) -> Optional[ResolvedIntent]:
        norm = self.resolver.normalize(utterance)

        # 0. Caso Especial Canônico: "visita e arrumar" (VISIT.GENERAL com fases estendidas de reparo)
        if re.search(r"\b(?:visita|visitar)\b", norm) and re.search(r"\b(?:arrumar|arruma|consertar|conserta|corrigir|corrige)\b", norm):
            cand = self.resolve_candidate(utterance, context)
            if cand:
                return self.build_single_mission(
                    cand, utterance, context, modifiers,
                    neg_tokens, excluded_actions, constraints, params,
                    inferred_object, resolved_scope, execution_surface,
                    input_source, raw_query
                )

        # 1. Verificar se há conectivos compostos na utterance
        connectors = r"\s+(?:e\s+depois|em\s+seguida|logo\s+após|depois|e)\s+|,\s*"
        raw_parts = re.split(connectors, utterance)
        clean_parts = []
        for p in raw_parts:
            p_clean = p.strip()
            for prefix in ["depois ", "em seguida ", "logo após ", "e "]:
                if p_clean.startswith(prefix):
                    p_clean = p_clean[len(prefix):].strip()
            if len(p_clean) >= 2 and not re.match(r"^(?:mas\s+não|mas\s+nao|sem\s+|não\s+|nao\s+)", p_clean):
                clean_parts.append(p_clean)

        # Se houver mais de uma parte, tenta resolver como pipeline composto
        if len(clean_parts) > 1:
            part_candidates = []
            for part in clean_parts:
                cand = self.resolve_candidate(part, context)
                if cand:
                    part_candidates.append(cand)
                else:
                    # Tentar resolver via resolver padrão (ex: "corrija" ou "teste")
                    sub_res = self.resolver.resolve(part, context=context)
                    if sub_res:
                        part_candidates.append(sub_res)

            if len(part_candidates) == len(clean_parts) and len(part_candidates) > 1:
                return self.build_compound_mission(
                    part_candidates, utterance, context, modifiers,
                    neg_tokens, excluded_actions, constraints, params,
                    inferred_object, resolved_scope, execution_surface,
                    input_source, raw_query
                )

        # 2. Resolução de Missão Única
        single_cand = self.resolve_candidate(utterance, context)
        if single_cand:
            return self.build_single_mission(
                single_cand, utterance, context, modifiers,
                neg_tokens, excluded_actions, constraints, params,
                inferred_object, resolved_scope, execution_surface,
                input_source, raw_query
            )

        return None

    def build_single_mission(self, cand: Tuple[str, Dict[str, Any], Dict[str, Any]],
                             utterance: str, context: Any, modifiers: List[str],
                             neg_tokens: List[str], excluded_actions: List[str],
                             constraints: Dict[str, Any], params: Dict[str, Any],
                             inferred_object: str, resolved_scope: str,
                             execution_surface: str, input_source: str,
                             raw_query: str) -> ResolvedIntent:
        mid, m_data, extra_attrs = cand

        defaults = MISSION_CANONICAL_DEFAULTS.get(mid)
        if not defaults:
            parent_id = extra_attrs.get("parent_mission") or mid.split(".")[0]
            for k, v in MISSION_CANONICAL_DEFAULTS.items():
                if k == parent_id or k.startswith(parent_id):
                    defaults = v
                    break
        if not defaults:
            defaults = {
                "intent_id": "audit.project.hard",
                "action": "EXECUTE",
                "default_depth": "NORMAL",
                "default_surface": "HYBRID",
                "default_profile": "DEEP",
                "read_only": False,
                "mutation_allowed": True
            }

        canon_id = defaults.get("intent_id", "audit.project.hard")

        # Context-sensitive macro re-routing
        if canon_id == "audit.project.hard":
            if resolved_scope == "HOST":
                canon_id = "audit.host.hard"
            elif resolved_scope == "DATABASE":
                canon_id = "audit.database.hard"
            elif resolved_scope == "NETWORK":
                canon_id = "audit.network.hard"
        elif canon_id == "recon.project.hard":
            if resolved_scope == "HOST":
                canon_id = "recon.host.hard"
            elif resolved_scope == "NETWORK":
                canon_id = "recon.network.hard"
        elif canon_id == "map.project.general":
            if resolved_scope == "HOST":
                canon_id = "map.host.general"
            elif resolved_scope == "NETWORK":
                canon_id = "map.network.hard"

        it = self.resolver.registry.get(canon_id, {})
        action = defaults.get("action", m_data.get("action", it.get("category", "EXECUTE")))
        depth = defaults.get("default_depth", m_data.get("default_depth", "NORMAL"))

        if "EXECUTION.ADVANCED" in modifiers:
            depth = "HARD"
        if "FAST" in modifiers:
            depth = "LIGHT"
        if "DEEP" in modifiers:
            depth = "HARD"

        read_only = defaults.get("read_only", False) or constraints.get("read_only", False) or ("READ_ONLY" in modifiers)
        mutation_allowed = defaults.get("mutation_allowed", True) and constraints.get("mutation_allowed", True) and ("READ_ONLY" not in modifiers)

        constraints["read_only"] = read_only
        constraints["mutation_allowed"] = mutation_allowed

        if read_only:
            exec_policy = "READ_ONLY_FIRST"
        elif not mutation_allowed:
            exec_policy = "READ_ONLY_FIRST"
        elif it.get("destructive", False):
            exec_policy = "HUMAN_GATE"
        else:
            exec_policy = it.get("execution_policy", "AUTO_ALLOWED")

        norm_q = (raw_query or "").lower()
        norm_u = (utterance or "").lower()
        is_global_audit = any(g in norm_q or g in norm_u for g in ["auditoria global", "aduitoria global", "audit-global", "auditoria-global", "raio-x global"])
        is_total_audit = any(t in norm_q or t in norm_u for t in ["auditoria total", "aduitoria total", "varredura completa"])
        phases = list(m_data.get("phases", []))
        if is_global_audit and self.resolver.audit_global_phases:
            phases = self.resolver.audit_global_phases
        elif is_total_audit and self.resolver.audit_total_phases:
            phases = self.resolver.audit_total_phases
        elif mid == "AUDIT.HARD" and depth == "HARD":
            phases = self.resolver.audit_phases
        if extra_attrs.get("extra_phases"):
            phases.extend(extra_attrs["extra_phases"])

        exec_plan = dict(it.get("execution_plan", {}))
        if not exec_plan:
            exec_plan = {
                "strategy": "DAG",
                "mission_id": mid,
                "phases": phases,
                "steps": [canon_id],
                "parallel_groups": m_data.get("parallel_groups", []),
                "dependencies": m_data.get("dependencies", {}),
                "completion_conditions": m_data.get("completion_conditions", []),
                "output": m_data.get("canonical_meaning", "")
            }
        default_surf = defaults.get("default_surface", m_data.get("default_surface", "HYBRID"))
        if is_global_audit or is_total_audit:
            default_surf = "AGY_BACKGROUND"
        exec_plan["default_surface"] = default_surf

        is_discreet = ("EXECUTION.DISCREET" in modifiers) or (mid == "EXECUTION.DISCREET") or self.resolver.is_discreet_requested(raw_query) or is_total_audit or is_global_audit

        template = it.get("command_template", f"agy_cmd {canon_id}")
        if "port" in params:
            template = template.replace("$1", str(params["port"])).replace("${1:-3000}", str(params["port"]))
        if "url" in params:
            template = template.replace("$1", params["url"]).replace("${1:-http://localhost:3000}", params["url"])

        res = ResolvedIntent(
            intent_id=canon_id,
            action=action,
            object=inferred_object,
            scope=resolved_scope,
            depth=depth,
            intensity="HIGH" if depth in ["HARD", "FORENSIC"] else ("LOW" if depth == "LIGHT" else "NORMAL"),
            target=extra_attrs.get("target") or params.get("target") or params.get("project") or inferred_object,
            context={"inferred_scope": resolved_scope, "inferred_object": inferred_object},
            parameters=params,
            constraints=constraints,
            negations=neg_tokens,
            excluded_actions=excluded_actions,
            output="forensic_report" if depth in ["HARD", "FORENSIC"] else "structured",
            mode="discreet_background" if is_discreet else ("read_only_first" if read_only else "normal"),
            risk=m_data.get("risk_policy", it.get("risk_class", "low")),
            execution_policy=exec_policy,
            confidence_score=920,
            matched_by="mission_template",
            canonical_phrase=m_data.get("canonical_meaning", mid),
            command_target=it.get("command_target", "agy_cmd"),
            command_template=template,
            destructive=it.get("destructive", False),
            sensitive=it.get("sensitive", False),
            requires_confirmation=it.get("requires_confirmation", False),
            requires_human_gate=it.get("requires_human_gate", False),
            is_compound=False,
            plan_steps=[canon_id],
            dependencies={},
            phases=phases,
            discreet_policy=self.resolver.discreet_policy,
            execution_plan=exec_plan,
            is_mission=True,
            mission_id=mid,
            mission_phases=m_data.get("phases", []),
            parallel_groups=m_data.get("parallel_groups", []),
            completion_conditions=m_data.get("completion_conditions", []),
            modifiers_applied=modifiers,
            mission_pipeline=[mid]
        )

        winning_surface, profile, scores, reasons, receipt = SurfaceRouter.route(
            res, raw_query or utterance, constraints, execution_surface, input_source
        )
        if is_global_audit:
            winning_surface = "AGY_BACKGROUND"
            if receipt:
                receipt["EXECUTION_SURFACE"] = "AGY_BACKGROUND"
                receipt["BACKGROUND"] = True
                receipt["UI_FOCUS"] = False
            res.total_layers = [
                "Camada de Apresentação (Interface de Usuário - UI)",
                "Camada de Lógica de Interação",
                "Camada de Gerenciamento de Estado",
                "Camada de Rede (Cliente de API)",
                "Camada de Segurança Perimetral (WAF - Firewall de Aplicação)",
                "Camada de Redes de Entrega de Conteúdo (CDN)",
                "Camada de Gateway e Roteamento de Borda (DNS e Load Balancers)",
                "Camada de Entrada e Roteamento (Controladores / API)",
                "Camada de Segurança e Autenticação (Middleware)",
                "Camada de Regras de Negócio (Serviços)",
                "Camada de Mensageria e Eventos (Filas Assíncronas)",
                "Camada de Cache Distribuído",
                "Camada de Acesso a Dados (Persistência / ORM)",
                "Camada de Armazenamento Principal (Banco de Dados Relacional/Não-Relacional)",
                "Camada de Réplicas de Leitura e Armazenamento Analítico (Data Warehouse / BI)",
                "Camada de Servidores Web e Proxies Reversos",
                "Camada de Virtualização e Containers",
                "Camada de Orquestração de Containers",
                "Camada de Sistema Operacional do Servidor",
                "Camada de Infraestrutura como Código (IaC)",
                "Camada de Hardware e Provedor de Nuvem (Cloud Computacional)",
                "Camada de Integração e Entrega Contínua (CI/CD)",
                "Camada de Observabilidade, Telemetria e Monitoramento (Logs e Métricas)"
            ]
            res.global_domains = [
                {"dominio": "1. Frontend (Client-Side)", "conceito": "Surface Web (Web Superficial)"},
                {"dominio": "2. Transporte, Borda e Segurança Perimetral", "conceito": "Transporte, Borda & Perímetro"},
                {"dominio": "3. Backend (Server-Side)", "conceito": "Deep Web (Web Profunda / Servidor)"},
                {"dominio": "4. Armazenamento e Análise de Dados", "conceito": "Camadas Avançadas de Dados e Performance"},
                {"dominio": "5. Hospedagem, Virtualização e Infraestrutura (DevOps)", "conceito": "Camadas de Infraestrutura e DevOps (Abaixo do Backend)"},
                {"dominio": "6. Operações Transversais (Cercam todas as outras)", "conceito": "Camadas de Operação e Segurança Transversal"}
            ]
            res.mode = "discreet_background"
        elif is_total_audit:
            winning_surface = "AGY_BACKGROUND"
            if receipt:
                receipt["EXECUTION_SURFACE"] = "AGY_BACKGROUND"
                receipt["BACKGROUND"] = True
                receipt["UI_FOCUS"] = False
            res.total_layers = [
                "Camada de Apresentação (Interface de Usuário - UI)",
                "Camada de Lógica de Interação",
                "Camada de Gerenciamento de Estado",
                "Camada de Rede (Cliente de API)",
                "Camada de Gateway e Roteamento de Borda",
                "Camada de Entrada e Roteamento (Controladores / API)",
                "Camada de Segurança e Autenticação (Middleware)",
                "Camada de Regras de Negócio (Serviços)",
                "Camada de Acesso a Dados (Persistência / ORM)",
                "Camada de Armazenamento (Banco de Dados)"
            ]
            res.mode = "discreet_background"

        res.execution_surface = execution_surface
        res.resolved_surface = winning_surface
        res.execution_profile = profile
        res.surface_scores = scores
        res.surface_reasons = reasons
        res.route_receipt = receipt
        return res

    def build_compound_mission(self, candidates: List[Any],
                               utterance: str, context: Any, modifiers: List[str],
                               neg_tokens: List[str], excluded_actions: List[str],
                               constraints: Dict[str, Any], params: Dict[str, Any],
                               inferred_object: str, resolved_scope: str,
                               execution_surface: str, input_source: str,
                               raw_query: str) -> ResolvedIntent:
        first_cand = candidates[0]
        if isinstance(first_cand, tuple):
            first_res = self.build_single_mission(
                first_cand, utterance, context, modifiers,
                neg_tokens, excluded_actions, constraints, params,
                inferred_object, resolved_scope, execution_surface,
                input_source, raw_query
            )
        else:
            first_res = first_cand

        mission_pipeline = []
        canonical_ids = []
        all_parallel_groups = []
        all_completion_conditions = []
        all_phases = []

        for cand in candidates:
            if isinstance(cand, tuple):
                mid, m_data, _ = cand
                mission_pipeline.append(mid)
                d = MISSION_CANONICAL_DEFAULTS.get(mid)
                if not d:
                    parent = mid.split(".")[0]
                    for k, v in MISSION_CANONICAL_DEFAULTS.items():
                        if k == parent or k.startswith(parent):
                            d = v
                            break
                if not d:
                    d = {}
                cid = d.get("intent_id", "conectar")
                canonical_ids.append(cid)
                all_parallel_groups.extend(m_data.get("parallel_groups", []))
                all_completion_conditions.extend(m_data.get("completion_conditions", []))
                all_phases.extend(m_data.get("phases", []))
            elif isinstance(cand, ResolvedIntent):
                mission_pipeline.append(cand.mission_id or cand.intent_id)
                canonical_ids.append(cand.intent_id)

        deps: Dict[str, List[str]] = {}
        for idx in range(1, len(canonical_ids)):
            deps[f"step_{idx+1}_{canonical_ids[idx]}"] = [f"step_{idx}_{canonical_ids[idx-1]}"]

        first_res.is_compound = True
        first_res.is_mission = True
        first_res.mission_pipeline = mission_pipeline
        first_res.plan_steps = canonical_ids
        first_res.dependencies = deps
        first_res.parallel_groups = all_parallel_groups
        first_res.completion_conditions = all_completion_conditions
        first_res.mission_phases = all_phases
        first_res.modifiers_applied = modifiers

        exec_plan = {
            "strategy": "DAG",
            "missions": mission_pipeline,
            "steps": canonical_ids,
            "dependencies": deps,
            "parallel_groups": all_parallel_groups,
            "completion_conditions": all_completion_conditions,
            "default_surface": "HYBRID"
        }
        first_res.execution_plan = exec_plan

        if "EXECUTION.ADVANCED" in modifiers:
            first_res.depth = "HARD"
            first_res.execution_profile = "DEEP"

        is_discreet = ("EXECUTION.DISCREET" in modifiers) or self.resolver.is_discreet_requested(raw_query)
        if is_discreet:
            first_res.mode = "discreet_background"

        winning_surface, profile, scores, reasons, receipt = SurfaceRouter.route(
            first_res, raw_query or utterance, constraints, execution_surface, input_source
        )
        first_res.execution_surface = execution_surface
        first_res.resolved_surface = winning_surface
        first_res.execution_profile = profile
        first_res.surface_scores = scores
        first_res.surface_reasons = reasons
        first_res.route_receipt = receipt
        return first_res

class SemanticResolver:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SemanticResolver, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.registry = self._load_json(REGISTRY_PATH).get("intents", {})
        self.sets = self._load_json(SETS_PATH)
        self.rules = self._load_json(RULES_PATH)
        self.indexes = self._load_json(INDEXES_PATH)
        self.sec_refs = self._load_json(SECURITY_REF_PATH).get("entries", [])
        self.missions_data = self._load_json(MISSIONS_PATH)
        self.missions = self.missions_data.get("missions", {})
        self.modifiers = self.missions_data.get("modifiers", {})
        self.composition_rules = self.missions_data.get("composition_rules", {})
        self.context_rules = self.missions_data.get("context_rules", {})
        self.discreet_policy = self.rules.get("discreet_execution_policy", {
            "EXECUTION_VISIBILITY": "BACKGROUND",
            "UI_FOCUS": False,
            "OPEN_NEW_WINDOWS": False,
            "OPEN_NEW_TABS": False,
            "HEADLESS_BROWSER": False,
            "VISIBLE_TERMINAL": False,
            "AUDIT_LOGGING": True,
            "SECURITY_LOGGING": True,
            "RESUME_FROM_GATE": True
        })
        self.audit_phases = self.rules.get("audit_hard_phases", [])
        self.audit_total_phases = self.rules.get("audit_total_phases", [])
        self.total_audit_rule = self.rules.get("regra_auditoria_total", {})
        self.audit_global_phases = self.rules.get("audit_global_phases", [])
        self.total_global_rule = self.rules.get("regra_auditoria_global", {})
        self.mission_resolver = MissionResolver(self)
        self._initialized = True

    @staticmethod
    def _load_json(path: Path) -> dict:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        norm = unicodedata.normalize("NFKC", text).strip().lower()
        norm = re.sub(r"[\t\r\n]+", " ", norm)
        norm = re.sub(r"\s+", " ", norm)
        return norm

    def strip_accents(self, text: str) -> str:
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    def extract_parameters(self, text: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}

        # Faixa de portas (ex: 3000 a 3010, 3000-3010)
        port_range_match = re.search(r"\b(?:portas?\s+)?(\d{2,5})\s*(?:a|à|-|to)\s*(\d{2,5})\b", text)
        if port_range_match:
            p_start, p_end = int(port_range_match.group(1)), int(port_range_match.group(2))
            if 1 <= p_start <= 65535 and 1 <= p_end <= 65535:
                params["port_range"] = [p_start, p_end]
                params["port_start"] = p_start
                params["port_end"] = p_end

        # Porta individual (ex: porta 8765, porta 3000)
        if "port_range" not in params:
            port_match = re.search(r"\b(?:portas?\s+)?(\d{2,5})\b", text)
            if port_match:
                port_val = int(port_match.group(1))
                if 1 <= port_val <= 65535:
                    params["port"] = port_val

        # URLs
        url_match = re.search(r"https?://[^\s'\"]+", text)
        if url_match:
            params["url"] = url_match.group(0)

        # Paths
        path_match = re.search(r"(?:/[a-zA-Z0-9_\.\-]+)+", text)
        if path_match:
            params["path"] = path_match.group(0)

        # PIDs
        pid_match = re.search(r"\bpid\s+(\d+)\b", text)
        if pid_match:
            params["pid"] = int(pid_match.group(1))

        # Projetos citados
        proj_match = re.search(r"(?:no\s+projeto|projeto|nesse\s+projeto)\s+([a-zA-Z0-9_\-\s]+)", text)
        if proj_match:
            cand = proj_match.group(1).strip()
            if cand and cand not in ["ativo", "corrente", "atual"]:
                params["project"] = cand

        return params

    def extract_negations_and_constraints(self, text: str) -> Tuple[List[str], List[str], Dict[str, Any]]:
        neg_tokens = []
        excluded_actions = []
        constraints = {
            "read_only": False,
            "mutation_allowed": True
        }

        # Detecção de tokens de negação
        for neg in ["não", "nao", "sem", "somente", "só", "so", "apenas", "exceto", "menos"]:
            if re.search(r"\b" + re.escape(neg) + r"\b", text):
                neg_tokens.append(neg)

        # Regras semânticas de exclusão
        if re.search(r"\b(?:sem|não|nao)\s+(?:alterar|altere|altera|modificar|modifique|modifica|mexer|mexa|mudar|mude|tocar|toque)\b", text) or \
           re.search(r"\bsem\s+tocar\s+nos\s+arquivos\b", text):
            excluded_actions.extend(["REPAIR", "WRITE", "DELETE", "MODIFY", "modify", "repair", "write", "delete"])
            constraints["read_only"] = True
            constraints["mutation_allowed"] = False

        if re.search(r"\b(?:sem|não|nao)\s+(?:corrigir|corrija|reparar|repare|consertar|conserte|resolver|resolva)\b", text):
            excluded_actions.extend(["REPAIR", "WRITE", "repair", "write"])
            constraints["mutation_allowed"] = False

        if re.search(r"\b(?:sem|não|nao)\s+(?:limpar|limpe|limpeza|apagar|apague|faxinar|deletar|delete)\b", text):
            excluded_actions.extend(["CLEAN", "DELETE", "PURGE", "clean", "delete", "purge"])

        if re.search(r"\b(?:sem|não|nao)\s+(?:matar|mate|derrubar|derrube|encerrar|encerre|finalizar|finalize)\s*(?:processos|pids)?\b", text):
            excluded_actions.extend(["KILL", "STOP", "kill", "stop"])

        if re.search(r"\b(?:sem|não|nao)\s+(?:fazer\s+)?backup\b", text):
            excluded_actions.extend(["BACKUP", "backup"])

        if re.search(r"\b(?:só|so|apenas|somente)\s*(?:leitura|audita|olhar|verificar)\b", text) or \
           re.search(r"\bsó\s+leitura\b", text) or re.search(r"\bso\s+leitura\b", text):
            constraints["read_only"] = True
            constraints["mutation_allowed"] = False
            excluded_actions.extend(["REPAIR", "WRITE", "DELETE", "MODIFY", "CLEAN", "clean", "modify", "repair", "write", "delete"])

        return list(set(neg_tokens)), list(set(excluded_actions)), constraints

    def is_discreet_requested(self, text: str) -> bool:
        norm_t = (text or "").lower()
        if "auditoria total" in norm_t or "auditoria global" in norm_t or "invisivel" in norm_t or "invisível" in norm_t or "silenciosa" in norm_t or "silencioso" in norm_t:
            return True
        discreet_triggers = self.sets.get("DISCREET_SETS", {}).get("triggers", [
            "modo silencioso", "roda sem aparecer", "faz em background",
            "não mexe na minha tela", "nao mexe na minha tela",
            "não troca minha janela", "nao troca minha janela",
            "silencioso", "background", "sem foco", "discreto"
        ])
        for dt in discreet_triggers:
            if dt in text:
                return True
        return False

    def resolve_context_scope(self, text: str, context: Optional[Union[Dict[str, Any], str]] = None) -> Tuple[str, str]:
        ctx_dict: Dict[str, Any] = {}
        if isinstance(context, str):
            ctx_dict = {"scope": context.upper()}
        elif isinstance(context, dict):
            ctx_dict = context

        # 1. Alvo explicitamente citado no texto
        if re.search(r"\b(?:projeto|workspace|repo|nesse projeto|no projeto)\b", text):
            return "PROJECT", "PROJECT"
        if re.search(r"\b(?:mac|host|sistema|máquina|maquina)\b", text):
            return "HOST", "HOST"
        if re.search(r"\b(?:rede|portas?|network|interfaces?)\b", text):
            return "NETWORK", "NETWORK"
        if re.search(r"\b(?:banco|database|sqlite|tabelas?)\b", text):
            return "DATABASE", "DATABASE"
        if re.search(r"\b(?:aplicação|aplicacao|app)\b", text):
            return "APPLICATION", "APPLICATION"
        if re.search(r"\b(?:infra|infraestrutura|docker|container)\b", text):
            return "INFRASTRUCTURE", "INFRASTRUCTURE"

        # 2, 3, 4, 5. Contexto passado pelo chamador
        if ctx_dict.get("active_project") or ctx_dict.get("project") or ctx_dict.get("scope") == "PROJECT":
            return "PROJECT", "PROJECT"
        if ctx_dict.get("active_host") or ctx_dict.get("host") or ctx_dict.get("scope") == "HOST":
            return "HOST", "HOST"
        if ctx_dict.get("scope") == "NETWORK":
            return "NETWORK", "NETWORK"
        if ctx_dict.get("scope") == "DATABASE":
            return "DATABASE", "DATABASE"
        if ctx_dict.get("scope") == "APPLICATION":
            return "APPLICATION", "APPLICATION"
        if ctx_dict.get("scope") == "INFRASTRUCTURE":
            return "INFRASTRUCTURE", "INFRASTRUCTURE"

        # Se houver projeto de contexto detectável por ambiente
        if os.environ.get("AGY_ACTIVE_PROJECT"):
            return "PROJECT", "PROJECT"

        # Fallback default no ecossistema Antigravity quando em repo local: PROJECT
        if Path(".git").exists() or (BASE_DIR / ".git").exists() or "estruturas" in str(BASE_DIR):
            return "PROJECT", "PROJECT"

        return "CONTEXT_INFERRED", "NEEDS_SCOPE_RESOLUTION"

    def resolve(self, utterance: str, context: Optional[Union[Dict[str, Any], str]] = None, execution_surface: str = "AUTO", input_source: str = "CHATGPT") -> Optional[ResolvedIntent]:
        t0 = time.perf_counter()
        raw = utterance.strip()
        norm = self.normalize(raw)
        unaccented = self.strip_accents(norm)

        # -------------------------------------------------------------
        # 0. Extração de Modificadores (Modificadores alteram a missão seguinte)
        # -------------------------------------------------------------
        core_utterance, modifiers_applied, mod_settings = self.mission_resolver.extract_modifiers(raw)
        norm_core = self.normalize(core_utterance)

        neg_tokens, excluded_actions, constraints = self.extract_negations_and_constraints(norm)
        params = self.extract_parameters(norm)
        inferred_object, resolved_scope = self.resolve_context_scope(norm, context)
        is_discreet = self.is_discreet_requested(norm) or ("EXECUTION.DISCREET" in modifiers_applied)

        if "READ_ONLY" in modifiers_applied:
            constraints["read_only"] = True
            constraints["mutation_allowed"] = False
            excluded_actions.extend(["REPAIR", "WRITE", "DELETE", "MODIFY"])

        # -------------------------------------------------------------
        # Limpeza de orações restritivas / adjetivas para resolução do núcleo
        # Ex: "audite mas não altere" -> core = "audite"
        # Ex: "mapeie sem encerrar processos" -> core = "mapeie"
        # Ex: "faça um mapa geral mas só leitura" -> core = "faça um mapa geral"
        # -------------------------------------------------------------
        core_phrase = norm_core
        core_phrase = re.sub(r"\s+mas\s+(?:não|nao|só|so|apenas)\b.*$", "", core_phrase).strip()
        core_phrase = re.sub(r"\s+sem\s+.*$", "", core_phrase).strip()
        core_phrase = re.sub(r"\s+(?:nesse|no)\s+projeto$", "", core_phrase).strip()
        core_unaccented = self.strip_accents(core_phrase)

        # -------------------------------------------------------------
        # 1. Score 1000: Atalho Numérico Exato
        # -------------------------------------------------------------
        num_index = self.indexes.get("numeric_index", {})
        if core_phrase in num_index:
            it_id = num_index[core_phrase]
            it = self.registry.get(it_id)
            if it:
                res = self._build_resolved(it, 1000, "exact_numeric_shortcut", core_phrase,
                                            params, neg_tokens, excluded_actions, constraints,
                                            inferred_object, resolved_scope, is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
                res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
                return res

        # -------------------------------------------------------------
        # 2. Score 950: Intent ID Exato
        # -------------------------------------------------------------
        clean_intent = core_phrase.replace("//", "").replace("agy_cmd ", "").strip()
        if clean_intent in self.registry:
            it = self.registry[clean_intent]
            res = self._build_resolved(it, 950, "exact_intent_id", core_phrase,
                                        params, neg_tokens, excluded_actions, constraints,
                                        inferred_object, resolved_scope, is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
            res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
            return res

        # -------------------------------------------------------------
        # 3. Resolução Canônica de Missões & DAGs (Mission Templates - Score 920)
        # -------------------------------------------------------------
        mission_res = self.mission_resolver.resolve(
            core_utterance, context, modifiers_applied,
            neg_tokens, excluded_actions, constraints,
            params, inferred_object, resolved_scope,
            execution_surface, input_source, raw
        )
        if mission_res:
            mission_res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
            return mission_res

        # -------------------------------------------------------------
        # 4. Comandos Compostos Legados / Genéricos (Planos em DAG)
        # -------------------------------------------------------------
        compound_res = self._resolve_compound(norm_core, context, excluded_actions, constraints, execution_surface, input_source)
        if compound_res:
            if modifiers_applied:
                compound_res.modifiers_applied = list(set(compound_res.modifiers_applied + modifiers_applied))
                if "EXECUTION.ADVANCED" in modifiers_applied:
                    compound_res.depth = "HARD"
                    compound_res.execution_profile = "DEEP"
                if "EXECUTION.DISCREET" in modifiers_applied:
                    compound_res.mode = "discreet_background"
                w_surf, prof, sc, rz, rec = SurfaceRouter.route(compound_res, raw, constraints, execution_surface, input_source)
                compound_res.resolved_surface = w_surf
                compound_res.execution_profile = prof
                compound_res.surface_scores = sc
                compound_res.surface_reasons = rz
                compound_res.route_receipt = rec
            compound_res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
            return compound_res

        # -------------------------------------------------------------
        # 4. Score 900: Slash Command Exato
        # -------------------------------------------------------------
        slash_index = self.indexes.get("slash_index", {})
        first_token = core_phrase.split()[0]
        if first_token in slash_index:
            it_id = slash_index[first_token]
            it = self.registry.get(it_id)
            if it:
                res = self._build_resolved(it, 900, "exact_slash_command", core_phrase,
                                            params, neg_tokens, excluded_actions, constraints,
                                            inferred_object, resolved_scope, is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
                res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
                return res

        # -------------------------------------------------------------
        # 5. Score 850: Macro Index / Alias Exato (Sensível a Contexto)
        # -------------------------------------------------------------
        macro_index = self.indexes.get("macro_index", {})
        matched_macro_id = macro_index.get(core_phrase) or macro_index.get(core_unaccented) or \
                           macro_index.get(norm) or macro_index.get(unaccented)

        if matched_macro_id:
            it_id = matched_macro_id
            # Context-sensitive macro re-routing
            if it_id == "audit.project.hard":
                if resolved_scope == "HOST":
                    it_id = "audit.host.hard"
                elif resolved_scope == "DATABASE":
                    it_id = "audit.database.hard"
                elif resolved_scope == "NETWORK":
                    it_id = "audit.network.hard"
            elif it_id == "recon.project.hard":
                if resolved_scope == "HOST":
                    it_id = "recon.host.hard"
                elif resolved_scope == "NETWORK":
                    it_id = "recon.network.hard"
            elif it_id == "map.project.general":
                if resolved_scope == "HOST":
                    it_id = "map.host.general"
                elif resolved_scope == "NETWORK":
                    it_id = "map.network.hard"

            it = self.registry.get(it_id)
            if it:
                res = self._build_resolved(it, 850, "macro_intent", core_phrase,
                                            params, neg_tokens, excluded_actions, constraints,
                                            inferred_object, resolved_scope, is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
                res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
                return res

        alias_index = self.indexes.get("alias_index", {})
        if core_phrase in alias_index or norm in alias_index:
            it_id = alias_index.get(core_phrase) or alias_index.get(norm)
            it = self.registry.get(it_id)
            if it:
                res = self._build_resolved(it, 850, "exact_alias", core_phrase,
                                            params, neg_tokens, excluded_actions, constraints,
                                            inferred_object, resolved_scope, is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
                res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
                return res

        unacc_alias_index = self.indexes.get("unaccented_alias_index", {})
        if core_unaccented in unacc_alias_index or unaccented in unacc_alias_index:
            it_id = unacc_alias_index.get(core_unaccented) or unacc_alias_index.get(unaccented)
            it = self.registry.get(it_id)
            if it:
                res = self._build_resolved(it, 840, "exact_alias_unaccented", core_phrase,
                                            params, neg_tokens, excluded_actions, constraints,
                                            inferred_object, resolved_scope, is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
                res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
                return res

        # -------------------------------------------------------------
        # 6. Score 800/750/650: Resolução Composicional por Gramática Semântica
        # -------------------------------------------------------------
        action_sets = self.sets.get("ACTION_SETS", {})
        object_sets = self.sets.get("OBJECT_SETS", {})
        qualifier_sets = self.sets.get("QUALIFIER_SETS", {})

        matched_actions = set()
        for act_name, act_data in action_sets.items():
            for v in act_data.get("inflections", []) + act_data.get("phrases", []):
                if re.search(r"\b" + re.escape(v) + r"\b", core_phrase) or re.search(r"\b" + re.escape(self.strip_accents(v)) + r"\b", core_unaccented):
                    matched_actions.add(act_name)

        matched_objects = set()
        for obj_name, obj_terms in object_sets.items():
            for term in obj_terms:
                if re.search(r"\b" + re.escape(term) + r"\b", core_phrase) or re.search(r"\b" + re.escape(self.strip_accents(term)) + r"\b", core_unaccented):
                    matched_objects.add(obj_name)

        matched_qualifiers = set()
        for ql_name, ql_terms in qualifier_sets.items():
            for term in ql_terms:
                if re.search(r"\b" + re.escape(term) + r"\b", core_phrase):
                    matched_qualifiers.add(ql_name)

        # Convergência Semântica de Alta Fidelidade
        if "AUDIT" in matched_actions or any(w in core_phrase for w in ["audite", "audita", "raio-x"]):
            if "SQLITE" in matched_objects or "DATABASE" in matched_objects:
                it = self.registry.get("audit.database.hard")
                if it:
                    res = self._build_resolved(it, 800, "semantic_action+object", core_phrase,
                                                params, neg_tokens, excluded_actions, constraints,
                                                "DATABASE", "DATABASE", is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
                    res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
                    return res
            if "GIT" in matched_objects:
                it = self.registry.get("audit-git-integrity") or self.registry.get("audit.project.hard")
                if it:
                    res = self._build_resolved(it, 800, "semantic_action+object", core_phrase,
                                                params, neg_tokens, excluded_actions, constraints,
                                                "GIT", "PROJECT", is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
                    res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
                    return res

        scored_candidates = []
        for it_id, it in self.registry.items():
            score = 0
            reason_parts = []
            it_name = it_id.lower()

            if any(ex.lower() in it_name for ex in excluded_actions):
                continue

            it_verbs = set(it.get("semantic", {}).get("verbs", []))
            it_objects = set(it.get("semantic", {}).get("objects", []))
            it_qualifiers = set(it.get("semantic", {}).get("qualifiers", []))

            # Match de Ação
            act_match = False
            for act in matched_actions:
                act_lower = act.lower()
                act_verbs = set(action_sets.get(act, {}).get("verbs", []))
                if act_lower in it_name or any(act_lower in vb for vb in it_verbs) or bool(act_verbs.intersection(it_verbs)):
                    act_match = True
                    break

            # Match de Objeto
            obj_match = False
            for obj in matched_objects:
                obj_lower = obj.lower()
                obj_terms = set(object_sets.get(obj, []))
                if obj_lower in it_name or any(obj_lower in o for o in it_objects) or bool(obj_terms.intersection(it_objects)):
                    obj_match = True
                    break

            # Match de Qualificador
            ql_match = False
            for ql in matched_qualifiers:
                ql_lower = ql.lower()
                ql_terms = set(qualifier_sets.get(ql, []))
                if ql_lower in it_name or any(ql_lower in q for q in it_qualifiers) or bool(ql_terms.intersection(it_qualifiers)):
                    ql_match = True
                    break

            if act_match and obj_match and ql_match:
                score = 800
                reason_parts.append("action+object+qualifier")
            elif act_match and ql_match:
                score = 750
                reason_parts.append("action+qualifier")
            elif act_match and obj_match:
                score = 700
                reason_parts.append("action+object")
            elif obj_match and any(v in core_phrase for v in ["destrava", "libera", "solta", "desengasga"]) and "unlock" in it_id:
                score = 650
                reason_parts.append("unlock_fallback")
            elif act_match and len(matched_objects) == 0 and any(q in core_phrase for q in ["tudo", "completo", "total"]) and "all" in it_id:
                score = 650
                reason_parts.append("all_qualifier_match")

            # Context boost se o scope for compatível
            if resolved_scope.lower() in it.get("semantic", {}).get("scopes", []):
                score += 30

            # Bonus por parâmetros compatíveis
            if "port" in params and ("port" in it_id or "socket" in it_id):
                score += 50
            if "url" in params and ("bench" in it_id or "check" in it_id or "fuzz" in it_id):
                score += 50

            # Penalização para sub-operações hiper-específicas se o termo não foi citado
            for specialized_term in ["bisect", "rebase", "worktree", "index", "config", "credentials", "credential", "ddos", "fuzz"]:
                if specialized_term in it_id and specialized_term not in core_phrase:
                    score -= 250

            # Boost canônico para unlock-git se repo ou repositorio citado
            if it_id == "unlock-git" and any(r in core_phrase for r in ["repo", "repositorio", "repositório"]):
                score += 100

            if score >= 500:
                scored_candidates.append((score, it, "+".join(reason_parts)))

        if scored_candidates:
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            top_score, top_it, top_reason = scored_candidates[0]

            min_margin = self.rules.get("scoring_hierarchy", {}).get("minimum_margin_to_second_candidate", 50)
            if len(scored_candidates) > 1:
                second_score, second_it, _ = scored_candidates[1]
                if (top_score - second_score) < min_margin and top_it["intent_id"] != second_it["intent_id"]:
                    res = self._build_resolved(top_it, top_score - 100, f"ambiguous_with_{second_it['intent_id']}", core_phrase,
                                                params, neg_tokens, excluded_actions, constraints,
                                                inferred_object, resolved_scope, is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
                    res.execution_policy = "AMBIGUOUS_REQUIRES_DISAMBIGUATION"
                    res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
                    return res

            res = self._build_resolved(top_it, top_score, f"semantic_{top_reason}", core_phrase,
                                        params, neg_tokens, excluded_actions, constraints,
                                        inferred_object, resolved_scope, is_discreet, execution_surface=execution_surface, input_source=input_source, raw_query=raw, modifiers_applied=modifiers_applied)
            res.resolution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
            return res

        return None

    def _resolve_compound(self, text: str, context: Optional[Union[Dict[str, Any], str]],
                          global_excluded: List[str], global_constraints: Dict[str, Any],
                          execution_surface: str = "AUTO", input_source: str = "CHATGPT") -> Optional[ResolvedIntent]:
        # Suporte a múltiplos conectivos sequenciais ("reconheça o projeto, audite e depois me mostre os problemas")
        # Expressão ordenada com multi-palavras primeiro
        connectors = r"\s+(?:e\s+depois|em\s+seguida|logo\s+após|depois|e)\s+|,\s*"
        raw_parts = re.split(connectors, text)
        if len(raw_parts) <= 1:
            return None

        clean_parts = []
        for p in raw_parts:
            p_clean = p.strip()
            # Limpa prefixos de conectivos residuais
            for prefix in ["depois ", "em seguida ", "logo após ", "e "]:
                if p_clean.startswith(prefix):
                    p_clean = p_clean[len(prefix):].strip()
            if len(p_clean) < 3 or re.match(r"^(?:mas\s+não|mas\s+nao|sem\s+|não\s+|nao\s+)", p_clean):
                continue
            clean_parts.append(p_clean)

        if len(clean_parts) <= 1:
            return None

        step_intents: List[ResolvedIntent] = []
        for part in clean_parts:
            r = self.resolve(part, context)
            if r:
                step_intents.append(r)

        if len(step_intents) <= 1:
            return None

        first = step_intents[0]
        step_ids = [si.intent_id for si in step_intents]

        # Construção do DAG de dependências: step[i] depends on step[i-1]
        deps: Dict[str, List[str]] = {}
        for idx in range(1, len(step_ids)):
            deps[f"step_{idx+1}_{step_ids[idx]}"] = [f"step_{idx}_{step_ids[idx-1]}"]

        first.is_compound = True
        first.plan_steps = step_ids
        first.dependencies = deps
        first.excluded_actions = list(set(first.excluded_actions + global_excluded))
        first.constraints.update(global_constraints)

        ctx_dict = {"scope": context.upper()} if isinstance(context, str) else (context or {})
        winning_surface, profile, scores, reasons, receipt = SurfaceRouter.route(
            first, text, ctx_dict, execution_surface, input_source
        )
        first.execution_surface = execution_surface
        first.resolved_surface = winning_surface
        first.execution_profile = profile
        first.surface_scores = scores
        first.surface_reasons = reasons
        first.route_receipt = receipt
        return first

    def _build_resolved(self, it: dict, score: int, match_by: str, norm_phrase: str,
                        params: dict, neg_tokens: list, excluded_actions: list,
                        constraints: dict, inferred_object: str, resolved_scope: str,
                        is_discreet: bool, execution_surface: str = "AUTO",
                        input_source: str = "CHATGPT", raw_query: str = "",
                        modifiers_applied: list = None) -> ResolvedIntent:
        template = it.get("command_template", f"agy_cmd {it['intent_id']}")
        if "port" in params:
            template = template.replace("$1", str(params["port"])).replace("${1:-3000}", str(params["port"]))
        if "url" in params:
            template = template.replace("$1", params["url"]).replace("${1:-http://localhost:3000}", params["url"])

        modifiers_applied = modifiers_applied or []

        # Determinar Ação, Objeto, Escopo e Intensidade
        intent_id = it.get("intent_id", "")
        action = it.get("category", "EXECUTE")
        if "audit" in intent_id:
            action = "AUDIT"
        elif "recon" in intent_id:
            action = "RECON"
        elif "map" in intent_id:
            action = "MAP"
        elif "unlock" in intent_id:
            action = "UNLOCK"
        elif "clean" in intent_id:
            action = "CLEAN"

        depth = "NORMAL"
        if intent_id.startswith("audit.") or "hard" in intent_id or any(w in norm_phrase for w in ["forense", "completo", "profund"]):
            depth = "HARD"
            if "rápido" in norm_phrase or "rapido" in norm_phrase:
                depth = "LIGHT"
            elif "forense" in norm_phrase:
                depth = "FORENSIC"
        elif action in ["RECON", "MAP"] and (intent_id.startswith("recon.") or intent_id.startswith("map.")):
            depth = "HARD"

        if "EXECUTION.ADVANCED" in modifiers_applied:
            depth = "HARD"
        if "FAST" in modifiers_applied:
            depth = "LIGHT"
        if "DEEP" in modifiers_applied:
            depth = "HARD"
        if "EXECUTION.DISCREET" in modifiers_applied:
            is_discreet = True
        if "READ_ONLY" in modifiers_applied:
            constraints["read_only"] = True
            constraints["mutation_allowed"] = False

        intensity = "HIGH" if depth in ["HARD", "FORENSIC"] else ("LOW" if depth == "LIGHT" else "NORMAL")

        # Se for ação de observação, default é READ_ONLY_FIRST e MUTATION_ALLOWED = False
        if action in ["AUDIT", "RECON", "MAP"] or constraints.get("read_only"):
            constraints["read_only"] = True
            constraints["mutation_allowed"] = False
            exec_policy = "READ_ONLY_FIRST"
        else:
            exec_policy = it.get("execution_policy", "AUTO_ALLOWED")

        # Sentinela Gate se houver mutação
        if constraints.get("mutation_allowed") and it.get("destructive", False):
            exec_policy = "HUMAN_GATE"
        elif constraints.get("mutation_allowed") and not it.get("destructive", False):
            exec_policy = "SENTINELA_GATE"

        norm_low = (norm_phrase or "").lower()
        raw_low = (raw_query or "").lower()
        is_global_audit = any(g in norm_low or g in raw_low for g in ["auditoria global", "aduitoria global", "audit-global", "auditoria-global", "raio-x global"]) or match_by in ["auditoria global", "audit-global", "auditoria-global"]
        is_total_audit = any(t in norm_low or t in raw_low for t in ["auditoria total", "aduitoria total", "varredura completa"]) or match_by in ["auditoria total", "auditoria-total"]
        phases_list = []
        if is_global_audit and self.audit_global_phases:
            phases_list = self.audit_global_phases
            is_discreet = True
        elif is_total_audit and self.audit_total_phases:
            phases_list = self.audit_total_phases
            is_discreet = True
        elif intent_id.startswith("audit.") and depth == "HARD":
            phases_list = self.audit_phases

        res = ResolvedIntent(
            intent_id=intent_id,
            action=action,
            object=inferred_object,
            scope=resolved_scope,
            depth=depth,
            intensity=intensity,
            target=params.get("target") or params.get("project") or inferred_object,
            context={"inferred_scope": resolved_scope, "inferred_object": inferred_object},
            parameters=params,
            constraints=constraints,
            negations=neg_tokens,
            excluded_actions=excluded_actions,
            output="forensic_report" if depth == "HARD" else "structured",
            mode="discreet_background" if is_discreet else ("read_only_first" if constraints.get("read_only") else "normal"),
            risk=it.get("risk_class", "low"),
            execution_policy=exec_policy,
            confidence_score=score,
            matched_by=match_by,
            canonical_phrase=it.get("canonical_phrase", intent_id),
            command_target=it.get("command_target", "agy_cmd"),
            command_template=template,
            destructive=it.get("destructive", False),
            sensitive=it.get("sensitive", False),
            requires_confirmation=it.get("requires_confirmation", False),
            requires_human_gate=it.get("requires_human_gate", False),
            phases=phases_list,
            discreet_policy=self.discreet_policy,
            execution_plan=it.get("execution_plan", {}),
            modifiers_applied=modifiers_applied
        )

        winning_surface, profile, scores, reasons, receipt = SurfaceRouter.route(
            res, raw_query or norm_phrase, constraints, execution_surface, input_source
        )
        if is_global_audit:
            winning_surface = "AGY_BACKGROUND"
            if receipt:
                receipt["EXECUTION_SURFACE"] = "AGY_BACKGROUND"
                receipt["BACKGROUND"] = True
                receipt["UI_FOCUS"] = False
            res.total_layers = [
                "Camada de Apresentação (Interface de Usuário - UI)",
                "Camada de Lógica de Interação",
                "Camada de Gerenciamento de Estado",
                "Camada de Rede (Cliente de API)",
                "Camada de Segurança Perimetral (WAF - Firewall de Aplicação)",
                "Camada de Redes de Entrega de Conteúdo (CDN)",
                "Camada de Gateway e Roteamento de Borda (DNS e Load Balancers)",
                "Camada de Entrada e Roteamento (Controladores / API)",
                "Camada de Segurança e Autenticação (Middleware)",
                "Camada de Regras de Negócio (Serviços)",
                "Camada de Mensageria e Eventos (Filas Assíncronas)",
                "Camada de Cache Distribuído",
                "Camada de Acesso a Dados (Persistência / ORM)",
                "Camada de Armazenamento Principal (Banco de Dados Relacional/Não-Relacional)",
                "Camada de Réplicas de Leitura e Armazenamento Analítico (Data Warehouse / BI)",
                "Camada de Servidores Web e Proxies Reversos",
                "Camada de Virtualização e Containers",
                "Camada de Orquestração de Containers",
                "Camada de Sistema Operacional do Servidor",
                "Camada de Infraestrutura como Código (IaC)",
                "Camada de Hardware e Provedor de Nuvem (Cloud Computacional)",
                "Camada de Integração e Entrega Contínua (CI/CD)",
                "Camada de Observabilidade, Telemetria e Monitoramento (Logs e Métricas)"
            ]
            res.global_domains = [
                {"dominio": "1. Frontend (Client-Side)", "conceito": "Surface Web (Web Superficial)"},
                {"dominio": "2. Transporte, Borda e Segurança Perimetral", "conceito": "Transporte, Borda & Perímetro"},
                {"dominio": "3. Backend (Server-Side)", "conceito": "Deep Web (Web Profunda / Servidor)"},
                {"dominio": "4. Armazenamento e Análise de Dados", "conceito": "Camadas Avançadas de Dados e Performance"},
                {"dominio": "5. Hospedagem, Virtualização e Infraestrutura (DevOps)", "conceito": "Camadas de Infraestrutura e DevOps (Abaixo do Backend)"},
                {"dominio": "6. Operações Transversais (Cercam todas as outras)", "conceito": "Camadas de Operação e Segurança Transversal"}
            ]
            res.mode = "discreet_background"
        elif is_total_audit:
            winning_surface = "AGY_BACKGROUND"
            if receipt:
                receipt["EXECUTION_SURFACE"] = "AGY_BACKGROUND"
                receipt["BACKGROUND"] = True
                receipt["UI_FOCUS"] = False
            res.total_layers = [
                "Camada de Apresentação (Interface de Usuário - UI)",
                "Camada de Lógica de Interação",
                "Camada de Gerenciamento de Estado",
                "Camada de Rede (Cliente de API)",
                "Camada de Gateway e Roteamento de Borda",
                "Camada de Entrada e Roteamento (Controladores / API)",
                "Camada de Segurança e Autenticação (Middleware)",
                "Camada de Regras de Negócio (Serviços)",
                "Camada de Acesso a Dados (Persistência / ORM)",
                "Camada de Armazenamento (Banco de Dados)"
            ]
            res.mode = "discreet_background"

        res.execution_surface = execution_surface
        res.resolved_surface = winning_surface
        res.execution_profile = profile
        res.surface_scores = scores
        res.surface_reasons = reasons
        res.route_receipt = receipt
        return res

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 semantic_resolver.py [--command-only|--json|--github-issue|--llm-prompt|--context=<scope>|--repo=<owner/repo>] '<frase ou comando>'")
        sys.exit(1)

    command_only = False
    as_json = False
    as_github_issue = False
    as_llm_prompt = False
    context_arg = None
    repo_arg = None
    query_args = []

    for arg in sys.argv[1:]:
        if arg == "--command-only":
            command_only = True
        elif arg == "--json":
            as_json = True
        elif arg == "--github-issue":
            as_github_issue = True
        elif arg == "--llm-prompt":
            as_llm_prompt = True
        elif arg.startswith("--context="):
            context_arg = arg.split("=", 1)[1]
        elif arg.startswith("--repo="):
            repo_arg = arg.split("=", 1)[1]
        elif arg == "--receipt":
            pass
        else:
            query_args.append(arg)

    if not query_args:
        sys.exit(1)

    query = " ".join(query_args)
    resolver = SemanticResolver()
    res = resolver.resolve(query, context=context_arg)

    if as_github_issue:
        if res:
            issue_data = res.to_github_issue(raw_query=query, repo=repo_arg)
            if as_json:
                print(json.dumps(issue_data, indent=2, ensure_ascii=False))
            else:
                print("📋 [GITHUB ISSUE GENERATOR]:")
                print(f"Título: {issue_data['title']}")
                print(f"Labels: {', '.join(issue_data['labels'])}")
                print("\n--- [CORPO DA ISSUE] ---")
                print(issue_data["body"])
                print("\n--- [COMANDO GH DISPATCH] ---")
                print(issue_data["command"])
        else:
            if as_json:
                print(json.dumps({"error": "unresolved"}, indent=2))
            else:
                print("⚠️ [UNRESOLVED]: Nenhuma intenção superou o limiar de confiança.")
        return

    if as_llm_prompt:
        if res:
            prompt_str = res.to_llm_prompt(raw_query=query)
            if as_json:
                print(json.dumps({"llm_prompt": prompt_str, "intent_id": res.intent_id}, indent=2, ensure_ascii=False))
            else:
                print(prompt_str)
        else:
            if as_json:
                print(json.dumps({"error": "unresolved"}, indent=2))
            else:
                print("⚠️ [UNRESOLVED]: Nenhuma intenção superou o limiar de confiança.")
        return

    if command_only:
        if res:
            if res.is_compound and res.plan_steps:
                cmds = []
                for step in res.plan_steps:
                    it_data = resolver.registry.get(step, {})
                    cmds.append(it_data.get("command_template", f"agy_cmd {step}"))
                print(" && ".join(cmds))
            else:
                print(res.command_template)
        else:
            print("NONE")
        return

    if as_json:
        if res:
            print(json.dumps(asdict(res), indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"error": "unresolved"}, indent=2))
        return

    show_receipt = "--receipt" in sys.argv
    if show_receipt and res:
        print("📜 [ROUTE RECEIPT]:")
        print(res.route_receipt_formatted())
        return

    if res:
        print("🧭 [RESOLVED INTENT]:")
        print(f"  Intent ID:         {res.intent_id}")
        print(f"  Action:            {res.action}")
        print(f"  Object:            {res.object}")
        print(f"  Scope:             {res.scope}")
        print(f"  Depth:             {res.depth} (Intensity: {res.intensity})")
        print(f"  Mode:              {res.mode}")
        print(f"  Score:             {res.confidence_score} ({res.matched_by})")
        print(f"  Command Template:  {res.command_template}")
        print(f"  Execution Policy:  {res.execution_policy}")
        print(f"  Resolution Time:   {res.resolution_time_ms} ms")
        if res.parameters:
            print(f"  Parameters:        {res.parameters}")
        if res.negations:
            print(f"  Negations:         {res.negations}")
        if res.excluded_actions:
            print(f"  Excluded Actions:  {res.excluded_actions}")
        if res.constraints:
            print(f"  Constraints:       {res.constraints}")
        if res.is_compound:
            print(f"  Compound Plan:     {' ➔ '.join(res.plan_steps)}")
            print(f"  Dependencies:      {res.dependencies}")
        if res.phases:
            print(f"  Audit Phases:      {len(res.phases)} fases ativas (1 a 10)")
    else:
        print("⚠️ [UNRESOLVED]: Nenhuma intenção superou o limiar de confiança.")

if __name__ == "__main__":
    main()
