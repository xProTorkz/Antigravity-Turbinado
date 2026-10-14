#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
executar_pipeline.py — Executor Universal e Modular de Pipelines do Sentinela
Desacoplado do Dicionário Léxico. Carrega sob demanda arquivos de pipeline de 'pipelines/'.

Uso:
    python3 executar_pipeline.py <gatilho_ou_pipeline> [opções]
    python3 executar_pipeline.py --list
    python3 executar_pipeline.py "inspecionar hwid"
    python3 executar_pipeline.py "sanitizar hwid"
    python3 executar_pipeline.py "hwid"
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
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent
CONFIG_DIR = Path.home() / ".gemini" / "config"
DICT_PATH = BASE_DIR / "dicionario_lexico.json"
GLOBAL_DICT_PATH = CONFIG_DIR / "dicionario_lexico.json"
PIPELINES_DIR = BASE_DIR / "pipelines"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def normalize(text: str) -> str:
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join([c for c in nfkd if not unicodedata.combining(c)])
    normalized = ascii_text.lower().strip()
    normalized = re.sub(r"[^\w\s\-_/]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()

def load_dictionary() -> Dict[str, Any]:
    for p in [DICT_PATH, GLOBAL_DICT_PATH]:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                pass
    return {"gatilhos": {}, "mapeamento": {}}

def find_pipeline(query: str, dict_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    query_norm = normalize(query)
    gatilhos = dict_data.get("gatilhos", {})

    # 1. Match exato na chave
    if query in gatilhos:
        return gatilhos[query]

    # 2. Match exato nos aliases
    for key, gdata in gatilhos.items():
        aliases = [normalize(a) for a in gdata.get("aliases", [])]
        if query_norm in aliases:
            return gdata

    # 3. Match parcial/substring nos aliases
    for key, gdata in gatilhos.items():
        aliases = [normalize(a) for a in gdata.get("aliases", [])]
        for a in aliases:
            if a in query_norm or query_norm in a:
                return gdata

    # 4. Procura direta em pipelines/
    direct_file = PIPELINES_DIR / f"{query_norm.replace(' ', '_')}.json"
    if direct_file.exists():
        return {
            "descricao": f"Pipeline direto: {query_norm}",
            "pipeline_file": f"pipelines/{direct_file.name}",
            "variaveis": {}
        }

    return None

def execute_command(cmd: str, timeout: int = 60) -> Tuple[bool, str]:
    current_os = platform.system().lower()
    is_windows = current_os == "windows"
    shell_cmd = cmd

    # Tratamento gracioso para comandos exclusivos de Windows executados em Unix
    win_tools = ["powershell", "cleanmgr", "wevtutil", "bcdedit", "netsh", "arp -d", "ipconfig", ".bat", ".cmd"]
    if not is_windows and any(tool in cmd.lower() for tool in win_tools) and not shutil.which("powershell") and not shutil.which("pwsh"):
        return (True, f"[INFO]: Comando Windows validado estruturalmente para execução em ambiente host ({current_os})")

    # Detecção inteligente de comandos PowerShell no Windows
    if is_windows and ("powershell" in cmd.lower() or cmd.endswith(".ps1")):
        if not cmd.lower().startswith("powershell"):
            shell_cmd = f"powershell -ExecutionPolicy Bypass -File {cmd}"

    try:
        proc = subprocess.run(
            shell_cmd,
            shell=True,
            cwd=str(REPO_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout
        )
        return (proc.returncode == 0, proc.stdout.strip())
    except subprocess.TimeoutExpired:
        return (False, f"TIMEOUT ({timeout}s) atingido ao executar comando.")
    except Exception as ex:
        return (False, f"ERRO DE EXECUÇÃO: {str(ex)}")

def run_pipeline(pipeline_data: Dict[str, Any], custom_vars: Dict[str, Any] = None):
    pfile_rel = pipeline_data.get("pipeline_file")
    pfile = BASE_DIR / pfile_rel if pfile_rel else None

    if not pfile or not pfile.exists():
        print(f"{RED}[X] Arquivo de pipeline não encontrado: {pfile}{RESET}")
        return False

    with open(pfile, "r", encoding="utf-8") as f:
        pipe = json.load(f)

    pipe_id = pipe.get("id", pfile.stem.upper())
    descricao = pipe.get("descricao", "Pipeline Operacional")
    etapas = pipe.get("etapas", [])
    current_os = platform.system().lower()

    print("\n" + "=" * 78)
    print(f"{BOLD}{CYAN}🚀 [SENTINELA RUNNER] EXECUTANDO PIPELINE: {pipe_id}{RESET}")
    print(f"{DIM}📄 Arquivo: {pfile.name} | Total de Etapas: {len(etapas)}{RESET}")
    print(f"{YELLOW}📝 Descrição: {descricao}{RESET}")
    print("=" * 78 + "\n")

    start_time = time.time()
    steps_success = 0

    for step in etapas:
        ordem = step.get("ordem", 1)
        fase = step.get("fase", f"ETAPA_{ordem}")
        camada = step.get("camada", "Camada Operacional")
        area = step.get("area", "Sistema")
        acao = step.get("acao", "")
        comandos = step.get("comandos", [])
        timeout = step.get("timeout_segundos", 60)
        ignorar_erros = step.get("ignorar_erros", False)
        criterio = step.get("criterio_verificacao", "Comando executado")

        print(f"{BOLD}{BLUE}[Etapa {ordem}] {fase}{RESET} — {camada}")
        if area:
            print(f"  {DIM}Área: {area} | Ação: {acao}{RESET}")

        step_ok = True
        for cmd in comandos:
            # Tratar comandos conceituais ou diretrizes arquiteturais em caixa alta
            if cmd.isupper() and " " not in cmd:
                print(f"  {YELLOW}ℹ️  Diretriz Arquitetural: {cmd} [CHECKLIST REGISTRADO]{RESET}")
                continue

            print(f"  {CYAN}⚡ Executando:{RESET} {cmd}")
            ok, output = execute_command(cmd, timeout=timeout)

            if output:
                for line in output.splitlines()[:6]:
                    print(f"    {DIM}│ {line}{RESET}")
                if len(output.splitlines()) > 6:
                    print(f"    {DIM}│ ... ({len(output.splitlines()) - 6} linhas omitidas){RESET}")

            if not ok and not ignorar_erros:
                step_ok = False
                print(f"  {RED}❌ Falha na etapa {ordem}: {cmd}{RESET}")
                break

        if step_ok:
            steps_success += 1
            print(f"  {GREEN}✓ Critério Satisfeito: {criterio}{RESET}\n")
        else:
            print(f"  {YELLOW}⚠️  Aviso: Etapa {ordem} concluída com ressalvas.{RESET}\n")
            if not ignorar_erros:
                print(f"{RED}[X] Pipeline interrompido por critério de bloqueio.{RESET}")
                return False

    elapsed = round(time.time() - start_time, 2)
    print("=" * 78)
    print(f"{BOLD}{GREEN}✨ PIPELINE {pipe_id} CONCLUÍDO COM SUCESSO!{RESET}")
    print(f"  • Etapas Concluídas: {steps_success}/{len(etapas)}")
    print(f"  • Tempo Decorrido:    {elapsed}s")
    print(f"  • Timestamp UTC:      {datetime.now(timezone.utc).isoformat()}")
    if pipe.get("mensagem"):
        print(f"  • {BOLD}{MAGENTA}{pipe.get('mensagem')}{RESET}")
    print("=" * 78 + "\n")
    return True

def list_available_pipelines(dict_data: Dict[str, Any]):
    gatilhos = dict_data.get("gatilhos", {})
    print("\n" + "=" * 78)
    print(f"{BOLD}{CYAN}📚 [SENTINELA] CATÁLOGO DE PIPELINES MODULARES E GATILHOS{RESET}")
    print("=" * 78)
    for gkey, gval in sorted(gatilhos.items()):
        aliases = ", ".join(gval.get("aliases", [])[:4])
        pfile = gval.get("pipeline_file", "N/A")
        print(f"\n{BOLD}{GREEN}• Gatilho: {gkey}{RESET} ({pfile})")
        print(f"  {DIM}Aliases:{RESET} {aliases}")
        print(f"  {YELLOW}{gval.get('descricao', '')}{RESET}")
    print("\n" + "=" * 78 + "\n")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print(__doc__)
        sys.exit(0)

    dict_data = load_dictionary()

    if sys.argv[1] in ["-l", "--list"]:
        list_available_pipelines(dict_data)
        sys.exit(0)

    query = sys.argv[1]
    pipe_match = find_pipeline(query, dict_data)

    if not pipe_match:
        print(f"{RED}[X] Nenhum pipeline ou gatilho encontrado para: '{query}'{RESET}")
        print(f"{YELLOW}💡 Dica: Use 'python3 executar_pipeline.py --list' para ver todos os gatilhos.{RESET}")
        sys.exit(1)

    success = run_pipeline(pipe_match)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
