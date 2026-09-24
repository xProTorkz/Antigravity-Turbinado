---
name: Antigravity Task (v5)
about: Crie uma tarefa estruturada com Execution Packet para execução autônoma pelo Antigravity
title: "[TASK] "
labels: ["ag:queued", "execution:auto"]
assignees: []
---

```yaml
agent_task:
  version: 5
  task_id: task-001
  target_project: <project-name>
  target_repo: <github-user>/<github-repo>
  priority: P1
  type: feature
  execution: auto
  source: chatgpt
  user_execution_confirmed: true
  risk: medium
  depends_on: []
  allowed_scope:
    - scripts/
    - docs/
  destructive_changes: false
  requires_human_approval: false
  baseline_sha: ""
  skills:
    primary: "@pesquisa-projeto"
```

## 1. OBJETIVO ÚNICO
Descreva o objetivo claro e determinístico desta tarefa.

## 2. ESCOPO PERMITIDO (SCOPE LOCK)
- `scripts/...`
- `docs/...`

## 3. FORA DE ESCOPO
- Não alterar dependências de infraestrutura.
- Não refatorar código fora dos diretórios permitidos.

## 4. CRITÉRIOS DE ACEITE
- [ ] Implementação concluída sem erros.
- [ ] Testes focados e regressão executados com sucesso.
- [ ] Auditoria de segredos e diff aprovada.
- [ ] Recibo com SHA e branch confirmado no GitHub.
