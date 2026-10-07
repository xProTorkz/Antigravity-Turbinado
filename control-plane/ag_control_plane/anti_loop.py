"""Anti-Loop Guard & Progress Verification (Itens 6 e 7).

Regra:
- MAX_SAME_APPROACH_RETRIES = 3
- Se 3 tentativas da mesma abordagem não produzirem progresso verificável:
  STOP_APPROACH e executar ALTERNATIVE_PATH_SELECTION.
- Não considerar uma ação como progresso apenas porque um comando executou.
  Cada sequência deve produzir mudança de estado verificável (novo commit, arquivo alterado,
  resposta diferente, recurso criado, teste alterado, página diferente).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("ag-anti-loop")

MAX_SAME_APPROACH_RETRIES = 3


class ActionVerdictStatus(str, Enum):
    PROGRESS = "PROGRESS"
    NO_PROGRESS = "NO_PROGRESS"
    STOP_APPROACH = "STOP_APPROACH"


@dataclass
class ActionVerdict:
    status: ActionVerdictStatus
    approach: str
    no_progress_count: int
    message: str
    recommended_alternative: Optional[str] = None


class AntiLoopGuard:
    """Detecta estratégias improdutivas e loops repetidos de comandos sem progresso."""

    # Cadeia canônica de alternativas quando uma abordagem se esgota
    FALLBACK_CHAINS: Dict[str, List[str]] = {
        "browser": ["api", "cli", "mcp", "script"],
        "applescript": ["cli", "api", "mcp", "script"],
        "osascript": ["cli", "api", "mcp", "script"],
        "ui_automation": ["cli", "api", "mcp", "script"],
        "api": ["cli", "mcp", "script", "browser"],
        "cli": ["api", "mcp", "script"],
        "mcp": ["cli", "api", "script"],
        "script": ["cli", "api", "mcp"],
    }

    def __init__(self, max_retries: int = MAX_SAME_APPROACH_RETRIES):
        self.max_retries = max_retries
        self.no_progress_counter = 0
        self.current_approach: Optional[str] = None
        self.last_state_fingerprint: Optional[str] = None
        self.action_history: List[Dict[str, Any]] = []

    def record_step(
        self,
        approach: str,
        state_fingerprint: str,
        command_executed: bool = True,
        explicit_state_changed: Optional[bool] = None,
    ) -> ActionVerdict:
        """Registra uma ação executada e avalia se houve progresso real.

        Args:
            approach: Nome da abordagem (ex: 'browser', 'osascript', 'api', 'cli')
            state_fingerprint: Hash ou resumo do estado atual (ex: hash de arquivos, commit SHA, url atual)
            command_executed: Se o comando de fato executou com sucesso
            explicit_state_changed: Se True/False explícito foi fornecido
        """
        approach_normalized = approach.lower().strip()

        # Verifica mudança de estado
        if explicit_state_changed is not None:
            state_changed = explicit_state_changed
        else:
            state_changed = (
                self.last_state_fingerprint is not None
                and state_fingerprint != self.last_state_fingerprint
            )

        # Se for primeira ação
        if self.last_state_fingerprint is None:
            self.last_state_fingerprint = state_fingerprint
            self.current_approach = approach_normalized
            self.no_progress_counter = 0
            self.action_history.append({
                "approach": approach_normalized,
                "state_changed": True,
                "fingerprint": state_fingerprint,
            })
            return ActionVerdict(
                status=ActionVerdictStatus.PROGRESS,
                approach=approach_normalized,
                no_progress_count=0,
                message="Primeira ação registrada com sucesso.",
            )

        # Se a abordagem for a mesma e o estado não mudou
        same_approach = (approach_normalized == self.current_approach)
        if same_approach and not state_changed:
            self.no_progress_counter += 1
            logger.warning(
                f"[ANTI_LOOP] Tentativa {self.no_progress_counter}/{self.max_retries} "
                f"da abordagem '{approach_normalized}' sem mudança de estado verificável."
            )

            if self.no_progress_counter >= self.max_retries:
                alt = self._pick_alternative(approach_normalized)
                msg = (
                    f"STOP_APPROACH: A abordagem '{approach_normalized}' atingiu {self.no_progress_counter} "
                    f"tentativas consecutivas sem progresso verificável. Mude para: {alt}."
                )
                logger.error(f"[ANTI_LOOP] {msg}")
                return ActionVerdict(
                    status=ActionVerdictStatus.STOP_APPROACH,
                    approach=approach_normalized,
                    no_progress_count=self.no_progress_counter,
                    message=msg,
                    recommended_alternative=alt,
                )

            return ActionVerdict(
                status=ActionVerdictStatus.NO_PROGRESS,
                approach=approach_normalized,
                no_progress_count=self.no_progress_counter,
                message=f"Comando executado mas estado permaneceu idêntico (count={self.no_progress_counter}).",
            )

        # Se o estado mudou ou mudou de abordagem
        self.last_state_fingerprint = state_fingerprint
        self.current_approach = approach_normalized
        self.no_progress_counter = 0
        return ActionVerdict(
            status=ActionVerdictStatus.PROGRESS,
            approach=approach_normalized,
            no_progress_count=0,
            message="Progresso verificável confirmado (STATE_CHANGED=YES).",
        )

    def _pick_alternative(self, approach: str) -> str:
        candidates = self.FALLBACK_CHAINS.get(approach, ["cli", "api", "script"])
        return candidates[0] if candidates else "cli"

    def reset(self) -> None:
        self.no_progress_counter = 0
        self.current_approach = None
        self.last_state_fingerprint = None
        self.action_history.clear()
