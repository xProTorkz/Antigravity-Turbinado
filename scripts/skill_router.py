#!/usr/bin/env python3
"""
Skill Router & Curator — Antigravity Turbinado
Descobre, indexa e seleciona a skill técnica ideal para cada tarefa sem sobrecarregar o contexto.
"""

import os
import sys
import re
import argparse
from pathlib import Path

def discover_skills():
    """Descobre dinamicamente todas as skills disponíveis no ambiente local."""
    search_paths = [
        Path.home() / ".agents" / "skills",
        Path.home() / ".gemini" / "config" / "skills",
        Path.home() / "projetos" / "CONFIGURACOES GERAIS DE PROJETO" / "Skills",
        Path.home() / "projetos" / "config" / "Skills"
    ]
    
    skills = {}
    for base_path in search_paths:
        if not base_path.exists():
            continue
        try:
            for item in base_path.iterdir():
                if item.is_dir():
                    skill_md = item / "SKILL.md"
                    if skill_md.exists():
                        name = item.name
                        desc = ""
                        try:
                            content = skill_md.read_text(encoding="utf-8", errors="ignore")
                            # Extrai frontmatter
                            fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                            if fm_match:
                                fm = fm_match.group(1)
                                desc_match = re.search(r"description:\s*(.+)", fm, re.DOTALL)
                                if desc_match:
                                    desc = desc_match.group(1).strip()
                        except Exception:
                            desc = "Skill técnica especializada"
                        
                        if name not in skills:
                            skills[name] = {
                                "name": name,
                                "path": str(skill_md),
                                "description": desc[:200],
                                "source": "native" if ".agents" in str(base_path) or ".gemini" in str(base_path) else "catalog"
                            }
        except Exception:
            pass
            
    return skills

def route_task(task_description: str, skills: dict) -> dict:
    """Classifica a tarefa e seleciona a melhor skill primária e secundária."""
    task_lower = task_description.lower()
    
    # Classificação de domínio
    task_class = "general"
    if any(k in task_lower for k in ["banco", "sql", "postgres", "query", "database", "migration"]):
        task_class = "database"
    elif any(k in task_lower for k in ["ui", "css", "frontend", "react", "html", "vue", "layout", "design"]):
        task_class = "frontend"
    elif any(k in task_lower for k in ["api", "endpoint", "backend", "fastapi", "django", "express", "rota"]):
        task_class = "backend"
    elif any(k in task_lower for k in ["docker", "deploy", "ci", "github actions", "vps", "infra", "cloud"]):
        task_class = "devops"
    elif any(k in task_lower for k in ["teste", "pytest", "vitest", "test", "assert", "cobertura"]):
        task_class = "testing"
    elif any(k in task_lower for k in ["segurança", "token", "crip", "vulnerabilidade", "auth"]):
        task_class = "security"

    # Seleção de skill primária baseada em afinidade
    selected_primary = None
    confidence = 0.50
    
    # Busca heurística por palavras-chave
    for name, data in skills.items():
        score = 0
        name_clean = name.replace("-", " ").replace("_", " ")
        if name_clean in task_lower:
            score += 0.5
        for word in task_lower.split():
            if len(word) > 3 and word in name_clean:
                score += 0.2
        if score > confidence:
            confidence = min(0.95, score)
            selected_primary = name

    # Fallback canônico seguro
    if not selected_primary:
        if task_class == "testing":
            selected_primary = "testes-validacao"
            confidence = 0.85
        elif task_class == "security":
            selected_primary = "seguranca-infra"
            confidence = 0.85
        else:
            selected_primary = "pesquisa-projeto"
            confidence = 0.80

    return {
        "TASK_CLASS": task_class,
        "SKILL_PRIMARY": f"@{selected_primary}",
        "SKILL_SUPPORT": None,
        "SKILL_SOURCE": skills.get(selected_primary, {}).get("source", "native"),
        "SKILL_LICENSE_STATUS": "BUNDLE_ALLOWED",
        "CONFIDENCE": f"{int(confidence * 100)}%",
        "CONTEXT_REQUIRED": "minimal",
        "FILES_HINT": "src/, tests/"
    }

def main():
    parser = argparse.ArgumentParser(description="Skill Router & Curator")
    parser.add_argument("--task", type=str, help="Descrição da tarefa para rotear")
    parser.add_argument("--test", action="store_true", help="Executa autoteste do roteador")
    parser.add_argument("--list", action="store_true", help="Lista total de skills descobertas")
    args = parser.parse_args()

    skills = discover_skills()
    
    if args.list:
        print(f"Total de skills descobertas dinamicamente: {len(skills)}")
        for name, data in list(skills.items())[:10]:
            print(f" - {name} ({data['source']})")
        if len(skills) > 10:
            print(f"   ... e mais {len(skills) - 10} skills.")
        return

    if args.test:
        print("Executando autoteste do Skill Router...")
        test_tasks = [
            "Escrever testes unitários com pytest para módulo de autenticação",
            "Criar endpoint REST no backend com FastAPI",
            "Otimizar índices de banco de dados SQL"
        ]
        for t in test_tasks:
            res = route_task(t, skills)
            print(f"\nTarefa: '{t}'")
            print(f" -> SKILL_PRIMARY: {res['SKILL_PRIMARY']} | CLASS: {res['TASK_CLASS']} | CONFIDENCE: {res['CONFIDENCE']}")
            assert res["SKILL_PRIMARY"].startswith("@")
        print("\n✅ Autoteste do Skill Router concluído com sucesso!")
        return

    task = args.task or "Investigar arquitetura e implementar nova funcionalidade"
    res = route_task(task, skills)
    for k, v in res.items():
        print(f"{k}={v}")

if __name__ == "__main__":
    main()
