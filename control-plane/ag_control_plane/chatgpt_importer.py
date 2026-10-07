"""Importador seguro e idempotente de histórico/exportação de conversas do ChatGPT."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from ag_control_plane.memory_manager import MemoryManager


class ChatGPTExportImporter:
    """Importa conversas/resumos autorizados do ChatGPT para a memória pessoal da Alexa."""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory = memory_manager or MemoryManager()

    def import_from_file(self, export_path: Path) -> Dict[str, Any]:
        """Lê um arquivo JSON de exportação de conversas e normaliza os tópicos na memória."""
        if not export_path.exists():
            return {
                "status": "PARTIAL",
                "human_gate": "CHATGPT_HISTORY_IMPORT_SOURCE_REQUIRED",
                "imported_count": 0,
                "error": f"Arquivo de exportação não encontrado: {export_path}",
            }

        try:
            content = json.loads(export_path.read_text(encoding="utf-8"))
        except Exception as err:
            return {
                "status": "ERROR",
                "imported_count": 0,
                "error": f"Erro ao decodificar JSON de exportação: {err}",
            }

        # Aceita lista de conversas (formato oficial OpenAI conversations.json) ou lista de fatos/resumos
        imported_facts = 0
        conversations = content if isinstance(content, list) else content.get("conversations", [])

        for item in conversations:
            if isinstance(item, dict):
                title = item.get("title", "").strip()
                if title and len(title) > 3 and not title.lower().startswith("new chat"):
                    fact_text = f"Tópico de interesse prévio: {title}"
                    res = self.memory.remember_fact(
                        fact=fact_text,
                        category="interesse_anterior",
                        source="chatgpt_export",
                        confidence="user_stated",
                    )
                    if res:
                        imported_facts += 1

        return {
            "status": "COMPLETED",
            "imported_count": imported_facts,
            "human_gate": None,
        }

    def import_manual_summary(self, summary_text: str, topic: str = "contexto_geral") -> Dict[str, Any]:
        """Importa um resumo/perfil fornecido manualmente pelo usuário."""
        lines = [line.strip() for line in summary_text.splitlines() if line.strip()]
        imported = 0
        for line in lines:
            if len(line) > 5 and not line.startswith("#"):
                self.memory.remember_fact(
                    fact=line,
                    category=topic,
                    source="user_summary",
                    confidence="verified",
                )
                imported += 1

        return {
            "status": "COMPLETED",
            "imported_count": imported,
            "human_gate": None,
        }
