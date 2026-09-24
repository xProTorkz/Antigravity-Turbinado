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

def install_skills(base_kit_dir: Path, custom_home: Path = None) -> dict:
    """Instala as 100 skills nativas e descompacta as 2.492 skills do catálogo."""
    home = custom_home or Path.home()
    agents_skills_dir = home / ".agents" / "skills"
    agents_skills_dir.mkdir(parents=True, exist_ok=True)

    projects_dir = home / "projetos"
    projects_dir.mkdir(parents=True, exist_ok=True)
    catalog_skills_dir = projects_dir / "config" / "Skills"
    catalog_skills_dir.mkdir(parents=True, exist_ok=True)

    stats = {"native": 0, "catalog": 0}

    # 1. Instalar as 100 skills nativas em ~/.agents/skills/
    src_native = base_kit_dir / "skills" / "native"
    if not src_native.exists():
        # Fallback local se estiver executando no próprio repositório original
        src_native = Path.home() / ".agents" / "skills"

    if src_native.exists():
        for skill_dir in src_native.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                dest = agents_skills_dir / skill_dir.name
                if not dest.exists():
                    shutil.copytree(skill_dir, dest, dirs_exist_ok=True)
                stats["native"] += 1

    # 2. Descompactar o catálogo de 2.492 skills em ~/projetos/config/Skills/
    tar_path = base_kit_dir / "skills" / "catalog.tar.gz"
    if tar_path.exists():
        with tarfile.open(tar_path, "r:gz") as tar:
            # Extrai apenas as pastas de skills para catalog_skills_dir
            for member in tar.getmembers():
                # se tiver prefixo Skills/, remove o prefixo
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
    else:
        # Fallback para pasta local se disponível
        source_catalog = Path.home() / "projetos" / "config" / "Skills"
        if source_catalog.exists() and source_catalog != catalog_skills_dir:
            for item in source_catalog.iterdir():
                if item.is_dir():
                    dest = catalog_skills_dir / item.name
                    if not dest.exists():
                        shutil.copytree(item, dest, dirs_exist_ok=True)

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

    print("\n" + "=" * 65)
    print("✅ AMBIENTE 100% CALIBRADO E PRONTO PARA O USO DO AGENTE!")
    print("=" * 65)

if __name__ == "__main__":
    main()
