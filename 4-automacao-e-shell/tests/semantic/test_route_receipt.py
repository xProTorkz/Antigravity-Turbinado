import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_route_receipt_schema_completeness(resolver):
    res = resolver.resolve("audite e corrija o projeto")
    assert res is not None
    receipt = res.route_receipt

    required_fields = [
        "INPUT_SOURCE", "INTENT_ID", "EXECUTION_PROFILE", "EXECUTION_SURFACE",
        "PROJECT", "TARGET", "RISK", "POLICY", "AGY_USED", "ANTIGRAVITY_USED",
        "SUBAGENTS_USED", "BACKGROUND", "UI_FOCUS", "STEPS", "PARALLEL_GROUPS",
        "SESSION_REUSED", "DURATION_MS", "RESULT"
    ]

    for f in required_fields:
        assert f in receipt, f"Campo {f} ausente no ROUTE_RECEIPT!"

    assert receipt["EXECUTION_SURFACE"] == "HYBRID"
    assert receipt["AGY_USED"] is True
    assert receipt["ANTIGRAVITY_USED"] is True
    assert receipt["BACKGROUND"] is True
    assert receipt["RESULT"] == "ROUTED"
    assert isinstance(receipt["STEPS"], list)
    assert len(receipt["STEPS"]) >= 2

def test_route_receipt_formatted_string(resolver):
    res = resolver.resolve("rode os testes")
    assert res is not None
    formatted = res.route_receipt_formatted()

    assert "INPUT_SOURCE=" in formatted
    assert "INTENT_ID=test-project" in formatted
    assert "EXECUTION_SURFACE=AGY_BACKGROUND" in formatted
    assert "AGY_USED=True" in formatted
    assert "RESULT=ROUTED" in formatted
