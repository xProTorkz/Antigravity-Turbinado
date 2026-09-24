# ARQUITETURA DETALHADA DO SISTEMA

## 1. VISÃO GERAL DO PIPELINE DE EXECUÇÃO

O Antigravity Turbinado estabelece um pipeline desacoplado e determinístico entre planejamento e execução:

```text
       ┌──────────────────────────┐
       │         USUÁRIO          │ (Comando em linguagem natural / Requisito)
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │    CHATGPT / PLANNER     │ (Planeja, decompõe, seleciona a Skill
       └────────────┬─────────────┘  e gera o Execution Packet com Scope Lock)
                    │
                    ▼
       ┌──────────────────────────┐
       │   GITHUB ISSUES (SOT)    │ (Fonte Única da Verdade operacional;
       └────────────┬─────────────┘  backlog e organizador de tarefas v5)
                    │ Execution Packet (agent_task v5)
                    ▼
       ┌──────────────────────────┐
       │    ANTIGRAVITY LOCAL     │ (Único executor local autorizado;
       └────────────┬─────────────┘  autonomia máxima no workspace do projeto)
                    │
                    ▼
       ┌──────────────────────────┐
       │     TESTES & COMMIT      │ (Metodologia: Test Before / Test After;
       └────────────┬─────────────┘  verificação de regressões e diff limpo)
                    │
                    ▼
       ┌──────────────────────────┐
       │    GITHUB STATE SYNC     │ (Recibo de entrega, SHA e fechamento da Issue)
       └──────────────────────────┘
```

---

## 2. CAMADAS E SEPARAÇÃO DE RESPONSABILIDADES

### 2.1. Planejador: ChatGPT
- Conectado via perfil comportamental padronizado (Custom Instructions).
- Analisa os requisitos do usuário e lê o estado do repositório GitHub escolhido pelo cliente.
- Sugere a melhor skill técnica a partir do acervo distribuível.
- Gera o **Execution Packet** (bloco YAML `agent_task` v5) com delimitação estrita de escopo (`allowed_scope`).
- **Nunca** executa código local, não acessa terminais e não manipula credenciais privadas.

### 2.2. Estado Operacional: GitHub
- Fonte Única da Verdade (State of Truth - SOT).
- Todas as tarefas são mantidas como Issues estruturadas com labels canônicas.
- O repositório armazena o histórico auditável de commits, PRs e recibos de entrega.
- Totalmente configurado com a conta e o repositório do próprio cliente.

### 2.3. Executor Local: Google Antigravity
- Único agente autorizado a alterar código e executar ferramentas na máquina local.
- Opera com **autonomia máxima dentro do workspace** autorizado pelo cliente (`Always Allow In-Workspace`).
- Fora do workspace do projeto, o acesso a arquivos é bloqueado com solicitação de revisão humana.
- Aplica a metodologia de validação empírica (*Test Before / Test After*) e auditoria de segredos antes de realizar commits.
