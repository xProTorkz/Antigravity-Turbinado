#!/usr/bin/env python3
"""
/Users/lucasvinicius/projetos/mcp_sentinela.py
Servidor MCP Local (Stdio) para Gemini App e Spark BETA.
Conecta diretamente o Google Gemini ao GitHub da organização xProTorkz.
Zero necessidade de OAuth na nuvem, zero permissões manuais e zero digitação de token.
"""
import sys
import json
import urllib.request
import urllib.error
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", os.environ.get("GH_TOKEN", ""))

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

TOOLS_DEFINITIONS = [
    {
        "name": "criar_tarefa_github",
        "description": "Cria uma nova Issue oficial no GitHub no repositório do projeto informado com contrato agent_task v5 e Scope Lock. NUNCA pede token ao usuário.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "projeto": {
                    "type": "string",
                    "description": "Nome do projeto (ex: Zentinel, Dados Bacbo, Atende Ai, Jarvis Assistente, Buy Station, etc.)"
                },
                "titulo": {
                    "type": "string",
                    "description": "Título claro e sucinto da tarefa"
                },
                "etapa": {
                    "type": "string",
                    "description": "Etapa do pipeline de 14 etapas (ex: '06. Desenvolver', '08. Testar', '10. Homologar')",
                    "default": "06. Desenvolver"
                },
                "skill": {
                    "type": "string",
                    "description": "Skill requerida (ex: '@backend', '@frontend', '@seguranca')",
                    "default": "@backend"
                },
                "scope_lock": {
                    "type": "string",
                    "description": "Arquivos específicos autorizados para alteração"
                },
                "detalhes": {
                    "type": "string",
                    "description": "Contexto técnico, justificativa e o que deve ser implementado"
                }
            },
            "required": ["projeto", "titulo"]
        }
    },
    {
        "name": "listar_projetos_repositorios",
        "description": "Retorna o catálogo completo de todos os projetos ativos de Lucas Vinicius e seus repositórios no GitHub.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "consultar_tarefas_abertas",
        "description": "Lista todas as Issues abertas no repositório do projeto especificado.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "projeto": {
                    "type": "string",
                    "description": "Nome do projeto (ex: Zentinel, Dados Bacbo, Atende Ai, Jarvis Assistente)"
                }
            },
            "required": ["projeto"]
        }
    },
    {
        "name": "obter_detalhes_tarefa",
        "description": "Obtém os detalhes completos de uma Issue específica pelo número e projeto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "projeto": {
                    "type": "string",
                    "description": "Nome do projeto (ex: Zentinel, Dados Bacbo)"
                },
                "issue_id": {
                    "type": "integer",
                    "description": "Número da Issue (ex: 1, 2, 25)"
                }
            },
            "required": ["projeto", "issue_id"]
        }
    },
    {
        "name": "fechar_tarefa_github",
        "description": "Fecha uma Issue no GitHub informando o resumo e evidências de conclusão.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "projeto": {
                    "type": "string",
                    "description": "Nome do projeto (ex: Zentinel, Dados Bacbo)"
                },
                "issue_id": {
                    "type": "integer",
                    "description": "Número da Issue (ex: 1, 2)"
                },
                "comentario": {
                    "type": "string",
                    "description": "Resumo da validação e encerramento da tarefa"
                }
            },
            "required": ["projeto", "issue_id"]
        }
    }
]

def github_api_request(endpoint, method="GET", data=None):
    url = f"https://api.github.com/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Sentinela-MCP-Local/1.0"
    }
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return {"error": e.code, "detail": json.loads(err_body)}
        except Exception:
            return {"error": e.code, "detail": err_body}
    except Exception as e:
        return {"error": 500, "detail": str(e)}

def handle_tool_call(tool_name, arguments):
    if tool_name == "listar_projetos_repositorios":
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(REPO_MAP, indent=2, ensure_ascii=False)
                }
            ]
        }
    
    elif tool_name == "consultar_tarefas_abertas":
        projeto = arguments.get("projeto", "").strip()
        repo = REPO_MAP.get(projeto)
        if not repo:
            for k, v in REPO_MAP.items():
                if k.lower() == projeto.lower():
                    repo = v
                    break
        if not repo:
            return {"isError": True, "content": [{"type": "text", "text": f"Projeto '{projeto}' não encontrado no catálogo."}]}
        
        issues = github_api_request(f"repos/{repo}/issues?state=open")
        if isinstance(issues, dict) and "error" in issues:
            return {"isError": True, "content": [{"type": "text", "text": f"Erro na API do GitHub: {json.dumps(issues)}"}]}
        
        resumo = [{"id": i.get("number"), "titulo": i.get("title"), "url": i.get("html_url")} for i in issues]
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(resumo, indent=2, ensure_ascii=False)
                }
            ]
        }

    elif tool_name == "obter_detalhes_tarefa":
        projeto = arguments.get("projeto", "").strip()
        issue_id = arguments.get("issue_id")
        repo = REPO_MAP.get(projeto)
        if not repo:
            for k, v in REPO_MAP.items():
                if k.lower() == projeto.lower():
                    repo = v
                    break
        if not repo:
            return {"isError": True, "content": [{"type": "text", "text": f"Projeto '{projeto}' não encontrado."}]}
        
        issue = github_api_request(f"repos/{repo}/issues/{issue_id}")
        if isinstance(issue, dict) and "error" in issue:
            return {"isError": True, "content": [{"type": "text", "text": f"Erro ao buscar Issue: {json.dumps(issue)}"}]}
        
        info = {
            "numero": issue.get("number"),
            "titulo": issue.get("title"),
            "estado": issue.get("state"),
            "corpo": issue.get("body"),
            "url": issue.get("html_url"),
            "autor": issue.get("user", {}).get("login")
        }
        return {"content": [{"type": "text", "text": json.dumps(info, indent=2, ensure_ascii=False)}]}

    elif tool_name == "fechar_tarefa_github":
        projeto = arguments.get("projeto", "").strip()
        issue_id = arguments.get("issue_id")
        comentario = arguments.get("comentario", "Tarefa concluída e validada conforme governança Sentinela.").strip()
        repo = REPO_MAP.get(projeto)
        if not repo:
            for k, v in REPO_MAP.items():
                if k.lower() == projeto.lower():
                    repo = v
                    break
        if not repo:
            return {"isError": True, "content": [{"type": "text", "text": f"Projeto '{projeto}' não encontrado."}]}
        
        github_api_request(f"repos/{repo}/issues/{issue_id}/comments", method="POST", data={"body": f"### 🏁 Encerramento de Tarefa\n\n{comentario}"})
        patch_res = github_api_request(f"repos/{repo}/issues/{issue_id}", method="PATCH", data={"state": "closed"})
        if isinstance(patch_res, dict) and "error" in patch_res:
            return {"isError": True, "content": [{"type": "text", "text": f"Erro ao fechar issue: {json.dumps(patch_res)}"}]}
        
        return {"content": [{"type": "text", "text": f"✅ Issue #{issue_id} no repositório '{repo}' foi encerrada com sucesso!"}]}

    elif tool_name == "criar_tarefa_github":
        projeto = arguments.get("projeto", "").strip()
        titulo = arguments.get("titulo", "").strip()
        etapa = arguments.get("etapa", "06. Desenvolver").strip()
        skill = arguments.get("skill", "@backend").strip()
        scope_lock = arguments.get("scope_lock", "- Modificar estritamente os arquivos necessários para esta tarefa.").strip()
        detalhes = arguments.get("detalhes", "Execução planejada pelo Cérebro Orquestrador Gemini.").strip()

        repo = REPO_MAP.get(projeto)
        if not repo:
            for k, v in REPO_MAP.items():
                if k.lower() == projeto.lower():
                    repo = v
                    projeto = k
                    break

        if not repo:
            return {"isError": True, "content": [{"type": "text", "text": f"Projeto '{projeto}' não encontrado no catálogo oficial."}]}

        data_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        issue_title = f"[{projeto}] {titulo}"
        issue_body = f"""```yaml
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
```

## 🎯 Contexto e Justificativa Arquitetural
{detalhes}

## 🔒 Scope Lock Cirúrgico (Arquivos Autorizados)
{scope_lock}

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

        payload = {
            "title": issue_title,
            "body": issue_body
        }

        resp = github_api_request(f"repos/{repo}/issues", method="POST", data=payload)
        if isinstance(resp, dict) and "error" in resp:
            return {"isError": True, "content": [{"type": "text", "text": f"Falha ao criar Issue no GitHub: {json.dumps(resp)}"}]}

        issue_url = resp.get("html_url")
        issue_num = resp.get("number")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ SUCESSO! Issue #{issue_num} criada oficialmente no repositório '{repo}':\n👉 URL: {issue_url}\n\nO Antigravity local já pode executar o código guiado pelo contrato da Issue."
                }
            ]
        }

    return {"isError": True, "content": [{"type": "text", "text": f"Ferramenta desconhecida: {tool_name}"}]}

def process_message(req):
    rpc_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "sentinela-github-mcp",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {}}
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "tools": TOOLS_DEFINITIONS
            }
        }
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        res = handle_tool_call(name, args)
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": res
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

def main():
    # Loop de leitura Stdio JSON-RPC
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = process_message(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Erro processando mensagem MCP: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
