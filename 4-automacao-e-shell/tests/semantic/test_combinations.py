import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_semantic_combinations(resolver):
    # Combinações não cadastradas literalmente
    test_cases = [
        "desbloqueia o repositorio",
        "solta as travas do repo",
        "verifica as portas",
        "analisa o banco sqlite",
        "otimiza a base de dados"
    ]
    for text in test_cases:
        res = resolver.resolve(text)
        assert res is not None, f"Falha na combinação: '{text}'"
        assert res.confidence_score >= 600, f"Score insuficiente para '{text}': {res.confidence_score}"
        print(f"Combinação '{text}' -> {res.intent_id} ({res.matched_by})")
