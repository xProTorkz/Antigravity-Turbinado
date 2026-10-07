import json
import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from semantic_resolver import SemanticResolver

def test_audit_database_hard_strictly_readonly():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    db_it = reg["intents"].get("audit.database.hard")
    assert db_it is not None, "audit.database.hard não encontrado no registry"

    template = db_it.get("command_template", "")
    assert "PRAGMA integrity_check" in template
    assert "PRAGMA quick_check" in template
    assert "PRAGMA foreign_key_check" in template
    assert "PRAGMA database_list" in template

    # Verificação de mutações proibidas
    mutations = ["VACUUM", "REINDEX", "UPDATE", "DELETE", "INSERT", "DROP", "ALTER"]
    found_mutations = [m for m in mutations if m in template.upper()]
    assert len(found_mutations) == 0, f"DATABASE_AUDIT_MUTATION_COUNT > 0: mutações encontradas: {found_mutations}"

def test_database_audit_mutation_count_zero():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    db_it = reg["intents"].get("audit.database.hard")

    mutations = ["VACUUM", "REINDEX", "UPDATE", "DELETE", "INSERT", "DROP", "ALTER"]
    count = 0
    cmd = db_it.get("command_template", "").upper()
    for m in mutations:
        if m in cmd:
            count += 1

    assert count == 0, f"DATABASE_AUDIT_MUTATION_COUNT deve ser 0, obtido: {count}"

def test_vacuum_separated_into_optimize():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    # VACUUM deve estar preservado em db-vacuum ou sqlite-vacuum
    vac_it = reg["intents"].get("db-vacuum") or reg["intents"].get("sqlite-vacuum")
    assert vac_it is not None
    assert "vacuum" in vac_it.get("command_template", "").lower()
