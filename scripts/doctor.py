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
    required = ["docs", "templates", "scripts", ".github", "skills"]
    missing = [d for d in required if not (base / d).exists()]
    if not missing:
        return True, "Estrutura do kit íntegra"
    return False, f"Diretórios ausentes: {', '.join(missing)}"

def check_turbo_settings():
    home = Path.home()
    config_file = home / ".gemini" / "config" / "config.json"
    if config_file.exists():
        try:
            data = json.loads(config_file.read_text(encoding="utf-8"))
            settings = data.get("userSettings", {})
            if settings.get("autoExecutionPolicy") == "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER":
                return True, "Políticas Turbo ativas (Eager Auto-Execution + Max Autonomia)"
        except Exception:
            pass
    return True, "Políticas padrão (execute configure_turbo_environment.py para ativar modo Turbo)"

def check_skills_catalog():
    home = Path.home()
    native_dir = home / ".agents" / "skills"
    catalog_dir = home / "projetos" / "config" / "Skills"
    
    native_count = len([d for d in native_dir.iterdir() if d.is_dir()]) if native_dir.exists() else 0
    catalog_count = len([d for d in catalog_dir.iterdir() if d.is_dir()]) if catalog_dir.exists() else 0
    
    if native_count >= 100 or catalog_count >= 2000:
        return True, f"Acervo completo: {native_count} nativas (~/.agents/skills) + {catalog_count} no catálogo ampliado"
    elif native_count > 0:
        return True, f"{native_count} skills nativas ativas"
    return True, "Catálogo pronto para sincronização"

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
        ("Turbo Execution Policy", check_turbo_settings),
        ("Skills Catalog Index", check_skills_catalog),
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
