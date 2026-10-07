import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_regra_auditoria_global_23_camadas_silenciosa(resolver):
    """
    Valida a nova regra e comando de auditoria global:
    - 6 domínios conceituais:
        1. Frontend (Client-Side) [Surface Web]
        2. Transporte, Borda e Segurança Perimetral
        3. Backend (Server-Side) [Deep Web]
        4. Armazenamento e Análise de Dados (Performance & BI)
        5. Hospedagem, Virtualização e Infraestrutura (DevOps) [Abaixo do Backend]
        6. Operações Transversais [CI/CD & Observabilidade]
    - 23 camadas estruturais completas
    - 23 fases sequenciais de auditoria
    - Execução invisível e silenciosa em segundo plano:
        (AGY_BACKGROUND, UI_FOCUS=False, BACKGROUND=True, modo discreto)
    """
    res = resolver.resolve("auditoria global")
    assert res is not None
    assert res.intent_id == "audit.project.hard"
    assert res.mode == "discreet_background"
    assert res.resolved_surface == "AGY_BACKGROUND"
    assert res.route_receipt.get("EXECUTION_SURFACE") == "AGY_BACKGROUND"
    assert res.route_receipt.get("BACKGROUND") is True
    assert res.route_receipt.get("UI_FOCUS") is False

    # Validação das 23 camadas estruturais
    camadas_esperadas = [
        # 1. Frontend (Client-Side) - Surface Web
        "Camada de Apresentação (Interface de Usuário - UI)",
        "Camada de Lógica de Interação",
        "Camada de Gerenciamento de Estado",
        "Camada de Rede (Cliente de API)",
        # 2. Transporte, Borda e Segurança Perimetral
        "Camada de Segurança Perimetral (WAF - Firewall de Aplicação)",
        "Camada de Redes de Entrega de Conteúdo (CDN)",
        "Camada de Gateway e Roteamento de Borda (DNS e Load Balancers)",
        # 3. Backend (Server-Side) - Deep Web
        "Camada de Entrada e Roteamento (Controladores / API)",
        "Camada de Segurança e Autenticação (Middleware)",
        "Camada de Regras de Negócio (Serviços)",
        "Camada de Mensageria e Eventos (Filas Assíncronas)",
        "Camada de Cache Distribuído",
        "Camada de Acesso a Dados (Persistência / ORM)",
        # 4. Armazenamento e Análise de Dados
        "Camada de Armazenamento Principal (Banco de Dados Relacional/Não-Relacional)",
        "Camada de Réplicas de Leitura e Armazenamento Analítico (Data Warehouse / BI)",
        # 5. Hospedagem, Virtualização e Infraestrutura (DevOps)
        "Camada de Servidores Web e Proxies Reversos",
        "Camada de Virtualização e Containers",
        "Camada de Orquestração de Containers",
        "Camada de Sistema Operacional do Servidor",
        "Camada de Infraestrutura como Código (IaC)",
        "Camada de Hardware e Provedor de Nuvem (Cloud Computacional)",
        # 6. Operações Transversais
        "Camada de Integração e Entrega Contínua (CI/CD)",
        "Camada de Observabilidade, Telemetria e Monitoramento (Logs e Métricas)"
    ]

    assert len(res.total_layers) == 23, f"Esperado 23 camadas totais, obtido {len(res.total_layers)}"
    assert res.total_layers == camadas_esperadas

    # Validação dos 6 domínios globais
    assert len(res.global_domains) == 6, f"Esperado 6 domínios globais, obtido {len(res.global_domains)}"
    dominios_esperados = [
        "1. Frontend (Client-Side)",
        "2. Transporte, Borda e Segurança Perimetral",
        "3. Backend (Server-Side)",
        "4. Armazenamento e Análise de Dados",
        "5. Hospedagem, Virtualização e Infraestrutura (DevOps)",
        "6. Operações Transversais (Cercam todas as outras)"
    ]
    for idx, expected_domain in enumerate(dominios_esperados):
        assert res.global_domains[idx]["dominio"] == expected_domain

    # Validação das 23 fases de auditoria
    assert len(res.phases) == 23, f"Esperado 23 fases na auditoria global, obtido {len(res.phases)}"
    for idx, expected_layer in enumerate(camadas_esperadas):
        assert res.phases[idx].get("layer") == expected_layer, (
            f"Fase {idx+1} esperava camada '{expected_layer}', obtido '{res.phases[idx].get('layer')}'"
        )

def test_variacoes_comando_auditoria_global(resolver):
    """
    Garante que todas as formas de invocação (comandos slash, linguagem natural e hifenizados)
    são resolvidas compulsoriamente para a auditoria global com 23 camadas e modo silencioso.
    """
    variacoes = [
        "auditoria global",
        "//audit-global",
        "/auditoria-global",
        "/audit-global",
        "auditoria-global",
        "audit-global",
        "auditoria global em todas as camadas",
        "raio-x global"
    ]
    for var in variacoes:
        res = resolver.resolve(var)
        assert res is not None, f"Falha ao resolver '{var}'"
        assert res.intent_id == "audit.project.hard"
        assert len(res.total_layers) == 23
        assert len(res.phases) == 23
        assert len(res.global_domains) == 6
        assert res.resolved_surface == "AGY_BACKGROUND"
        assert res.mode == "discreet_background"
