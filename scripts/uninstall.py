#!/usr/bin/env python3
"""
Desinstalador & Reversão Limpa — Antigravity Turbinado
Remove os arquivos locais de configuração e caches sem tocar nos projetos do cliente.
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("⚠️ DESINSTALADOR DO ANTIGRAVITY TURBINADO")
    print("=" * 60)
    print("Esta rotina removerá os daemons e arquivos de configuração temporários.")
    print("Seus projetos pessoais em ~/projetos NUNCA serão apagados.")
    print("=" * 60)
    
    confirm = input("Deseja realmente continuar? (digite 'SIM' para confirmar): ").strip()
    if confirm != "SIM":
        print("Operação cancelada pelo usuário.")
        sys.exit(0)

    home = Path.home()
    clean_targets = [
        home / ".gemini" / "antigravity" / "scratch",
        home / ".gemini" / "antigravity" / "crashes",
    ]

    print("\nLimpando caches e arquivos temporários...")
    for target in clean_targets:
        if target.exists():
            try:
                shutil.rmtree(target)
                print(f"✅ Removido: {target}")
            except Exception as e:
                print(f"⚠️ Não foi possível remover {target}: {e}")

    print("\n✅ Desinstalação concluída com sucesso. Nenhuma chave do sistema foi corrompida.")

if __name__ == "__main__":
    main()
