"""Roteamento inteligente de modelo e esforço de reasoning (Item 8).

Classificação:
- FAST: tarefa localizada, arquivo conhecido, sem termos de alta complexidade.
  Modelo: Flash, reasoning: low ou medium.
- STANDARD: tarefa moderada com múltiplos arquivos ou regras de negócio.
  Modelo: Flash, reasoning: medium.
- DEEP: arquitetura, segurança, OAuth/auth, migração, schema, investigação difícil, refactor transversal.
  Modelo: Flash/Pro, reasoning: high.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class RoutingTier(str, Enum):
    FAST = "FAST"
    STANDARD = "STANDARD"
    DEEP = "DEEP"


@dataclass
class ModelRoute:
    tier: RoutingTier
    model: str
    reasoning_effort: str  # "low", "medium", "high"
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier.value,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "rationale": self.rationale,
        }


class ModelRouter:
    """Classifica a complexidade da tarefa e seleciona o modelo e reasoning adequados."""

    DEEP_PATTERNS = [
        r"\barquitetura\b",
        r"\barchitecture\b",
        r"\bsegurança\b",
        r"\bsecurity\b",
        r"\boauth\b",
        r"\bautentica[çc][ãa]o\b",
        r"\bmigra[çc][ãa]o\b",
        r"\bmigration\b",
        r"\bschema\b",
        r"\binvestiga[çc][ãa]o\s+dif[íi]cil\b",
        r"\brefactor\s+transversal\b",
        r"\bcross-cutting\b",
        r"\bhardlock\b",
    ]

    FAST_PATTERNS = [
        r"\bfix\s+typo\b",
        r"\bdocumenta[çc][ãa]o\b",
        r"\bdocs\b",
        r"\bcoment[áa]rio\b",
        r"\bpequeno\s+ajuste\b",
        r"\bconstante\b",
        r"\bconfigura[çc][ãa]o\s+simples\b",
    ]

    @classmethod
    def classify(
        cls,
        title: str,
        body: str,
        file_count: int = 1,
        labels: Optional[List[str]] = None,
    ) -> ModelRoute:
        combined = f"{title} {body}".lower()
        lbls = [l.lower() for l in (labels or [])]

        # 1. Checagem explícita em labels
        if "tier:deep" in lbls or "reasoning:high" in lbls:
            return ModelRoute(
                tier=RoutingTier.DEEP,
                model="gemini-2.5-pro",
                reasoning_effort="high",
                rationale="Explicitamente rotulado como tier:deep/reasoning:high",
            )
        if "tier:fast" in lbls or "reasoning:low" in lbls:
            return ModelRoute(
                tier=RoutingTier.FAST,
                model="gemini-2.5-flash",
                reasoning_effort="low",
                rationale="Explicitamente rotulado como tier:fast",
            )

        # 2. Avaliação de padrões DEEP
        for pat in cls.DEEP_PATTERNS:
            if re.search(pat, combined):
                return ModelRoute(
                    tier=RoutingTier.DEEP,
                    model="gemini-2.5-flash",
                    reasoning_effort="high",
                    rationale=f"Gatilho DEEP detectado ({pat})",
                )

        # 3. Avaliação de padrões FAST
        is_small_scope = (file_count <= 2)
        for pat in cls.FAST_PATTERNS:
            if re.search(pat, combined) and is_small_scope:
                return ModelRoute(
                    tier=RoutingTier.FAST,
                    model="gemini-2.5-flash",
                    reasoning_effort="low",
                    rationale=f"Tarefa localizada de escopo restrito ({pat})",
                )

        if is_small_scope and len(body) < 1500:
            return ModelRoute(
                tier=RoutingTier.FAST,
                model="gemini-2.5-flash",
                reasoning_effort="medium",
                rationale="Escopo restrito com arquivos conhecidos e baixa ambiguidade",
            )

        # 4. Caso geral STANDARD
        return ModelRoute(
            tier=RoutingTier.STANDARD,
            model="gemini-2.5-flash",
            reasoning_effort="medium",
            rationale="Tarefa padrão: Flash com reasoning médio",
        )
