#!/usr/bin/env python3
# ==============================================================================
# criar_e_executar.py — Motor Autônomo de Tarefas (Despacho GitHub + Execução)
# Ecossistema Sentinela Guardião / Antigravity Turbinado
# ==============================================================================
import os, sys, json, subprocess, argparse, datetime

BASE_PROJETOS = "/Users/lucasvinicius/projetos"

# Mapeamento canônico de projetos para repositórios GitHub
REPO_MAP = {
    "Zentinel": "xProTorkz/Zentinel",
    "Dados Bacbo": "xProTorkz/Dados-Bacbo",
    "Atende Ai": "xProTorkz/Atende-Ai",
    "Jarvis Assistente": "xProTorkz/Jarvis-Assistente",
    "Buy Station": "xProTorkz/Buy-Station",
    "Minha Agenda": "xProTorkz/Minha-Agenda",
    "Arena Beach": "xProTorkz/gestao-arena",
    "Nu Bank": "xProTorkz/Nu-Bank",
    "Premium Car": "xProTorkz/PremiumCar",
    "Skills Catalog": "xProTorkz/Skills-Catalog",
    "Chama Oferta": "xProTorkz/Chama-Oferta",
    "Whaticket Meta": "xProTorkz/Whaticket-Meta",
    "Deriv Bot": "xProTorkz/Deriv-Bot",
    "Config Bot": "xProTorkz/Config-Bot",
    "Antigravity Turbinado": "xProTorkz/Antigravity-Turbinado"
}

def resolver_repositorio(projeto):
    if projeto in REPO_MAP:
        return REPO_MAP[projeto]
    for cat in ["SISTEMAS", "APLICAÇÕES", "SITES", "BOTS"]:
        caminho = os.path.join(BASE_PROJETOS, cat, projeto)
        if os.path.exists(os.path.join(caminho, ".git")):
            try:
                url = subprocess.check_output(["git", "-C", caminho, "remote", "get-url", "origin"], stderr=subprocess.DEVNULL).decode().strip()
                if "github.com" in url:
                    partes = url.split("github.com")[1].lstrip(":").lstrip("/")
                    return partes.replace(".git", "")
            except Exception:
                pass
    return None

def criar_issue(projeto, repo, titulo, etapa, skill, scope, corpo):
    data_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    issue_title = f"[{projeto}] {titulo}"
    
    yaml_header = f"""```yaml
agent_task:
  version: 5.0
  target_project: "{projeto}"
  target_repo: "{repo}"
  pipeline_stage: "{etapa}"
  required_skill: "{skill}"
  priority: "P1_HIGH"
  type: "AUTONOMOUS_TASK"
  execution: "AUTONOMOUS_LOCAL"
  created_at_utc: "{data_utc}"
  assigned_agent: "antigravity-local"
  write_permission: true
```"""

    issue_body = f"""{yaml_header}

## 🎯 Contexto e Justificativa Arquitetural
{corpo}

## 🔒 Scope Lock Cirúrgico (Arquivos Autorizados)
{scope}

## 📋 Critérios de Aceitação (DoD)
- [ ] Implementação determinística sem refatoração oportunista.
- [ ] Preservação de estabilidade e integridade funcional.
- [ ] Test Before / Test After executado e validado.
- [ ] Sincronização verificável no GitHub.

## 🧪 Protocolo de Testes Mandatório
1. **Baseline (Antes):** Validar se o ambiente e testes existentes passam.
2. **Execução:** Aplicar alterações cirúrgicas no escopo autorizado.
3. **Validação (Depois):** Confirmar que o novo comportamento funciona e não há regressão.
"""

    cmd = ["gh", "issue", "create", "--repo", repo, "--title", issue_title, "--body", issue_body]
    res = subprocess.check_output(cmd).decode().strip()
    return res

def fechar_issue(repo, issue_id, commit_sha, arquivos_alterados, resumo):
    data_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    recibo = f"""### RECIBO OPERACIONAL DE ENCERRAMENTO (SENTINELA)

• **Tarefa / Issue:** #{issue_id}
• **Data e Horário:** {data_utc}
• **Resultado:** DONE / IMPLEMENTADO / VALIDADO / SINCRONIZADO
• **Componentes Alterados:**
{arquivos_alterados}
• **Evidências de Validação:** {resumo}
• **Commit SHA:** {commit_sha}
• **Status:** FECHADA COM SUCESSO.
"""
    subprocess.run(["gh", "issue", "comment", str(issue_id), "--repo", repo, "--body", recibo], check=True)
    subprocess.run(["gh", "issue", "close", str(issue_id), "--repo", repo], check=True)

def main():
    parser = argparse.ArgumentParser(description="Motor Autônomo de Criação e Despacho de Tarefas")
    parser.add_argument("-p", "--projeto", required=True, help="Nome do Projeto (ex: Zentinel, Dados Bacbo)")
    parser.add_argument("-t", "--titulo", required=True, help="Título da Tarefa")
    parser.add_argument("-e", "--etapa", default="06. Desenvolver", help="Etapa do Pipeline (14 etapas)")
    parser.add_argument("-s", "--skill", default="@backend", help="Skill técnica requerida")
    parser.add_argument("--scope", default="- Arquivos pertinentes à tarefa", help="Scope Lock")
    parser.add_argument("-b", "--corpo", default="Tarefa criada para execução autônoma.", help="Detalhamento")
    
    args = parser.parse_args()
    repo = resolver_repositorio(args.projeto)
    if not repo:
        print(f"❌ Erro: Repositório para o projeto '{args.projeto}' não encontrado.")
        sys.exit(1)
        
    print(f"🚀 Criando Issue oficial no GitHub: {repo}...")
    issue_url = criar_issue(args.projeto, repo, args.titulo, args.etapa, args.skill, args.scope, args.corpo)
    print(f"✅ Issue criada com sucesso: {issue_url}")

if __name__ == "__main__":
    main()
