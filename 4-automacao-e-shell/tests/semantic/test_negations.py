import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_negations_and_exclusions(resolver):
    # Teste 1: audita tudo sem limpar nada
    res1 = resolver.resolve("audita tudo sem limpar nada")
    assert res1 is not None
    assert "clean" in res1.excluded_actions, f"Ação 'clean' não foi excluída: {res1.excluded_actions}"
    assert "clean" not in res1.intent_id, f"Intent incorreto com negação: {res1.intent_id}"

    # Teste 2: verifica as portas sem matar processos
    res2 = resolver.resolve("verifica as portas sem matar processos")
    assert res2 is not None
    assert "kill" in res2.excluded_actions

    # Teste 3: só audita o sistema
    res3 = resolver.resolve("só audita o sistema")
    assert res3 is not None
    assert "clean" in res3.excluded_actions

    # Teste 4: otimiza o banco sem fazer backup
    res4 = resolver.resolve("otimiza o banco sem fazer backup")
    assert res4 is not None
    assert "backup" in res4.excluded_actions
