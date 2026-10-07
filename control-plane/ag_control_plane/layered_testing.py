"""Estratégia de Testes em Camadas (Layered Testing) (Item 13).

Camadas:
1. FAST_TIER (Durante a implementação contínua):
   - syntax check (py_compile)
   - lint focado apenas nos arquivos alterados
   - unit tests afetados diretamente
2. COMPONENT_TIER (Pós-implementação local):
   - testes do módulo/componente afetado
3. FULL_SUITE_TIER (Apenas em integração, risco alto ou antes de merge/release):
   - todos os testes do projeto
   - E2E / browser (apenas quando estritamente indispensável)
"""

from __future__ import annotations

import logging
import py_compile
import subprocess
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ag-layered-testing")


class LayerTier(str, Enum):
    SYNTAX = "SYNTAX"
    TARGETED_UNIT = "TARGETED_UNIT"
    COMPONENT = "COMPONENT"
    FULL_SUITE = "FULL_SUITE"


@dataclass
class LayerTestResult:
    tier: LayerTier
    passed: bool
    commands_executed: List[str]
    output: str
    duration_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier.value,
            "passed": self.passed,
            "commands_executed": self.commands_executed,
            "output": self.output[:500],
            "duration_ms": round(self.duration_ms, 2),
        }


class LayeredTestingRunner:
    """Executa testes em camadas para evitar execução de testes caros/E2E prematuramente."""

    @classmethod
    def check_syntax(cls, files: List[str], workspace_path: Path) -> LayerTestResult:
        """Camada 1: Validação de sintaxe ultra-rápida sem spawn de processo pesado."""
        import time
        t0 = time.perf_counter()
        errors = []
        checked = []

        for rel in files:
            p = workspace_path / rel
            if p.suffix == ".py" and p.exists():
                try:
                    py_compile.compile(str(p), doraise=True)
                    checked.append(rel)
                except py_compile.PyCompileError as e:
                    errors.append(f"{rel}: {e}")

        dt = (time.perf_counter() - t0) * 1000.0
        if errors:
            return LayerTestResult(
                tier=LayerTier.SYNTAX,
                passed=False,
                commands_executed=[f"py_compile ({len(checked)} files)"],
                output="\n".join(errors),
                duration_ms=dt,
            )

        return LayerTestResult(
            tier=LayerTier.SYNTAX,
            passed=True,
            commands_executed=[f"py_compile ({len(checked)} files)"],
            output=f"Sintaxe validada com sucesso em {len(checked)} arquivos.",
            duration_ms=dt,
        )

    @classmethod
    def run_targeted_unit(
        cls,
        test_files: List[str],
        workspace_path: Path,
        python_bin: Optional[Path] = None,
    ) -> LayerTestResult:
        """Camada 2: Roda apenas os testes unitários afetados diretamente."""
        import time
        t0 = time.perf_counter()

        if not test_files:
            return LayerTestResult(
                tier=LayerTier.TARGETED_UNIT,
                passed=True,
                commands_executed=[],
                output="Nenhum teste unitário afetado identificado.",
                duration_ms=0.0,
            )

        py = str(python_bin or (workspace_path / ".venv" / "bin" / "pytest"))
        if not Path(py).exists():
            py = sys.executable

        cmd = [py, "-m", "pytest"] if not py.endswith("pytest") else [py]
        cmd.extend(test_files)

        try:
            res = subprocess.run(
                cmd,
                cwd=str(workspace_path),
                capture_output=True,
                text=True,
                timeout=30,
            )
            dt = (time.perf_counter() - t0) * 1000.0
            return LayerTestResult(
                tier=LayerTier.TARGETED_UNIT,
                passed=(res.returncode == 0),
                commands_executed=[" ".join(cmd)],
                output=res.stdout + res.stderr,
                duration_ms=dt,
            )
        except Exception as e:
            dt = (time.perf_counter() - t0) * 1000.0
            return LayerTestResult(
                tier=LayerTier.TARGETED_UNIT,
                passed=False,
                commands_executed=[" ".join(cmd)],
                output=f"Erro ao executar testes focados: {e}",
                duration_ms=dt,
            )
