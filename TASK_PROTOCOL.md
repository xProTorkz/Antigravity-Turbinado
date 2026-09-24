# TASK_PROTOCOL v5 — ESPECIFICAÇÃO DE EXECUTION PACKETS

Este documento define o formato universal e padronizado de tarefas transmitidas via GitHub Issues para o executor Antigravity.

---

## 1. BLOCO CANÔNICO DE METADADOS (YAML)

Toda Issue executável deve começar obrigatoriamente com o bloco YAML delimitado:

```yaml
agent_task:
  version: 5
  task_id: task-unique-slug-001
  target_project: nome-do-projeto
  target_repo: owner/repo
  priority: P0 # P0 | P1 | P2 | P3
  type: feature # feature | fix | refactor | audit | ops | security | docs
  execution: auto # auto | manual | plan
  source: chatgpt # chatgpt | cli | manual
  user_execution_confirmed: true
  risk: medium # low | medium | high
  depends_on: []
  supersedes: []
  allowed_scope:
    - src/
    - tests/
  destructive_changes: false
  requires_human_approval: false
  baseline_sha: "commit-sha-de-referencia"
  skills:
    primary: "@skill-primaria"
    support: "@skill-secundaria-opcional"
```

---

## 2. DICIONÁRIO DE CAMPOS

| Campo | Tipo | Descrição |
|---|---|---|
| `version` | Inteiro | Versão do protocolo (`5`). |
| `task_id` | String | Identificador determinístico da tarefa. |
| `target_project` | String | Slug canônico do projeto cadastrado no `PROJECT_REGISTRY.json`. |
| `target_repo` | String | Repositório remoto no formato `owner/repo`. |
| `priority` | String | Criticidade da tarefa (`P0` a `P3`). |
| `type` | String | Categoria técnica da demanda. |
| `execution` | String | Modo de execução (`auto` para execução autônoma, `manual` ou `plan`). |
| `allowed_scope` | Lista | Diretórios ou arquivos estritamente autorizados para alteração (Scope Lock). |
| `baseline_sha` | String | SHA do commit de referência para detecção de conflitos e drift. |
| `skills.primary` | String | Skill técnica primária selecionada pelo Skill Router. |

---

## 3. ESTADOS CANÔNICOS DE ENCERRAMENTO

| Estado | Significado Operacional |
|---|---|
| `IMPLEMENTADO` | Código alterado e salvo no workspace local. |
| `VALIDADO` | Testes executados com sucesso comprovado por evidências. |
| `INSTALADO` | Componente disponibilizado no ambiente de destino. |
| `SINCRONIZADO` | Commit recebido e confirmado no repositório remoto. |
| `SYNC_PENDING` | Alterações locais salvas, mas push remoto pendente de envio. |
| `BLOCKED` | Tarefa interrompida aguardando liberação de Human Gate. |
| `DONE` | **TODOS** os critérios de aceite e validações cumpridos integralmente. |
