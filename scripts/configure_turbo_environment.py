#!/usr/bin/env python3
"""
Configure Turbo Environment — Antigravity Turbinado
===================================================
Aplica na máquina do cliente a mesma arquitetura de alto rendimento:
- Configura auto-execução contínua (CASCADE_COMMANDS_AUTO_EXECUTION_EAGER) no Antigravity
- Configura políticas Turbo de artefatos e browser JS
- Instala as 100 skills nativas em ~/.agents/skills/
- Descompacta o catálogo de 2.492 skills em ~/projetos/config/Skills/
- Cria symlinks canônicos para compatibilidade total
- Garante permissões irrestritas no workspace do projeto
"""

import os
import sys
import json
import shutil
import tarfile
from pathlib import Path

def configure_antigravity_settings(custom_home: Path = None) -> bool:
    """Configura userSettings no config.json do Antigravity para máxima autonomia."""
    home = custom_home or Path.home()
    config_file = home / ".gemini" / "config" / "config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if config_file.exists():
        try:
            data = json.loads(config_file.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    if "userSettings" not in data:
        data["userSettings"] = {}

    user_settings = data["userSettings"]
    user_settings["autoExecutionPolicy"] = "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER"
    user_settings["artifactReviewMode"] = "ARTIFACT_REVIEW_MODE_TURBO"
    user_settings["browserJsExecutionPolicy"] = "BROWSER_JS_EXECUTION_POLICY_TURBO"
    user_settings["nonWorkspaceFileAccessPolicy"] = "AGENT_SETTING_POLICY_ALLOW"

    config_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return True

def install_skills(base_kit_dir: Path, custom_home: Path = None, custom_projects_dir: Path = None) -> dict:
    """Instala as 100 skills nativas e descompacta as 2.492 skills do catálogo."""
    home = custom_home or Path.home()
    agents_skills_dir = home / ".agents" / "skills"
    agents_skills_dir.mkdir(parents=True, exist_ok=True)

    env_proj = os.environ.get("ANTIGRAVITY_PROJECTS_DIR")
    if custom_projects_dir:
        projects_dir = custom_projects_dir
    elif env_proj:
        projects_dir = Path(env_proj)
    else:
        projects_dir = home / "projects" if (home / "projects").exists() else home / "projetos"
    projects_dir.mkdir(parents=True, exist_ok=True)
    catalog_skills_dir = projects_dir / "config" / "Skills"
    catalog_skills_dir.mkdir(parents=True, exist_ok=True)

    stats = {"native": 0, "catalog": 0}

    # 1. Instalar as 100 skills nativas em ~/.agents/skills/
    src_native = base_kit_dir / "skills" / "native"
    if not src_native.exists():
        env_native = os.environ.get("ANTIGRAVITY_NATIVE_SKILLS_DIR")
        if env_native:
            src_native = Path(env_native)

    if src_native.exists():
        for skill_dir in src_native.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                dest = agents_skills_dir / skill_dir.name
                if not dest.exists():
                    shutil.copytree(skill_dir, dest, dirs_exist_ok=True)
                stats["native"] += 1

    # 2. Descompactar o catálogo de 2.492 skills em ~/projetos/config/Skills/
    tar_path = base_kit_dir / "skills" / "catalog.tar.gz"
    if not tar_path.exists():
        env_tar = os.environ.get("ANTIGRAVITY_CATALOG_TAR")
        if env_tar:
            tar_path = Path(env_tar)

    if tar_path.exists():
        with tarfile.open(tar_path, "r:gz") as tar:
            # Extrai apenas as pastas de skills para catalog_skills_dir
            for member in tar.getmembers():
                rel_path = member.name
                if rel_path.startswith("Skills/"):
                    rel_path = rel_path[len("Skills/"):]
                elif rel_path == "Skills":
                    continue
                if not rel_path:
                    continue

                target_item = catalog_skills_dir / rel_path
                if member.isdir():
                    target_item.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target_item.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(member) as source_f, open(target_item, "wb") as dest_f:
                        shutil.copyfileobj(source_f, dest_f)

    # Conta total real de skills instaladas no catálogo
    if catalog_skills_dir.exists():
        stats["catalog"] = len([d for d in catalog_skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])

    # 3. Criar symlink CONFIGURACOES GERAIS DE PROJETO -> config para compatibilidade
    alias_dir = projects_dir / "CONFIGURACOES GERAIS DE PROJETO"
    alias_dir.mkdir(parents=True, exist_ok=True)
    alias_skills = alias_dir / "Skills"
    if not alias_skills.exists():
        try:
            alias_skills.symlink_to(catalog_skills_dir, target_is_directory=True)
        except Exception:
            pass

    return stats

def install_automation_dictionary(base_kit_dir: Path, custom_projects_dir: Path = None) -> bool:
    """Provisiona o Dicionário Canônico de Automação e o roteador agy_cmd na pasta estruturas do cliente."""
    home = Path.home()
    env_proj = os.environ.get("ANTIGRAVITY_PROJECTS_DIR")
    if custom_projects_dir:
        projects_dir = custom_projects_dir
    elif env_proj:
        projects_dir = Path(env_proj)
    else:
        projects_dir = home / "projects" if (home / "projects").exists() else home / "projetos"

    estruturas_dir = projects_dir / "estruturas"
    estruturas_dir.mkdir(parents=True, exist_ok=True)

    # 1. Provisiona dicionario_automacao_core.md
    target_dict = estruturas_dir / "dicionario_automacao_core.md"
    template_dict = base_kit_dir / "templates" / "dicionario_automacao_core.template.md"
    if template_dict.exists():
        shutil.copy2(template_dict, target_dict)

    # 2. Provisiona roteador executável agy_cmd.sh
    target_router = estruturas_dir / "agy_cmd.sh"
    template_router = base_kit_dir / "templates" / "agy_cmd.template.sh"
    if template_router.exists():
        shutil.copy2(template_router, target_router)
        try:
            target_router.chmod(0o755)
        except Exception:
            pass

    # 3. Garante carregamento no ~/.zshrc se existir shell zsh
    zshrc = home / ".zshrc"
    if zshrc.exists():
        try:
            content = zshrc.read_text(encoding="utf-8")
            source_line = f'[ -f "{target_router}" ] && source "{target_router}"'
            if str(target_router) not in content:
                with open(zshrc, "a", encoding="utf-8") as f:
                    f.write(f"\n# Antigravity SRE/DevOps Command Router\n{source_line}\n")
        except Exception:
            pass

    return True

def main():
    kit_dir = Path(__file__).resolve().parent.parent
    print("=" * 65)
    print("⚡ CONFIGURAÇÃO DO AMBIENTE TURBO — ANTIGRAVITY TURBINADO")
    print("=" * 65)

    print("1. Aplicando políticas de autonomia máxima no Antigravity...")
    configure_antigravity_settings()
    print("   [OK] autoExecutionPolicy = CASCADE_COMMANDS_AUTO_EXECUTION_EAGER")
    print("   [OK] artifactReviewMode  = ARTIFACT_REVIEW_MODE_TURBO")
    print("   [OK] nonWorkspaceAccess  = AGENT_SETTING_POLICY_ALLOW")

    print("\n2. Instalando acervo de skills especializadas...")
    stats = install_skills(kit_dir)
    print(f"   [OK] Skills Nativas em ~/.agents/skills/: {stats['native']}")
    print(f"   [OK] Catálogo Ampliado em ~/projetos/config/Skills: {stats['catalog']}")

    print("\n3. Provisionando Dicionário Canônico de Automação & Aliases...")
    install_automation_dictionary(kit_dir)
    print("   [OK] Dicionário Canônico em ~/projetos/estruturas/dicionario_automacao_core.md")

    print("\n" + "=" * 65)
    print("✅ AMBIENTE 100% CALIBRADO E PRONTO PARA O USO DO AGENTE!")
    print("=" * 65)

if __name__ == "__main__":
    main()
