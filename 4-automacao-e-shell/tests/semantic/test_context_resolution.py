import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_same_phrase_different_contexts(resolver):
    # Mesma frase "audite" em contextos distintos não pode ser tratada como igual
    res_proj = resolver.resolve("audite", context="PROJECT")
    res_host = resolver.resolve("audite", context="HOST")
    res_db = resolver.resolve("audite", context="DATABASE")
    res_net = resolver.resolve("audite", context="NETWORK")

    assert res_proj is not None
    assert res_host is not None
    assert res_db is not None
    assert res_net is not None

    assert res_proj.intent_id == "audit.project.hard"
    assert res_host.intent_id == "audit.host.hard"
    assert res_db.intent_id == "audit.database.hard"
    assert res_net.intent_id == "audit.network.hard"

    assert res_proj.scope == "PROJECT"
    assert res_host.scope == "HOST"
    assert res_db.scope == "DATABASE"
    assert res_net.scope == "NETWORK"

def test_recon_contextual(resolver):
    res_proj = resolver.resolve("reconhecimento", context="PROJECT")
    res_host = resolver.resolve("reconhecimento", context="HOST")
    res_net = resolver.resolve("reconhecimento", context="NETWORK")

    assert res_proj.intent_id == "recon.project.hard"
    assert res_host.intent_id == "recon.host.hard"
    assert res_net.intent_id == "recon.network.hard"

def test_map_contextual(resolver):
    res_proj = resolver.resolve("mapeie", context="PROJECT")
    res_host = resolver.resolve("mapeie", context="HOST")

    assert res_proj.intent_id == "map.project.general"
    assert res_host.intent_id == "map.host.general"
