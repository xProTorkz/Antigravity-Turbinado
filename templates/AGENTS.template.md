# AGENTS.md — CONTRATO DE ROLES E GOVERNANÇA

Este arquivo estabelece os papéis canônicos de cada agente no projeto `{{PROJECT_NAME}}`.

---

## 1. MATRIZ DE RESPONSABILIDADES

| Agente | Papel | O que FAZ | O que NUNCA FAZ |
|---|---|---|---|
| **ChatGPT** | Planner & Orchestrator | Planeja requisitos, decompõe problemas, seleciona @skill e gera o Execution Packet | Não executa código local, não manipula credenciais |
| **GitHub** | Fonte da Verdade (SOT) | Persiste tarefas, estado, commits e recibos de entrega | Nada é verdade se não estiver versionado aqui |
| **Control Plane** | Coordenador Local | Resolve o diretório local e previne concorrência | Não executa tarefas não registradas |
| **Sentinela** | Governança | Aplica Scope Lock, audita segredos e valida testes | Não programa código, não relaxa segurança |
| **Antigravity** | Único Executor | Executa alterações locais, roda testes e faz commits | Não planeja fora de Issues, não fura allowed_scope |
