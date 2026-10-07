import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_discreet_execution_policy(resolver):
    discreet_phrases = [
        "modo silencioso",
        "roda sem aparecer",
        "faz em background",
        "não mexe na minha tela",
        "não troca minha janela"
    ]

    for phrase in discreet_phrases:
        res = resolver.resolve(phrase)
        assert res is not None, f"Falha na resolução de frase discreta: {phrase}"
        assert res.mode == "discreet_background"
        assert res.discreet_policy["EXECUTION_VISIBILITY"] == "BACKGROUND"
        assert res.discreet_policy["UI_FOCUS"] is False
        assert res.discreet_policy["VISIBLE_TERMINAL"] is False
        assert res.discreet_policy["OPEN_NEW_WINDOWS"] is False
        assert res.discreet_policy["OPEN_NEW_TABS"] is False
        assert res.discreet_policy["HEADLESS_BROWSER"] is False
        assert res.discreet_policy["AUDIT_LOGGING"] is True
        assert res.discreet_policy["SECURITY_LOGGING"] is True

        # Invariante de Segurança: NUNCA mapear para deleção de histórico ou ofuscação
        forbidden = res.discreet_policy.get("forbidden_mappings", [])
        for f in ["DELETE_HISTORY", "DISGUISE_PROCESS", "DISABLE_LOGGING", "HIDE_FROM_SECURITY", "BYPASS_MONITORING"]:
            assert f in forbidden, f"Mapeamento proibido não catalogado: {f}"

def test_modo_silencioso_never_stealth_or_disguise(resolver):
    # Requisito 15 e 30: 'modo silencioso' deve resolver para execution.discreet.background
    # NUNCA para stealth-exec ou disguise-proc
    res = resolver.resolve("modo silencioso")
    assert res is not None
    assert res.intent_id == "execution.discreet.background", f"Esperado execution.discreet.background, obtido {res.intent_id}"
    assert res.intent_id not in ["stealth-exec", "disguise-proc"], "Violação de segurança: resolvido para stealth ou disguise!"

    for q in ["roda sem aparecer", "faz em background", "não mexe na tela"]:
        res_q = resolver.resolve(q)
        assert res_q is not None
        assert res_q.intent_id != "stealth-exec"
        assert res_q.intent_id != "disguise-proc"
