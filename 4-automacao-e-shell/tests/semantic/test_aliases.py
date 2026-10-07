import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_exact_aliases(resolver):
    samples = [
        ("destrava o git", "unlock-git"),
        ("arranca o lock", "unlock-git"),
        ("destrava index", "unlock-git-index"),
        ("aborta rebase", "unlock-git-rebase"),
        ("limpa as portas de dev", "unlock-dev-ports"),
        ("mata processos zumbis", "unlock-zombie-deadlocks"),
        ("faxina profunda", "deep-clean"),
        ("auditoria completa", "audit-all"),
        ("aumenta o ulimit", "unlock-limits"),
        ("limpa cache de dns do mac", "unlock-dns-cache")
    ]
    for phrase, expected_intent in samples:
        res = resolver.resolve(phrase)
        assert res is not None, f"Falha ao resolver alias: '{phrase}'"
        if expected_intent == "audit-all":
            assert res.intent_id in ["audit-all", "audit-full"], f"Alias '{phrase}' resolveu para {res.intent_id}"
        else:
            assert res.intent_id == expected_intent, f"Alias '{phrase}' resolveu para {res.intent_id}, esperado {expected_intent}"
        assert res.confidence_score >= 800
