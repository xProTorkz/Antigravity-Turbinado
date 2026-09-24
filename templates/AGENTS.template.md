# AGENTS.md — CONTRATO DE ROLES E GOVERNANÇA

Este arquivo estabelece os papéis canônicos de cada agente no projeto `{{PROJECT_NAME}}`.

---

## 1. MATRIZ DE RESPONSABILIDADES

| Agente | Papel | O que FAZ | O que NUNCA FAZ |
|---|---|---|---|
| **ChatGPT** | Planner & Orchestrator | Planeja requisitos, decompõe problemas, seleciona @skill e gera o Execution Packet | Não executa código local, não manipula credenciais |
| **GitHub** | Fonte da Verdade (SOT) | Persiste tarefas, estado, commits e recibos de entrega | Nada é verdade se não estiver versionado aqui |
| **Antigravity** | Único Executor Local | Executa alterações locais no workspace, roda testes e faz commits | Não planeja fora de Issues, não fura allowed_scope |
