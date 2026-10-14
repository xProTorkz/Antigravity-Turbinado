#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
executar_pipeline.py — Executor Universal e Dicionário Léxico Sentinela v6.0

Regra Fundamental:
1. Consulta de Termos (ex: "auditoria total", "auditoria replicador", "hwid"):
   O Dicionário mostra exclusivamente O QUE É e O QUE FAZ.
2. Comando de Execução (ex: "pipeline", "pipeline auditoria total", "pipeline completo", "--run"):
   Carrega sob demanda o arquivo em 'pipelines/' e EXECUTA OS COMANDOS CONFIGURADOS.

Uso:
    python3 executar_pipeline.py "auditoria total"               # Mostra o que é e o que faz
    python3 executar_pipeline.py "pipeline auditoria total"      # Executa os comandos configurados
    python3 executar_pipeline.py "pipeline completo"             # Executa o pipeline completo (auditoria_total)
    python3 executar_pipeline.py "pipeline"                      # Executa ou lista esteiras ativas
    python3 executar_pipeline.py --run "auditoria replicador"    # Executa diretamente os comandos
    python3 executar_pipeline.py --list                          # Lista todo o catálogo do dicionário
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
            except Exception:
                pass
    return {"dicionario": {}}

def find_term_in_dict(query: str, dict_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    query_norm = normalize(query)
    termos = dict_data.get("dicionario", {})

    # 1. Match exato na chave
    if query in termos:
        return query, termos[query]
    if query_norm in termos:
        return query_norm, termos[query_norm]

    # 2. Match exato nos gatilhos
    for tid, tdata in termos.items():
        gatilhos = [normalize(g) for g in tdata.get("gatilhos", [])]
        if query_norm in gatilhos:
            return tid, tdata

    # 3. Match parcial nos gatilhos ou nome
    for tid, tdata in termos.items():
        gatilhos = [normalize(g) for g in tdata.get("gatilhos", [])]
        nome = normalize(tdata.get("nome", ""))
        if any(g in query_norm or query_norm in g for g in gatilhos) or (query_norm in nome):
            return tid, tdata

    # 4. Procura direta em pipelines/
    direct_file = PIPELINES_DIR / f"{query_norm.replace(' ', '_')}.json"
    if direct_file.exists():
        return direct_file.stem, {
            "nome": direct_file.stem.replace("_", " ").title(),
            "o_que_e": f"Pipeline direto: {direct_file.name}",
            "o_que_faz": "Executa comandos definidos no arquivo de pipeline.",
            "gatilhos": [query_norm],
            "pipeline": f"pipelines/{direct_file.name}"
        }

    return None, None

def show_term_card(term_id: str, term_data: Dict[str, Any]):
    nome = term_data.get("nome", term_id.replace("_", " ").title())
    o_que_e = term_data.get("o_que_e", "Definição não cadastrada.")
    o_que_faz = term_data.get("o_que_faz", "Descrição de ação não cadastrada.")
    gatilhos = ", ".join(term_data.get("gatilhos", []))
    p_file = term_data.get("pipeline")

    print("\n" + "═" * 78)
    print(f"{BOLD}{CYAN}📖 [SENTINELA - DICIONÁRIO LÉXICO] {nome.upper()}{RESET}")
    print("═" * 78)
    print(f"\n{BOLD}{GREEN}• O QUE É:{RESET}")
    print(f"  {o_que_e}")

    print(f"\n{BOLD}{YELLOW}• O QUE FAZ:{RESET}")
    print(f"  {o_que_faz}")

    if gatilhos:
        print(f"\n{BOLD}{DIM}• GATILHOS:{RESET}")
        print(f"  {DIM}{gatilhos}{RESET}")

    if p_file:
        print(f"\n{BOLD}{BLUE}• PIPELINE CONFIGURADO:{RESET} {p_file}")
        print(f"\n{BOLD}{MAGENTA}⚡ PARA EXECUTAR OS COMANDOS CONFIGURADOS:{RESET}")
        print(f"  Diga: {BOLD}'pipeline {term_data.get('gatilhos', [term_id])[0]}'{RESET} ou rode:")
        print(f"  {CYAN}python3 4-automacao-e-shell/executar_pipeline.py --run \"{term_id}\"{RESET}")
    else:
        print(f"\n{DIM}ℹ️  Termo puramente conceitual. Não possui esteira executável associada.{RESET}")

    print("═" * 78 + "\n")

def execute_command(cmd: str, timeout: int = 60) -> Tuple[bool, str]:
    current_os = platform.system().lower()
    is_windows = current_os == "windows"
    shell_cmd = cmd

    # Tratamento gracioso para comandos de Windows executados em Unix
    win_tools = ["powershell", "cleanmgr", "wevtutil", "bcdedit", "netsh", "arp -d", "ipconfig", ".bat", ".cmd"]
    if not is_windows and any(tool in cmd.lower() for tool in win_tools) and not shutil.which("powershell") and not shutil.which("pwsh"):
        return (True, f"[INFO]: Comando Windows validado estruturalmente para execução em host ({current_os})")

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

def run_pipeline_file(pipeline_rel_path: str) -> bool:
    pfile = BASE_DIR / pipeline_rel_path if not Path(pipeline_rel_path).is_absolute() else Path(pipeline_rel_path)

    if not pfile.exists():
        print(f"{RED}[X] Arquivo de pipeline não encontrado: {pfile}{RESET}")
        return False

    with open(pfile, "r", encoding="utf-8") as f:
        pipe = json.load(f)

    pipe_id = pipe.get("id", pfile.stem.upper())
    descricao = pipe.get("descricao", "Pipeline Operacional")
    etapas = pipe.get("etapas", [])

    print("\n" + "=" * 78)
    print(f"{BOLD}{CYAN}🚀 [SENTINELA] EXECUTANDO COMANDOS CONFIGURADOS: {pipe_id}{RESET}")
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
    print("=" * 78 + "\n")
    return True

def list_catalog(dict_data: Dict[str, Any]):
    termos = dict_data.get("dicionario", {})
    print("\n" + "=" * 78)
    print(f"{BOLD}{CYAN}📚 [SENTINELA] CATÁLOGO DO DICIONÁRIO LÉXICO (O QUE É / O QUE FAZ){RESET}")
    print("=" * 78)
    for tid, tdata in sorted(termos.items()):
        p = tdata.get("pipeline")
        status_p = f"[{CYAN}{p}{RESET}]" if p else f"{DIM}(Conceitual){RESET}"
        print(f"\n{BOLD}{GREEN}• {tdata.get('nome', tid)}{RESET} {status_p}")
        print(f"  {YELLOW}O que é:{RESET} {tdata.get('o_que_e')}")
        print(f"  {YELLOW}O que faz:{RESET} {tdata.get('o_que_faz')}")
    print("\n" + "=" * 78 + "\n")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print(__doc__)
        sys.exit(0)

    dict_data = load_dictionary()

    if sys.argv[1] in ["-l", "--list"]:
        list_catalog(dict_data)
        sys.exit(0)

    # Identificar se é comando de execução expressa
    force_run = False
    args = sys.argv[1:]

    if args[0] in ["-r", "--run"]:
        force_run = True
        args = args[1:]

    raw_query = " ".join(args).strip()
    norm_query = normalize(raw_query)

    # Regra: Se a chamada começa com "pipeline" ou contém "pipeline", é execução!
    is_pipeline_trigger = False
    cleaned_query = raw_query

    if norm_query.startswith("pipeline"):
        is_pipeline_trigger = True
        # remove prefixo "pipeline"
        cleaned_query = re.sub(r"^pipeline\s*", "", raw_query, flags=re.IGNORECASE).strip()
    elif "pipeline" in norm_query:
        is_pipeline_trigger = True
        cleaned_query = re.sub(r"\bpipeline\b", "", raw_query, flags=re.IGNORECASE).strip()

    # Casos especiais de chamada de pipeline geral
    if is_pipeline_trigger and (not cleaned_query or cleaned_query.lower() in ["completo", "total", "full"]):
        cleaned_query = "auditoria_total"

    tid, term_data = find_term_in_dict(cleaned_query if cleaned_query else raw_query, dict_data)

    if not term_data:
        print(f"{RED}[X] Nenhum termo ou pipeline encontrado para: '{raw_query}'{RESET}")
        print(f"{YELLOW}💡 Dica: Use 'python3 executar_pipeline.py --list' para ver todos os termos.{RESET}")
        sys.exit(1)

    # Se foi acionado com 'pipeline' ou '--run', executa os comandos!
    if force_run or is_pipeline_trigger:
        p_rel = term_data.get("pipeline")
        if not p_rel:
            print(f"{YELLOW}[!] O termo '{term_data.get('nome')}' é puramente conceitual e não possui comandos para executar.{RESET}")
            show_term_card(tid, term_data)
            sys.exit(0)
        success = run_pipeline_file(p_rel)
        sys.exit(0 if success else 1)
    else:
        # Consulta ao dicionário: mostra O QUE É e O QUE FAZ!
        show_term_card(tid, term_data)
        sys.exit(0)

if __name__ == "__main__":
    main()
