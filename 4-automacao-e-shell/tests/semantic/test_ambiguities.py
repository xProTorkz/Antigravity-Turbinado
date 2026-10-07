import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_controlled_ambiguity_and_margin(resolver):
    # Frase genérica que toca em múltiplas intenções de rede
    res = resolver.resolve("verifica rede")
    assert res is not None
    # Deve resolver deterministicamente ou acusar ambiguidade controlada sem crash
    assert res.confidence_score >= 500
