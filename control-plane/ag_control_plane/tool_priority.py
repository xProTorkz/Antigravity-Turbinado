"""Hierarquia e prioridade operacional estrita de ferramentas (Item 5).

Hierarquia canônica:
1. API
2. MCP
3. CLI
4. SDK
5. script Python/shell
6. HTTP autenticado
7. browser automation
8. AppleScript/UI automation

Browser e AppleScript/UI automation são estritamente o ÚLTIMO RECURSO.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict, List, Optional, Tuple


class ToolTier(IntEnum):
    API = 1
    MCP = 2
    CLI = 3
    SDK = 4
    SCRIPT = 5
    HTTP = 6
    BROWSER = 7
    APPLESCRIPT = 8


# Mapeamento de ferramentas conhecidas para seus tiers de prioridade
TOOL_TIER_MAPPING: Dict[str, ToolTier] = {
    # Tier 1: APIs diretas
    "api": ToolTier.API,
    "github_api": ToolTier.API,
    "rest_api": ToolTier.API,
    "fastapi": ToolTier.API,
    "gemini_api": ToolTier.API,
    # Tier 2: MCP (Model Context Protocol)
    "mcp": ToolTier.MCP,
    "call_mcp_tool": ToolTier.MCP,
    "aas-mcp": ToolTier.MCP,
    "gitkraken_mcp": ToolTier.MCP,
    # Tier 3: CLI
    "cli": ToolTier.CLI,
    "run_command": ToolTier.CLI,
    "git_cli": ToolTier.CLI,
    "pytest_cli": ToolTier.CLI,
    "gh_cli": ToolTier.CLI,
    # Tier 4: SDK
    "sdk": ToolTier.SDK,
    "google_genai_sdk": ToolTier.SDK,
    "boto3": ToolTier.SDK,
    # Tier 5: Scripts Shell / Python locais
    "script": ToolTier.SCRIPT,
    "python_script": ToolTier.SCRIPT,
    "shell_script": ToolTier.SCRIPT,
    # Tier 6: HTTP autenticado
    "http": ToolTier.HTTP,
    "urllib": ToolTier.HTTP,
    "requests": ToolTier.HTTP,
    "read_url_content": ToolTier.HTTP,
    # Tier 7: Browser automation (ÚLTIMO RECURSO)
    "browser": ToolTier.BROWSER,
    "playwright": ToolTier.BROWSER,
    "puppeteer": ToolTier.BROWSER,
    "selenium": ToolTier.BROWSER,
    "chrome_devtools": ToolTier.BROWSER,
    # Tier 8: AppleScript / UI automation (ÚLTIMO RECURSO)
    "applescript": ToolTier.APPLESCRIPT,
    "osascript": ToolTier.APPLESCRIPT,
    "ui_automation": ToolTier.APPLESCRIPT,
    "system_events": ToolTier.APPLESCRIPT,
}


class ToolPriorityPolicy:
    """Aplica a regra global de prioridade de ferramentas."""

    @staticmethod
    def get_tier(tool_name: str) -> ToolTier:
        lower = tool_name.lower().strip()
        for k, tier in TOOL_TIER_MAPPING.items():
            if k in lower:
                return tier
        return ToolTier.SCRIPT

    @classmethod
    def enforce_priority(
        cls, candidate_tool: str, available_tools: List[str]
    ) -> Tuple[bool, str, Optional[str]]:
        """Verifica se o uso da ferramenta candidata respeita a prioridade.

        Se for Browser ou AppleScript e houver ferramenta de maior prioridade (API, MCP, CLI, SDK, Script),
        retorna aviso/bloqueio com a recomendação da melhor ferramenta.
        """
        cand_tier = cls.get_tier(candidate_tool)

        if cand_tier in (ToolTier.BROWSER, ToolTier.APPLESCRIPT):
            # Procura alternativa de maior prioridade entre as disponíveis
            better_alternatives = []
            for avail in available_tools:
                avail_tier = cls.get_tier(avail)
                if avail_tier < cand_tier:
                    better_alternatives.append((avail_tier, avail))

            if better_alternatives:
                better_alternatives.sort(key=lambda x: x[0])
                best = better_alternatives[0][1]
                msg = (
                    f"PRIORITY_VIOLATION: Ferramenta '{candidate_tool}' (Tier {cand_tier.name}) "
                    f"é último recurso. Alternativa de maior prioridade disponível: '{best}' (Tier {better_alternatives[0][0].name})."
                )
                return False, msg, best

        return True, "TOOL_PRIORITY=PASS", None

    @classmethod
    def get_preferred_tool(cls, available_tools: List[str]) -> Optional[str]:
        """Retorna a ferramenta de maior prioridade da lista."""
        if not available_tools:
            return None
        sorted_tools = sorted(available_tools, key=lambda t: cls.get_tier(t))
        return sorted_tools[0]


ToolPriorityManager = ToolPriorityPolicy

