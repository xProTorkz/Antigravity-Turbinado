---
name: Antigravity Task
about: Template canônico de tarefas com Execution Packet v5 para o Antigravity
title: "[TASK] "
labels: ["ag:queued", "execution:auto"]
assignees: []
---

```yaml
agent_task:
  version: 5
  task_id: task-{{SLUG}}-001
  target_project: {{PROJECT_SLUG}}
  target_repo: {{OWNER_REPO}}
  priority: P1
  type: feature
  execution: auto
  source: chatgpt
  user_execution_confirmed: true
  risk: medium
  depends_on: []
  allowed_scope:
    - src/
    - tests/
  destructive_changes: false
  requires_human_approval: false
  baseline_sha: ""
  skills:
    primary: "@pesquisa-projeto"
```

## 1. OBJETIVO ÚNICO
Descreva objetivamente o que deve ser implementado.

## 2. ESCOPO PERMITIDO (SCOPE LOCK)
- `src/...`
- `tests/...`

## 3. FORA DO ESCOPO
- Não alterar dependências de infraestrutura.
- Não refatorar módulos não relacionados.

## 4. CRITÉRIOS DE ACEITE
- [ ] Implementação concluída conforme especificado.
- [ ] Testes unitários passando com sucesso.
- [ ] Zero arquivos modificados fora de `allowed_scope`.
- [ ] Recibo de commit gerado e sincronizado.
