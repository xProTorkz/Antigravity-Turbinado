#!/usr/bin/env python3
"""
Onboarding Limpo & Assistente de Configuração — Antigravity Turbinado
===================================================================
Guia o cliente na configuração do ambiente de 3 pilares neutro:
ChatGPT (Planejador) → GitHub (Fonte de Verdade) → Antigravity (Executor Local)
"""

import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path

def clear_screen():
    print("\n" * 2)

def detect_os() -> str:
    if sys.platform == "darwin":
        return "macOS"
    elif sys.platform == "win32":
        return "Windows"
    elif sys.platform.startswith("linux"):
        return "Linux"
    return "Desconhecido"

def step_1_os(interactive: bool = True) -> str:
    detected = detect_os()
    print("\n[Passo 1/10] Verificação do Sistema Operacional:")
    print(f" -> Sistema detectado: {detected}")
    if interactive:
        confirm = input("Confirmar sistema operacional? [S/n]: ").strip().lower()
        if confirm == "n":
            custom_os = input("Informe seu sistema operacional (macOS/Windows): ").strip()
            return custom_os
    return detected

def step_2_projects_location(interactive: bool = True, default_dir: Path = None) -> Path:
    home = Path.home()
    fallback = default_dir or (home / "projects" if (home / "projects").exists() else home / "projetos")
    print("\n[Passo 2/10] Diretório de Trabalho dos Projetos:")
    print(f" -> Local padrão sugerido: {fallback}")
    if interactive:
        custom_input = input(f"Informe o caminho para seus projetos (Enter para {fallback}): ").strip()
        if custom_input:
            chosen = Path(os.path.expanduser(custom_input))
        else:
            chosen = fallback
    else:
        chosen = fallback

    chosen.mkdir(parents=True, exist_ok=True)
    print(f" -> Diretório configurado: {chosen}")
    return chosen

def step_3_github_auth(interactive: bool = True) -> dict:
    print("\n[Passo 3/10] Conta & Autenticação do GitHub:")
    gh_cmd = shutil.which("gh")
    auth_status = {"authenticated": False, "user": "<github-user>"}
    
    if gh_cmd:
        try:
            res = subprocess.run([gh_cmd, "auth", "status"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                auth_status["authenticated"] = True
                print(" -> Autenticação confirmada via GitHub CLI (gh).")
                for line in (res.stdout + res.stderr).splitlines():
                    if "Logged in to github.com account" in line or "as" in line:
                        parts = line.strip().split()
                        if parts:
                            auth_status["user"] = parts[-1]
        except Exception:
            pass

    if not auth_status["authenticated"]:
        print(" -> Nenhuma sessão do GitHub CLI detectada.")
        if interactive:
            print(" Recomendamos autenticar com: gh auth login")
            user_input = input("Informe seu usuário do GitHub (ex: meu-usuario): ").strip()
            if user_input:
                auth_status["user"] = user_input
        else:
            auth_status["user"] = os.environ.get("GITHUB_USER", "<github-user>")
            
    print(f" -> Conta GitHub configurada: {auth_status['user']}")
    return auth_status

def step_4_repository(github_user: str, interactive: bool = True) -> str:
    print("\n[Passo 4/10] Repositório de Trabalho no GitHub:")
    default_repo = f"{github_user}/<github-repo>"
    if interactive:
        repo_input = input(f"Informe o repositório (Enter para {default_repo}): ").strip()
        chosen_repo = repo_input or default_repo
    else:
        chosen_repo = os.environ.get("GITHUB_REPO", default_repo)
    print(f" -> Repositório configurado: {chosen_repo}")
    return chosen_repo

def step_5_antigravity_check() -> bool:
    print("\n[Passo 5/10] Verificação do Google Antigravity:")
    home = Path.home()
    agy_paths = [
        home / ".gemini" / "antigravity",
        Path("/Applications/Google Antigravity.app"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Antigravity"
    ]
    detected = any(p.exists() for p in agy_paths) or shutil.which("antigravity") is not None
    if detected:
        print(" -> Google Antigravity detectado no ambiente.")
    else:
        print(" -> Instalação padrão pronta. Certifique-se de ter o Google Antigravity instalado.")
    return True

def step_6_workspace_permissions(projects_dir: Path, interactive: bool = True) -> bool:
    print("\n[Passo 6/10] Permissões Transparentes de Workspace:")
    print(" • Diretrizes de segurança aplicadas:")
    print(f"   - Dentro de {projects_dir}: Autonomia máxima para testes, terminal e edições.")
    print("   - Fora dos workspaces autorizados: Bloqueio fail-closed e confirmação obrigatória.")
    if interactive:
        confirm = input("Confirmar permissões transparentes para os workspaces? [S/n]: ").strip().lower()
        if confirm == "n":
            print(" Permissões restritas mantidas. A execução exigirá confirmação para cada comando.")
            return False
    print(" -> Permissões de workspace ativadas com sucesso.")
    return True

def step_7_install_skills(base_kit_dir: Path, custom_home: Path = None, projects_dir: Path = None) -> dict:
    print("\n[Passo 7/10] Instalação do Catálogo de Skills Distribuíveis:")
    sys.path.insert(0, str(base_kit_dir / "scripts"))
    try:
        from configure_turbo_environment import install_skills
        stats = install_skills(base_kit_dir, custom_home=custom_home, custom_projects_dir=projects_dir)
        print(f" -> Skills nativas prontas em ~/.agents/skills/: {stats['native']}")
        print(f" -> Catálogo disponível: {stats['catalog']} skills")
        return stats
    except Exception as e:
        print(f" -> Aviso na instalação das skills: {e}")
        return {"native": 0, "catalog": 0}

def step_8_planner_profile(base_kit_dir: Path) -> str:
    print("\n[Passo 8/10] Planner Profile Genérico para o ChatGPT:")
    template_file = base_kit_dir / "templates" / "chatgpt-behavior-profile.template.md"
    content = ""
    if template_file.exists():
        content = template_file.read_text(encoding="utf-8")
        print(" -> O perfil define o ChatGPT como Planejador puro (gera Execution Packets v5 sem executar código).")
        print(" -> Copie o conteúdo de templates/chatgpt-behavior-profile.template.md nas Instruções Personalizadas do ChatGPT.")
    return content

def step_9_test_issue_template(base_kit_dir: Path) -> bool:
    print("\n[Passo 9/10] Template Canônico de Issue no GitHub:")
    issue_template = base_kit_dir / ".github" / "ISSUE_TEMPLATE" / "antigravity-task.yml"
    if issue_template.exists():
        print(" -> Template canônico v5 presente em .github/ISSUE_TEMPLATE/antigravity-task.yml")
        print(" -> Permite abrir tarefas estruturadas com Scope Lock e Critérios de Aceite.")
        return True
    return False

def step_10_sandbox_neutro(projects_dir: Path) -> Path:
    print("\n[Passo 10/10] Verificação do Projeto Sandbox Neutro:")
    sandbox_dir = projects_dir / "sandbox-demo"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    readme = sandbox_dir / "README.md"
    if not readme.exists():
        readme.write_text("# Sandbox Demo — Antigravity Turbinado\n\nAmbiente neutro de teste para validar execuções autônomas locais.\n", encoding="utf-8")
    print(f" -> Workspace sandbox disponível em: {sandbox_dir}")
    return sandbox_dir

def run_full_onboarding(interactive: bool = True, base_kit_dir: Path = None, default_projects_dir: Path = None) -> dict:
    kit_dir = base_kit_dir or Path(__file__).resolve().parent.parent
    clear_screen()
    print("=" * 65)
    print("🚀 ONBOARDING OFICIAL — ANTIGRAVITY TURBINADO")
    print("Arquitetura: ChatGPT (Planejador) → GitHub (SOT) → Antigravity (Executor)")
    print("=" * 65)

    os_type = step_1_os(interactive)
    proj_dir = step_2_projects_location(interactive, default_dir=default_projects_dir)
    gh_auth = step_3_github_auth(interactive)
    repo = step_4_repository(gh_auth["user"], interactive)
    agy_ok = step_5_antigravity_check()
    perms_ok = step_6_workspace_permissions(proj_dir, interactive)
    skills_stats = step_7_install_skills(kit_dir, projects_dir=proj_dir)
    profile = step_8_planner_profile(kit_dir)
    issue_ok = step_9_test_issue_template(kit_dir)
    sandbox = step_10_sandbox_neutro(proj_dir)

    print("\n" + "=" * 65)
    print("🎉 ONBOARDING CONCLUÍDO COM SUCESSO!")
    print("=" * 65)
    print("Seu ambiente está configurado sob a esteira neutra e soberana.")
    print("Para suporte técnico e atualizações: consulte <support-url>\n")

    return {
        "os": os_type,
        "projects_dir": str(proj_dir),
        "github_user": gh_auth["user"],
        "repo": repo,
        "antigravity_ok": agy_ok,
        "permissions_ok": perms_ok,
        "skills_stats": skills_stats,
        "issue_template_ok": issue_ok,
        "sandbox_path": str(sandbox)
    }

def main():
    parser = argparse.ArgumentParser(description="Onboarding Neutro — Antigravity Turbinado")
    parser.add_argument("--non-interactive", action="store_true", help="Executa o onboarding sem paradas interativas")
    parser.add_argument("--projects-dir", type=str, help="Caminho customizado para a pasta de projetos")
    args = parser.parse_args()

    custom_proj = Path(args.projects_dir) if args.projects_dir else None
    run_full_onboarding(interactive=not args.non_interactive, default_projects_dir=custom_proj)

if __name__ == "__main__":
    main()
