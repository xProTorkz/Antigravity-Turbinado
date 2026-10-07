import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_parameter_extraction(resolver):
    # Teste porta
    res = resolver.resolve("libera a porta 8080")
    assert res is not None
    assert res.parameters.get("port") == 8080

    # Teste porta padrão
    res2 = resolver.resolve("mata a porta 3000")
    assert res2 is not None
    assert res2.parameters.get("port") == 3000

    # Teste URL
    res3 = resolver.resolve("testa o endpoint http://localhost:8000/api")
    assert res3 is not None
    assert "url" in res3.parameters
    assert "localhost:8000" in res3.parameters["url"]
