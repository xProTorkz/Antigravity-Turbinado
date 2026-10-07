import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_13_mandatory_phrases(resolver):
    # 1. audite
    res1 = resolver.resolve("audite")
    assert res1 is not None
    assert res1.action == "AUDIT"
    assert res1.depth == "HARD"
    assert res1.constraints["read_only"] is True
    assert res1.constraints["mutation_allowed"] is False
    assert len(res1.phases) == 10

    # 2. faça um reconhecimento
    res2 = resolver.resolve("faça um reconhecimento")
    assert res2 is not None
    assert res2.action == "RECON"
    assert res2.depth == "HARD"
    assert res2.constraints["read_only"] is True

    # 3. reconhecimento
    res3 = resolver.resolve("reconhecimento")
    assert res3 is not None
    assert res3.action == "RECON"
    assert res3.depth == "HARD"

    # 4. faça um mapeamento geral
    res4 = resolver.resolve("faça um mapeamento geral")
    assert res4 is not None
    assert res4.action == "MAP"
    assert res4.depth == "HARD"

    # 5. mapeie
    res5 = resolver.resolve("mapeie")
    assert res5 is not None
    assert res5.action == "MAP"
    assert res5.depth == "HARD"

    # 6. raio-x
    res6 = resolver.resolve("raio-x")
    assert res6 is not None
    assert res6.action == "AUDIT"

    # 7. audita tudo
    res7 = resolver.resolve("audita tudo")
    assert res7 is not None
    assert res7.action == "AUDIT"

    # 8. audite mas não altere
    res8 = resolver.resolve("audite mas não altere")
    assert res8 is not None
    assert res8.action == "AUDIT"
    assert res8.constraints["mutation_allowed"] is False
    assert "REPAIR" in res8.excluded_actions or "WRITE" in res8.excluded_actions or "MODIFY" in res8.excluded_actions

    # 9. mapeie sem encerrar processos
    res9 = resolver.resolve("mapeie sem encerrar processos")
    assert res9 is not None
    assert res9.action == "MAP"
    assert "KILL" in res9.excluded_actions or "kill" in res9.excluded_actions

    # 10. faça reconhecimento nesse projeto
    res10 = resolver.resolve("faça reconhecimento nesse projeto")
    assert res10 is not None
    assert res10.action == "RECON"
    assert res10.scope == "PROJECT"

    # 11. audite Git e SQLite
    res11 = resolver.resolve("audite Git e SQLite")
    assert res11 is not None
    assert res11.is_compound is True
    assert len(res11.plan_steps) == 2

    # 12. reconheça e depois audite
    res12 = resolver.resolve("reconheça e depois audite")
    assert res12 is not None
    assert res12.is_compound is True
    assert "recon" in res12.plan_steps[0]
    assert "audit" in res12.plan_steps[1]

    # 13. faça um mapa geral mas só leitura
    res13 = resolver.resolve("faça um mapa geral mas só leitura")
    assert res13 is not None
    assert res13.action == "MAP"
    assert res13.constraints["read_only"] is True
    assert res13.constraints["mutation_allowed"] is False
