# Protocolo de Tarefas do Agente (TASK_PROTOCOL v5)

Este documento define a especificação canônica do formato de tarefas transmitidas via GitHub Issues para o ecossistema Antigravity através do `antigravity-control-plane`.

---

## 1. Estrutura Obrigatória da Tarefa (v5)

Toda Issue processável pelo dispatcher deve iniciar com um bloco de metadados em YAML delimitado por marcadores de código `yaml`:

```yaml
agent_task:
  version: 5
  task_id: task-control-plane-001
  target_project: antigravity-control-plane
  target_repo: xProTorkz/antigravity-control-plane
  assigned_agent: antigravity
  agent_role: executor
  priority: P0
  type: fix
  execution: implement
  source: chatgpt
  user_execution_confirmed: true
  risk: high
  depends_on: []
  supersedes: []
  allowed_scope:
    - ag_control_plane/
    - tests/
  destructive_changes: false
  requires_human_approval: false
  baseline_sha: ""
```

---

## 2. Campos dos Metadados

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `version` | Inteiro | Versão do protocolo (atualmente `5`). |
| `task_id` | String | Identificador único e determinístico da tarefa. |
| `target_project` | String | Slug do projeto autorizado em `PROJECT_REGISTRY.json`. Obrigatório. |
| `target_repo` | String | Repositório GitHub oficial (`owner/repo`), exatamente idêntico ao do registro. **As issues são criadas exclusivamente dentro do repositório do projeto.** |
| `assigned_agent` | String | Agente responsável pela execução (`antigravity`, `subagent-audit`, etc.). Definido via GitHub. |
| `agent_role` | String | Papel do agente na tarefa (`executor`, `auditor`, `planner`). |
| `priority` | String | Nível de urgência (`P0`, `P1`, `P2`, `P3`). |
| `type` | String | Natureza da tarefa (`fix`, `feature`, `audit`, `refactor`, `ops`, `security`, `docs`). |
| `execution` | String | Modo de execução (`implement`, `plan`, `audit`). |
| `source` | String | Origem da solicitação (`chatgpt`, `siri`, `alexa`, `manual`). |
| `user_execution_confirmed` | Booleano | **Obrigatório para `execution:auto`**. Confirmação explícita do usuário para executar. |
| `risk` | String | Nível de risco da alteração (`low`, `medium`, `high`). P0 é `high` por padrão. |
| `depends_on` | Lista | Lista de números de Issues que devem estar concluídas antes desta. |
| `supersedes` | Lista | Lista de números de Issues substituídas ou canceladas por esta. |
| `repair_mode` | String | `normal` ou `surgical` (intervenção estrita em código defeituoso). |
| `allowed_scope` | Lista | Caminhos relativos permitidos para modificação. Não pode conter arquivos protegidos. |
| `destructive_changes`| Booleano | Se true, exige confirmação humana explícita antes de aplicar. |
| `requires_human_approval` | Booleano | Se true, finaliza em `ag:review` em vez de `ag:done`. |
| `baseline_sha` | String | SHA do commit de referência para detecção de stale. |

---

## 3. Taxonomia Canônica e Padrão de Nomenclatura

### 3.1. Padronização Universal de Títulos: `[Projeto - Sistema]`
Toda Issue e tarefa deve ser nomeada estritamente no padrão:
`[Projeto - Sistema] Descrição Clara da Tarefa`
Exemplos:
* `[API Catalogador - DADO88X - Backend] Refatorar rotas de telemetria`
* `[Jarvis Assistente - Control Plane] Atualizar dispatcher de tarefas`
* `[ConfigBot - Automação] Ajustar sincronização com servidor`

### 3.2. Taxonomia de Labels (GitHub)
Cada Issue no repositório do projeto deve obedecer rigorosamente:
1. **Exatamente um Projeto**: `project:<slug>` (compatível com `PROJECT_REGISTRY.json`).
2. **Exatamente uma Prioridade**: `priority:p0`, `priority:p1`, `priority:p2`, `priority:p3`.
3. **Exatamente um Tipo**: `type:fix`, `type:feature`, `type:audit`, `type:refactor`, `type:ops`, `type:security`, `type:docs`.
4. **Exatamente um Modo de Execução**: `execution:auto`, `execution:manual`, `execution:plan`.
5. **Exatamente um Estado de Ciclo de Vida**: `ag:queued`, `ag:working`, `ag:blocked`, `ag:review`, `ag:done`, `ag:cancelled`.
6. **Risco Opcional**: `risk:low`, `risk:medium`, `risk:high`.

---

## 4. Portões de Auditoria Pré e Pós-Execução

### 4.1. Dupla Verificação Independente Obrigatória
1. **Verificação 1 (Planejamento & Despacho - Lógica/Metadados):**
   - Valida `target_project` e `target_repo` diretamente no repositório do projeto ativo (`queue_repo == target_repo`).
   - O nome da pasta física local é quem manda na identidade do projeto no GitHub e nas ferramentas.
2. **Verificação 2 (Pré-Escrita Física - Ambiente, Soberania da Pasta & Git Real):**
   - **Soberania da Pasta Local:** Valida existência prévia do diretório físico do workspace (`basename` local manda; auto-criação via `git init` é estritamente proibida / Fail-Closed).
   - Valida correspondência de top-level do Git com a pasta física real do projeto (`git rev-parse --show-toplevel == workspace`).
   - Valida URL de origem remota do Git (`git remote get-url origin`).
   - Avalia estado do worktree e stale contra o baseline SHA.
   - Bloqueia mutação se qualquer verificação falhar (`PRE_FLIGHT=BLOCKED`).

### 4.2. Auditoria Pós-Execução (POST_FLIGHT_AUDIT)
- Verifica se nenhum arquivo fora de `allowed_scope` foi modificado (`FILES_OUTSIDE_ALLOWED_SCOPE=0`).
- Verifica se nenhum arquivo fora do workspace foi criado (`FILES_OUTSIDE_WORKSPACE=0`).
- Executa testes direcionados e regressão completa (`Test Before / Test After`).
- Realiza escaneamento contra segredos e credenciais vazadas.
- **`ag:done` é ESTRITAMENTE PROIBIDO** se a auditoria pós-execução não passar com `POST_FLIGHT=PASS`.

---

## 5. Governança Canônica de Filas, Planos e Agentes

1. **Criação Exclusiva no Repositório do Projeto:** Issues de tarefas são criadas única e exclusivamente no repositório de cada projeto (`queue_repo == target_repo`). Proibido centralizar em repositórios externos.
2. **Independência Total de Filas e Isolamento de ID:** As tarefas de cada projeto são estritamente isoladas. A menção a "fila número 25" refere-se exclusivamente ao projeto ativo (`<Projeto_Ativo>#25`), sem confusão entre projetos.
3. **Fonte Única de Planejamento (Apenas UM `current_plan`):** Existe exatamente um plano ativo por projeto (`CURRENT_PLAN.md` ou `current_plan` no estado canônico). Novos planos substituem ou refinam o `current_plan` existente; proibido manter planos paralelos.
4. **Higienização de Tarefas Obsoletas / Puladas / com Risco de Regressão:** Issues pendentes que foram puladas, tornaram-se redundantes após avanços do código, ou cuja execução causaria regressão ao estado atual, devem ser formalmente auditadas e excluídas/canceladas com justificativa explícita.
5. **Organização Hiperdetalhada das Issues no GitHub:** O corpo de cada Issue deve conter o contrato técnico integral (metadados YAML, objetivo detalhado, Scope Lock, critérios de aceitação e comandos de validação), garantindo máxima clareza do GitHub até o executor Antigravity.
6. **Separação de Agentes Definida pelo GitHub:** A delegação de agentes/subagentes é controlada e registrada diretamente nas Issues do GitHub (`assigned_agent`, `agent_role`, `MAX_WRITER_PER_PROJECT = 1`).
7. **Conversa não é Execução**: Conversas e diagnósticos não despacham tarefas autônomas sem confirmação explícita (`user_execution_confirmed: true`).
