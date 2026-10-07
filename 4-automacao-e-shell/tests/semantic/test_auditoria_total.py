import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_regra_auditoria_total_10_camadas_silenciosa(resolver):
    """
    Valida a nova regra de auditoria total:
    - Execução realizada nas 10 camadas totais solicitadas
    - Execução de forma invisível e silenciosa (AGY_BACKGROUND, UI_FOCUS=False, BACKGROUND=True, modo discreto)
    """
    res = resolver.resolve("auditoria total")
    assert res is not None
    assert res.intent_id == "audit.project.hard"
    assert res.mode == "discreet_background"
    assert res.resolved_surface == "AGY_BACKGROUND"
    assert res.route_receipt.get("EXECUTION_SURFACE") == "AGY_BACKGROUND"
    assert res.route_receipt.get("BACKGROUND") is True
    assert res.route_receipt.get("UI_FOCUS") is False

    # Validação das 10 camadas totais
    camadas_esperadas = [
        "Camada de Apresentação (Interface de Usuário - UI)",
        "Camada de Lógica de Interação",
        "Camada de Gerenciamento de Estado",
        "Camada de Rede (Cliente de API)",
        "Camada de Gateway e Roteamento de Borda",
        "Camada de Entrada e Roteamento (Controladores / API)",
        "Camada de Segurança e Autenticação (Middleware)",
        "Camada de Regras de Negócio (Serviços)",
        "Camada de Acesso a Dados (Persistência / ORM)",
        "Camada de Armazenamento (Banco de Dados)"
    ]

    assert len(res.total_layers) == 10, f"Esperado 10 camadas totais, obtido {len(res.total_layers)}"
    assert res.total_layers == camadas_esperadas

    # Validação das 10 fases da auditoria total
    assert len(res.phases) == 10, f"Esperado 10 fases na auditoria total, obtido {len(res.phases)}"
    for idx, expected_layer in enumerate(camadas_esperadas):
        assert res.phases[idx].get("layer") == expected_layer, (
            f"Fase {idx+1} esperava camada '{expected_layer}', obtido '{res.phases[idx].get('layer')}'"
        )
