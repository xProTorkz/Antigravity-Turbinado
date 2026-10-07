import json
from pathlib import Path
import pytest
from semantic_resolver import SemanticResolver

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@pytest.fixture(scope="module")
def resolver():
    return SemanticResolver()

@pytest.fixture(scope="module")
def missions_data():
    path = BASE_DIR / "semantic_missions.json"
    assert path.exists(), "semantic_missions.json não encontrado"
    return json.loads(path.read_text(encoding="utf-8"))

def test_semantic_missions_schema_completeness(missions_data):
    """
    Valida que todas as 21 missões possuem os 14 campos canônicos obrigatórios:
    mission_id, aliases, canonical_meaning, scope_resolution, default_depth,
    default_profile, default_surface, mutation_policy, phases, parallel_groups,
    dependencies, completion_conditions, fallback_policy, risk_policy.
    """
    missions = missions_data.get("missions", {})
    assert len(missions) == 21, f"Esperado 21 missões, encontrado {len(missions)}"

    required_keys = [
        "mission_id", "aliases", "canonical_meaning", "scope_resolution",
        "default_depth", "default_profile", "default_surface", "mutation_policy",
        "phases", "parallel_groups", "dependencies", "completion_conditions",
        "fallback_policy", "risk_policy"
    ]

    for mid, m in missions.items():
        for rk in required_keys:
            assert rk in m, f"Missão {mid} não possui o campo obrigatório '{rk}'"
        assert len(m["aliases"]) > 0, f"Missão {mid} deve possuir ao menos 1 alias"
        assert len(m["phases"]) > 0, f"Missão {mid} deve possuir fases no DAG"

def test_zero_intent_duplication_with_registry(missions_data):
    """
    Valida que as missões não duplicam os intents do semantic_registry.json,
    apenas referenciam intents existentes.
    """
    registry_path = BASE_DIR / "semantic_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")).get("intents", {})

    missions = missions_data.get("missions", {})
    for mid, m in missions.items():
        assert mid not in registry, f"Missão ID {mid} colide com intent existente no registry!"
        canon_intents = m.get("canonical_intents", [])
        for cid in canon_intents:
            assert cid in registry, f"Missão {mid} referencia intent inexistente no registry: {cid}"

def test_21_single_mission_phrases(resolver):
    """
    Testa a resolução de todas as 21 frases individuais de missão do Section 26.
    """
    samples = [
        ("audite", "AUDIT.HARD", "audit.project.hard"),
        ("vamos fazer uma visita", "VISIT.GENERAL", "recon.project.hard"),
        ("me manda um relatório", "REPORT.GENERAL", "report.problems"),
        ("encontre o problema", "FIND.PROBLEM", "report.problems"),
        ("modo oculto", "EXECUTION.DISCREET", "execution.discreet.background"),
        ("modo avançado", "EXECUTION.ADVANCED", "mode-advanced"),
        ("se conecte", "CONNECT.SMART", "conectar"),
        ("ative", "ACTIVATE.SMART", "conectar"),
        ("organiza tudo", "ORGANIZE.SYSTEM", "deep-clean"),
        ("faça funcionar", "MAKE_IT_WORK", "repair-project"),
        ("faz um reconhecimento", "RECON.HARD", "recon.project.hard"),
        ("mapeie tudo", "MAP.GENERAL", "map.project.general"),
        ("corrija", "REPAIR.SMART", "repair-project"),
        ("otimize", "OPTIMIZE.SMART", "bench-endpoint"),
        ("valide", "VALIDATE.COMPLETE", "test-project"),
        ("sincronize", "SYNC.SMART", "config-sync"),
        ("integre", "INTEGRATE.SMART", "conectar"),
        ("prepara pra produção", "PREPARE.PRODUCTION", "test-project"),
        ("faz um pente fino", "REVIEW.DEEP", "audit.project.hard"),
        ("deixa redondo", "STABILIZE.SYSTEM", "repair-project"),
        ("fecha isso", "COMPLETE.WORK", "test-project"),
    ]

    for phrase, expected_mission_id, expected_intent_id in samples:
        res = resolver.resolve(phrase)
        assert res is not None, f"Falha ao resolver frase de missão: '{phrase}'"
        assert res.is_mission is True, f"Frase '{phrase}' não foi resolvida como missão"
        assert res.mission_id == expected_mission_id, f"Frase '{phrase}' esperava missão {expected_mission_id}, obteve {res.mission_id}"
        assert res.intent_id == expected_intent_id, f"Frase '{phrase}' esperava intent {expected_intent_id}, obteve {res.intent_id}"

def test_7_compound_combinations(resolver):
    """
    Testa as 7 combinações compostas obrigatórias do Section 26.
    """
    # 1. "modo oculto, se conecte e faça uma visita"
    c1 = resolver.resolve("modo oculto, se conecte e faça uma visita")
    assert c1 is not None
    assert c1.is_mission is True and c1.is_compound is True
    assert c1.mission_pipeline == ["CONNECT.SMART", "VISIT.GENERAL"]
    assert "EXECUTION.DISCREET" in c1.modifiers_applied
    assert c1.mode == "discreet_background"

    # 2. "modo avançado, audite e encontre qualquer problema"
    c2 = resolver.resolve("modo avançado, audite e encontre qualquer problema")
    assert c2 is not None
    assert c2.is_mission is True and c2.is_compound is True
    assert c2.mission_pipeline == ["AUDIT.HARD", "FIND.PROBLEM"]
    assert "EXECUTION.ADVANCED" in c2.modifiers_applied
    assert c2.depth == "HARD"
    assert c2.execution_profile == "DEEP"

    # 3. "faça uma visita e me mande um relatório"
    c3 = resolver.resolve("faça uma visita e me mande um relatório")
    assert c3 is not None
    assert c3.is_mission is True and c3.is_compound is True
    assert c3.mission_pipeline == ["VISIT.GENERAL", "REPORT.GENERAL"]
    assert c3.plan_steps == ["recon.project.hard", "report.problems"]

    # 4. "encontre o problema, corrija e valide"
    c4 = resolver.resolve("encontre o problema, corrija e valide")
    assert c4 is not None
    assert c4.is_mission is True and c4.is_compound is True
    assert c4.mission_pipeline == ["FIND.PROBLEM", "REPAIR.SMART", "VALIDATE.COMPLETE"]
    assert c4.plan_steps == ["report.problems", "repair-project", "test-project"]

    # 5. "organiza tudo e faça funcionar"
    c5 = resolver.resolve("organiza tudo e faça funcionar")
    assert c5 is not None
    assert c5.is_mission is True and c5.is_compound is True
    assert c5.mission_pipeline == ["ORGANIZE.SYSTEM", "MAKE_IT_WORK"]
    assert c5.plan_steps == ["deep-clean", "repair-project"]

    # 6. "reconheça, mapeie e audite"
    c6 = resolver.resolve("reconheça, mapeie e audite")
    assert c6 is not None
    assert c6.is_mission is True and c6.is_compound is True
    assert c6.mission_pipeline == ["RECON.HARD", "MAP.GENERAL", "AUDIT.HARD"]
    assert c6.plan_steps == ["recon.project.hard", "map.project.general", "audit.project.hard"]

    # 7. "otimize, teste e me mostre a diferença"
    c7 = resolver.resolve("otimize, teste e me mostre a diferença")
    assert c7 is not None
    assert c7.is_mission is True and c7.is_compound is True
    assert c7.mission_pipeline == ["OPTIMIZE.SMART", "VALIDATE.COMPLETE", "REPORT.GENERAL"]
    assert c7.plan_steps == ["bench-endpoint", "test-project", "report.problems"]

def test_contextual_specialization(resolver):
    """
    Testa resolução contextual de alvos dinâmicos.
    """
    # Contexto GitHub
    r_gh = resolver.resolve("se conecte", context="GITHUB")
    assert r_gh.mission_id == "CONNECT.GITHUB"

    # Contexto VPS
    r_vps = resolver.resolve("se conecte", context="VPS")
    assert r_vps.mission_id == "CONNECT.VPS"

    # Contexto Database
    r_db = resolver.resolve("se conecte", context="DATABASE")
    assert r_db.mission_id == "CONNECT.DATABASE"

    # Especializações de busca
    assert resolver.resolve("encontre o erro").mission_id == "FIND.ROOT_CAUSE_CANDIDATES"
    assert resolver.resolve("encontre esse arquivo").mission_id == "FIND.FILE"
    assert resolver.resolve("encontre de onde vem essa função").mission_id == "FIND.CODE_ORIGIN"

    # Especializações de ativação
    assert resolver.resolve("ative o bot").mission_id == "ACTIVATE.SERVICE"
    assert resolver.resolve("ative o projeto").mission_id == "ACTIVATE.PROJECT_CONTEXT"

    # Visita com reparo estendido
    r_visit_repair = resolver.resolve("vamos fazer uma visita e arrumar")
    assert r_visit_repair.mission_id == "VISIT.GENERAL"
    phase_names = [p.get("name") or p.get("phase_id") for p in r_visit_repair.phases]
    for required_ext in ["DIAGNOSE", "REPAIR", "TEST", "VALIDATE"]:
        assert required_ext in phase_names, f"Fase estendida {required_ext} não encontrada em visita e arrumar"

def test_modifiers_do_not_create_orphaned_tasks(resolver):
    """
    Garante que modificadores prefixados alteram os parâmetros da missão
    sem criar tarefas desconectadas.
    """
    r_disc = resolver.resolve("modo oculto, audite")
    assert r_disc.mission_id == "AUDIT.HARD"
    assert "EXECUTION.DISCREET" in r_disc.modifiers_applied
    assert r_disc.mode == "discreet_background"

    r_adv = resolver.resolve("modo avançado, audite")
    assert r_adv.mission_id == "AUDIT.HARD"
    assert "EXECUTION.ADVANCED" in r_adv.modifiers_applied
    assert r_adv.depth == "HARD"
    assert r_adv.execution_profile == "DEEP"
