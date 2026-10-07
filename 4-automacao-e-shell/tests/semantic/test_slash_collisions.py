import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_zero_silent_slash_collisions_in_report():
    report_path = BASE_DIR / "slash_collision_report.json"
    assert report_path.exists(), "slash_collision_report.json não encontrado!"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report.get("silent_slash_collisions") == 0, (
        f"Detectadas colisões silenciosas de slash: {report.get('collisions')}"
    )
    assert report.get("collision_status") == "PASS"

def test_registry_slash_uniqueness():
    reg_path = BASE_DIR / "semantic_registry.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    intents = reg.get("intents", {})

    slash_map = {}
    collisions = []
    for i_id, it in intents.items():
        for s in it.get("slash_commands", []):
            if s in slash_map:
                collisions.append((s, slash_map[s], i_id))
            slash_map[s] = i_id

    assert len(collisions) == 0, f"Colisões de slash encontradas no registry: {collisions}"
    assert len(slash_map) >= 300, f"Total de slash commands esperado >= 300, obtido: {len(slash_map)}"
