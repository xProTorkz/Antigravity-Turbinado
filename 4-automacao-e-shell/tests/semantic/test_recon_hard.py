import json
import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_recon_project_hard_definition():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    recon_it = reg["intents"].get("recon.project.hard")
    assert recon_it is not None

    plan = recon_it.get("execution_plan")
    assert plan is not None
    assert plan.get("strategy") == "DAG"
    assert "technical_inventory" in plan.get("output", "")

    # Invariantes: Somente leitura e zero mutação
    assert recon_it.get("destructive") is False
    se = recon_it.get("side_effects", {})
    assert se.get("filesystem_write") is False
    assert se.get("process_kill") is False

def test_recon_resolution_and_constraints(resolver):
    res = resolver.resolve("faça um reconhecimento")
    assert res is not None
    assert res.intent_id == "recon.project.hard"
    assert res.action == "RECON"
    assert res.constraints.get("read_only") is True
    assert res.constraints.get("mutation_allowed") is False
    assert res.execution_plan.get("strategy") == "DAG"
