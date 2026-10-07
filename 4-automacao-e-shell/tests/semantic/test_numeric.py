import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_numeric_shortcuts_1_to_9(resolver):
    expected = {
        "1": "unlock-git",
        "2": "unlock-dev-ports",
        "3": "unlock-all",
        "4": "mode-advanced",
        "5": "deep-clean",
        "6": "audit-full",
        "7": "unlock-limits",
        "8": "sqlite-vacuum",
        "9": "backup-quick"
    }
    for num, target in expected.items():
        res = resolver.resolve(num)
        assert res is not None, f"Falha na resolução do número {num}"
        assert res.intent_id == target, f"Número {num} resolveu para {res.intent_id}, esperado {target}"
        assert res.confidence_score == 1000, f"Score esperado 1000 para atalho numérico {num}"

def test_numeric_words(resolver):
    word_map = {
        "git": "unlock-git",
        "porta": "unlock-dev-ports",
        "portas": "unlock-dev-ports",
        "tudo": "unlock-all",
        "total": "unlock-all",
        "turbo": "mode-advanced",
        "limpa": "deep-clean",
        "clean": "deep-clean",
        "audit": "audit-full",
        "raio-x": "audit-full",
        "limites": "unlock-limits",
        "ulimit": "unlock-limits",
        "banco": "sqlite-vacuum",
        "sqlite": "sqlite-vacuum",
        "backup": "backup-quick"
    }
    for word, target in word_map.items():
        res = resolver.resolve(word)
        assert res is not None, f"Falha na resolução da palavra-chave {word}"
        assert res.intent_id == target, f"Palavra {word} resolveu para {res.intent_id}, esperado {target}"
        assert res.confidence_score == 1000
