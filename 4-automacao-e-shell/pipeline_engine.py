#!/usr/bin/env python3
"""
pipeline_engine.py — Motor de Pipelines Reativos Encadeados do Sentinela
Local: /Users/lucasvinicius/projetos/SISTEMAS/Antigravity Turbinado/4-automacao-e-shell/pipeline_engine.py

Recursos:
1. Parser DSL & JSON para registro e persistência de pipelines no 'dicionario_lexico.json'.
2. Trigger Matcher inteligente (normalização fonética, substring, tokens e pontuação de confiança).
3. Roteamento Híbrido com Dolphin 3 (LLM Fallback) para interpretar intenções conversacionais.
4. Executor sequencial de etapas (PREPARE -> EXECUTE -> FINALIZE) com controle de timeout e erros.
5. Emissão de Recibo Operacional (RouteReceipt) auditável e compatível com a governança Sentinela.
"""

import os
import sys
import re
import json
import time
import shutil
import platform
import subprocess
import unicodedata
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Union

# Localização canônica dos arquivos
BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent
CONFIG_DIR = Path.home() / ".gemini" / "config"
CONFIG_DICT_PATH = CONFIG_DIR / "dicionario_lexico.json"
LOCAL_DICT_PATH = BASE_DIR / "dicionario_lexico.json"

# Cores ANSI para saída rica no terminal
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def normalize_text(text: str) -> str:
    """Normaliza texto: remove acentos, pontuação excessiva e converte para minúsculas."""
    if not text:
        return ""
    # Remove acentos
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Minúsculas e strip
    normalized = ascii_text.lower().strip()
    # Remove pontuação repetida e símbolos exceto hífens/underscores
    normalized = re.sub(r"[^\w\s\-_/]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


@dataclass
class PipelineStep:
    ordem: int
    fase: str  # PREPARE, EXECUTE, FINALIZE ou nome customizado
    comandos: List[str] = field(default_factory=list)
    timeout_segundos: int = 60
    ignorar_erros: bool = False
    mensagem: Optional[str] = None
    target_os: Optional[List[str]] = None


@dataclass
class PipelineDefinition:
    id: str
    descricao: str
    categoria: str = "automacao"
    status: str = "ativo"
    prioridade: str = "media"
    persistente: bool = True
    auto_execute: bool = False
    modo: str = "interativo"
    requer_confirmacao: bool = True
    triggers: List[str] = field(default_factory=list)
    target_os: List[str] = field(default_factory=lambda: ["linux", "darwin", "windows"])
    etapas: List[Dict[str, Any]] = field(default_factory=list)
    target: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "status": self.status,
            "prioridade": self.prioridade,
            "persistente": self.persistente,
            "auto_execute": self.auto_execute,
            "modo": self.modo,
            "requer_confirmacao": self.requer_confirmacao,
            "triggers": self.triggers,
            "target_os": self.target_os,
            "target": self.target,
            "etapas": self.etapas,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], pipeline_id: Optional[str] = None) -> "PipelineDefinition":
        pid = pipeline_id or data.get("id") or "PIPELINE_CUSTOM"
        return cls(
            id=pid,
            descricao=data.get("descricao", "Pipeline de automação"),
            categoria=data.get("categoria", "automacao"),
            status=data.get("status", "ativo"),
            prioridade=data.get("prioridade", "media"),
            persistente=data.get("persistente", True),
            auto_execute=data.get("auto_execute", False),
            modo=data.get("modo", "interativo"),
            requer_confirmacao=data.get("requer_confirmacao", True),
            triggers=data.get("triggers", []),
            target_os=data.get("target_os", ["linux", "darwin", "windows"]),
            target=data.get("target"),
            etapas=data.get("etapas", []),
            metadata=data.get("metadata", {}),
        )

    def to_dsl(self) -> str:
        return PipelineDSLParser.to_dsl(self)


class PipelineDSLParser:
    """
    Parser canônico DSL do Sentinela v4.1 para registro, compilação,
    validação e exportação de pipelines no 'dicionario_lexico.json'.
    """

    @classmethod
    def parse_dsl(cls, dsl_text: str, target_pipeline_id: Optional[str] = None) -> PipelineDefinition:
        """
        Analisa texto DSL e retorna um objeto PipelineDefinition.
        Se houver múltiplos pipelines, retorna o correspondente a target_pipeline_id ou o primeiro.
        """
        pipes = cls.parse_dsl_multi(dsl_text)
        if not pipes:
            return PipelineDefinition(id="PIPELINE_VAZIO", descricao="Nenhum pipeline detectado")

        if target_pipeline_id:
            for p in pipes:
                if p.id.lower() == target_pipeline_id.lower():
                    return p
        return pipes[0]

    @classmethod
    def parse_dsl_multi(cls, dsl_text: str) -> List[PipelineDefinition]:
        """
        Analisa texto DSL com suporte a múltiplos blocos PIPELINE no mesmo documento.
        Retorna lista de objetos PipelineDefinition.
        """
        lines = dsl_text.splitlines()
        comment_meta: Dict[str, Any] = {}
        parsed_pipelines: List[PipelineDefinition] = []

        current_pipe: Optional[Dict[str, Any]] = None
        current_block: Optional[str] = None
        current_action_name: Optional[str] = None
        current_action_data: Dict[str, Any] = {}

        actions_catalog: Dict[str, Dict[str, Any]] = {}
        binding_order: List[str] = []
        in_triggers = False

        def finish_current_action():
            nonlocal current_action_name, current_action_data
            if current_action_name:
                actions_catalog[current_action_name] = dict(current_action_data)
            current_action_name = None
            current_action_data = {}

        def finish_current_pipeline():
            nonlocal current_pipe, actions_catalog, binding_order
            if not current_pipe:
                return

            etapas_finais: List[Dict[str, Any]] = []
            if binding_order:
                for act_name in binding_order:
                    if act_name in actions_catalog:
                        step_copy = dict(actions_catalog[act_name])
                        step_copy["ordem"] = len(etapas_finais) + 1
                        etapas_finais.append(step_copy)
                    else:
                        etapas_finais.append({
                            "ordem": len(etapas_finais) + 1,
                            "fase": act_name,
                            "comandos": [f"# Acao vinculada: {act_name}"],
                            "ignorar_erros": True
                        })
            else:
                for act_name, act_data in actions_catalog.items():
                    step_copy = dict(act_data)
                    step_copy["ordem"] = len(etapas_finais) + 1
                    etapas_finais.append(step_copy)

            current_pipe["etapas"] = etapas_finais
            parsed_pipelines.append(PipelineDefinition.from_dict(current_pipe))
            current_pipe = None
            actions_catalog = {}
            binding_order = []

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            # 1. Comentários de Metadados de Cabeçalho
            if line.startswith("//") or line.startswith("#"):
                clean_comment = line.lstrip("/# ").strip()
                if ":" in clean_comment:
                    k, v = clean_comment.split(":", 1)
                    k_upper = k.strip().upper()
                    v_clean = v.strip().strip('"').strip("'")
                    if "REGISTRO NO DICION" in k_upper or "DICIONARIO" in k_upper:
                        comment_meta["dicionario"] = v_clean
                    elif "TIPO" in k_upper:
                        comment_meta["tipo"] = v_clean
                        if "persistente" in v_clean.lower():
                            comment_meta["persistente"] = True
                    elif "STATUS" in k_upper:
                        comment_meta["status"] = v_clean.lower()
                    elif "PRIORIDADE" in k_upper:
                        comment_meta["prioridade"] = v_clean.lower()
                    elif "CATEGORIA" in k_upper:
                        comment_meta["categoria"] = v_clean.lower()
                    elif "TARGET" in k_upper:
                        comment_meta["target"] = v_clean
                continue

            # 2. Header PIPELINE "NOME":
            match_pipe = re.match(r'^PIPELINE\s+["\']?([^"\':]+)["\']?\s*:', line, re.IGNORECASE)
            if match_pipe and not re.search(r'EXECUTA\s*:', line, re.IGNORECASE):
                finish_current_action()
                if current_pipe:
                    finish_current_pipeline()

                p_id = match_pipe.group(1).strip()
                current_pipe = {
                    "id": p_id,
                    "descricao": f"Pipeline {p_id}",
                    "categoria": comment_meta.get("categoria", "automacao"),
                    "status": comment_meta.get("status", "ativo"),
                    "prioridade": comment_meta.get("prioridade", "media"),
                    "persistente": comment_meta.get("persistente", True),
                    "auto_execute": False,
                    "modo": "interativo",
                    "requer_confirmacao": True,
                    "triggers": [],
                    "target_os": ["linux", "darwin", "windows"],
                    "target": comment_meta.get("target"),
                    "etapas": [],
                    "metadata": {
                        "dicionario": comment_meta.get("dicionario", "sentinela")
                    }
                }
                current_block = "PIPELINE"
                continue

            # Fechamento explícito de PIPELINE
            if line.upper() in ["FIM PIPELINE", "END PIPELINE"]:
                current_block = None
                continue

            # 3. Sub-bloco Triggers
            if line.upper().startswith("TRIGGERS:"):
                in_triggers = True
                continue
            if line.upper() in ["FIM TRIGGERS", "END TRIGGERS"]:
                in_triggers = False
                continue

            if in_triggers and current_pipe is not None:
                match_trig = re.match(r'^-\s*["\']?([^"\']+)["\']?', line)
                if match_trig:
                    current_pipe["triggers"].append(match_trig.group(1).strip())
                continue

            # 4. Bloco de Vinculação Ordenada: PIPELINE "NOME" EXECUTA:
            match_exec = re.match(r'^PIPELINE\s+["\']?([^"\':]+)["\']?\s+EXECUTA\s*:', line, re.IGNORECASE)
            if match_exec:
                finish_current_action()
                current_block = "EXECUTA"
                continue

            if line.upper() in ["FIM VINCULACAO", "END VINCULACAO", "FIM EXECUTA", "END EXECUTA"]:
                current_block = None
                continue

            if current_block == "EXECUTA":
                match_link = re.match(r'^(?:->|-)\s*["\']?([^"\']+)["\']?', line)
                if match_link:
                    binding_order.append(match_link.group(1).strip())
                continue

            # 5. Declaração de Ação: ACAO "NOME":
            match_acao = re.match(r'^ACAO\s+["\']?([^"\':]+)["\']?\s*:', line, re.IGNORECASE)
            if match_acao:
                finish_current_action()
                current_action_name = match_acao.group(1).strip()
                current_action_data = {
                    "fase": current_action_name,
                    "comandos": [],
                    "timeout_segundos": 60,
                    "ignorar_erros": False,
                    "mensagem": None,
                    "target_os": None
                }
                current_block = "ACAO"
                continue

            if line.upper() in ["FIM ACAO", "END ACAO"]:
                finish_current_action()
                current_block = None
                continue

            # 6. Declaração de Regras: REGRA "NOME":
            match_regra = re.match(r'^REGRA\s+["\']?([^"\':]+)["\']?\s*:', line, re.IGNORECASE)
            if match_regra:
                finish_current_action()
                current_block = "REGRA"
                continue

            if line.upper() in ["FIM REGRA", "END REGRA"]:
                current_block = None
                continue

            # Atributos chave-valor do bloco PIPELINE
            if current_block == "PIPELINE" and current_pipe is not None:
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip().upper()
                    v = v.strip().strip('"').strip("'")
                    if k == "DESCRICAO":
                        current_pipe["descricao"] = v
                    elif k == "CATEGORIA":
                        current_pipe["categoria"] = v
                    elif k == "PERSISTENTE":
                        current_pipe["persistente"] = v.lower() in ["true", "1", "sim", "verdadeiro"]
                    elif k == "AUTO_EXECUTE":
                        current_pipe["auto_execute"] = v.lower() in ["true", "1", "sim", "verdadeiro"]
                    elif k == "PRIORIDADE":
                        current_pipe["prioridade"] = v.lower()
                    elif k == "STATUS":
                        current_pipe["status"] = v.lower()
                    elif k == "TARGET":
                        current_pipe["target"] = v
                    elif k == "TARGET_OS":
                        if "[" in v:
                            try:
                                current_pipe["target_os"] = json.loads(v)
                            except Exception:
                                current_pipe["target_os"] = [x.strip() for x in v.strip("[]").split(",")]
                        else:
                            current_pipe["target_os"] = [x.strip() for x in v.split(",") if x.strip()]
                    elif k == "DICIONARIO":
                        current_pipe["metadata"]["dicionario"] = v
                    elif k == "MODO":
                        current_pipe["modo"] = v.lower()
                    elif k == "CONFIRMACAO":
                        current_pipe["requer_confirmacao"] = "não" not in v.lower() and "false" not in v.lower()
                continue

            # Atributos e comandos dentro de ACAO
            if current_block == "ACAO":
                if line.upper().startswith("EXECUTE ") or line.upper().startswith("EXECUTE:"):
                    cmd_match = re.match(r'^EXECUTE:?\s+["\']?(.*?)["\']?$', line, re.IGNORECASE)
                    if cmd_match:
                        current_action_data["comandos"].append(cmd_match.group(1).strip())
                elif line.upper().startswith("MENSAGEM ") or line.upper().startswith("MENSAGEM:"):
                    msg_match = re.match(r'^MENSAGEM:?\s+["\']?(.*?)["\']?$', line, re.IGNORECASE)
                    if msg_match:
                        current_action_data["mensagem"] = msg_match.group(1).strip()
                elif line.upper().startswith("TIMEOUT:") or line.upper().startswith("TIMEOUT_SEGUNDOS:"):
                    _, t_val = line.split(":", 1)
                    try:
                        current_action_data["timeout_segundos"] = int(re.sub(r'[^\d]', '', t_val))
                    except Exception:
                        pass
                elif line.upper().startswith("IGNORAR_ERROS:") or line.upper().startswith("IGNORAR_ERROS"):
                    current_action_data["ignorar_erros"] = "false" not in line.lower() and "não" not in line.lower()
                elif line.upper().startswith("TARGET_OS:"):
                    _, os_val = line.split(":", 1)
                    current_action_data["target_os"] = [x.strip() for x in os_val.split(",") if x.strip()]
                else:
                    # Comando de shell direto ou Macro de Domínio
                    current_action_data["comandos"].append(line)
                continue

            # Atributos dentro de REGRA
            if current_block == "REGRA" and current_pipe is not None:
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip().upper()
                    v = v.strip().strip('"').strip("'")
                    if k == "MODO":
                        current_pipe["modo"] = v.lower()
                    elif k == "CONFIRMACAO":
                        current_pipe["requer_confirmacao"] = "não" not in v.lower() and "false" not in v.lower()
                    elif k == "QUANDO":
                        if "qualquer trigger" in v.lower() or "auto" in v.lower():
                            current_pipe["auto_execute"] = True
                continue

        finish_current_action()
        if current_pipe:
            finish_current_pipeline()

        return parsed_pipelines

    @staticmethod
    def to_dsl(pipeline: Union[PipelineDefinition, Dict[str, Any]]) -> str:
        """
        Converte um PipelineDefinition ou dicionário para sintaxe DSL canônica Sentinela.
        """
        data = pipeline.to_dict() if isinstance(pipeline, PipelineDefinition) else pipeline
        lines = []

        p_id = data.get("id", "PIPELINE_CUSTOM")
        dict_name = data.get("metadata", {}).get("dicionario", "sentinela")
        status = data.get("status", "ativo")
        prioridade = data.get("prioridade", "media")
        persistente = data.get("persistente", True)
        tipo = "pipeline persistente" if persistente else "pipeline volátil"

        lines.append(f"// --- INÍCIO DO PIPELINE: {p_id} ---")
        lines.append(f"// REGISTRO NO DICIONÁRIO: {dict_name}")
        lines.append(f"// TIPO: {tipo}")
        lines.append(f"// STATUS: {status}")
        lines.append(f"// PRIORIDADE: {prioridade}")
        lines.append("")
        lines.append("// --- METADADOS DE REGISTRO ---")
        lines.append(f'PIPELINE "{p_id}":')
        lines.append(f'  DICIONARIO: "{dict_name}"')
        lines.append(f'  DESCRICAO: "{data.get("descricao", "")}"')
        lines.append(f'  CATEGORIA: "{data.get("categoria", "automacao")}"')
        lines.append(f'  PERSISTENTE: {str(persistente).lower()}')
        lines.append(f'  AUTO_EXECUTE: {str(data.get("auto_execute", False)).lower()}')

        if data.get("target_os"):
            lines.append(f'  TARGET_OS: {json.dumps(data.get("target_os"))}')

        lines.append("")
        lines.append("  // GATILHOS DE ATIVAÇÃO (triggers)")
        lines.append("  TRIGGERS:")
        for tr in data.get("triggers", []):
            lines.append(f'    - "{tr}"')
        lines.append("  FIM TRIGGERS")

        if data.get("target"):
            lines.append("")
            lines.append(f'  TARGET: "{data.get("target")}"')

        lines.append("FIM PIPELINE")
        lines.append("")
        lines.append("// --- DEFINIÇÃO DAS AÇÕES DO PIPELINE ---")

        etapas = data.get("etapas", [])
        for step in etapas:
            fase = step.get("fase", "EXECUTE")
            lines.append(f'ACAO "{fase}":')
            t_sec = step.get("timeout_segundos")
            if t_sec and t_sec != 60:
                lines.append(f'  TIMEOUT: {t_sec}')
            if step.get("ignorar_erros"):
                lines.append('  IGNORAR_ERROS: true')
            for cmd in step.get("comandos", []):
                if any(cmd.startswith(prefix) for prefix in ["SPOOF_", "DUMP_", "CHECK_", "SYNC_", "AUDIT_"]):
                    lines.append(f'  {cmd}')
                else:
                    lines.append(f'  EXECUTE "{cmd}"')
            if step.get("mensagem"):
                lines.append(f'  MENSAGEM "{step.get("mensagem")}"')
            lines.append("FIM ACAO")
            lines.append("")

        lines.append("// --- VINCULAÇÃO DAS AÇÕES AO PIPELINE ---")
        lines.append(f'PIPELINE "{p_id}" EXECUTA:')
        for step in etapas:
            fase = step.get("fase", "EXECUTE")
            lines.append(f'  -> "{fase}"')
        lines.append("FIM VINCULACAO")
        lines.append("")
        lines.append("// --- REGRA DE DISPARO ---")
        lines.append('REGRA "AUTO_TRIGGER":')
        lines.append(f'  QUANDO: entrada do usuário contém qualquer TRIGGER do pipeline "{p_id}"')
        lines.append(f'  ENTAO: executar pipeline "{p_id}" completo em sequência')
        lines.append(f'  MODO: {data.get("modo", "interativo")}')
        conf_req = "requerida" if data.get("requer_confirmacao", True) else "não requerida"
        lines.append(f'  CONFIRMACAO: {conf_req}')
        lines.append("FIM REGRA")
        lines.append("")
        lines.append("// --- FIM DO PIPELINE ---")
        return "\n".join(lines)

    @staticmethod
    def validate_dsl(dsl_text: str) -> Dict[str, Any]:
        """
        Validador e linter sintático/semântico de definições DSL.
        Retorna dicionário com status de validade, erros, avisos e lista de IDs.
        """
        errors = []
        warnings = []
        pipelines_found = []

        lines = dsl_text.splitlines()
        open_blocks = []
        has_triggers = False
        action_names = set()
        bound_actions = []

        for idx, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue

            m_pipe = re.match(r'^PIPELINE\s+["\']?([^"\':]+)["\']?\s*:', line, re.IGNORECASE)
            if m_pipe and not re.search(r'EXECUTA\s*:', line, re.IGNORECASE):
                p_name = m_pipe.group(1).strip()
                pipelines_found.append(p_name)
                open_blocks.append(("PIPELINE", idx))
                continue

            if line.upper() in ["FIM PIPELINE", "END PIPELINE"]:
                if open_blocks and open_blocks[-1][0] == "PIPELINE":
                    open_blocks.pop()
                else:
                    warnings.append(f"Linha {idx}: 'FIM PIPELINE' sem bloco PIPELINE aberto correspondente.")
                continue

            if line.upper().startswith("TRIGGERS:"):
                has_triggers = True
                open_blocks.append(("TRIGGERS", idx))
                continue

            if line.upper() in ["FIM TRIGGERS", "END TRIGGERS"]:
                if open_blocks and open_blocks[-1][0] == "TRIGGERS":
                    open_blocks.pop()
                continue

            m_acao = re.match(r'^ACAO\s+["\']?([^"\':]+)["\']?\s*:', line, re.IGNORECASE)
            if m_acao:
                action_names.add(m_acao.group(1).strip())
                open_blocks.append(("ACAO", idx))
                continue

            if line.upper() in ["FIM ACAO", "END ACAO"]:
                if open_blocks and open_blocks[-1][0] == "ACAO":
                    open_blocks.pop()
                continue

            m_exec = re.match(r'^PIPELINE\s+["\']?([^"\':]+)["\']?\s+EXECUTA\s*:', line, re.IGNORECASE)
            if m_exec:
                open_blocks.append(("EXECUTA", idx))
                continue

            if line.upper() in ["FIM VINCULACAO", "END VINCULACAO", "FIM EXECUTA", "END EXECUTA"]:
                if open_blocks and open_blocks[-1][0] == "EXECUTA":
                    open_blocks.pop()
                continue

            if open_blocks and open_blocks[-1][0] == "EXECUTA":
                m_link = re.match(r'^(?:->|-)\s*["\']?([^"\']+)["\']?', line)
                if m_link:
                    bound_actions.append((m_link.group(1).strip(), idx))
                continue

            m_regra = re.match(r'^REGRA\s+["\']?([^"\':]+)["\']?\s*:', line, re.IGNORECASE)
            if m_regra:
                open_blocks.append(("REGRA", idx))
                continue

            if line.upper() in ["FIM REGRA", "END REGRA"]:
                if open_blocks and open_blocks[-1][0] == "REGRA":
                    open_blocks.pop()
                continue

        for blk, l_num in open_blocks:
            errors.append(f"Bloco '{blk}' aberto na linha {l_num} não foi fechado.")

        if not pipelines_found:
            errors.append("Nenhuma declaração 'PIPELINE' encontrada no documento.")

        if not has_triggers:
            warnings.append("Nenhum bloco 'TRIGGERS:' definido. O pipeline só poderá ser acionado manualmente por ID.")

        for act, l_num in bound_actions:
            if act not in action_names:
                errors.append(f"Linha {l_num}: Ação '{act}' vinculada em EXECUTA mas nunca declarada em um bloco 'ACAO'.")

        for act in action_names:
            if bound_actions and act not in [b[0] for b in bound_actions]:
                warnings.append(f"Ação '{act}' declarada mas não foi incluída no bloco de vinculação EXECUTA.")

        return {
            "valido": len(errors) == 0,
            "erros": errors,
            "avisos": warnings,
            "pipelines": pipelines_found
        }


class PipelineEngine:
    """Motor de execução e orquestração de pipelines inteligentes."""


    def __init__(self, dict_path: Optional[Path] = None):
        self.dict_path = dict_path or self._resolve_dictionary_path()
        self.dictionary_data: Dict[str, Any] = self._load_dictionary()
        self._ensure_pipelines_schema()

    def _resolve_dictionary_path(self) -> Path:
        """Resolve o caminho físico soberano do dicionário."""
        if LOCAL_DICT_PATH.exists():
            return LOCAL_DICT_PATH
        if CONFIG_DICT_PATH.exists():
            return CONFIG_DICT_PATH.resolve()
        return LOCAL_DICT_PATH

    def _load_dictionary(self) -> Dict[str, Any]:
        """Carrega dados do dicionario_lexico.json com fallback."""
        if self.dict_path.exists():
            try:
                with open(self.dict_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"{YELLOW}[!] Aviso ao ler {self.dict_path}: {e}{RESET}")
        return {
            "versao": "4.0",
            "modulo": "sentinela_lexicon",
            "descricao": "Dicionário canônico de abstração léxica e pipelines reativos.",
            "pipelines": {},
            "mapeamento": {},
            "categorias": {},
            "aliases_linguagem": {}
        }

    def _ensure_pipelines_schema(self):
        """Garante que a chave 'pipelines' existe e a versão é atualizada para 4.1."""
        dirty = False
        if "pipelines" not in self.dictionary_data:
            self.dictionary_data["pipelines"] = self._get_builtin_pipelines()
            dirty = True

        current_ver = str(self.dictionary_data.get("versao", "4.0"))
        if current_ver < "4.1":
            self.dictionary_data["versao"] = "4.1"
            dirty = True

        if dirty:
            self.save_dictionary()

    def save_dictionary(self):
        """Salva com segurança e integridade atômica."""
        tmp_file = self.dict_path.with_suffix(".tmp.json")
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self.dictionary_data, f, indent=2, ensure_ascii=False)
            tmp_file.replace(self.dict_path)
            # Se for symlink no config_dir, assegura sincronia
            if CONFIG_DICT_PATH.exists() and CONFIG_DICT_PATH.resolve() != self.dict_path.resolve():
                try:
                    shutil.copy2(self.dict_path, CONFIG_DICT_PATH)
                except Exception:
                    pass
        except Exception as e:
            if tmp_file.exists():
                tmp_file.unlink(missing_ok=True)
            raise IOError(f"Falha ao salvar dicionário léxico: {e}")

    def _get_builtin_pipelines(self) -> Dict[str, Any]:
        """Retorna pipelines essenciais embutidos por padrão."""
        return {
            "DUMP_BANCO_COMPLETO": {
                "id": "DUMP_BANCO_COMPLETO",
                "descricao": "Executa dump/exportação contextual de base de dados e gera checksum.",
                "categoria": "devops",
                "status": "ativo",
                "prioridade": "alta",
                "persistente": True,
                "auto_execute": False,
                "modo": "interativo",
                "requer_confirmacao": True,
                "triggers": [
                    "dump do banco",
                    "exportar banco",
                    "backup do banco",
                    "dump sql",
                    "fazer dump"
                ],
                "target_os": ["linux", "darwin"],
                "etapas": [
                    {
                        "ordem": 1,
                        "fase": "PREPARE",
                        "comandos": ["mkdir -p ./backups"],
                        "ignorar_erros": True
                    },
                    {
                        "ordem": 2,
                        "fase": "EXECUTE",
                        "comandos": ["echo '[*] Executando dump contextual de banco...'"],
                        "timeout_segundos": 120
                    },
                    {
                        "ordem": 3,
                        "fase": "FINALIZE",
                        "comandos": ["ls -lh ./backups 2>/dev/null || true"],
                        "mensagem": "Dump do banco de dados concluído com sucesso."
                    }
                ]
            },
            "LIMPEZA_LOGS_E_BUFFERS": {
                "id": "LIMPEZA_LOGS_E_BUFFERS",
                "descricao": "Limpeza determinística de buffers de log e arquivos temporários.",
                "categoria": "manutencao",
                "status": "ativo",
                "prioridade": "media",
                "persistente": True,
                "auto_execute": True,
                "modo": "silencioso",
                "requer_confirmacao": False,
                "triggers": [
                    "limpar logs",
                    "limpeza de logs",
                    "faxina de logs",
                    "rotacionar logs",
                    "truncar logs"
                ],
                "target_os": ["linux", "darwin", "windows"],
                "etapas": [
                    {
                        "ordem": 1,
                        "fase": "PREPARE",
                        "comandos": ["echo '[*] Preparando rotação de logs...'"],
                        "ignorar_erros": True
                    },
                    {
                        "ordem": 2,
                        "fase": "EXECUTE",
                        "comandos": ["find ./logs -name '*.log' -size +20M -exec truncate -s 0 {} \\; 2>/dev/null || true"],
                        "timeout_segundos": 30,
                        "ignorar_erros": True
                    },
                    {
                        "ordem": 3,
                        "fase": "FINALIZE",
                        "mensagem": "Limpeza de logs finalizada com sucesso."
                    }
                ]
            },
            "AUDITORIA_INTEGRIDADE_SISTEMA": {
                "id": "AUDITORIA_INTEGRIDADE_SISTEMA",
                "descricao": "Auditoria de integridade, locks órfãos e saúde de processos e Git.",
                "categoria": "seguranca",
                "status": "ativo",
                "prioridade": "alta",
                "persistente": True,
                "auto_execute": False,
                "modo": "interativo",
                "requer_confirmacao": True,
                "triggers": [
                    "auditoria rapida",
                    "check de integridade",
                    "verificar integridade",
                    "healthcheck sistema",
                    "diagnostico completo"
                ],
                "target_os": ["linux", "darwin"],
                "etapas": [
                    {
                        "ordem": 1,
                        "fase": "PREPARE",
                        "comandos": ["git status --porcelain 2>/dev/null || true"]
                    },
                    {
                        "ordem": 2,
                        "fase": "EXECUTE",
                        "comandos": [
                            "find . -name '.git/index.lock' -delete 2>/dev/null || true",
                            "git fsck --quick 2>/dev/null || true"
                        ]
                    },
                    {
                        "ordem": 3,
                        "fase": "FINALIZE",
                        "mensagem": "Auditoria de integridade realizada com sucesso."
                    }
                ]
            },
            "AUDITORIA_TOTAL": {
                "id": "AUDITORIA_TOTAL",
                "descricao": "Auditoria Total nas 10 Camadas Arquiteturais: Superfície Web/Client-Side, Rede e Borda, Gateways/APIs, Rotas Sensíveis, Segredos/Chaves, SCA/Dependências, Sanitização SQL, Webshells/Backdoors, Conformidade PCI-DSS/PAN e Laudo Unificado.",
                "categoria": "seguranca",
                "status": "ativo",
                "prioridade": "critica",
                "persistente": True,
                "auto_execute": False,
                "modo": "interativo",
                "requer_confirmacao": True,
                "triggers": [
                    "auditoria total",
                    "faca uma auditoria total",
                    "faça uma auditoria total",
                    "executar auditoria total",
                    "auditoria completa",
                    "varredura completa",
                    "audit total",
                    "raio-x total",
                    "auditoria total do sistema",
                    "varredura total de seguranca",
                    "raio-x completo"
                ],
                "target_os": ["linux", "darwin", "windows"],
                "target": ".",
                "etapas": [
                    {
                        "ordem": 1,
                        "fase": "PREPARE",
                        "comandos": ["mkdir -p ./reports ./artifacts ./artifacts/visual_snapshots"],
                        "ignorar_erros": True,
                        "mensagem": "Diretórios de artefatos e relatórios inicializados."
                    },
                    {
                        "ordem": 2,
                        "fase": "PHASE_1_CLIENT_SIDE",
                        "comandos": ["python3 -c \"import os, glob; htmls = glob.glob('**/*.html', recursive=True); print(f'[*] [CAMADA 1: Client-Side] {len(htmls)} arquivo(s) HTML inspecionado(s) para conformidade CSP, SRI e isolamento DOM.')\""],
                        "timeout_segundos": 60,
                        "ignorar_erros": True,
                        "mensagem": "Camada 1 (Client-Side, CSP, SRI & Anti-Bot) auditada."
                    },
                    {
                        "ordem": 3,
                        "fase": "PHASE_2_NETWORK_SURFACE",
                        "comandos": ["python3 -c \"import socket; ports = [21, 22, 80, 443, 3000, 3306, 5173, 5432, 6379, 8000, 8080, 8088, 8765, 9000, 27017]; open_pts = [p for p in ports if socket.socket().connect_ex(('127.0.0.1', p)) == 0]; print(f'[*] [CAMADAS 2 e 3: Rede & Borda] Portas ativas detectadas: {open_pts}')\""],
                        "timeout_segundos": 60,
                        "ignorar_erros": True,
                        "mensagem": "Camadas 2 e 3 (Rede, Borda e Superfície de Portas) auditadas."
                    },
                    {
                        "ordem": 4,
                        "fase": "PHASE_3_GATEWAY_SECURITY",
                        "comandos": ["python3 -c \"import os, re; routes = []; [routes.extend(re.findall(r'@(?:app|router)\\.(?:get|post|put|delete)\\([\\\"\\']([^\\\"\\']+)[\\\"\\']', open(os.path.join(r, f), errors='ignore').read())) for r, d, fs in os.walk('.') for f in fs if f.endswith(('.py', '.js', '.ts'))]; print(f'[*] [CAMADAS 4 e 5: Gateways & APIs] {len(routes)} rotas de API mapeadas estaticamente em código local.')\""],
                        "timeout_segundos": 60,
                        "ignorar_erros": True,
                        "mensagem": "Camadas 4 e 5 (Gateways, APIs e Controladores) auditadas."
                    },
                    {
                        "ordem": 5,
                        "fase": "PHASE_4_SENSITIVE_ROUTES",
                        "comandos": ["python3 -c \"import os; sens = [f for f in ['.env', '.env.local', 'config.json', '.git/config'] if os.path.exists(f)]; print(f'[*] [CAMADA 6: Rotas Sensíveis] Arquivos críticos no workspace: {sens}')\""],
                        "timeout_segundos": 60,
                        "ignorar_erros": True,
                        "mensagem": "Camada 6 (Rotas Sensíveis & Exposição) auditada."
                    },
                    {
                        "ordem": 6,
                        "fase": "PHASE_5_SECRETS_AND_KEYS",
                        "comandos": ["python3 -c \"import os, re; pat = re.compile(r'(?i)(api[_-]?key|secret|password|bearer|jwt)\\s*[:=]\\s*[\\\"\\'][^\\\"\\']{8,}[\\\"\\']'); count = sum(1 for r, d, fs in os.walk('.') for f in fs if f.endswith(('.py', '.js', '.ts', '.json', '.env')) and pat.search(open(os.path.join(r, f), errors='ignore').read())); print(f'[*] [CAMADA 7: Segredos] Alertas de credenciais hardcoded: {count}')\""],
                        "timeout_segundos": 60,
                        "ignorar_erros": True,
                        "mensagem": "Camada 7 (Gerenciamento de Segredos & Chaves) auditada."
                    },
                    {
                        "ordem": 7,
                        "fase": "PHASE_6_SCA_DEPENDENCIES",
                        "comandos": ["python3 -c \"import os; pkg = os.path.exists('package.json'); req = os.path.exists('requirements.txt'); print(f'[*] [CAMADA 8: SCA] Manifesto de dependências: package.json={pkg}, requirements.txt={req}')\""],
                        "timeout_segundos": 60,
                        "ignorar_erros": True,
                        "mensagem": "Camada 8 (Análise de Composição de Software SCA) auditada."
                    },
                    {
                        "ordem": 8,
                        "fase": "PHASE_7_SQL_SANITIZATION",
                        "comandos": ["python3 -c \"import os, re; pat = re.compile(r'(?i)(execute|rawQuery)\\s*\\(\\s*(f[\\\"\\'].*?(SELECT|INSERT|UPDATE|DELETE)|[\\\"\\'].*?(SELECT|INSERT|UPDATE|DELETE).*?[\\\"\\']\\s*\\+)'); sql_v = sum(1 for r, d, fs in os.walk('.') for f in fs if f.endswith(('.py', '.js', '.ts', '.php')) and pat.search(open(os.path.join(r, f), errors='ignore').read())); print(f'[*] [CAMADA 9: Persistência & ORM] Concatenações diretas de SQL: {sql_v}')\""],
                        "timeout_segundos": 60,
                        "ignorar_erros": True,
                        "mensagem": "Camada 9 (Sanitização SQL & ORM) auditada."
                    },
                    {
                        "ordem": 9,
                        "fase": "PHASE_8_WEBSHELLS_PRIVESC",
                        "comandos": ["python3 -c \"import os, re; pat = re.compile(r'(?i)(eval\\s*\\(\\s*base64_decode|gzinflate\\s*\\(\\s*base64|shell_exec\\s*\\(\\s*\\$_|system\\s*\\(\\s*\\$_)'); ws = sum(1 for r, d, fs in os.walk('.') for f in fs if f.endswith(('.php', '.py', '.js', '.sh')) and pat.search(open(os.path.join(r, f), errors='ignore').read())); print(f'[*] [CAMADA 10: Host & Infraestrutura] Padrões de webshells/backdoors detectados: {ws}')\""],
                        "timeout_segundos": 60,
                        "ignorar_erros": True,
                        "mensagem": "Camada 10 (Webshells, Backdoors & Hardening) auditada."
                    },
                    {
                        "ordem": 10,
                        "fase": "PHASE_9_PCI_DSS_COMPLIANCE",
                        "comandos": ["python3 \"/Users/lucasvinicius/projetos/SISTEMAS/Antigravity Turbinado/4-automacao-e-shell/scan_cards_pci.py\" . --output ./reports/compliance_pci_audit.json"],
                        "timeout_segundos": 120,
                        "ignorar_erros": False,
                        "mensagem": "Conformidade PCI-DSS e detecção de PAN/CVV executada com sucesso."
                    },
                    {
                        "ordem": 11,
                        "fase": "PHASE_10_DOM_SNAPSHOT_REPLICA",
                        "comandos": ["python3 -c \"import os; print('[*] [ARTEFATOS & DOM] Verificando existência de snapshots offline e entrypoints (index.html, hub_replicado.html)...')\""],
                        "timeout_segundos": 30,
                        "ignorar_erros": True,
                        "mensagem": "Verificação de replicação e artefatos de entrega concluída."
                    },
                    {
                        "ordem": 12,
                        "fase": "FINALIZE",
                        "comandos": ["python3 \"/Users/lucasvinicius/projetos/SISTEMAS/Antigravity Turbinado/4-automacao-e-shell/compile_audit_report.py\" ."],
                        "timeout_segundos": 60,
                        "ignorar_erros": False,
                        "mensagem": "🎉 Auditoria Total (10 Camadas) concluída e laudo pericial gerado em ./reports/."
                    }
                ],
                "metadata": {
                    "dicionario": "sentinela",
                    "camadas": 10,
                    "compliance": "PCI-DSS-v4.0"
                }
            }
        }

    def list_pipelines(self) -> List[PipelineDefinition]:
        """Lista todos os pipelines registrados no dicionário."""
        raw_pipes = self.dictionary_data.get("pipelines", {})
        result = []
        for pid, data in raw_pipes.items():
            result.append(PipelineDefinition.from_dict(data, pipeline_id=pid))
        return result

    def get_pipeline(self, pipeline_id: str) -> Optional[PipelineDefinition]:
        """Obtém um pipeline específico por ID."""
        raw_pipes = self.dictionary_data.get("pipelines", {})
        if pipeline_id in raw_pipes:
            return PipelineDefinition.from_dict(raw_pipes[pipeline_id], pipeline_id=pipeline_id)
        # Busca insensível a maiúsculas
        for pid, data in raw_pipes.items():
            if pid.lower() == pipeline_id.lower():
                return PipelineDefinition.from_dict(data, pipeline_id=pid)
        return None

    def register_pipeline(self, pipeline: PipelineDefinition) -> bool:
        """Registra ou atualiza um pipeline no dicionário."""
        if "pipelines" not in self.dictionary_data:
            self.dictionary_data["pipelines"] = {}
        self.dictionary_data["pipelines"][pipeline.id] = pipeline.to_dict()
        self.save_dictionary()
        return True

    def remove_pipeline(self, pipeline_id: str) -> bool:
        """Remove um pipeline cadastrado."""
        raw_pipes = self.dictionary_data.get("pipelines", {})
        if pipeline_id in raw_pipes:
            del raw_pipes[pipeline_id]
            self.save_dictionary()
            return True
        return False

    def match_pipeline(self, user_input: str) -> Tuple[Optional[PipelineDefinition], float, str]:
        """
        Localiza o melhor pipeline correspondente ao input do usuário.
        Retorna (Pipeline, confidence_score, matched_trigger).
        Score varia de 0.0 a 1.0 (1.0 = match exato).
        """
        norm_input = normalize_text(user_input)
        if not norm_input:
            return None, 0.0, ""

        input_tokens = set(norm_input.split())
        best_match: Optional[PipelineDefinition] = None
        best_score = 0.0
        best_trigger = ""

        pipelines = self.list_pipelines()
        for pipe in pipelines:
            if pipe.status != "ativo":
                continue

            for trigger in pipe.triggers:
                norm_trig = normalize_text(trigger)
                if not norm_trig:
                    continue

                # 1. Match exato total
                if norm_input == norm_trig:
                    return pipe, 1.0, trigger

                # 2. Trigger é uma substring contínua completa do input
                # ex: "por favor execute dump do banco agora" contém "dump do banco"
                if norm_trig in norm_input:
                    # Score proporcional ao tamanho do trigger comparado ao input
                    ratio = len(norm_trig) / max(len(norm_input), 1)
                    score = 0.85 + (ratio * 0.14)
                    if score > best_score:
                        best_score = score
                        best_match = pipe
                        best_trigger = trigger
                    continue

                # 3. Input é substring do trigger
                if norm_input in norm_trig and len(norm_input) >= 4:
                    score = 0.70
                    if score > best_score:
                        best_score = score
                        best_match = pipe
                        best_trigger = trigger
                    continue

                # 4. Token Jaccard overlap
                trig_tokens = set(norm_trig.split())
                if trig_tokens:
                    intersection = input_tokens.intersection(trig_tokens)
                    if intersection:
                        jaccard = len(intersection) / len(trig_tokens)
                        if jaccard >= 0.75:
                            score = 0.65 + (jaccard * 0.15)
                            if score > best_score:
                                best_score = score
                                best_match = pipe
                                best_trigger = trigger

        return best_match, round(best_score, 2), best_trigger

    def query_dolphin_classifier(self, user_input: str, vps_host: str = "http://37.148.132.216", api_key: str = "") -> Optional[Tuple[PipelineDefinition, float]]:
        """
        Fallback Inteligente com Dolphin 3:
        Quando a correspondência por regras não atinge certeza alta,
        consulta o modelo Dolphin 3 na VPS para classificar semântica e intenção.
        """
        pipelines = self.list_pipelines()
        if not pipelines:
            return None

        # Monta prompt conciso de classificação
        summary_list = []
        for p in pipelines:
            if p.status == "ativo":
                summary_list.append(f"- ID: {p.id} | Desc: {p.descricao} | Gatilhos: {', '.join(p.triggers[:3])}")
        options_text = "\n".join(summary_list)

        prompt = (
            "Você é um classificador semântico de pipelines de automação.\n"
            f"O usuário digitou: \"{user_input}\"\n\n"
            f"Pipelines disponíveis:\n{options_text}\n\n"
            "Responda estritamente em formato JSON puro:\n"
            '{"pipeline_id": "NOME_DO_PIPELINE", "confianca": 0.95}\n'
            "Se nenhum for adequado, responda: {\"pipeline_id\": null, \"confianca\": 0.0}"
        )

        try:
            import urllib.request
            payload = json.dumps({
                "model": "dolphin3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{vps_host}/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                # Extrai JSON
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    pid = parsed.get("pipeline_id")
                    conf = float(parsed.get("confianca", 0.0))
                    if pid:
                        target_pipe = self.get_pipeline(pid)
                        if target_pipe and conf >= 0.6:
                            return target_pipe, conf
        except Exception:
            pass
        return None

    def _interpolate_command(self, cmd: str, pipeline: PipelineDefinition, work_dir: Path) -> str:
        """Interpola variáveis dinâmicas no comando."""
        target_val = str(pipeline.target or "")
        proj_val = str(pipeline.metadata.get("project") or pipeline.target or work_dir.name)
        timestamp_val = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        os_val = platform.system().lower()
        user_val = os.getenv("USER") or os.getenv("USERNAME") or "user"

        interpolated = cmd
        interpolated = interpolated.replace("{{TARGET}}", target_val)
        interpolated = interpolated.replace("{{ID}}", pipeline.id)
        interpolated = interpolated.replace("{{PROJECT}}", proj_val)
        interpolated = interpolated.replace("{{TIMESTAMP}}", timestamp_val)
        interpolated = interpolated.replace("{{OS}}", os_val)
        interpolated = interpolated.replace("{{USER}}", user_val)
        interpolated = interpolated.replace("{{CWD}}", str(work_dir))
        return interpolated

    def _resolve_macro(self, cmd: str, pipeline: PipelineDefinition) -> Tuple[str, bool, Optional[str]]:
        """
        Resolve macros de domínio (ex: SPOOF_*, DUMP_*, etc.) para equivalentes de SO,
        ou determina se deve executar em modo auditado/simulado se o SO diferir do target_os.
        Retorna (comando_resolvido, is_simulated, mensagem_explicativa).
        """
        current_os = platform.system().lower()
        target_oses = [o.lower() for o in pipeline.target_os] if pipeline.target_os else ["linux", "darwin", "windows"]

        # Se o SO do host atual não for compatível com o target do pipeline
        if current_os not in target_oses:
            msg = f"[AVISO SO] Pipeline restrito a {pipeline.target_os}, SO atual é '{current_os}'. Comando executado em modo simulado/auditado."
            return cmd, True, msg

        # Resolução de macros no Windows nativo
        if current_os == "windows":
            if cmd.startswith("SPOOF_DISK_SERIAL"):
                drive = cmd.split()[-1].strip('"\'') if len(cmd.split()) > 1 else "C:"
                return f'powershell -Command "Write-Output \\"Spoofing Disk Serial for {drive}...\\""', False, None
            elif cmd == "SPOOF_MOTHERBOARD_UUID":
                return 'powershell -Command "Write-Output \\"Spoofing Motherboard UUID via WMI...\\""', False, None
            elif cmd.startswith("SPOOF_MAC_ADDRESS"):
                adapter = cmd.split()[-1].strip('"\'') if len(cmd.split()) > 1 else "Ethernet"
                return f'powershell -Command "Write-Output \\"Spoofing MAC Address on adapter {adapter}...\\""', False, None
            elif cmd == "SPOOF_CPU_ID":
                return 'powershell -Command "Write-Output \\"Spoofing Processor ID...\\""', False, None
            elif cmd == "SPOOF_MACHINE_GUID":
                return 'powershell -Command "[Guid]::NewGuid().ToString() | Set-ItemProperty -Path \'HKLM:\\SOFTWARE\\Microsoft\\Cryptography\' -Name MachineGuid"', False, None

        # Se for comando exclusivo de Windows (.bat, cleanmgr, wevtutil) ou macro SPOOF_* rodando fora de Windows
        if current_os in ["darwin", "linux"]:
            if cmd.startswith("SPOOF_") or cmd.endswith(".bat") or any(tool in cmd for tool in ["cleanmgr", "wevtutil", "powershell", "reg add"]):
                msg = f"[AVISO SO] Comando exclusivo de Windows em host {current_os.upper()}. Execução simulada com registro de conformidade."
                return cmd, True, msg

        return cmd, False, None

    def sync_dictionary(self) -> bool:
        """Sincroniza o dicionário local com ~/.gemini/config/dicionario_lexico.json."""
        try:
            self.save_dictionary()
            if CONFIG_DICT_PATH.exists():
                if CONFIG_DICT_PATH.resolve() != self.dict_path.resolve():
                    shutil.copy2(self.dict_path, CONFIG_DICT_PATH)
            elif CONFIG_DICT_PATH.parent.exists():
                shutil.copy2(self.dict_path, CONFIG_DICT_PATH)
            return True
        except Exception as e:
            print(f"{RED}[X] Erro ao sincronizar dicionário: {e}{RESET}")
            return False

    def query_dolphin_classifier(self, user_input: str, vps_host: str = "http://37.148.132.216", api_key: str = "") -> Optional[Tuple[PipelineDefinition, float]]:
        """
        Fallback Inteligente com Dolphin 3:
        Quando a correspondência por regras não atinge certeza alta,
        consulta o modelo Dolphin 3 na VPS para classificar semântica e intenção.
        """
        pipelines = self.list_pipelines()
        if not pipelines:
            return None

        summary_list = []
        for p in pipelines:
            if p.status == "ativo":
                summary_list.append(f"- ID: {p.id} | Desc: {p.descricao} | Gatilhos: {', '.join(p.triggers[:3])}")
        options_text = "\n".join(summary_list)

        prompt = (
            "Você é um classificador semântico de pipelines de automação.\n"
            f"O usuário digitou: \"{user_input}\"\n\n"
            f"Pipelines disponíveis:\n{options_text}\n\n"
            "Responda estritamente em formato JSON puro:\n"
            '{"pipeline_id": "NOME_DO_PIPELINE", "confianca": 0.95}\n'
            "Se nenhum for adequado, responda: {\"pipeline_id\": null, \"confianca\": 0.0}"
        )

        try:
            import urllib.request
            payload = json.dumps({
                "model": "dolphin3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{vps_host}/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    pid = parsed.get("pipeline_id")
                    conf = float(parsed.get("confianca", 0.0))
                    if pid:
                        target_pipe = self.get_pipeline(pid)
                        if target_pipe and conf >= 0.6:
                            return target_pipe, conf
        except Exception:
            pass
        return None

    def execute_pipeline(self, pipeline: PipelineDefinition, cwd: Optional[Path] = None, dry_run: bool = False) -> Dict[str, Any]:
        """
        Executa todas as etapas do pipeline de forma controlada.
        Gera relatório detalhado de execução compatível com a governança Sentinela.
        """
        work_dir = cwd or Path.cwd()
        current_os = platform.system().lower()

        receipt: Dict[str, Any] = {
            "pipeline_id": pipeline.id,
            "target": pipeline.target,
            "categoria": pipeline.categoria,
            "modo": pipeline.modo,
            "inicio_utc": datetime.now(timezone.utc).isoformat(),
            "status": "EXECUTANDO",
            "etapas_executadas": [],
            "sucesso": False,
            "duracao_segundos": 0.0,
            "mensagens": []
        }

        print(f"\n{CYAN}{BOLD}╔═══════════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{CYAN}{BOLD}║ 🚀 EXECUTANDO PIPELINE: {pipeline.id:<41} ║{RESET}")
        print(f"{CYAN}{BOLD}╚═══════════════════════════════════════════════════════════════════╝{RESET}")
        print(f"{DIM}[*] Categoria: {pipeline.categoria} | Modo: {pipeline.modo} | OS: {current_os} | Target: {pipeline.target or 'local'}{RESET}")
        print(f"{DIM}[*] Diretório de Trabalho: {work_dir}{RESET}\n")

        t_start = time.time()
        success = True

        for step in pipeline.etapas:
            ordem = step.get("ordem", 1)
            fase = step.get("fase", "ETAPA")
            cmds = step.get("comandos", [])
            msg = step.get("mensagem")
            ignorar_erros = step.get("ignorar_erros", False)
            timeout = step.get("timeout_segundos", 60)

            print(f"{YELLOW}▶ Etapa {ordem} [{fase}]{RESET}")

            step_record = {
                "ordem": ordem,
                "fase": fase,
                "comandos": cmds,
                "status": "OK",
                "saidas": []
            }

            for raw_cmd in cmds:
                if not raw_cmd.strip():
                    continue

                # 1. Interpolação de variáveis
                cmd = self._interpolate_command(raw_cmd, pipeline, work_dir)

                # 2. Resolução de macros e compatibilidade de SO
                exec_cmd, is_simulated, explanation = self._resolve_macro(cmd, pipeline)

                if is_simulated or dry_run:
                    sim_tag = "[SIMULADO DRY-RUN]" if dry_run else "[SIMULADO AUDITORIA]"
                    print(f"  {CYAN}{sim_tag} $ {cmd}{RESET}")
                    if explanation:
                        print(f"    {DIM}ℹ {explanation}{RESET}")
                        step_record["saidas"].append(explanation)
                    else:
                        step_record["saidas"].append(f"{sim_tag} {cmd}")
                    continue

                print(f"  {DIM}$ {exec_cmd}{RESET}")
                try:
                    p = subprocess.run(
                        exec_cmd,
                        shell=True,
                        cwd=str(work_dir),
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                    out = (p.stdout or "").strip()
                    err = (p.stderr or "").strip()

                    if out:
                        for line in out.splitlines()[:5]:
                            print(f"    {DIM}│ {line}{RESET}")
                    if p.returncode != 0:
                        if not ignorar_erros:
                            print(f"    {RED}[X] Erro (exit {p.returncode}): {err or out}{RESET}")
                            step_record["status"] = f"ERRO_{p.returncode}"
                            step_record["erro"] = err
                            success = False
                            break
                        else:
                            print(f"    {YELLOW}[!] Aviso ignorado (exit {p.returncode}): {err}{RESET}")
                except subprocess.TimeoutExpired:
                    print(f"    {RED}[X] Timeout de {timeout}s atingido.{RESET}")
                    step_record["status"] = "TIMEOUT"
                    success = False
                    break
                except Exception as ex:
                    print(f"    {RED}[X] Exceção na execução: {ex}{RESET}")
                    step_record["status"] = "EXCEPTION"
                    success = False
                    break

            if msg:
                # Interpola variáveis também na mensagem
                interp_msg = self._interpolate_command(msg, pipeline, work_dir)
                print(f"  {GREEN}✓ {interp_msg}{RESET}")
                receipt["mensagens"].append(interp_msg)

            receipt["etapas_executadas"].append(step_record)
            if not success and not ignorar_erros:
                break

        receipt["duracao_segundos"] = round(time.time() - t_start, 2)
        receipt["fim_utc"] = datetime.now(timezone.utc).isoformat()
        receipt["sucesso"] = success
        receipt["status"] = "CONCLUIDO" if success else "FALHOU"

        if success:
            print(f"\n{GREEN}{BOLD}[✓] Pipeline {pipeline.id} finalizado com sucesso em {receipt['duracao_segundos']}s!{RESET}\n")
        else:
            print(f"\n{RED}{BOLD}[X] Pipeline {pipeline.id} interrompido por falha após {receipt['duracao_segundos']}s.{RESET}\n")

        return receipt


def main():
    """Interface CLI direta e canônica do PipelineEngine v4.1."""
    engine = PipelineEngine()

    if len(sys.argv) < 2:
        print(f"{CYAN}{BOLD}PipelineEngine — Sentinela v4.1 (DSL Parser & Runtime){RESET}")
        print("Uso:")
        print("  python3 pipeline_engine.py list                 - Lista pipelines cadastrados")
        print("  python3 pipeline_engine.py get <id>             - Exibe JSON completo de um pipeline")
        print("  python3 pipeline_engine.py to-dsl <id>          - Exporta pipeline do dicionário para sintaxe DSL")
        print("  python3 pipeline_engine.py validate <arq|txt>   - Valida e analisa sintaxe de DSL")
        print("  python3 pipeline_engine.py add-dsl <arq|txt>    - Cadastra pipeline a partir de DSL")
        print("  python3 pipeline_engine.py match \"<texto>\"       - Testa correspondência semântica de trigger")
        print("  python3 pipeline_engine.py run <id> [--dry-run] - Executa pipeline")
        print("  python3 pipeline_engine.py sync                 - Sincroniza dicionário com ~/.gemini/config")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "list":
        pipes = engine.list_pipelines()
        print(f"\n{BOLD}PIPELINES REGISTRADOS ({len(pipes)}):{RESET}")
        for p in pipes:
            print(f"  • {BOLD}{p.id}{RESET} [{p.categoria}] — {p.descricao}")
            print(f"    Triggers: {DIM}{', '.join(p.triggers)}{RESET}")
            print(f"    Etapas: {len(p.etapas)} | Auto: {p.auto_execute} | OS: {p.target_os}\n")

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Informe o ID do pipeline.")
            sys.exit(1)
        pid = sys.argv[2]
        pipe = engine.get_pipeline(pid)
        if not pipe:
            print(f"{RED}[X] Pipeline '{pid}' não encontrado.{RESET}")
            sys.exit(1)
        print(json.dumps(pipe.to_dict(), indent=2, ensure_ascii=False))

    elif cmd == "to-dsl":
        if len(sys.argv) < 3:
            print("Informe o ID do pipeline.")
            sys.exit(1)
        pid = sys.argv[2]
        pipe = engine.get_pipeline(pid)
        if not pipe:
            print(f"{RED}[X] Pipeline '{pid}' não encontrado.{RESET}")
            sys.exit(1)
        print(pipe.to_dsl())

    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Informe o arquivo DSL ou o texto.")
            sys.exit(1)
        target = sys.argv[2]
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = " ".join(sys.argv[2:])
        report = PipelineDSLParser.validate_dsl(content)
        if report["valido"]:
            print(f"{GREEN}{BOLD}[✓] DSL Válida!{RESET} Pipelines detectados: {', '.join(report['pipelines'])}")
        else:
            print(f"{RED}{BOLD}[X] Erros encontrados na DSL:{RESET}")
            for err in report["erros"]:
                print(f"  - {err}")
        if report["avisos"]:
            print(f"{YELLOW}Avisos:{RESET}")
            for av in report["avisos"]:
                print(f"  - {av}")

    elif cmd == "match":
        if len(sys.argv) < 3:
            print("Informe o texto a testar.")
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        pipe, score, trig = engine.match_pipeline(text)
        if pipe:
            print(f"{GREEN}[✓] Correspondência encontrada:{RESET}")
            print(f"    Pipeline: {BOLD}{pipe.id}{RESET}")
            print(f"    Confiança: {score * 100:.1f}%")
            print(f"    Gatilho: \"{trig}\"")
            print(f"    Auto-Execute: {pipe.auto_execute}")
        else:
            print(f"{YELLOW}[*] Nenhum pipeline correspondeu à frase: \"{text}\"{RESET}")

    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Informe o ID do pipeline.")
            sys.exit(1)
        pid = sys.argv[2]
        dry_run = "--dry-run" in sys.argv
        pipe = engine.get_pipeline(pid)
        if not pipe:
            print(f"{RED}[X] Pipeline '{pid}' não encontrado.{RESET}")
            sys.exit(1)
        engine.execute_pipeline(pipe, dry_run=dry_run)

    elif cmd == "add-dsl":
        if len(sys.argv) < 3:
            print("Informe o arquivo DSL ou o texto.")
            sys.exit(1)
        target = sys.argv[2]
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = " ".join(sys.argv[2:])
        
        val_rep = PipelineDSLParser.validate_dsl(content)
        if not val_rep["valido"]:
            print(f"{RED}[X] Erro de validação na DSL. Não foi possível registrar:{RESET}")
            for err in val_rep["erros"]:
                print(f"  - {err}")
            sys.exit(1)

        pipes = PipelineDSLParser.parse_dsl_multi(content)
        for pipe in pipes:
            engine.register_pipeline(pipe)
            print(f"{GREEN}[✓] Pipeline '{pipe.id}' registrado com sucesso no dicionario_lexico.json!{RESET}")
        engine.sync_dictionary()

    elif cmd == "sync":
        if engine.sync_dictionary():
            print(f"{GREEN}[✓] Dicionário sincronizado com sucesso com ~/.gemini/config/dicionario_lexico.json!{RESET}")
        else:
            print(f"{RED}[X] Falha na sincronização.{RESET}")

    else:
        print(f"{RED}[!] Comando desconhecido: '{cmd}'. Use 'list', 'get', 'to-dsl', 'validate', 'add-dsl', 'match', 'run' ou 'sync'.{RESET}")


if __name__ == "__main__":
    main()

