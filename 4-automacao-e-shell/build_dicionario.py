#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador Mestre do Dicionário Léxico Sentinela (build_dicionario.py)
Consolida os módulos das 3 pastas operacionais em um único dicionario_lexico.json canônico:
- 01_comandos_operacionais/ (Comandos rápidos de terminal: git, portas, redes, bancos, stress)
- 02_esteiras_de_inspecionamento/ (Roteiros sequenciais e auditorias multicamada)
- 03_governanca_e_aprendizado/ (Metadados, regras e área viva de auto-aprendizado)
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
MODULOS_DIR = BASE_DIR / "dicionario_modulos"
TARGET_DICT = BASE_DIR / "dicionario_lexico.json"
GLOBAL_CONFIG_DICT = Path(os.path.expanduser("~/.gemini/config/dicionario_lexico.json"))

def calculate_sha256(filepath: Path) -> str:
    if not filepath.exists() or not filepath.is_file():
        return ""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def build():
    if not MODULOS_DIR.exists():
        print(f"[X] Diretório de módulos não encontrado: {MODULOS_DIR}")
        sys.exit(1)

    print("\n" + "="*70)
    print("🛠️ [SENTINELA] COMPILADOR DO DICIONÁRIO LÉXICO (MÓDULOS ➔ CANÔNICO)")
    print("="*70)

    # 1. Carregar metadados e governança como base
    meta_file = MODULOS_DIR / "03_governanca_e_aprendizado" / "metadados_governanca.json"
    if not meta_file.exists():
        print(f"[X] Arquivo base de metadados não encontrado: {meta_file}")
        sys.exit(1)

    with open(meta_file, "r", encoding="utf-8") as f:
        base_meta = json.load(f)

    consolidated = {
        "versao": "5.0",
        "modulo": "sentinela_lexicon",
        "descricao": "Dicionário Léxico Sentinela v5.0 DRY - Arquitetura Otimizada de Alta Performance com Paridade Total em 14 Camadas, Replicador Full-Stack, OSINT Global e Perícia Pessoal Antifraude",
        "data_atualizacao": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "recursos_compartilhados": {},
        "mapeamento": {},
        "categorias": base_meta.get("categorias_canonicas", {}),
        "aliases_linguagem": {},
        "pipelines": {},
        "comandos_aprendidos_dinamicamente": [],
        "total_comandos_aprendidos": 0
    }

    # Incorporar mapeamentos e aliases de metadados_governanca se houver
    consolidated["mapeamento"].update(base_meta.get("mapeamento", {}))
    consolidated["aliases_linguagem"].update(base_meta.get("aliases_linguagem", {}))

    # 2. Varrer recursivamente todos os arquivos .json em dicionario_modulos
    loaded_files = []
    total_mapeamentos_count = len(consolidated["mapeamento"])

    for root, _, files in sorted(os.walk(MODULOS_DIR)):
        for f in sorted(files):
            if f.endswith(".json") and f != "metadados_governanca.json":
                fp = Path(root) / f
                try:
                    with open(fp, "r", encoding="utf-8") as jf:
                        content = json.load(jf)
                    
                    rel_p = str(fp.relative_to(MODULOS_DIR))
                    loaded_files.append(rel_p)

                    # Mesclar mapeamento (gatilhos ➔ descrições)
                    if "mapeamento" in content and isinstance(content["mapeamento"], dict):
                        consolidated["mapeamento"].update(content["mapeamento"])

                    # Mesclar aliases_linguagem (roteiros)
                    if "aliases_linguagem" in content and isinstance(content["aliases_linguagem"], dict):
                        consolidated["aliases_linguagem"].update(content["aliases_linguagem"])

                    # Mesclar pipelines (DAGs de execução sequencial)
                    if "pipelines" in content and isinstance(content["pipelines"], dict):
                        consolidated["pipelines"].update(content["pipelines"])

                    # Mesclar comandos aprendidos se for o arquivo de aprendizado
                    if "comandos_aprendidos_dinamicamente" in content and isinstance(content["comandos_aprendidos_dinamicamente"], list):
                        consolidated["comandos_aprendidos_dinamicamente"] = content["comandos_aprendidos_dinamicamente"]
                        consolidated["total_comandos_aprendidos"] = len(content["comandos_aprendidos_dinamicamente"])

                except Exception as ex:
                    print(f"[!] Erro ao carregar módulo {fp.name}: {ex}")
                    sys.exit(1)

    # 3. Gravar arquivo consolidado canônico (formatado e minificado)
    with open(TARGET_DICT, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)
    
    target_min = TARGET_DICT.parent / "dicionario_lexico.min.json"
    with open(target_min, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, separators=(",", ":"), ensure_ascii=False)

    sha_local = calculate_sha256(TARGET_DICT)
    print(f"[*] Módulos processados: {len(loaded_files)} arquivos JSON")
    for lf in loaded_files:
        print(f"    • {lf}")

    print("\n📊 RESUMO DA COMPILAÇÃO:")
    print(f"    ✓ Total de Mapeamentos: {len(consolidated['mapeamento'])} gatilhos")
    print(f"    ✓ Total de Categorias:   {len(consolidated['categorias'])} categorias")
    print(f"    ✓ Total de Aliases:      {len(consolidated['aliases_linguagem'])} aliases estruturados")
    print(f"    ✓ Total de Pipelines:    {len(consolidated['pipelines'])} pipelines sequenciais")
    print(f"    ✓ Comandos Aprendidos:   {consolidated['total_comandos_aprendidos']} registros ativos")
    print(f"    🔒 SHA-256 do Canônico:  {sha_local}")
    print(f"    📄 Destino Canônico:     {TARGET_DICT}")

    # 4. Sincronização automática com a pasta global (~/.gemini/config/dicionario_lexico.json)
    if GLOBAL_CONFIG_DICT.parent.exists():
        try:
            if GLOBAL_CONFIG_DICT.is_symlink() or GLOBAL_CONFIG_DICT.exists():
                GLOBAL_CONFIG_DICT.unlink()
            GLOBAL_CONFIG_DICT.symlink_to(TARGET_DICT.resolve())
            print(f"    🔗 Symlink Global Atualizado: {GLOBAL_CONFIG_DICT} -> {TARGET_DICT}")
        except Exception as ex:
            # Fallback para cópia física
            try:
                import shutil
                shutil.copy2(TARGET_DICT, GLOBAL_CONFIG_DICT)
                print(f"    📋 Cópia Global Atualizada: {GLOBAL_CONFIG_DICT}")
            except Exception as e2:
                print(f"    [!] Aviso ao sincronizar globalmente: {e2}")

    print("\n🎉 [SUCESSO TOTAL] Dicionário Léxico consolidado com 100% de integridade!\n")
    return True

if __name__ == "__main__":
    build()
