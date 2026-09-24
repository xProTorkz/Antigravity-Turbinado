#!/usr/bin/env python3
"""
Test Suite — Antigravity Turbinado Produto Neutro & Comercial
Valida todos os critérios de aceitação do refactor:
1. Arquitetura 3 pilares: ChatGPT → GitHub → Antigravity
2. Denylist de termos privados e projetos do proprietário em allowed_scope
3. Ausência de dependência de Sentinela ou Control Plane privado no produto
4. Onboarding limpo em 10 passos executável em modo headless
5. Auditoria de segurança e zero segredos (PASS)
6. Funcionamento de doctor.py, skill_router.py e license_guard.py
"""

import os
import sys
import subprocess
import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

ALLOWED_SCOPE_PATHS = [
    "README.md",
    "docs",
    "installer",
    "scripts",
    "templates",
    ".github",
    "tests"
]

DENYLIST_TERMS = [
    "lucasvinicius",
    "xprotorkz",
    "xProTorkz",
    "Sharkbot",
    "sharkbot",
    "Jarvis",
    "Minha Agenda",
    "DADO88X",
    "DerivBot",
    "GESTAO ARENA",
    "project-blueprint",
    "sentinela",
    "Sentinela"
]

def test_denylist_in_allowed_scope():
    """Garante que nenhum termo da denylist apareça nos arquivos do produto comercial."""
    violations = []
    
    for scope_item in ALLOWED_SCOPE_PATHS:
        target = ROOT_DIR / scope_item
        if not target.exists():
            continue
            
        if target.is_file():
            files_to_check = [target]
        else:
            files_to_check = [
                p for p in target.rglob("*")
                if p.is_file() and not p.name.endswith(".pyc") and "__pycache__" not in str(p)
                # Não checa o próprio arquivo de teste onde a denylist está definida
                and p != Path(__file__).resolve()
            ]
            
        for f in files_to_check:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                for term in DENYLIST_TERMS:
                    if term.lower() in content.lower():
                        violations.append(f"{f.relative_to(ROOT_DIR)}: contém '{term}'")
            except Exception:
                pass

    assert not violations, f"Termos proibidos encontrados em allowed_scope:\n" + "\n".join(violations)

def test_three_pillar_architecture_in_docs():
    """Valida se README e ARCHITECTURE descrevem o fluxo ChatGPT → GitHub → Antigravity."""
    arch_file = ROOT_DIR / "docs" / "ARCHITECTURE.md"
    readme_file = ROOT_DIR / "README.md"
    agents_file = ROOT_DIR / "templates" / "AGENTS.template.md"
    
    assert arch_file.exists()
    assert readme_file.exists()
    assert agents_file.exists()
    
    arch_content = arch_file.read_text(encoding="utf-8")
    assert "CHATGPT / PLANNER" in arch_content
    assert "GITHUB ISSUES (SOT)" in arch_content
    assert "ANTIGRAVITY LOCAL" in arch_content
    assert "CONTROL PLANE / ROUTER" not in arch_content
    assert "SENTINELA" not in arch_content
    
    readme_content = readme_file.read_text(encoding="utf-8")
    assert "CHATGPT / PLANNER" in readme_content
    assert "GITHUB ISSUES (SOT)" in readme_content
    assert "ANTIGRAVITY LOCAL" in readme_content

def test_templates_use_placeholders():
    """Garante que templates contenham placeholders genéricos em vez de dados fixos."""
    task_tpl = ROOT_DIR / ".github" / "ISSUE_TEMPLATE" / "antigravity-task.md"
    assert task_tpl.exists()
    content = task_tpl.read_text(encoding="utf-8")
    assert "<github-user>/<github-repo>" in content
    assert "<project-name>" in content
    assert "xProTorkz" not in content

def test_license_guard_functionality():
    """Testa geração e validação de licença com Hardware ID."""
    from scripts.license_guard import get_machine_hwid, generate_license_key, verify_license_signature
    hwid = get_machine_hwid()
    assert len(hwid) > 0
    
    key = generate_license_key(99999, "core")
    assert key.startswith("TURBO-CORE-99999-")
    
    is_valid, user_id, plan_id = verify_license_signature(key)
    assert is_valid is True
    assert user_id == 99999
    assert plan_id == "core"

def test_skill_router_autotest():
    """Verifica se o Skill Router executa seu autoteste com 100% de sucesso."""
    res = subprocess.run([sys.executable, "scripts/skill_router.py", "--test"], cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
    assert "Autoteste do Skill Router concluído com sucesso!" in res.stdout

def test_doctor_passes():
    """Garante que o diagnóstico do Doctor retorne DOCTOR=PASS."""
    res = subprocess.run([sys.executable, "scripts/doctor.py", "--ci"], cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
    assert "DOCTOR=PASS" in res.stdout

def test_security_audit_passes():
    """Verifica se a auditoria anti-spyware e de segredos passa com sucesso."""
    res = subprocess.run([sys.executable, "scripts/security_audit.py"], cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0
    assert "SECURITY_AUDIT=PASS" in res.stdout

def test_onboarding_menu_non_interactive():
    """Valida a execução completa dos 10 passos do onboarding limpo em modo não interativo."""
    test_projects_dir = ROOT_DIR / "tests" / "sandbox_test_dir"
    res = subprocess.run(
        [sys.executable, "scripts/onboarding_menu.py", "--non-interactive", "--projects-dir", str(test_projects_dir)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True
    )
    assert res.returncode == 0
    assert "[Passo 1/10]" in res.stdout
    assert "[Passo 10/10]" in res.stdout
    assert "ONBOARDING CONCLUÍDO COM SUCESSO!" in res.stdout
    
    # Limpa diretório temporário se criado
    if test_projects_dir.exists():
        import shutil
        shutil.rmtree(test_projects_dir, ignore_errors=True)
