# ARQUITETURA DETALHADA DO SISTEMA

## 1. VISÃO GERAL DO PIPELINE DE EXECUÇÃO

O Antigravity Turbinado estabelece um pipeline estritamente desacoplado entre planejamento e execução:

```text
       ┌──────────────────────────┐
       │         USUÁRIO          │
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │    CHATGPT / PLANNER     │
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │   GITHUB ISSUES (SOT)    │
       └────────────┬─────────────┘
                    │ Execution Packet (agent_task v5)
                    ▼
       ┌──────────────────────────┐
       │   CONTROL PLANE / ROUTER │
       └──────┬────────────┬──────┘
              │            │
              ▼            ▼
  ┌───────────────┐   ┌───────────────────────┐
  │ SKILL ROUTER  │   │  SENTINELA GUARDIÃO   │
  │   (Curator)   │   │ (Segurança & Escopo)  │
  └───────────────┘   └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │      ANTIGRAVITY      │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │    TESTES & COMMIT    │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │   GITHUB STATE SYNC   │
                      └───────────────────────┘
```

---

## 2. CAMADAS E SEPARAÇÃO DE RESPONSABILIDADES

### 2.1. Planejador: ChatGPT
- Conectado via perfil comportamental padronizado.
- Analisa o pedido do usuário, lê o histórico canônico no GitHub e monta o pacote executivo.
- Nunca roda comandos de terminal nem altera arquivos locais.

### 2.2. Estado Operacional: GitHub
- Todas as tarefas são mantidas como Issues.
- Commits utilizam mensagens semânticas com referência direta à Issue.
- As branches de features seguem o isolamento por demanda.

### 2.3. Roteador & Coordenação: Control Plane
- O daemon do Control Plane roda localmente em `http://127.0.0.1:8765`.
- Consulta `PROJECT_REGISTRY.json` para mapear nomes de projeto a pastas físicas.
- Bloqueia execuções paralelas no mesmo projeto para evitar condições de corrida no Git.

### 2.4. Integridade & Segurança: Sentinela Guardião
- Monitor permanente e transversal.
- Executa PRE_FLIGHT (validação de worktree e baseline SHA) e POST_FLIGHT (garantia de diff limpo e sem vazamento de segredos).
- Intercepta comandos perigosos e abre Human Gate quando necessário.

### 2.5. Executor Técnico: Antigravity
- Único agente com permissão de escrita de código no workspace do projeto.
- Opera no modo "Sempre permitir e proceder" dentro da pasta do projeto.
- Executa testes obrigatórios antes e depois de cada alteração.
