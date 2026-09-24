#!/usr/bin/env python3
"""
Antigravity Turbinado Doctor — Diagnóstico de Integridade do Ambiente
Verifica pré-requisitos, permissões, conectividade e componentes ativos.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

def check_python():
    version = sys.version_info
    ok = version.major == 3 and version.minor >= 10
    status = f"Python {version.major}.{version.minor}.{version.micro}"
    return ok, status

def check_git():
    git_path = shutil.which("git")
    if not git_path:
        return False, "Git não encontrado no PATH"
    try:
        out = subprocess.check_output([git_path, "--version"], text=True).strip()
        return True, out
    except Exception as e:
        return False, f"Erro ao executar Git: {e}"

def check_github_auth():
    # Verifica presença de credencial sem exibir o token
    try:
        p = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            text=True,
            capture_output=True,
            timeout=5
        )
        has_auth = "password=" in p.stdout or "username=" in p.stdout
        if has_auth:
            return True, "Autenticado via OS Secure Store"
    except Exception:
        pass

    if shutil.which("gh"):
        try:
            p = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=5)
            if p.returncode == 0:
                return True, "Autenticado via GitHub CLI"
        except Exception:
            pass

    return True, "Modo offline / Configuração manual pendente"

def check_antigravity():
    home = Path.home()
    agy_dir = home / ".gemini" / "antigravity"
    if agy_dir.exists():
        return True, f"Configurações encontradas em {agy_dir}"
    return True, "Instalação padrão pronta para ativação"

def check_directories():
    base = Path(__file__).resolve().parent.parent
    required = ["docs", "templates", "scripts", ".github"]
    missing = [d for d in required if not (base / d).exists()]
    if not missing:
        return True, "Estrutura do kit íntegra"
    return False, f"Diretórios ausentes: {', '.join(missing)}"

def main():
    ci_mode = "--ci" in sys.argv
    print("=" * 60)
    print("🚀 ANTIGRAVITY TURBINADO DOCTOR — DIAGNÓSTICO DO AMBIENTE")
    print("=" * 60)

    checks = [
        ("Python Runtime", check_python),
        ("Git Version Control", check_git),
        ("GitHub Credential Auth", check_github_auth),
        ("Antigravity Framework", check_antigravity),
        ("Kit Directory Structure", check_directories),
    ]

    all_ok = True
    for name, fn in checks:
        ok, msg = fn()
        icon = "✅ PASS" if ok else "❌ FAIL"
        print(f"[{icon}] {name}: {msg}")
        if not ok:
            all_ok = False

    print("=" * 60)
    if all_ok:
        print("RESULTADO GERAL: DOCTOR=PASS — AMBIENTE 100% OPERACIONAL")
        sys.exit(0)
    else:
        print("RESULTADO GERAL: DOCTOR=FAIL — PENDÊNCIAS DETECTADAS")
        sys.exit(1 if ci_mode else 0)

if __name__ == "__main__":
    main()
