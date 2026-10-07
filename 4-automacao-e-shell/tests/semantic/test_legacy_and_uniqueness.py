import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_legacy_traceability_100_percent():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    reg_intents = set(reg.get("intents", {}).keys())

    leg_map = json.loads((BASE_DIR / "legacy_migration_map.json").read_text(encoding="utf-8"))
    entries = leg_map.get("entries", [])

    assert len(entries) > 0
    mapped_count = 0
    for e in entries:
        target = e.get("new_intent_id") or e.get("target_intent_id")
        assert target in reg_intents, f"Target intent legada não encontrada no registry: {target}"
        mapped_count += 1

    rate = (mapped_count / len(entries)) * 100
    assert rate == 100.0, f"Rastreabilidade legada menor que 100%: {rate}%"

def test_canonical_intent_uniqueness():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    intents = reg.get("intents", {})
    intent_keys = list(intents.keys())

    assert len(intent_keys) == len(set(intent_keys)), "Existem Intent IDs duplicados!"
    assert len(intent_keys) >= 211, f"Total de intents esperado >= 211, obtido: {len(intent_keys)}"

def test_zero_silent_collisions():
    idx = json.loads((BASE_DIR / "semantic_indexes.json").read_text(encoding="utf-8"))
    num_idx = idx.get("numeric_index", {})
    slash_idx = idx.get("slash_index", {})

    # Cada atalho numérico de 1 a 9 deve apontar para uma intent válida e exclusiva
    num_targets = [num_idx[str(i)] for i in range(1, 10) if str(i) in num_idx]
    assert len(num_targets) == len(set(num_targets)), "Colisão detectada nos atalhos numéricos 1 a 9!"
