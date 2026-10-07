#!/usr/bin/env python3
"""
mcp_http_server.py — Servidor MCP via HTTP/SSE para integração com ChatGPT

Expõe o Jarvis Control Plane via protocolo MCP (Model Context Protocol)
sobre HTTP com SSE (Server-Sent Events), compatível com ChatGPT e Claude.

Roda em: http://localhost:8766/sse (SSE stream)
         http://localhost:8766/messages (POST endpoint)

Uso:
    python3 mcp_http_server.py
    python3 mcp_http_server.py --port 8766

Tools expostas (read + write):
    - get_control_plane_status
    - get_active_project
    - get_project_state
    - get_queue_status
    - get_git_status
    - get_recent_diff
    - send_command          ← envia comando para o Antigravity executar
    - activate_orb          ← ativa o Orb de voz
    - get_projects_list     ← lista todos os projetos registrados
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

BRIDGE_BASE = "http://localhost:8765"


def _get(path: str) -> dict:
    """Faz GET no bridge local."""
    try:
        with urllib.request.urlopen(f"{BRIDGE_BASE}{path}", timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e), "path": path}


def _get_auth_token() -> str:
    """Recupera o token do dispositivo chatgpt_mcp_bridge registrado localmente."""
    dev_path = ROOT_DIR / ".control-plane" / "remote" / "paired_devices.json"
    if dev_path.exists():
        try:
            with open(dev_path, "r", encoding="utf-8") as f:
                devs = json.load(f)
                return devs.get("chatgpt_mcp_bridge", {}).get("token", "")
        except Exception:
            pass
    return ""


def _post(path: str, body: dict) -> dict:
    """Faz POST no bridge local autenticado com token do dispositivo."""
    try:
        data = json.dumps(body).encode()
        headers = {"Content-Type": "application/json"}
        token = _get_auth_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        req = urllib.request.Request(
            f"{BRIDGE_BASE}{path}",
            data=data,
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e), "path": path}


# Importar FastMCP para expor via HTTP/SSE
try:
    from fastmcp import FastMCP
except ImportError:
    print("❌ FastMCP não instalado. Execute: pip install fastmcp", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP(
    name="jarvis-control-plane",
    instructions="""
Você está conectado ao Jarvis Control Plane de Sr. Lucas (MacBook Air).
Este servidor MCP fornece acesso em tempo real aos projetos, estado do Git,
fila de execução e controle do Antigravity.

Projetos disponíveis (slugs):
- antigravity-control-plane (Jarvis)
- derivbot
- sharkbot
- api-catalogador
- minha-agenda
- project-blueprint

Para executar código no Mac, use send_command com a instrução desejada.
O Antigravity irá executar a tarefa no projeto ativo.
"""
)


@mcp.tool()
def get_control_plane_status() -> dict:
    """Obtém o status completo do Jarvis Control Plane: daemons, projetos, executor."""
    return _get("/api/context/status")


@mcp.tool()
def get_active_project() -> dict:
    """Retorna o projeto atualmente ativo no Control Plane."""
    return _get("/api/context/active_project")


@mcp.tool()
def get_projects_list() -> dict:
    """Lista todos os projetos registrados no Control Plane com seus estados."""
    status = _get("/api/context/status")
    queue = _get("/api/context/queue")
    return {
        "projects_count": status.get("projects_count", 0),
        "active_project": status.get("active_project"),
        "queue": queue,
        "known_slugs": [
            "antigravity-control-plane",
            "derivbot",
            "sharkbot",
            "api-catalogador",
            "minha-agenda",
            "project-blueprint"
        ]
    }


@mcp.tool()
def get_project_state(project_slug: str) -> dict:
    """
    Consulta o estado completo de um projeto registrado.

    Args:
        project_slug: Identificador do projeto (ex: antigravity-control-plane, derivbot, sharkbot)
    """
    return _get(f"/api/context/project/{project_slug}")


@mcp.tool()
def get_queue_status() -> dict:
    """Lista todas as tarefas e leases ativos nas filas dos projetos."""
    return _get("/api/context/queue")


@mcp.tool()
def get_git_status(project_slug: str) -> dict:
    """
    Executa inspeção Git read-only no workspace do projeto.
    Retorna branch atual, último commit, arquivos modificados.

    Args:
        project_slug: Identificador do projeto (ex: antigravity-control-plane)
    """
    return _get(f"/api/context/project/{project_slug}/git")


@mcp.tool()
def get_recent_diff(project_slug: str) -> dict:
    """
    Retorna resumo das mudanças recentes no código do projeto.

    Args:
        project_slug: Identificador do projeto
    """
    return _get(f"/api/context/project/{project_slug}/diff")


@mcp.tool()
def get_recent_actions(project_slug: str, limit: int = 10) -> dict:
    """
    Retorna histórico recente de ações do projeto.

    Args:
        project_slug: Identificador do projeto
        limit: Número máximo de ações a retornar (padrão: 10)
    """
    return _get(f"/api/context/project/{project_slug}/actions?limit={limit}")


@mcp.tool()
def get_runtime_health() -> dict:
    """Verifica a saúde do runtime: bridge, daemons, portas."""
    health = _get("/api/health")
    status = _get("/api/status")
    return {"health": health, "orb_status": status}


@mcp.tool()
def send_command(text: str, project: str = "") -> dict:
    """
    Envia um comando de texto para o Antigravity executar no Mac.
    Use para iniciar tarefas, executar código, fazer commits, etc.

    Args:
        text: Comando ou instrução a ser executada (ex: "execute os testes do projeto derivbot")
        project: Slug do projeto alvo (opcional, usa o projeto ativo se vazio)
    """
    body = {"text": text}
    if project:
        body["project"] = project
    return _post("/api/voice/command", body)


@mcp.tool()
def activate_orb() -> dict:
    """Ativa o Orb do Jarvis para iniciar uma sessão de voz/execução."""
    return _post("/api/activate", {"device_id": "chatgpt-mcp"})


@mcp.tool()
def stop_orb() -> dict:
    """Para o Orb do Jarvis."""
    return _post("/api/stop", {})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis MCP HTTP Server")
    parser.add_argument("--port", type=int, default=8766, help="Porta HTTP (padrão: 8766)")
    parser.add_argument("--host", default="0.0.0.0", help="Host (padrão: 0.0.0.0)")
    parser.add_argument("--transport", default="sse", choices=["sse", "streamable-http"],
                        help="Transporte MCP (padrão: sse)")
    args = parser.parse_args()

    print(f"🚀 Jarvis MCP HTTP Server")
    print(f"   Endereço: http://{args.host}:{args.port}")
    print(f"   SSE:      http://localhost:{args.port}/sse")
    print(f"   Messages: http://localhost:{args.port}/messages")
    print(f"   Tools:    11 tools expostas")
    print(f"   Bridge:   {BRIDGE_BASE}")
    print()

    # Testar bridge
    try:
        with urllib.request.urlopen(f"{BRIDGE_BASE}/api/health", timeout=3) as r:
            health = json.loads(r.read())
            print(f"✅ Bridge: {health.get('status', 'OK')}")
    except Exception as e:
        print(f"⚠️  Bridge offline: {e}")
        print("   Certifique-se de que o Jarvis Control Plane está rodando")

    mcp.run(transport=args.transport, host=args.host, port=args.port)
