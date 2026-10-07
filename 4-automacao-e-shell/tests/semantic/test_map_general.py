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

def test_map_project_general_definition():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    map_it = reg["intents"].get("map.project.general")
    assert map_it is not None

    plan = map_it.get("execution_plan")
    assert plan is not None
    assert plan.get("strategy") == "DAG"
    assert "dependency_graph" in plan.get("output", "")

    # Validação de relacionamentos estruturados
    rel_edges = [s["action"] for s in plan.get("steps", [])]
    assert any("depends_on" in e for e in rel_edges)
    assert any("reads_writes" in e for e in rel_edges)
    assert any("listens_on" in e for e in rel_edges)

def test_map_resolution_and_output(resolver):
    res = resolver.resolve("faça um mapeamento geral")
    assert res is not None
    assert res.intent_id == "map.project.general"
    assert res.action == "MAP"
    assert res.execution_plan.get("strategy") == "DAG"
    assert res.resolved_surface in ["AGY_BACKGROUND", "HYBRID"]
