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

def test_audit_project_hard_dag_structure():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    audit_it = reg["intents"].get("audit.project.hard")
    assert audit_it is not None

    plan = audit_it.get("execution_plan")
    assert plan is not None, "execution_plan ausente em audit.project.hard"
    assert plan.get("strategy") == "DAG"
    assert len(plan.get("steps", [])) == 12, f"Esperado 12 steps na DAG, obtido: {len(plan.get('steps', []))}"
    assert len(plan.get("parallel_groups", [])) >= 2, "Esperado pelo menos 2 parallel groups"

    step_ids = [s["id"] for s in plan.get("steps", [])]
    expected_steps = [
        "step_1_identity", "step_2_git_integrity", "step_3_architecture",
        "step_4_dependencies", "step_5_runtime", "step_6_processes",
        "step_7_network", "step_8_configuration", "step_9_security_defensive",
        "step_10_database", "step_11_observability", "step_12_report"
    ]
    for exp in expected_steps:
        assert exp in step_ids, f"Step {exp} ausente na DAG de audit.project.hard"

def test_macro_audite_query_resolution(resolver):
    res = resolver.resolve("audite")
    assert res is not None
    assert res.intent_id == "audit.project.hard"
    assert res.depth == "HARD"
    assert res.constraints.get("read_only") is True
    assert res.constraints.get("mutation_allowed") is False
    assert res.execution_plan.get("strategy") == "DAG"

def test_macro_recon_query_resolution(resolver):
    res = resolver.resolve("faça um reconhecimento")
    assert res is not None
    assert res.intent_id == "recon.project.hard"
    assert res.depth == "HARD"
    assert res.constraints.get("read_only") is True
    assert res.execution_plan.get("strategy") == "DAG"
    assert "technical_inventory" in res.execution_plan.get("output", "")

def test_macro_map_query_resolution(resolver):
    res = resolver.resolve("faça um mapeamento geral")
    assert res is not None
    assert res.intent_id == "map.project.general"
    assert res.depth == "HARD"
    assert res.execution_plan.get("strategy") == "DAG"
    assert "dependency_graph" in res.execution_plan.get("output", "")
