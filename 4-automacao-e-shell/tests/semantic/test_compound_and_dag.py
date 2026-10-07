import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_compound_dag_pipeline(resolver):
    # Teste de pipeline composto: "reconheça o projeto, audite e depois me mostre os problemas"
    phrase = "reconheça o projeto, audite e depois me mostre os problemas"
    res = resolver.resolve(phrase)

    assert res is not None
    assert res.is_compound is True
    assert len(res.plan_steps) == 3
    assert "recon" in res.plan_steps[0]
    assert "audit" in res.plan_steps[1]
    assert "report.problems" == res.plan_steps[2]

    # Validação do grafo de dependências
    assert len(res.dependencies) == 2
    step2_key = f"step_2_{res.plan_steps[1]}"
    step3_key = f"step_3_{res.plan_steps[2]}"
    assert res.dependencies[step2_key] == [f"step_1_{res.plan_steps[0]}"]
    assert res.dependencies[step3_key] == [step2_key]

def test_compound_with_negation(resolver):
    # Teste: "mapeia tudo mas não altera nada"
    phrase = "mapeia tudo mas não altera nada"
    res = resolver.resolve(phrase)

    assert res is not None
    assert res.action == "MAP"
    assert res.constraints["read_only"] is True
    assert res.constraints["mutation_allowed"] is False
    assert any(a in res.excluded_actions for a in ["REPAIR", "WRITE", "DELETE", "MODIFY"])
