import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from semantic_resolver import SemanticResolver, SurfaceRouter

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_surface_router_six_canonical_queries(resolver):
    cases = [
        ("verifique a porta 8080", "AGY_BACKGROUND"),
        ("rode os testes", "AGY_BACKGROUND"),
        ("corrija o backend", "ANTIGRAVITY_VISUAL"),
        ("refatore autenticação", "ANTIGRAVITY_VISUAL"),
        ("audite e corrija o projeto", "HYBRID"),
        ("reconheça, corrija e valide", "HYBRID"),
    ]
    for query, expected_surface in cases:
        res = resolver.resolve(query)
        assert res is not None, f"Falha ao resolver query: {query}"
        assert res.resolved_surface == expected_surface, (
            f"Query '{query}' roteada para {res.resolved_surface}, esperado {expected_surface}. "
            f"Scores: {res.surface_scores}, Razões: {res.surface_reasons}"
        )

def test_surface_router_explicit_override(resolver):
    # Se usuário explicitar superfície, o router deve honrar
    res = resolver.resolve("rode os testes", execution_surface="ANTIGRAVITY_VISUAL")
    assert res is not None
    assert res.resolved_surface == "ANTIGRAVITY_VISUAL"

    res2 = resolver.resolve("corrija o backend", execution_surface="AGY_BACKGROUND")
    assert res2 is not None
    assert res2.resolved_surface == "AGY_BACKGROUND"

def test_surface_router_scoring_breakdown(resolver):
    # Teste unitário das parcelas de score do SurfaceRouter
    res_sre = resolver.resolve("verifique a porta 8080")
    scores_sre, reasons_sre = SurfaceRouter.calculate_scores(res_sre, "verifique a porta 8080")
    assert scores_sre["AGY_BACKGROUND"] >= 90
    assert any("deterministic" in r for r in reasons_sre["AGY_BACKGROUND"])

    res_code = resolver.resolve("corrija o backend")
    scores_code, reasons_code = SurfaceRouter.calculate_scores(res_code, "corrija o backend")
    assert scores_code["ANTIGRAVITY_VISUAL"] >= 100
    assert any("code_change" in r for r in reasons_code["ANTIGRAVITY_VISUAL"])

    res_hybrid = resolver.resolve("audite e corrija o projeto")
    scores_hybrid, reasons_hybrid = SurfaceRouter.calculate_scores(res_hybrid, "audite e corrija o projeto")
    assert scores_hybrid["HYBRID"] >= 100
    assert any("multi_stage" in r for r in reasons_hybrid["HYBRID"])

def test_execution_profiles(resolver):
    # FAST: determinístico e curto
    res_fast = resolver.resolve("rode os testes")
    assert res_fast.execution_profile in ["FAST", "STANDARD"]

    # DEEP: auditoria macro / multi-stage
    res_deep = resolver.resolve("audite e corrija o projeto")
    assert res_deep.execution_profile in ["DEEP", "PARALLEL"]
