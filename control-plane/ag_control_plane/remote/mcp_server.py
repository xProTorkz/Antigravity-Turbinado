#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Jarvis / Antigravity Local Context Bridge.
Provides standard, read-only MCP tool execution over stdio JSON-RPC 2.0.

Exposed Tools (Read-Only):
- get_control_plane_status
- get_active_project
- get_project_state
- get_queue_status
- get_git_status
- get_recent_actions
- get_recent_changed_files
- get_recent_diff_summary
- get_runtime_health
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ag_control_plane.remote.context_bridge import LocalContextBridge

logger = logging.getLogger("ag-mcp-server")

SERVER_NAME = "jarvis-control-plane-context"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "get_control_plane_status",
        "description": "Obtém o status operacional global do Jarvis Control Plane, daemons em execução e saúde do Mac.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "get_active_project",
        "description": "Retorna o projeto atualmente ativo, workspace e detalhes do lease/tarefa em execução.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "get_project_state",
        "description": "Consulta o estado completo de um projeto registrado (repo GitHub, workspace em disco, write_allowed, sessão).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_slug": {
                    "type": "string",
                    "description": "Identificador do projeto (ex: antigravity-control-plane, dado88x, sharkbot-automation, minha-agenda)",
                },
            },
            "required": ["project_slug"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_queue_status",
        "description": "Lista todas as tarefas e leases ativos nas filas dos projetos do Control Plane.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "get_git_status",
        "description": "Executa inspeção Git estritamente read-only no workspace do projeto (branch atual, último commit, arquivos modificados sanitizados).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_slug": {
                    "type": "string",
                    "description": "Identificador do projeto registrado",
                },
            },
            "required": ["project_slug"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_recent_actions",
        "description": "Retorna histórico recente de ações e commits Git sanitizados do projeto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_slug": {
                    "type": "string",
                    "description": "Identificador do projeto registrado",
                },
                "limit": {
                    "type": "integer",
                    "description": "Número máximo de commits/ações a retornar (padrão: 10)",
                    "default": 10,
                },
            },
            "required": ["project_slug"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_recent_changed_files",
        "description": "Lista arquivos modificados e não versionados do projeto, com bloqueio estrito contra .env e arquivos de segredos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_slug": {
                    "type": "string",
                    "description": "Identificador do projeto registrado",
                },
                "limit": {
                    "type": "integer",
                    "description": "Número máximo de arquivos a retornar (padrão: 20)",
                    "default": 20,
                },
            },
            "required": ["project_slug"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_recent_diff_summary",
        "description": "Retorna o sumário de diferenças (git diff --stat) sanitizado de um projeto registrado.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_slug": {
                    "type": "string",
                    "description": "Identificador do projeto registrado",
                },
            },
            "required": ["project_slug"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_runtime_health",
        "description": "Verifica a integridade geral do ecossistema Jarvis (portas locais, kill-switch, status de daemons).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]


class MCPServer:
    def __init__(self, bridge: Optional[LocalContextBridge] = None):
        self.bridge = bridge or LocalContextBridge(root_dir=ROOT_DIR)

    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {}) or {}

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {
                            "listChanged": False,
                        },
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION,
                    },
                },
            }

        if method == "notifications/initialized":
            return None

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS,
                },
            }

        if method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {}) or {}
            result_data = self._execute_tool(tool_name, args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result_data, indent=2, ensure_ascii=False),
                        }
                    ],
                    "isError": result_data.get("status") == "ERROR",
                },
            }

        if method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {},
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found",
            },
        }

    def _execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "get_control_plane_status":
            return self.bridge.get_control_plane_status()
        elif name == "get_active_project":
            return self.bridge.get_active_project()
        elif name == "get_project_state":
            slug = args.get("project_slug", "")
            return self.bridge.get_project_state(slug)
        elif name == "get_queue_status":
            return self.bridge.get_queue_status()
        elif name == "get_git_status":
            slug = args.get("project_slug", "")
            return self.bridge.get_git_status(slug)
        elif name == "get_recent_actions":
            slug = args.get("project_slug", "")
            limit = int(args.get("limit", 10))
            return self.bridge.get_recent_actions(slug, limit=limit)
        elif name == "get_recent_changed_files":
            slug = args.get("project_slug", "")
            limit = int(args.get("limit", 20))
            return self.bridge.get_recent_changed_files(slug, limit=limit)
        elif name == "get_recent_diff_summary":
            slug = args.get("project_slug", "")
            return self.bridge.get_recent_diff_summary(slug)
        elif name == "get_runtime_health":
            return self.bridge.get_runtime_health()
        else:
            return {"status": "ERROR", "error": f"Tool '{name}' unknown or unauthorized"}

    def run_stdio(self) -> None:
        """Runs the JSON-RPC loop reading from stdin and writing to stdout."""
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                req = json.loads(line_str)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {e}",
                    },
                }
                sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()


def main():
    server = MCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
