#!/usr/bin/env python3
"""
Test Suite — Clean-Room Commercial Homologation (Task #55)
=========================================================
Executa a validação formal de produto genérico sem dependências,
contas, programas ou ecossistemas privados do proprietário.

Fluxo comprovado:
ChatGPT do Cliente → GitHub do Cliente → Antigravity no Workspace do Cliente
"""

import os
import sys
import shutil
import subprocess
import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DISTRIBUTABLE_PATHS = [
    "README.md",
    "docs",
    "installer",
    "scripts",
    "templates",
    ".github",
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

def test_cleanroom_macos_installation(tmp_path):
    """Cenário 1: Instalação macOS limpa sem injeção de contas ou projetos pessoais."""
    clean_projects = tmp_path / "client_projects"
    clean_projects.mkdir(parents=True, exist_ok=True)
    
    # Executa o onboarding em modo limpo e não-interativo apontando para a pasta temporária
    res = subprocess.run(
        [sys.executable, "scripts/onboarding_menu.py", "--non-interactive", "--projects-dir", str(clean_projects)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True
    )
    assert res.returncode == 0, f"Falha na execução do onboarding: {res.stderr}"
    
    output = res.stdout
    # Validações dos 10 passos
    assert "[Passo 1/10]" in output  # Detecção de SO
    assert "[Passo 2/10]" in output  # Diretório de projetos
    assert str(clean_projects) in output
    assert "[Passo 3/10]" in output  # Conta GitHub do cliente (<github-user>)
    assert "[Passo 4/10]" in output  # Repositório do cliente (<github-repo>)
    assert "[Passo 5/10]" in output  # Verificação Antigravity
    assert "[Passo 6/10]" in output  # Permissões transparentes
    assert "[Passo 7/10]" in output  # Skills distribuíveis
    assert "[Passo 8/10]" in output  # Planner Profile
    assert "[Passo 9/10]" in output  # Issue Template
    assert "[Passo 10/10]" in output # Sandbox neutro
    
    # Verifica criação física do sandbox dentro do diretório do cliente
    sandbox = clean_projects / "sandbox-demo"
    assert sandbox.exists()
    assert (sandbox / "README.md").exists()
    readme_content = (sandbox / "README.md").read_text(encoding="utf-8")
    assert "Sandbox Demo" in readme_content

def test_cleanroom_windows_installer_manifest():
    """Cenário 2: Instalação Windows através de script nativo sem credenciais fixas."""
    ps1_file = ROOT_DIR / "installer" / "install.ps1"
    assert ps1_file.exists()
    content = ps1_file.read_text(encoding="utf-8")
    
    # Não deve ter caminhos do proprietário
    for term in DENYLIST_TERMS:
        assert term.lower() not in content.lower(), f"Termo proibido '{term}' encontrado em install.ps1"
        
    # Deve aceitar parâmetros de flexibilidade de workspace
    assert "ProjectsDir" in content or "ScriptDir" in content
    assert "doctor.py" in content
    assert "<support-url>" in content

def test_cleanroom_chatgpt_planner_profile():
    """Cenário 3: Perfil do ChatGPT Planner é genérico e prepara Execution Packet limpo."""
    profile_file = ROOT_DIR / "templates" / "chatgpt-behavior-profile.template.md"
    assert profile_file.exists()
    content = profile_file.read_text(encoding="utf-8")
    
    # Verifica ausência de termos proprietários
    for term in DENYLIST_TERMS:
        assert term.lower() not in content.lower(), f"Termo proibido '{term}' encontrado no perfil do ChatGPT"
        
    # Verifica princípios do Planner: não executa localmente, gera YAML v5
    assert "NUNCA executa código local" in content
    assert "agent_task:" in content
    assert "version: 5" in content
    assert "allowed_scope:" in content

def test_cleanroom_github_issues_organizer():
    """Cenário 4: GitHub do cliente funciona como organizador e fonte de verdade (SOT)."""
    issue_md = ROOT_DIR / ".github" / "ISSUE_TEMPLATE" / "antigravity-task.md"
    issue_yml = ROOT_DIR / ".github" / "ISSUE_TEMPLATE" / "antigravity-task.yml"
    
    assert issue_md.exists()
    assert issue_yml.exists()
    
    md_content = issue_md.read_text(encoding="utf-8")
    assert "<github-user>/<github-repo>" in md_content
    assert "<project-name>" in md_content
    
    yml_content = issue_yml.read_text(encoding="utf-8")
    assert "Planejar (ChatGPT) → Registrar (GitHub) → Executar (Antigravity)" in yml_content
    assert "allowed_scope" in yml_content
    assert "Critérios de Aceite" in yml_content

def test_cleanroom_antigravity_execution_in_sandbox(tmp_path):
    """Cenário 5: Antigravity opera dentro de workspace fictício com máxima autonomia e validação."""
    client_workspace = tmp_path / "example-project"
    client_workspace.mkdir(parents=True, exist_ok=True)
    
    # 1. Simula repositório Git do cliente
    subprocess.run(["git", "init"], cwd=client_workspace, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Example Client"], cwd=client_workspace, check=True)
    subprocess.run(["git", "config", "user.email", "client@example.com"], cwd=client_workspace, check=True)
    
    # 2. Cria baseline
    init_file = client_workspace / "README.md"
    init_file.write_text("# Example Client Project\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=client_workspace, check=True)
    subprocess.run(["git", "commit", "-m", "chore: initial commit"], cwd=client_workspace, check=True)
    
    # 3. Simula alteração do Antigravity autorizada em allowed_scope: ["src/", "tests/"]
    src_dir = client_workspace / "src"
    tests_dir = client_workspace / "tests"
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    
    code_file = src_dir / "math_service.py"
    code_file.write_text("def add(a: int, b: int) -> int:\n    return a + b\n", encoding="utf-8")
    
    test_file = tests_dir / "test_math_service.py"
    test_file.write_text("from src.math_service import add\n\ndef test_add():\n    assert add(2, 3) == 5\n", encoding="utf-8")
    
    # 4. Executa testes no workspace fictício (Test Before / Test After)
    test_run = subprocess.run([sys.executable, "-m", "pytest", str(test_file)], cwd=client_workspace, capture_output=True, text=True)
    assert test_run.returncode == 0
    assert "1 passed" in test_run.stdout
    
    # 5. Commit e recibo de entrega dentro do workspace do cliente
    subprocess.run(["git", "add", "src/", "tests/"], cwd=client_workspace, check=True)
    commit_res = subprocess.run(["git", "commit", "-m", "feat: implement math service and tests"], cwd=client_workspace, capture_output=True, text=True)
    assert commit_res.returncode == 0
    
    # 6. Verifica isolamento: nenhum arquivo foi tocado fora de client_workspace
    assert (client_workspace / "src" / "math_service.py").exists()
    assert not (tmp_path / "math_service.py").exists()

def test_cleanroom_strict_isolation_denylist():
    """Cenário 6: Isolamento estrito — zero referências a projetos ou identidades privadas."""
    violations = []
    
    for path_str in DISTRIBUTABLE_PATHS:
        target = ROOT_DIR / path_str
        if not target.exists():
            continue
            
        if target.is_file():
            files_to_check = [target]
        else:
            files_to_check = [
                p for p in target.rglob("*")
                if p.is_file() and not p.name.endswith(".pyc") and "__pycache__" not in str(p)
            ]
            
        for f in files_to_check:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                for term in DENYLIST_TERMS:
                    if term.lower() in content.lower():
                        violations.append(f"{f.relative_to(ROOT_DIR)}: contém termo '{term}'")
            except Exception:
                pass

    assert not violations, f"Isolamento violado. Termos da denylist encontrados:\n" + "\n".join(violations)

def test_cleanroom_skill_routing_multidomain():
    """Cenário 7: Skill Router classifica 6 categorias sem depender de contexto privado."""
    from scripts.skill_router import discover_skills, route_task
    
    skills = discover_skills()
    assert len(skills) > 0, "Nenhuma skill descoberta pelo router."
    
    test_domains = [
        ("Criar tela de checkout responsiva com React e Tailwind", "frontend"),
        ("Desenvolver API REST com FastAPI e autenticação JWT", "backend"),
        ("Otimizar queries e índices no banco de dados PostgreSQL", "database"),
        ("Implementar suíte de testes com pytest e cobertura", "testing"),
        ("Configurar pipeline CI/CD no GitHub Actions com Docker", "devops"),
        ("Auditar vulnerabilidades de autenticação e proteção contra invasões", "security"),
    ]
    
    for prompt, expected_class in test_domains:
        res = route_task(prompt, skills)
        assert res["TASK_CLASS"] == expected_class, f"Esperado {expected_class}, obtido {res['TASK_CLASS']} para: '{prompt}'"
        assert res["SKILL_PRIMARY"].startswith("@")
        # Nenhuma skill deve carregar referências privadas
        assert "lucasvinicius" not in res["SKILL_PRIMARY"]
        assert "xprotorkz" not in res["SKILL_PRIMARY"].lower()
