import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_policy_audit_report_validity():
    rep_path = BASE_DIR / "policy_audit_report.json"
    assert rep_path.exists(), "policy_audit_report.json não existe!"
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    assert rep.get("policy_status") == "PASS"
    assert rep.get("reclassified_count") >= 16

def test_risk_intent_reclassifications():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    intents = reg.get("intents", {})

    expected_policies = {
        "disguise-proc": "DENIED_BY_POLICY",
        "stealth-exec": "REFERENCE_ONLY",
        "bypass-hooks": "REFERENCE_ONLY",
        "exec-raw": "HUMAN_GATE",
        "stress-fd-exhaustion": "HUMAN_GATE",
        "stress-ram": "HUMAN_GATE",
        "wipe-session": "HUMAN_GATE",
        "unlock-kill-by-name": "CONFIRM_REQUIRED",
        "deep-clean": "CONFIRM_REQUIRED",
        "reset-clean": "HUMAN_GATE",
        "shred-file": "HUMAN_GATE",
        "clean-history-tail": "HUMAN_GATE",
        "clean-history-secrets": "HUMAN_GATE",
        "daemon-kill": "CONFIRM_REQUIRED",
        "chaos-kill-worker": "HUMAN_GATE",
        "chaos-freeze-thaw": "HUMAN_GATE"
    }

    for i_id, exp_pol in expected_policies.items():
        assert i_id in intents, f"Intent de risco {i_id} não encontrada no registry"
        actual_pol = intents[i_id].get("execution_policy")
        assert actual_pol == exp_pol, f"Intent {i_id} possui política {actual_pol}, esperado {exp_pol}"

def test_side_effects_and_idempotency_metadata():
    reg = json.loads((BASE_DIR / "semantic_registry.json").read_text(encoding="utf-8"))
    intents = reg.get("intents", {})

    required_side_effect_keys = {
        "filesystem_write", "process_kill", "network_change", "config_change",
        "credential_touch", "privilege_change", "destructive", "reversible"
    }

    for i_id, it in intents.items():
        se = it.get("side_effects")
        assert se is not None, f"Intent {i_id} sem side_effects"
        assert required_side_effect_keys.issubset(set(se.keys())), (
            f"Intent {i_id} com side_effects incompletos: {se}"
        )
        idem = it.get("idempotency")
        assert idem in ["IDEMPOTENT", "CONDITIONALLY_IDEMPOTENT", "NON_IDEMPOTENT"], (
            f"Intent {i_id} com idempotency inválido: {idem}"
        )
