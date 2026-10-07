import json
import re
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_slash_sanitization_blacklist_tokens():
    idx_path = BASE_DIR / "semantic_indexes.json"
    indexes = json.loads(idx_path.read_text(encoding="utf-8"))
    slash_index = indexes.get("slash_index", {})

    forbidden_tokens = [
        "/null", "/HEAD", "/RAM", "/SSH", "/Python", "/403", "/UDP",
        "/Data", "/lucasvinicius", "/ApplicationFirewall", "/Keychains",
        "/Bash", "/O", "/S", "/display", "/config", "/commit",
        "/heads", "/index", "/refs", "/opt", "/homebrew", "/local",
        "/projetos", "/run", "/task", "/pip", "/yarn", "/brew", "/pids"
    ]

    for bad in forbidden_tokens:
        assert bad not in slash_index, f"Token proibido ainda presente no slash_index: {bad}"

def test_canonical_slash_derivations():
    idx_path = BASE_DIR / "semantic_indexes.json"
    indexes = json.loads(idx_path.read_text(encoding="utf-8"))
    slash_index = indexes.get("slash_index", {})

    assert slash_index.get("/unlock-git") == "unlock-git"
    assert slash_index.get("/audit-git-integrity") == "audit-git-integrity"
    assert slash_index.get("/audit-project-hard") == "audit.project.hard"
    assert slash_index.get("/recon-project-hard") == "recon.project.hard"
    assert slash_index.get("/map-project-general") == "map.project.general"

def test_all_slashes_match_strict_regex():
    idx_path = BASE_DIR / "semantic_indexes.json"
    indexes = json.loads(idx_path.read_text(encoding="utf-8"))
    slash_index = indexes.get("slash_index", {})

    pattern = re.compile(r"^/[a-z0-9][a-z0-9-]{1,63}$")
    for s in slash_index:
        assert pattern.match(s), f"Slash command não obedece ao padrão regex estrito: {s}"

def test_slash_provenance_metadata():
    reg_path = BASE_DIR / "semantic_registry.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    intents = reg.get("intents", {})

    for i_id, it in intents.items():
        meta = it.get("slash_metadata", [])
        assert len(meta) > 0, f"Intent {i_id} sem metadados de slash_metadata!"
        for item in meta:
            assert "slash_command" in item
            assert item["slash_source"] in ["DERIVED", "EXPLICIT", "LEGACY_VERIFIED"]
            assert item["slash_validated"] is True
