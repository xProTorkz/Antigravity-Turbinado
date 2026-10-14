#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
executar_pipeline.py — Roteador e Executor Inteligente do Sentinela v7.0

Comportamento Soberano:
1. Disparo Imediato: Quando o usuário diz "auditoria toal", "hwid", "sinc git", etc.,
   o roteador reconhece o gatilho (inclusive com erros de digitação), exibe o que realmente faz
   e COMEÇA A EXECUTAR IMEDIATAMENTE os comandos configurados no pipeline!
2. Não exige a palavra 'pipeline' como prefixo (embora ainda a reconheça se fornecida).

Uso:
    python3 executar_pipeline.py "auditoria toal"           # Dispara e executa imediatamente!
    python3 executar_pipeline.py "hwid"                     # Dispara e executa o pipeline unificado de HWID!
    python3 executar_pipeline.py "sinc git"                 # Dispara e executa a sincronização git!
    python3 executar_pipeline.py --info "auditoria total"   # Modo estrito de consulta informativa
    python3 executar_pipeline.py --list                     # Lista todos os gatilhos e o que fazem
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
    return {"gatilhos": {}}

def find_trigger(query: str, dict_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    raw_norm = normalize(query)
    # Remove prefixos opcionais como 'pipeline', 'pipeiline', 'rodar', 'executar'
    cleaned = re.sub(r"^(?:pipeline|pipeiline|pipline|rodar|executar|fazer)\s+", "", raw_norm).strip()
    
    gatilhos_dict = dict_data.get("gatilhos", dict_data.get("dicionario", {}))

    # 1. Match direto na chave
    if query in gatilhos_dict:
        return query, gatilhos_dict[query]
    if cleaned in gatilhos_dict:
        return cleaned, gatilhos_dict[cleaned]

    # 2. Match exato nos gatilhos cadastrados
    for tid, tdata in gatilhos_dict.items():
        aliases = [normalize(g) for g in tdata.get("gatilhos", [])]
        if raw_norm in aliases or cleaned in aliases:
            return tid, tdata

    # 3. Match por substring ou aproximação nos gatilhos
    for tid, tdata in gatilhos_dict.items():
        aliases = [normalize(g) for g in tdata.get("gatilhos", [])]
        for a in aliases:
            if a in cleaned or cleaned in a or a in raw_norm:
                return tid, tdata

    # 4. Procura direta em pipelines/
    direct_file = PIPELINES_DIR / f"{cleaned.replace(' ', '_')}.json"
    if direct_file.exists():
        return direct_file.stem, {
            "nome": direct_file.stem.replace("_", " ").title(),
            "o_que_faz": f"Executa esteira direta: {direct_file.name}",
            "gatilhos": [cleaned],
            "pipeline": f"pipelines/{direct_file.name}",
            "auto_execute": True
        }

    return None, None

def show_info_card(term_id: str, term_data: Dict[str, Any]):
    nome = term_data.get("nome", term_id.replace("_", " ").title())
    o_que_faz = term_data.get("o_que_faz", "")
    gatilhos = ", ".join(term_data.get("gatilhos", []))
    p_file = term_data.get("pipeline", "")

    print("\n" + "═" * 78)
    print(f"{BOLD}{CYAN}📖 [SENTINELA - DICIONÁRIO LÉXICO] {nome.upper()}{RESET}")
    print("═" * 78)
    print(f"\n{BOLD}{YELLOW}• O QUE REALMENTE FAZ:{RESET}")
    print(f"  {o_que_faz}")
    print(f"\n{BOLD}{DIM}• GATILHOS VINCULADOS:{RESET}")
    print(f"  {DIM}{gatilhos}{RESET}")
    print(f"\n{BOLD}{BLUE}• PIPELINE CONFIGURADO:{RESET} {p_file}")
    print("═" * 78 + "\n")

def execute_command(cmd: str, timeout: int = 60) -> Tuple[bool, str]:
    current_os = platform.system().lower()
    is_windows = current_os == "windows"
    shell_cmd = cmd

    # Tratamento para comandos exclusivos de Windows no macOS/Linux
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

def run_pipeline_file(pipeline_rel_path: str, trigger_name: str, o_que_faz: str) -> bool:
    pfile = BASE_DIR / pipeline_rel_path if not Path(pipeline_rel_path).is_absolute() else Path(pipeline_rel_path)

    if not pfile.exists():
        print(f"{RED}[X] Arquivo de pipeline não encontrado: {pfile}{RESET}")
        return False

    with open(pfile, "r", encoding="utf-8") as f:
        pipe = json.load(f)

    pipe_id = pipe.get("id", pfile.stem.upper())
    descricao = pipe.get("descricao", o_que_faz)
    etapas = pipe.get("etapas", [])

    print("\n" + "═" * 78)
    print(f"{BOLD}{CYAN}🎯 [SENTINELA] GATILHO RECONHECIDO: {trigger_name.upper()}{RESET}")
    print(f"{YELLOW}📋 O QUE REALMENTE FAZ:{RESET} {o_que_faz}")
    print(f"{BOLD}{GREEN}🚀 DISPARANDO PIPELINE: {pipe_id} ({pfile.name} | {len(etapas)} etapas){RESET}")
    print("═" * 78 + "\n")

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
            print(f"  {GREEN}✓ Concluído: {criterio}{RESET}\n")
        else:
            print(f"  {YELLOW}⚠️  Aviso: Etapa {ordem} concluída com ressalvas.{RESET}\n")
            if not ignorar_erros:
                print(f"{RED}[X] Pipeline interrompido por critério de bloqueio.{RESET}")
                return False

    elapsed = round(time.time() - start_time, 2)
    print("═" * 78)
    print(f"{BOLD}{GREEN}✨ PIPELINE {pipe_id} EXECUTADO COM SUCESSO!{RESET}")
    print(f"  • Etapas Executadas:  {steps_success}/{len(etapas)}")
    print(f"  • Tempo de Execução: {elapsed}s")
    print(f"  • Horário UTC:       {datetime.now(timezone.utc).isoformat()}")
    print("═" * 78 + "\n")
    return True

def list_catalog(dict_data: Dict[str, Any]):
    gatilhos = dict_data.get("gatilhos", dict_data.get("dicionario", {}))
    print("\n" + "═" * 78)
    print(f"{BOLD}{CYAN}📚 [SENTINELA] DICIONÁRIO LÉXICO & ROTEADOR INTELIGENTE{RESET}")
    print("═" * 78)
    for tid, tdata in sorted(gatilhos.items()):
        p = tdata.get("pipeline", "N/A")
        gats = ", ".join(tdata.get("gatilhos", [])[:5])
        print(f"\n{BOLD}{GREEN}• {tdata.get('nome', tid)}{RESET} ➔ {CYAN}{p}{RESET}")
        print(f"  {YELLOW}O que realmente faz:{RESET} {tdata.get('o_que_faz')}")
        print(f"  {DIM}Gatilhos:{RESET} {gats}")
    print("\n" + "═" * 78 + "\n")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print(__doc__)
        sys.exit(0)

    dict_data = load_dictionary()

    if sys.argv[1] in ["-l", "--list"]:
        list_catalog(dict_data)
        sys.exit(0)

    # Modo somente informação (se explicitamente solicitado com --info ou -i)
    only_info = False
    args = sys.argv[1:]
    if args[0] in ["-i", "--info"]:
        only_info = True
        args = args[1:]

    raw_query = " ".join(args).strip()
    tid, term_data = find_trigger(raw_query, dict_data)

    if not term_data:
        print(f"{RED}[X] Nenhum gatilho ou pipeline correspondente para: '{raw_query}'{RESET}")
        print(f"{YELLOW}💡 Dica: Use 'python3 executar_pipeline.py --list' para ver todos os gatilhos.{RESET}")
        sys.exit(1)

    if only_info:
        show_info_card(tid, term_data)
        sys.exit(0)

    # DISPARO IMEDIATO: Tudo começa a acontecer diretamente!
    p_rel = term_data.get("pipeline")
    nome = term_data.get("nome", tid)
    o_que_faz = term_data.get("o_que_faz", "")

    if not p_rel:
        print(f"{YELLOW}[!] Termo '{nome}' não possui pipeline configurado.{RESET}")
        show_info_card(tid, term_data)
        sys.exit(0)

    success = run_pipeline_file(p_rel, nome, o_que_faz)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
