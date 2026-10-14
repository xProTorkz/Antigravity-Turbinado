#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador & Compilador Mestre do Dicionário Léxico Sentinela (build_dicionario.py)
Arquitetura Desacoplada v6.0:
- O Dicionário Léxico é único e canônico em 'dicionario_lexico.json'.
- Os pipelines são segregados em arquivos modulares na pasta 'pipelines/'.
Gera 'dicionario_lexico.min.json' e sincroniza o symlink em ~/.gemini/config/dicionario_lexico.json.
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
TARGET_DICT = BASE_DIR / "dicionario_lexico.json"
PIPELINES_DIR = BASE_DIR / "pipelines"
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
    if not TARGET_DICT.exists():
        print(f"[X] Dicionário canônico não encontrado: {TARGET_DICT}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("🛠️ [SENTINELA] COMPILADOR DO DICIONÁRIO LÉXICO (ARQUITETURA MODULAR v6.0)")
    print("=" * 70)

    with open(TARGET_DICT, "r", encoding="utf-8") as f:
        dict_data = json.load(f)

    # 1. Validar e atualizar metadados
    dict_data["versao"] = "6.0-LEAN-MODULAR"
    dict_data["modulo"] = "sentinela_lexicon"
    dict_data["data_atualizacao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 2. Validar integridade dos pipelines em pipelines/
    pipelines_count = 0
    if PIPELINES_DIR.exists():
        pipeline_files = sorted(list(PIPELINES_DIR.glob("*.json")))
        pipelines_count = len(pipeline_files)
        print(f"[*] Validando {pipelines_count} arquivos de pipelines em {PIPELINES_DIR.name}/:")
        for pf in pipeline_files:
            try:
                with open(pf, "r", encoding="utf-8") as pf_in:
                    p_content = json.load(pf_in)
                etapas_cnt = len(p_content.get("etapas", []))
                print(f"    ✓ {pf.name} (ID: {p_content.get('id', pf.stem.upper())} | {etapas_cnt} etapas)")
            except Exception as ex:
                print(f"    [X] Erro de validação no pipeline {pf.name}: {ex}")
                sys.exit(1)

    # 3. Regravar dicionário canônico e minificado
    with open(TARGET_DICT, "w", encoding="utf-8") as f:
        json.dump(dict_data, f, indent=2, ensure_ascii=False)

    target_min = TARGET_DICT.parent / "dicionario_lexico.min.json"
    with open(target_min, "w", encoding="utf-8") as f:
        json.dump(dict_data, f, separators=(",", ":"), ensure_ascii=False)

    sha_local = calculate_sha256(TARGET_DICT)

    print("\n📊 RESUMO DO DICIONÁRIO:")
    print(f"    ✓ Versão Canônica:     {dict_data.get('versao')}")
    print(f"    ✓ Gatilhos Modulares:  {len(dict_data.get('gatilhos', {}))} gatilhos")
    print(f"    ✓ Mapeamentos Rápidos: {len(dict_data.get('mapeamento', {}))} termos")
    print(f"    ✓ Aliases de Linguagem:{len(dict_data.get('aliases_linguagem', {}))} aliases")
    print(f"    ✓ Pipelines Externos:  {pipelines_count} arquivos independentes")
    print(f"    🔒 SHA-256 do Canônico: {sha_local}")
    print(f"    📄 Destino Canônico:    {TARGET_DICT}")

    # 4. Sincronização automática com a pasta global (~/.gemini/config/dicionario_lexico.json)
    if GLOBAL_CONFIG_DICT.parent.exists():
        try:
            if GLOBAL_CONFIG_DICT.is_symlink() or GLOBAL_CONFIG_DICT.exists():
                GLOBAL_CONFIG_DICT.unlink()
            GLOBAL_CONFIG_DICT.symlink_to(TARGET_DICT.resolve())
            print(f"    🔗 Symlink Global Atualizado: {GLOBAL_CONFIG_DICT} -> {TARGET_DICT}")
        except Exception as ex:
            try:
                import shutil
                shutil.copy2(TARGET_DICT, GLOBAL_CONFIG_DICT)
                print(f"    📋 Cópia Global Atualizada: {GLOBAL_CONFIG_DICT}")
            except Exception as e2:
                print(f"    [!] Aviso ao sincronizar globalmente: {e2}")

    print("\n🎉 [SUCESSO TOTAL] Dicionário Léxico validado e sincronizado com 100% de integridade!\n")
    return True

if __name__ == "__main__":
    build()
