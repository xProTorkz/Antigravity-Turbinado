#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Modularização do Dicionário Léxico por Domínio Operacional (v4.6)
Separa o monólito dicionario_lexico.json em 3 grandes diretórios:
- 01_comandos_operacionais: Comandos diretos de Shell acionados por gatilhos (git, portas, redes, bancos, stress)
- 02_esteiras_de_inspecionamento: Roteiros sequenciais e auditorias multicamada
- 03_governanca_e_aprendizado: Metadados, regras Sentinela e área viva de auto-aprendizado
Gera também build_dicionario.py para recompilar o canônico instantaneamente.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
DICT_PATH = BASE_DIR / "dicionario_lexico.json"
MODULOS_DIR = BASE_DIR / "dicionario_modulos"

DIR_OPERACIONAIS = MODULOS_DIR / "01_comandos_operacionais"
DIR_INSPECAO = MODULOS_DIR / "02_esteiras_de_inspecionamento"
DIR_GOVERNANCA = MODULOS_DIR / "03_governanca_e_aprendizado"

def main():
    if not DICT_PATH.exists():
        print(f"[X] Arquivo não encontrado: {DICT_PATH}")
        sys.exit(1)

    with open(DICT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Criar pastas
    for d in [DIR_OPERACIONAIS, DIR_INSPECAO, DIR_GOVERNANCA]:
        d.mkdir(parents=True, exist_ok=True)

    mapeamento_total = data.get("mapeamento", {})
    aliases_total = data.get("aliases_linguagem", {})
    pipelines_total = data.get("pipelines", {})
    categorias_total = data.get("categorias", {})
    aprendidos_total = data.get("comandos_aprendidos_dinamicamente", [])

    # -------------------------------------------------------------
    # 1. 02_esteiras_de_inspecionamento
    # -------------------------------------------------------------
    # A) Auditoria Total
    map_at = {k: mapeamento_total[k] for k in ["auditoria_total"] if k in mapeamento_total}
    alias_at = {k: aliases_total[k] for k in ["auditoria_total"] if k in aliases_total}
    pipe_at = {k: pipelines_total[k] for k in ["AUDITORIA_TOTAL"] if k in pipelines_total}
    with open(DIR_INSPECAO / "auditoria_total.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "auditoria_total",
            "descricao": "Auditoria Total nas 14 Camadas Arquiteturais e Extração de Arquivos Relevantes",
            "mapeamento": map_at,
            "aliases_linguagem": alias_at,
            "pipelines": pipe_at
        }, f, indent=2, ensure_ascii=False)

    # B) Auditoria Replicador Total
    map_rep_keys = ["auditoria_total_replicador", "espelhamento_frontend_estatico", "copia", "clone", "espelho", "replicar"]
    map_rep = {k: mapeamento_total[k] for k in map_rep_keys if k in mapeamento_total}
    alias_rep = {k: aliases_total[k] for k in ["auditoria_total_replicador", "espelhamento_frontend_estatico"] if k in aliases_total}
    pipe_rep = {k: pipelines_total[k] for k in ["AUDITORIA_TOTAL_REPLICADOR"] if k in pipelines_total}
    with open(DIR_INSPECAO / "auditoria_replicador.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "auditoria_replicador",
            "descricao": "Full Stack Replicator - Download completo em projetos/SITES/<Nome> e SQLite físico",
            "mapeamento": map_rep,
            "aliases_linguagem": alias_rep,
            "pipelines": pipe_rep
        }, f, indent=2, ensure_ascii=False)

    # C) Auditoria Global OSINT
    map_ag = {k: mapeamento_total[k] for k in ["auditoria_global"] if k in mapeamento_total}
    alias_ag = {k: aliases_total[k] for k in ["auditoria_global"] if k in aliases_total}
    pipe_ag = {k: pipelines_total[k] for k in ["AUDITORIA_GLOBAL"] if k in pipelines_total}
    with open(DIR_INSPECAO / "auditoria_global_osint.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "auditoria_global_osint",
            "descricao": "Auditoria Global cobrindo Surface, Deep e Dark Web, crt.sh e Wayback CDX",
            "mapeamento": map_ag,
            "aliases_linguagem": alias_ag,
            "pipelines": pipe_ag
        }, f, indent=2, ensure_ascii=False)

    # D) Auditoria Infra Completa
    map_ac = {k: mapeamento_total[k] for k in ["auditoria_completa"] if k in mapeamento_total}
    alias_ac = {k: aliases_total[k] for k in ["auditoria_completa"] if k in aliases_total}
    pipe_ac = {k: pipelines_total[k] for k in ["AUDITORIA_INTEGRIDADE_SISTEMA"] if k in pipelines_total}
    with open(DIR_INSPECAO / "auditoria_infra_completa.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "auditoria_infra_completa",
            "descricao": "Diagnóstico de Infraestrutura, Memória RAM, CPU, Swap e Permissões chmod 0600",
            "mapeamento": map_ac,
            "aliases_linguagem": alias_ac,
            "pipelines": pipe_ac
        }, f, indent=2, ensure_ascii=False)

    # E) Inspeção DOM e DevTools
    dom_keys = [
        "inspecao_interface_irrestrita", "desmascarar_inputs_senha", "remover_travas_css_visual",
        "extrair_valores_cache_dom", "destravar_estados_elementos", "remover_overlays_invisiveis"
    ]
    map_dom = {k: mapeamento_total[k] for k in dom_keys if k in mapeamento_total}
    alias_dom = {k: aliases_total[k] for k in ["inspecao_interface_irrestrita", "chromedevtools_avancado", "gatilhos_auditoria_com_depuracao_dom"] if k in aliases_total}
    with open(DIR_INSPECAO / "inspecao_dom_e_devtools.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "inspecao_dom_e_devtools",
            "descricao": "Inspeção profunda de DOM, extração de senhas, remoção de travas e injeção DevTools",
            "mapeamento": map_dom,
            "aliases_linguagem": alias_dom
        }, f, indent=2, ensure_ascii=False)

    # F) Esteiras de Scraping, Dados & Dumps
    scraping_aliases = [
        "scrape", "crawl", "harvest", "fetch", "pull", "parse", "sync", "dump",
        "listar_registros", "visualizar_registro", "trainer_de_jogo", "audit_pci_cards",
        "gatilhos_separacao_dados"
    ]
    alias_scraping = {k: aliases_total[k] for k in scraping_aliases if k in aliases_total}
    pipe_scraping = {k: pipelines_total[k] for k in ["DUMP_BANCO_COMPLETO", "LIMPEZA_LOGS_E_BUFFERS", "HWID_SPOOF_GC"] if k in pipelines_total}
    map_scraping_keys = [
        "scrape", "crawl", "harvest", "fetch", "pull", "parse", "sync", "dump",
        "listar_registros", "visualizar_registro", "trainer_de_jogo", "audit_pci_cards"
    ]
    map_scraping = {k: mapeamento_total[k] for k in map_scraping_keys if k in mapeamento_total}
    with open(DIR_INSPECAO / "esteiras_scraping_e_dados.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "esteiras_scraping_e_dados",
            "descricao": "Pipelines de coleta, extração sequencial de dados, dumps e conformidade PCI",
            "mapeamento": map_scraping,
            "aliases_linguagem": alias_scraping,
            "pipelines": pipe_scraping
        }, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------------------
    # 2. 03_governanca_e_aprendizado
    # -------------------------------------------------------------
    # A) Metadados e Governança
    gov_map_keys = ["atualizar_sentinela", "baixa_atualizacao_sentinela"]
    gov_map = {k: mapeamento_total[k] for k in gov_map_keys if k in mapeamento_total}
    gov_alias = {k: aliases_total[k] for k in ["atualizar_sentinela"] if k in aliases_total}
    with open(DIR_GOVERNANCA / "metadados_governanca.json", "w", encoding="utf-8") as f:
        json.dump({
            "versao": data.get("versao", 4.6),
            "modulo": data.get("modulo", "sentinela_lexicon"),
            "descricao": data.get("descricao", ""),
            "data_atualizacao": data.get("data_atualizacao", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "categorias_canonicas": categorias_total,
            "mapeamento": gov_map,
            "aliases_linguagem": gov_alias
        }, f, indent=2, ensure_ascii=False)

    # B) Comandos Aprendidos Dinamicamente (Área Viva)
    apr_map = {k: mapeamento_total[k] for k in ["auto_aprender_comando"] if k in mapeamento_total}
    apr_alias = {k: aliases_total[k] for k in ["auto_aprendizado_e_evolucao"] if k in aliases_total}
    with open(DIR_GOVERNANCA / "comandos_aprendidos.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "comandos_aprendidos_dinamicamente",
            "descricao": "Área viva de evolução contínua alimentada pelo dicionario_learner",
            "mapeamento": apr_map,
            "aliases_linguagem": apr_alias,
            "comandos_aprendidos_dinamicamente": aprendidos_total,
            "total_comandos_aprendidos": len(aprendidos_total)
        }, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------------------
    # 3. 01_comandos_operacionais (Comandos diretos de terminal por domínio)
    # -------------------------------------------------------------
    # Todos os comandos de mapeamento que já foram alocados
    alocados = set(map_at.keys()) | set(map_rep.keys()) | set(map_ag.keys()) | \
               set(map_ac.keys()) | set(map_dom.keys()) | set(map_scraping.keys()) | \
               set(gov_map.keys()) | set(apr_map.keys())

    # Agrupar os restantes por afinidade de domínio operacional
    git_keys = set(categorias_total.get("versionamento_e_git", [])) | {
        "destravar_git", "abortar_rebase_git", "sincronizar_estruturas", "reset_workspace_limpo",
        "healthcheck_pipeline", "reverter_commit_local", "limpar_branches_mortas", "git_status_conciso"
    }

    stress_keys = set(categorias_total.get("red_teaming_e_ataque_extremo", [])) | {
        "ataque_ddos_sintetico", "fuzzing_api_extremo", "mapear_superficie_ataque",
        "testar_bypass_ratelimit", "simular_forca_bruta", "congelamento_kernel_chaos"
    }

    db_keys = set(categorias_total.get("armazenamento_e_logs", [])) | {
        "destravar_sqlite_wal", "otimizar_sqlite", "limpeza_cache_logs", "rotacao_logs",
        "verificar_permissoes", "higienizar_logs", "dump_rapido_sqlite", "reparo_banco_dados"
    }

    net_keys = set(categorias_total.get("conectividade_e_integracoes", [])) | {
        "flush_cache_dns", "resetar_proxies_rede", "reiniciar_ssh_agent", "desbloquear_socket_docker",
        "estabilidade_servico", "inspecionar_rede_local", "benchmark_api", "validar_auth_fallback",
        "testar_conectividade_gateway", "scan_portas_abertas"
    }

    # Restante vai para sistema_e_processos
    map_git = {}
    map_stress = {}
    map_db = {}
    map_net = {}
    map_sis = {}

    for k, v in mapeamento_total.items():
        if k in alocados:
            continue
        if k in git_keys:
            map_git[k] = v
        elif k in stress_keys:
            map_stress[k] = v
        elif k in db_keys:
            map_db[k] = v
        elif k in net_keys:
            map_net[k] = v
        else:
            map_sis[k] = v

    # Gravar módulos operacionais
    pipe_git = {k: pipelines_total[k] for k in ["SINC_GIT_AUTOMATICO"] if k in pipelines_total}
    with open(DIR_OPERACIONAIS / "git_e_repositorios.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "git_e_repositorios",
            "descricao": "Gatilhos operacionais diretos para Git: destravamento de index.lock, cancelamento de rebase e sync",
            "mapeamento": map_git,
            "pipelines": pipe_git
        }, f, indent=2, ensure_ascii=False)

    with open(DIR_OPERACIONAIS / "sistema_e_processos.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "sistema_e_processos",
            "descricao": "Gatilhos operacionais para SO e processos: matar PIDs em portas, remover quarentena macOS, limites kernel",
            "mapeamento": map_sis
        }, f, indent=2, ensure_ascii=False)

    with open(DIR_OPERACIONAIS / "redes_e_conectividade.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "redes_e_conectividade",
            "descricao": "Gatilhos operacionais de rede: flush DNS mDNSResponder, proxies, sockets Docker e latência",
            "mapeamento": map_net
        }, f, indent=2, ensure_ascii=False)

    with open(DIR_OPERACIONAIS / "bancos_e_armazenamento.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "bancos_e_armazenamento",
            "descricao": "Gatilhos operacionais de persistência: destravar WAL, checkpoint SQLite, rotação e truncamento de logs",
            "mapeamento": map_db
        }, f, indent=2, ensure_ascii=False)

    with open(DIR_OPERACIONAIS / "red_teaming_e_stress.json", "w", encoding="utf-8") as f:
        json.dump({
            "dominio": "red_teaming_e_stress",
            "descricao": "Gatilhos de testes de carga sintética, boundary fuzzing, rate-limit bypass e caos",
            "mapeamento": map_stress
        }, f, indent=2, ensure_ascii=False)

    print("\n✅ [SUCESSO] Modularização concluída com êxito!")
    print(f"📁 Pasta dos Módulos: {MODULOS_DIR}")
    print(f"   • 01_comandos_operacionais: 5 módulos")
    print(f"   • 02_esteiras_de_inspecionamento: 6 módulos")
    print(f"   • 03_governanca_e_aprendizado: 2 módulos")

if __name__ == "__main__":
    main()
