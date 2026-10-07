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

def test_legacy_parity_100_percent(resolver):
    map_path = BASE_DIR / "legacy_migration_map.json"
    migration_data = json.loads(map_path.read_text(encoding="utf-8"))
    entries = migration_data.get("entries", [])

    assert len(entries) > 0, "Nenhuma entrada no manifesto de migração!"

    total_tested = 0
    passed = 0

    for item in entries:
        canon_cmd = item["legacy_command"]
        res = resolver.resolve(canon_cmd)
        assert res is not None, f"Falha na resolução do comando legado: {canon_cmd}"
        assert res.intent_id == item["new_intent_id"], f"Comando {canon_cmd} resolveu para {res.intent_id}, esperado {item['new_intent_id']}"
        total_tested += 1
        passed += 1

    print(f"\n✅ Paridade Legada 100%: {passed}/{total_tested} comandos testados e validados.")
