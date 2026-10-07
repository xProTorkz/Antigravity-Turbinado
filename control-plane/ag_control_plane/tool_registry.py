"""Registro e controle de permissões de ferramentas/plugins da assistente Alexa."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class PermissionTier(str, Enum):
    READ = "READ"
    WRITE_LOW_RISK = "WRITE_LOW_RISK"
    WRITE_HIGH_RISK = "WRITE_HIGH_RISK"
    FINANCIAL_SECURITY = "FINANCIAL_SECURITY"


@dataclass
class ToolDefinition:
    name: str
    tier: PermissionTier
    scopes: List[str]
    description: str
    requires_human_confirmation: bool = False


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        defaults = [
            ToolDefinition(
                name="antigravity",
                tier=PermissionTier.WRITE_HIGH_RISK,
                scopes=["project:execute", "direct:execute"],
                description="Executa tarefas de código e projetos no workspace canônico Antigravity.",
                requires_human_confirmation=False,  # Governed by Router & Task queue
            ),
            ToolDefinition(
                name="github",
                tier=PermissionTier.WRITE_LOW_RISK,
                scopes=["repo:read", "issue:write"],
                description="Lê repositório e cria issues de tarefas no GitHub.",
                requires_human_confirmation=False,
            ),
            ToolDefinition(
                name="project_status",
                tier=PermissionTier.READ,
                scopes=["project:read"],
                description="Consulta status de repositório, branch, leases e serviços locais.",
                requires_human_confirmation=False,
            ),
            ToolDefinition(
                name="calendar",
                tier=PermissionTier.WRITE_LOW_RISK,
                scopes=["calendar:read", "calendar:write"],
                description="Consulta agenda e cria compromissos.",
                requires_human_confirmation=False,
            ),
            ToolDefinition(
                name="gmail",
                tier=PermissionTier.WRITE_HIGH_RISK,
                scopes=["mail:read", "mail:send"],
                description="Lê resumos e envia e-mails aprovados.",
                requires_human_confirmation=True,
            ),
            ToolDefinition(
                name="drive",
                tier=PermissionTier.WRITE_LOW_RISK,
                scopes=["drive:read", "drive:write"],
                description="Acessa e gerencia documentos no Google Drive.",
                requires_human_confirmation=False,
            ),
            ToolDefinition(
                name="contacts",
                tier=PermissionTier.READ,
                scopes=["contacts:read"],
                description="Consulta informações de contatos.",
                requires_human_confirmation=False,
            ),
            ToolDefinition(
                name="mac_apps",
                tier=PermissionTier.WRITE_LOW_RISK,
                scopes=["app:control", "shortcuts:run"],
                description="Executa aplicativos e Apple Shortcuts aprovados no Mac.",
                requires_human_confirmation=False,
            ),
            ToolDefinition(
                name="alexa",
                tier=PermissionTier.READ,
                scopes=["voice:speak"],
                description="Interface de voz e interação Alexa.",
                requires_human_confirmation=False,
            ),
            ToolDefinition(
                name="home_automation",
                tier=PermissionTier.WRITE_LOW_RISK,
                scopes=["home:control"],
                description="Controla dispositivos domésticos inteligentes.",
                requires_human_confirmation=False,
            ),
            ToolDefinition(
                name="finance_payment",
                tier=PermissionTier.FINANCIAL_SECURITY,
                scopes=["finance:execute"],
                description="Operações financeiras ou de pagamento.",
                requires_human_confirmation=True,
            ),
        ]
        for t in defaults:
            self._tools[t.name] = t

    def register_tool(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def check_permission(
        self,
        tool_name: str,
        requested_scope: Optional[str] = None,
        confirmed: bool = False,
    ) -> Tuple[bool, str]:
        tool = self._tools.get(tool_name)
        if not tool:
            return False, f"Ferramenta '{tool_name}' não está cadastrada no registro."

        if requested_scope and requested_scope not in tool.scopes:
            return False, f"Escopo '{requested_scope}' não permitido para a ferramenta '{tool_name}'."

        if tool.tier == PermissionTier.FINANCIAL_SECURITY:
            if not confirmed:
                return False, f"A ferramenta '{tool_name}' requer confirmação humana explícita (FINANCIAL_SECURITY)."

        if tool.requires_human_confirmation and not confirmed:
            return False, f"A operação com a ferramenta '{tool_name}' requer confirmação do usuário."

        return True, "Permissão concedida."
