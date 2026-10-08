# 🗺️ Dicionário Canônico de Automação SRE & Motor Semântico v5.1

**Localização Canônica:** `/Users/lucasvinicius/projetos/estruturas/dicionario_automacao_core.md`  
**Fonte Canônica da Verdade (Single Source of Truth):** `semantic_registry.json`  
**Escopo:** Ecossistema Jarvis / Antigravity 2.0 / Sentinela Guardião (macOS / Unix)  
**Versão:** 5.1 (Surface Router, Execuções Compostas em DAG, Sanitização de Slash & Auditoria de Políticas)  
**Status do Documento:** *GENERATED VIEW (Documentação Gerada Compilada a partir da Single Source of Truth)*  
**Data de Geração:** `2026-10-06 11:33:07 UTC`  
**Total de Intenções Ativas:** `214` | **Slash Commands Válidos:** `351` | **Colisões Silenciosas:** `0`  

---

## 1. 🏛️ Arquitetura do Motor Semântico Global v5.1

O ecossistema opera sobre uma **Single Source of Truth** JSON (`semantic_registry.json`), garantindo desacoplamento estrito entre compreensão semântica, planejamento e execução:

```text
semantic_registry.json ➔ semantic_sets.json ➔ semantic_rules.json ➔ semantic_indexes.json
                                   ↓
                           semantic_resolver
                                   ↓
                           execution_planner (DAG)
                                   ↓
                            SURFACE_ROUTER
                        ├── AGY_BACKGROUND
                        ├── ANTIGRAVITY_VISUAL
                        └── HYBRID
                                   ↓
                               SENTINELA
                                   ↓
                                EXECUTOR
```

---

## 2. 🔀 Surface Router & Perfis de Execução

O **Surface Router** adiciona uma camada explícita de decisão entre o planejamento da tarefa e sua execução material, calculando scores dinâmicos para cada superfície:

### 2.1. Superfícies Disponíveis (`execution_surface`)
* **`AGY_BACKGROUND`:** Operações mecânicas, determinísticas, diagnósticos SRE, testes, sockets, processos e verificações Git. Executa em segundo plano com `BACKGROUND=true`, `VISIBLE_TERMINAL=false`, `UI_FOCUS=false`, mantendo logs auditáveis.
* **`ANTIGRAVITY_VISUAL`:** Modificações de código-fonte, refatorações multi-arquivo, criação de componentes e arquitetura onde a visualização de diffs e raciocínio contínuo são mandatórios.
* **`HYBRID`:** Pipelines compostos multi-etapa. Exemplo: `AGY_BACKGROUND (Recon/Audit)` ➔ `ANTIGRAVITY_VISUAL (Implementação/Reparo)` ➔ `AGY_BACKGROUND (Testes/Validação)` ➔ `SENTINELA (Post-flight)`.
* **`AUTO` (Padrão):** O Surface Router calcula os scores e seleciona automaticamente a superfície de maior pontuação.

### 2.2. Perfis de Execução (`execution_profile`)
* **`FAST`:** Tarefa pontual, intent inequívoco, baixo risco, determinística (`AGY_BACKGROUND`).
* **`STANDARD`:** Fluxo operacional normal de 1 ou 2 passos.
* **`PARALLEL`:** Múltiplos fluxos paralelos e subagentes independentes.
* **`DEEP`:** Auditoria profunda, arquitetura, investigações forenses ou alto risco.

### 2.3. Route Receipt Canônico (`ROUTE_RECEIPT`)
Toda execução gera um comprovante estruturado de roteamento contendo:
`INPUT_SOURCE`, `INTENT_ID`, `EXECUTION_PROFILE`, `EXECUTION_SURFACE`, `PROJECT`, `TARGET`, `RISK`, `POLICY`, `AGY_USED`, `ANTIGRAVITY_USED`, `SUBAGENTS_USED`, `BACKGROUND`, `UI_FOCUS`, `STEPS`, `PARALLEL_GROUPS`, `SESSION_REUSED`, `DURATION_MS`, `RESULT`.

---

## 3. 🎯 Macro-Intenções Estruturadas em DAG

Macro-intenções operam como grafos direcionados acíclicos (DAG) de execução com grupos paralelos:

### 3.1. `audit.project.hard`
* **Estratégia:** `DAG` | **Superfície Preferida:** `HYBRID` | **Política:** `READ_ONLY_FIRST`
* **Entregável / Output:** `reports/audit_diagnostic_TIMESTAMP.md`
* **Total de Passos:** `12`
* **Etapas da DAG:**
  - `step_1_identity`: identify_target (Surface: `AGY_BACKGROUND`)
  - `step_2_git_integrity`: agy_cmd audit-git-integrity (Surface: `AGY_BACKGROUND`)
  - `step_3_architecture`: inspect_topology (Surface: `AGY_BACKGROUND`)
  - `step_4_dependencies`: agy_cmd audit-deps (Surface: `AGY_BACKGROUND`)
  - `step_5_runtime`: check_runtimes (Surface: `AGY_BACKGROUND`)
  - `step_6_processes`: lsof -iTCP -sTCP:LISTEN (Surface: `AGY_BACKGROUND`)
  - `step_7_network`: agy_cmd audit-network-surface (Surface: `AGY_BACKGROUND`)
  - `step_8_configuration`: agy_cmd audit-env-drift (Surface: `AGY_BACKGROUND`)
  - `step_9_security_defensive`: agy_cmd audit-git-history-pii (Surface: `AGY_BACKGROUND`)
  - `step_10_database`: agy_cmd audit-sqlite-readonly (Surface: `AGY_BACKGROUND`)
  - `step_11_observability`: tail -n 30 *.log 2>/dev/null || true (Surface: `AGY_BACKGROUND`)
  - `step_12_report`: generate_diagnostic_report (Surface: `AGY_BACKGROUND`)
* **Grupos de Execução Paralela:** `[['step_2_git_integrity', 'step_4_dependencies', 'step_5_runtime', 'step_8_configuration'], ['step_7_network', 'step_9_security_defensive', 'step_10_database', 'step_11_observability']]`

### 3.2. `recon.project.hard`
* **Estratégia:** `DAG` | **Superfície Preferida:** `HYBRID` | **Política:** `READ_ONLY_FIRST`
* **Entregável / Output:** `technical_inventory.json`
* **Total de Passos:** `6`
* **Etapas da DAG:**
  - `step_1_identity`: project_identity (Surface: `AGY_BACKGROUND`)
  - `step_2_topology`: tree -L 3 -I node_modules 2>/dev/null || ls -la (Surface: `AGY_BACKGROUND`)
  - `step_3_entrypoints`: find . -maxdepth 3 -name package.json -o -name pyproject.toml -o -name Dockerfile (Surface: `AGY_BACKGROUND`)
  - `step_4_services`: lsof -iTCP -sTCP:LISTEN -P (Surface: `AGY_BACKGROUND`)
  - `step_5_git_state`: git status -s; git branch -vv (Surface: `AGY_BACKGROUND`)
  - `step_6_inventory`: compile_technical_inventory (Surface: `AGY_BACKGROUND`)
* **Grupos de Execução Paralela:** `[['step_2_topology', 'step_4_services', 'step_5_git_state']]`

### 3.3. `map.project.general`
* **Estratégia:** `DAG` | **Superfície Preferida:** `HYBRID` | **Política:** `READ_ONLY_FIRST`
* **Entregável / Output:** `dependency_graph.json`
* **Total de Passos:** `5`
* **Etapas da DAG:**
  - `step_1_components`: discover_nodes (Surface: `AGY_BACKGROUND`)
  - `step_2_dependencies`: discover_edges_depends_on (Surface: `AGY_BACKGROUND`)
  - `step_3_dataflows`: discover_edges_reads_writes (Surface: `AGY_BACKGROUND`)
  - `step_4_network_bindings`: discover_edges_listens_on (Surface: `AGY_BACKGROUND`)
  - `step_5_graph`: synthesize_relationship_graph (Surface: `ANTIGRAVITY_VISUAL`)
* **Grupos de Execução Paralela:** `[['step_2_dependencies', 'step_3_dataflows', 'step_4_network_bindings']]`

---

## 4. 🛡️ Governança de Risco & Auditoria de Políticas

Políticas rigorosamente auditadas com base em efeitos colaterais materiais:
* **`AUTO_ALLOWED`:** Diagnósticos e testes sem mutação de estado de produção.
* **`READ_ONLY_FIRST`:** Inspeções com bloqueio compulsório de escrita (`MUTATION_ALLOWED=false`).
* **`CONFIRM_REQUIRED`:** Mutações pontuais (ex: encerramento de processos, limpeza de caches).
* **`HUMAN_GATE`:** Ações destrutivas ou de alto risco operacional (reset, shred, chaos).
* **`REFERENCE_ONLY`:** Táticas de segurança ofensiva preservadas exclusivamente para consulta.
* **`DENIED_BY_POLICY`:** Práticas proibidas no ecossistema (ex: camuflagem de processos).

### 4.1. Invariante de Banco de Dados (`DATABASE_AUDIT_MUTATION_COUNT = 0`)
A macro `audit.database.hard` executa **estritamente PRAGMAs consultivos** (`integrity_check`, `quick_check`, `foreign_key_check`, `table_list`, etc.). Operações de compactação e alteração (`VACUUM`, `REINDEX`) residem exclusivamente nos comandos de manutenção (`db-vacuum`, `db-optimize-full`).

---

## 5. 📋 Catálogo Completo de Intenções (214 Intents Sanitizadas)

| Intent ID | Frase Canônica | Superfície | Política | Slash Commands | Idempotência |
|:---|:---|:---:|:---:|:---|:---:|
| `stress-test-load` | stress test load | `AGY_BACKGROUND` | `REFERENCE_ONLY` | `/teste-de-carga`, `/stress-test-load` | `NON_IDEMPOTENT` |
| `audit-all` | audit all | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-all`, `/auditoria-completa`, `/raio-x-completo` | `IDEMPOTENT` |
| `audit-clipboard-pii` | audit clipboard pii | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-clipboard-pii`, `/limpa-clipboard-pii` | `IDEMPOTENT` |
| `audit-compliance` | audit compliance | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-compliance` | `IDEMPOTENT` |
| `audit-cron-launchd` | audit cron launchd | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-cron-launchd`, `/audita-cron-launchd` | `IDEMPOTENT` |
| `audit-cve-extreme` | audit cve extreme | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-cve-extreme` | `IDEMPOTENT` |
| `audit-deps` | audit deps | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-deps` | `IDEMPOTENT` |
| `audit-disk-heavy` | audit disk heavy | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-disk-heavy` | `IDEMPOTENT` |
| `audit-dns-leak` | audit dns leak | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-dns-leak`, `/audita-dns-leak` | `IDEMPOTENT` |
| `audit-env-drift` | audit env drift | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-env-drift`, `/audita-env-drift` | `IDEMPOTENT` |
| `audit-full` | audit full | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-full` | `IDEMPOTENT` |
| `audit-git-history-pii` | audit git history pii | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-git-history-pii` | `IDEMPOTENT` |
| `audit-git-integrity` | audit git integrity | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-git-integrity`, `/audita-integridade-git` | `IDEMPOTENT` |
| `audit-installed-binaries` | audit installed binaries | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-installed-binaries`, `/audita-binarios` | `IDEMPOTENT` |
| `audit-licenses` | audit licenses | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-licenses` | `IDEMPOTENT` |
| `audit-network-routes` | audit network routes | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-network-routes`, `/audita-rotas-rede` | `IDEMPOTENT` |
| `audit-npm-global` | audit npm global | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-npm-global`, `/audita-npm-global`, `/node` | `IDEMPOTENT` |
| `audit-open-files-leak` | audit open files leak | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-open-files-leak`, `/audita-fd-leak` | `IDEMPOTENT` |
| `audit-open-sockets` | audit open sockets | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-open-sockets` | `IDEMPOTENT` |
| `audit-privacy` | audit privacy | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-privacy` | `IDEMPOTENT` |
| `audit-privesc-vectors` | audit privesc vectors | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-privesc-vectors`, `/audita-privilegios` | `IDEMPOTENT` |
| `audit-quick` | audit quick | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-quick`, `/auditoria-rapida` | `IDEMPOTENT` |
| `audit-secrets-deep` | audit secrets deep | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-secrets-deep`, `/procura-vazamento` | `IDEMPOTENT` |
| `audit-storage-smart` | audit storage smart | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-storage-smart`, `/audita-saude-ssd` | `IDEMPOTENT` |
| `audit-thermal-throttling` | audit thermal throttling | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-thermal-throttling`, `/audita-throttling` | `IDEMPOTENT` |
| `audit-tls-cert` | audit tls cert | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-tls-cert`, `/audita-tls` | `IDEMPOTENT` |
| `audit-zsh-env` | audit zsh env | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-zsh-env`, `/audita-zsh-env`, `/eval` | `IDEMPOTENT` |
| `audit.database.hard` | audite o banco de dados | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-database-hard`, `/audite-banco` | `IDEMPOTENT` |
| `audit.host.hard` | audite o host | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-host-hard`, `/audite-host` | `IDEMPOTENT` |
| `audit.network.hard` | audite a rede | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/audit-network-hard`, `/audite-rede` | `IDEMPOTENT` |
| `audit.project.hard` | audite o projeto | `HYBRID` | `READ_ONLY_FIRST` | `/audit-project-hard`, `/audite`, `/raio-x` | `IDEMPOTENT` |
| `auto-approve` | auto approve | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/auto-approve` | `CONDITIONALLY_IDEMPOTENT` |
| `backup-git-bundle` | backup git bundle | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/backup-git-bundle` | `CONDITIONALLY_IDEMPOTENT` |
| `backup-incremental` | backup incremental | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/backup-incremental` | `CONDITIONALLY_IDEMPOTENT` |
| `backup-quick` | backup quick | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/backup-quick`, `/empacotar`, `/salva-snapshot` | `CONDITIONALLY_IDEMPOTENT` |
| `bench-endpoint` | bench endpoint | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/bench-endpoint` | `NON_IDEMPOTENT` |
| `blindar` | blindar | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/blindar` | `CONDITIONALLY_IDEMPOTENT` |
| `auth-rate-limit-test` | auth rate limit test | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/auth-rate-limit-test`, `/testa-limite-tentativas` | `CONDITIONALLY_IDEMPOTENT` |
| `skip-git-hooks` | skip git hooks | `AGY_BACKGROUND` | `REFERENCE_ONLY` | `/skip-git-hooks`, `/ignora-hooks`, `/pula-hooks` | `CONDITIONALLY_IDEMPOTENT` |
| `ratelimit-resilience-test` | ratelimit resilience test | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/ratelimit-resilience-test`, `/testa-ratelimit` | `CONDITIONALLY_IDEMPOTENT` |
| `cert-check` | cert check | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/cert-check` | `CONDITIONALLY_IDEMPOTENT` |
| `chaos-freeze-thaw` | chaos freeze thaw | `AGY_BACKGROUND` | `HUMAN_GATE` | `/chaos-freeze-thaw`, `/congelamento-chaos` | `NON_IDEMPOTENT` |
| `chaos-kill-worker` | chaos kill worker | `AGY_BACKGROUND` | `HUMAN_GATE` | `/chaos-kill-worker` | `NON_IDEMPOTENT` |
| `check-endpoint` | check endpoint | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/check-endpoint` | `CONDITIONALLY_IDEMPOTENT` |
| `check-net` | check net | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/check-net` | `CONDITIONALLY_IDEMPOTENT` |
| `circular-deps-node` | circular deps node | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/circular-deps-node`, `/javascript` | `CONDITIONALLY_IDEMPOTENT` |
| `clean-history-secrets` | clean history secrets | `AGY_BACKGROUND` | `HUMAN_GATE` | `/clean-history-secrets` | `CONDITIONALLY_IDEMPOTENT` |
| `clean-history-tail` | clean history tail | `ANTIGRAVITY_VISUAL` | `HUMAN_GATE` | `/apaga-historico`, `/clean-history-tail` | `NON_IDEMPOTENT` |
| `clean-modules` | clean modules | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/clean-modules` | `CONDITIONALLY_IDEMPOTENT` |
| `clean-orphan-sockets` | clean orphan sockets | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/clean-orphan-sockets` | `CONDITIONALLY_IDEMPOTENT` |
| `clean-pkg-cache` | clean pkg cache | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/clean-pkg-cache` | `CONDITIONALLY_IDEMPOTENT` |
| `clean-pycache` | clean pycache | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/clean-pycache` | `CONDITIONALLY_IDEMPOTENT` |
| `clean-scratch` | clean scratch | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/antigravity-ide`, `/clean-scratch`, `/limpa-scratch`, `/scratch` | `CONDITIONALLY_IDEMPOTENT` |
| `clear-screen-mem` | clear screen mem | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/clear-screen-mem` | `CONDITIONALLY_IDEMPOTENT` |
| `cloc-code` | cloc code | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/cloc-code` | `CONDITIONALLY_IDEMPOTENT` |
| `comando` | comando | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/comando`, `/unix` | `CONDITIONALLY_IDEMPOTENT` |
| `conectar` | conectar | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/conectar` | `CONDITIONALLY_IDEMPOTENT` |
| `config-sync` | config sync | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/config-sync` | `CONDITIONALLY_IDEMPOTENT` |
| `cron-add` | cron add | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/cron-add` | `CONDITIONALLY_IDEMPOTENT` |
| `daemon-kill` | daemon kill | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/daemon-kill` | `NON_IDEMPOTENT` |
| `daemon-watch` | daemon watch | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/daemon-watch` | `CONDITIONALLY_IDEMPOTENT` |
| `daemonize` | daemonize | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/daemonize` | `CONDITIONALLY_IDEMPOTENT` |
| `db-checkpoint` | db checkpoint | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/db-checkpoint`, `/forca-checkpoint` | `CONDITIONALLY_IDEMPOTENT` |
| `db-fragmentation` | db fragmentation | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/db-fragmentation` | `CONDITIONALLY_IDEMPOTENT` |
| `db-integrity` | db integrity | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/checa-integridade`, `/db-integrity` | `CONDITIONALLY_IDEMPOTENT` |
| `db-integrity-deep` | db integrity deep | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/db-integrity-deep` | `CONDITIONALLY_IDEMPOTENT` |
| `db-optimize-full` | db optimize full | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/db-optimize-full`, `/otimiza-banco` | `CONDITIONALLY_IDEMPOTENT` |
| `db-reindex` | db reindex | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/db-reindex` | `CONDITIONALLY_IDEMPOTENT` |
| `db-stats-summary` | db stats summary | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/db-stats-summary` | `CONDITIONALLY_IDEMPOTENT` |
| `db-vacuum` | db vacuum | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/db-vacuum` | `CONDITIONALLY_IDEMPOTENT` |
| `deep-clean` | deep clean | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/deep-clean`, `/faxina-profunda` | `CONDITIONALLY_IDEMPOTENT` |
| `diff-db-schemas` | diff db schemas | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/compara-schemas`, `/diff-db-schemas` | `CONDITIONALLY_IDEMPOTENT` |
| `disguise-proc` | disguise proc | `AGY_BACKGROUND` | `DENIED_BY_POLICY` | `/disguise-proc` | `CONDITIONALLY_IDEMPOTENT` |
| `disk-usage` | disk usage | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/disk-usage`, `/system`, `/volumes` | `CONDITIONALLY_IDEMPOTENT` |
| `disown-job` | disown job | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/disown-job`, `/roda-desacoplado` | `CONDITIONALLY_IDEMPOTENT` |
| `dump-env` | dump env | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/dump-env` | `CONDITIONALLY_IDEMPOTENT` |
| `empty-trash` | empty trash | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/empty-trash` | `CONDITIONALLY_IDEMPOTENT` |
| `exec-raw` | exec raw | `AGY_BACKGROUND` | `HUMAN_GATE` | `/exec-raw` | `CONDITIONALLY_IDEMPOTENT` |
| `execution.discreet.background` | modo silencioso em background | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/background`, `/discreto`, `/execution-discreet-background`, `/modo-silencioso` | `CONDITIONALLY_IDEMPOTENT` |
| `expandir` | expandir | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/expandir` | `CONDITIONALLY_IDEMPOTENT` |
| `explain-query` | explain query | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/explain-query` | `CONDITIONALLY_IDEMPOTENT` |
| `export-db-sample` | export db sample | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/export-db-sample` | `CONDITIONALLY_IDEMPOTENT` |
| `export-sqlite-schema` | export sqlite schema | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/export-sqlite-schema` | `CONDITIONALLY_IDEMPOTENT` |
| `fd-count` | fd count | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/fd-count` | `CONDITIONALLY_IDEMPOTENT` |
| `fixar` | fixar | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/fixar` | `CONDITIONALLY_IDEMPOTENT` |
| `foco-ativo` | foco ativo | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/foco-ativo` | `CONDITIONALLY_IDEMPOTENT` |
| `force-task` | force task | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/force-task` | `CONDITIONALLY_IDEMPOTENT` |
| `fuzz-api-extreme` | fuzz api extreme | `AGY_BACKGROUND` | `REFERENCE_ONLY` | `/fuzz-api-extreme`, `/fuzzing-extremo` | `CONDITIONALLY_IDEMPOTENT` |
| `gen-secret` | gen secret | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/gen-secret` | `CONDITIONALLY_IDEMPOTENT` |
| `git-blame-clean` | git blame clean | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/git-blame-clean` | `CONDITIONALLY_IDEMPOTENT` |
| `git-dangling` | git dangling | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/git-dangling` | `CONDITIONALLY_IDEMPOTENT` |
| `git-gc-aggressive` | git gc aggressive | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/git-gc-aggressive` | `CONDITIONALLY_IDEMPOTENT` |
| `git-pickaxe` | git pickaxe | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/git-pickaxe` | `CONDITIONALLY_IDEMPOTENT` |
| `git-reflog-search` | git reflog search | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/git-reflog-search` | `CONDITIONALLY_IDEMPOTENT` |
| `inspect-headers` | inspect headers | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/inspect-headers` | `CONDITIONALLY_IDEMPOTENT` |
| `ip-local` | ip local | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/ip-local` | `CONDITIONALLY_IDEMPOTENT` |
| `isolate-dir-exec` | isolate dir exec | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/isolate-dir-exec` | `CONDITIONALLY_IDEMPOTENT` |
| `kill-port` | kill port | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/kill-port` | `NON_IDEMPOTENT` |
| `launchd-create` | launchd create | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/launchd-create` | `CONDITIONALLY_IDEMPOTENT` |
| `leak-check` | leak check | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/leak-check` | `CONDITIONALLY_IDEMPOTENT` |
| `localhost` | localhost | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/localhost` | `CONDITIONALLY_IDEMPOTENT` |
| `locked-dir` | locked dir | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/locked-dir` | `CONDITIONALLY_IDEMPOTENT` |
| `log-rotate-force` | log rotate force | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/log-rotate-force` | `CONDITIONALLY_IDEMPOTENT` |
| `map.host.general` | faça um mapeamento geral do host | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/map-host-general` | `IDEMPOTENT` |
| `map.network.hard` | faça um mapeamento da rede | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/map-network-hard` | `IDEMPOTENT` |
| `map.project.general` | faça um mapeamento geral do projeto | `HYBRID` | `READ_ONLY_FIRST` | `/map-general`, `/map-project-general`, `/mapeie` | `IDEMPOTENT` |
| `mirror-state` | mirror state | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/mirror-state` | `CONDITIONALLY_IDEMPOTENT` |
| `mock-api-server` | mock api server | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/mock-api-server` | `CONDITIONALLY_IDEMPOTENT` |
| `mock-traffic` | mock traffic | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/mock-traffic` | `CONDITIONALLY_IDEMPOTENT` |
| `mode-advanced` | mode advanced | `ANTIGRAVITY_VISUAL` | `AUTO_ALLOWED` | `/mode-advanced` | `CONDITIONALLY_IDEMPOTENT` |
| `passo-a-passo` | passo a passo | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/passo-a-passo` | `CONDITIONALLY_IDEMPOTENT` |
| `pre-deploy-audit` | pre deploy audit | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/pre-deploy-audit`, `/prepara-deploy` | `CONDITIONALLY_IDEMPOTENT` |
| `profile-cpu` | profile cpu | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/profile-cpu` | `CONDITIONALLY_IDEMPOTENT` |
| `purgar-buffers` | purgar buffers | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/purgar-buffers` | `CONDITIONALLY_IDEMPOTENT` |
| `purge-ram` | purge ram | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/purga-ram`, `/purge-ram` | `CONDITIONALLY_IDEMPOTENT` |
| `quiet-mode` | quiet mode | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/quiet-mode` | `CONDITIONALLY_IDEMPOTENT` |
| `realtime-cpu` | realtime cpu | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/eleva-prioridade`, `/realtime-cpu` | `CONDITIONALLY_IDEMPOTENT` |
| `recon.application.hard` | faça um reconhecimento na aplicação | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/recon-app-hard`, `/recon-application-hard` | `IDEMPOTENT` |
| `recon.host.hard` | faça um reconhecimento no host | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/recon-host-hard` | `IDEMPOTENT` |
| `recon.infrastructure.hard` | faça um reconhecimento na infraestrutura | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/recon-infra-hard`, `/recon-infrastructure-hard` | `IDEMPOTENT` |
| `recon.network.hard` | faça um reconhecimento na rede | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/recon-network-hard` | `IDEMPOTENT` |
| `recon.project.hard` | faça um reconhecimento no projeto | `HYBRID` | `READ_ONLY_FIRST` | `/recon`, `/recon-project-hard`, `/reconhecimento` | `IDEMPOTENT` |
| `refactor-code` | refatore o código | `ANTIGRAVITY_VISUAL` | `CONFIRM_REQUIRED` | `/refactor-code`, `/refatore` | `NON_IDEMPOTENT` |
| `repair-project` | corrija o projeto | `ANTIGRAVITY_VISUAL` | `CONFIRM_REQUIRED` | `/corrija-projeto`, `/repair-project` | `NON_IDEMPOTENT` |
| `report.problems` | mostre os problemas | `AGY_BACKGROUND` | `READ_ONLY_FIRST` | `/mostre-problemas`, `/report-problems` | `CONDITIONALLY_IDEMPOTENT` |
| `reset-clean` | reset clean | `ANTIGRAVITY_VISUAL` | `HUMAN_GATE` | `/reset-clean`, `/reseta-workspace` | `NON_IDEMPOTENT` |
| `reset-contexto` | reset contexto | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/reset-contexto` | `CONDITIONALLY_IDEMPOTENT` |
| `resilience-suite` | resilience suite | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/resilience-suite`, `/teste-resiliencia` | `CONDITIONALLY_IDEMPOTENT` |
| `rotacionar-logs` | rotacionar logs | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/rotacionar-logs` | `CONDITIONALLY_IDEMPOTENT` |
| `run-detached-subshell` | run detached subshell | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/roda-em-subshell`, `/run-detached-subshell`, `/script` | `CONDITIONALLY_IDEMPOTENT` |
| `run-idle` | run idle | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/run-idle` | `CONDITIONALLY_IDEMPOTENT` |
| `sandbox-run` | sandbox run | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/sandbox-run` | `CONDITIONALLY_IDEMPOTENT` |
| `sanitize-logs` | sanitize logs | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/gi`, `/mascara-logs`, `/sanitize-logs` | `CONDITIONALLY_IDEMPOTENT` |
| `audit-network-surface` | audit network surface | `AGY_BACKGROUND` | `REFERENCE_ONLY` | `/audit-network-surface`, `/audita-portas`, `/varre-portas` | `NON_IDEMPOTENT` |
| `scan-fixtures` | scan fixtures | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/scan-fixtures` | `CONDITIONALLY_IDEMPOTENT` |
| `sha256-check` | sha256 check | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/sha256-check` | `CONDITIONALLY_IDEMPOTENT` |
| `shred-file` | shred file | `ANTIGRAVITY_VISUAL` | `HUMAN_GATE` | `/shred-file` | `NON_IDEMPOTENT` |
| `silence-terminal` | silence terminal | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/silence-terminal` | `CONDITIONALLY_IDEMPOTENT` |
| `simulate-latency` | simulate latency | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/1000`, `/simulate-latency` | `CONDITIONALLY_IDEMPOTENT` |
| `simulate-packet-drop` | simulate packet drop | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/simulate-packet-drop` | `CONDITIONALLY_IDEMPOTENT` |
| `slowloris-sim` | connection timeout test | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/slowloris-sim`, `/testa-timeout-conexoes` | `CONDITIONALLY_IDEMPOTENT` |
| `spindump-proc` | spindump proc | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/spindump-proc` | `CONDITIONALLY_IDEMPOTENT` |
| `sqlite-vacuum` | sqlite vacuum | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/sqlite-vacuum` | `CONDITIONALLY_IDEMPOTENT` |
| `status-arquitetura` | status arquitetura | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/status-arquitetura` | `IDEMPOTENT` |
| `background-silent-exec` | background silent exec | `AGY_BACKGROUND` | `REFERENCE_ONLY` | `/background-silent-exec`, `/exec-silenciosa` | `CONDITIONALLY_IDEMPOTENT` |
| `stress-fd-exhaustion` | stress fd exhaustion | `AGY_BACKGROUND` | `HUMAN_GATE` | `/esgota-descritores`, `/stress-fd-exhaustion` | `CONDITIONALLY_IDEMPOTENT` |
| `stress-ram` | stress ram | `AGY_BACKGROUND` | `HUMAN_GATE` | `/stress-ram` | `CONDITIONALLY_IDEMPOTENT` |
| `stress-test` | stress test | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/stress-test` | `CONDITIONALLY_IDEMPOTENT` |
| `sudo-check` | sudo check | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/sudo-check` | `CONDITIONALLY_IDEMPOTENT` |
| `sudo-keepalive` | sudo keepalive | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/mantem-sudo`, `/sudo-keepalive` | `CONDITIONALLY_IDEMPOTENT` |
| `telemetria-full` | telemetria full | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/telemetria-full` | `CONDITIONALLY_IDEMPOTENT` |
| `test-project` | rode os testes | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/test-project`, `/testes`, `/valide` | `IDEMPOTENT` |
| `top-cpu` | top cpu | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/top-cpu` | `CONDITIONALLY_IDEMPOTENT` |
| `top-ram` | top ram | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/top-ram` | `CONDITIONALLY_IDEMPOTENT` |
| `trace-io` | trace io | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/trace-io` | `CONDITIONALLY_IDEMPOTENT` |
| `trace-leaks` | trace leaks | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/trace-leaks` | `CONDITIONALLY_IDEMPOTENT` |
| `travar` | travar | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/travar` | `CONDITIONALLY_IDEMPOTENT` |
| `turbo-run` | turbo run | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/modo-turbo`, `/turbo-run` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-agent-full` | unlock agent full | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/autonomia-total`, `/unlock-agent-full` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-all` | unlock all | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/desbloqueio-total`, `/unlock-all` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-arp-cache` | unlock arp cache | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/limpa-tabela-arp`, `/unlock-arp-cache` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-brew` | unlock brew | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-brew`, `/unlock-brew` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-caffeinate-session` | unlock caffeinate session | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/impede-sono-mac`, `/unlock-caffeinate-session` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-chrome-debug` | unlock chrome debug | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/fecha-chrome-debug`, `/unlock-chrome-debug` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-coreaudio` | unlock coreaudio | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/reinicia-coreaudio`, `/unlock-coreaudio` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-dev-ports` | unlock dev ports | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/mata-portas-padrao`, `/unlock-dev-ports` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-dir` | unlock dir | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-pasta`, `/unlock-dir` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-dir-tree` | unlock dir tree | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/forca-soltar-pasta`, `/unlock-dir-tree` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-dns-cache` | unlock dns cache | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/limpa-dns`, `/unlock-dns-cache` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-docker-compose` | unlock docker compose | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-docker-compose`, `/unlock-docker-compose` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-docker-sock` | unlock docker sock | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-docker`, `/docker`, `/escrita`, `/unlock-docker-sock` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-ephemeral-ports` | unlock ephemeral ports | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/recicla-portas-rapidas`, `/unlock-ephemeral-ports` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-file` | unlock file | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-arquivo`, `/unlock-file` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-file-force` | unlock file force | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/forca-soltar-arquivo`, `/unlock-file-force` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-firewall-dev` | unlock firewall dev | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/checa-firewall`, `/libexec`, `/socketfilterfw`, `/unlock-firewall-dev` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-git` | unlock git | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/arranca-o-lock`, `/destrava-o-git`, `/unlock-git` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-git-bisect` | unlock git bisect | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/aborta-bisect`, `/unlock-git-bisect` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-git-config` | unlock git config | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-git-config`, `/unlock-git-config` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-git-credentials` | unlock git credentials | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/reseta-credenciais-git`, `/unlock-git-credentials` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-git-index` | unlock git index | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-index`, `/unlock-git-index` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-git-rebase` | unlock git rebase | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/aborta-rebase`, `/rebase-apply`, `/rebase-merge`, `/travado`, `/unlock-git-rebase` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-git-worktree` | unlock git worktree | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/poda-worktree`, `/unlock-git-worktree` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-ipv6-disable` | unlock ipv6 disable | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/desativa-ipv6-wifi`, `/unlock-ipv6-disable` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-kernel-maxproc` | unlock kernel maxproc | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/aumenta-maxproc`, `/unlock-kernel-maxproc` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-kill-by-name` | unlock kill by name | `AGY_BACKGROUND` | `CONFIRM_REQUIRED` | `/mata-por-nome`, `/unlock-kill-by-name` | `NON_IDEMPOTENT` |
| `unlock-launchd-service` | unlock launchd service | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/reinicia-servico-launchd`, `/unlock-launchd-service` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-limits` | unlock limits | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/sobe-limites`, `/unlock-limits` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-macos-keychain` | unlock macos keychain | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-keychain`, `/unlock-macos-keychain` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-node-memory` | unlock node memory | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/aumenta-ram-node`, `/unlock-node-memory` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-npm` | unlock npm | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-npm`, `/unlock-npm` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-pids` | unlock pids | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/limpa-pids-orfaos`, `/unlock-pids` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-pip-lock` | unlock pip lock | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-pip`, `/state`, `/unlock-pip-lock` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-pnpm-lock` | unlock pnpm lock | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-pnpm`, `/unlock-pnpm-lock` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-port` | unlock port | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/mata-porta`, `/unlock-port` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-port-range` | unlock port range | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/libera-faixa-portas`, `/unlock-port-range` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-postgres-local` | unlock postgres local | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-postgres-local`, `/unlock-postgres-local` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-proxy` | unlock proxy | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/reseta-proxy`, `/unlock-proxy` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-python-recursion` | unlock python recursion | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/aumenta-recursao-python`, `/unlock-python-recursion` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-quarantine` | unlock quarantine | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/tira-quarentena`, `/unlock-quarantine` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-quarantine-recursive` | unlock quarantine recursive | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/tira-quarentena-pasta`, `/unlock-quarantine-recursive` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-redis-local` | unlock redis local | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-redis-local`, `/redis`, `/unlock-redis-local` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-spotlight-indexing` | unlock spotlight indexing | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/pausa-spotlight`, `/unlock-spotlight-indexing` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-sqlite` | unlock sqlite | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-sqlite`, `/unlock-sqlite` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-sqlite-force` | unlock sqlite force | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/forca-destrave-sqlite`, `/unlock-sqlite-force` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-ssh-agent` | unlock ssh agent | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-ssh`, `/unlock-ssh-agent` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-stuck-terminals` | unlock stuck terminals | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/mata-terminais-ociosos`, `/unlock-stuck-terminals` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-write-perms` | unlock write perms | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/destrava-escrita`, `/unlock-write-perms` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-yarn-lock` | unlock yarn lock | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/cache`, `/destrava-yarn`, `/unlock-yarn-lock` | `CONDITIONALLY_IDEMPOTENT` |
| `unlock-zombie-deadlocks` | unlock zombie deadlocks | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/mata-zumbis`, `/unlock-zombie-deadlocks` | `CONDITIONALLY_IDEMPOTENT` |
| `validar-schema` | validar schema | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/validar-schema` | `CONDITIONALLY_IDEMPOTENT` |
| `vmmap-summary` | vmmap summary | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/vmmap-summary` | `CONDITIONALLY_IDEMPOTENT` |
| `wal-checkpoint` | wal checkpoint | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/wal-checkpoint` | `CONDITIONALLY_IDEMPOTENT` |
| `watchdog-cpu` | watchdog cpu | `AGY_BACKGROUND` | `AUTO_ALLOWED` | `/watchdog-cpu` | `CONDITIONALLY_IDEMPOTENT` |
| `wipe-session` | wipe session | `ANTIGRAVITY_VISUAL` | `HUMAN_GATE` | `/wipe-session` | `NON_IDEMPOTENT` |

---

## 6. 🚀 Atalhos Numéricos Legados Preservados (1 a 11)

| Dígito | Intent Canônica | Ação | Superfície |
|:---:|:---|:---|:---:|
| **1** | `unlock-git` | unlock git | `AGY_BACKGROUND` |
| **2** | `unlock-dev-ports` | unlock dev ports | `AGY_BACKGROUND` |
| **3** | `unlock-all` | unlock all | `AGY_BACKGROUND` |
| **4** | `mode-advanced` | mode advanced | `ANTIGRAVITY_VISUAL` |
| **5** | `deep-clean` | deep clean | `AGY_BACKGROUND` |
| **6** | `audit-full` | audit full | `AGY_BACKGROUND` |
| **7** | `unlock-limits` | unlock limits | `AGY_BACKGROUND` |
| **8** | `sqlite-vacuum` | sqlite vacuum | `AGY_BACKGROUND` |
| **9** | `backup-quick` | backup quick | `AGY_BACKGROUND` |
| **10** | `audit-network-surface` | audit network surface | `AGY_BACKGROUND` |
| **11** | `hacker-recon-full` | hacker recon full (Forense de Baixo Nível) | `AGY_BACKGROUND` |

---

## 7. 🎯 Vocabulário Operacional do Usuário — Mission Templates (v5.2)

Transforma expressões recorrentes e frases curtas do usuário em **MISSÕES compostas, contextuais e previsíveis**.  
Uma **MISSION** não é um alias para um único comando: é uma especificação canônica que orquestra **objetivos, fases (DAG), intents referenciadas, dependências, execução paralela, roteamento de superfície e critérios de conclusão**.

### 7.1 Catálogo Canônico de Missões (21 Templates)

| Mission ID | Significado Canônico | Aliases Principais | Superfície | Política de Mutação | Fases do DAG |
|:---|:---|:---|:---:|:---:|:---|
| **`AUDIT.HARD`** | Avaliar profundamente o estado atual do alvo autorizado. | `audite`, `auditoria`, `raio-x`, `puxa a ficha`, `confere tudo` | `HYBRID` | `READ_ONLY=true` | IDENTIFY → RECON → ARCHITECTURE → CORRELATE → REPORT |
| **`VISIT.GENERAL`** | Entrar no contexto autorizado e construir visão completa sem modificar inicialmente. | `vamos fazer uma visita`, `visita técnica`, `dá uma olhada geral` | `HYBRID` | `READ_ONLY_FIRST=true` | IDENTIFY_TARGET → VERIFY_CONTEXT → CONNECT → RECON → MAP → AUDIT → FINDINGS → VISIT_REPORT *(+ DIAGNOSE, REPAIR, TEST, VALIDATE se houver "arrumar")* |
| **`REPORT.GENERAL`** | Recuperar evidências estruturadas do contexto atual e gerar panorama executivo. | `relatório`, `me manda um relatório`, `me passa o relatório`, `me dá o diagnóstico` | `ANTIGRAVITY_VISUAL` | `READ_ONLY=true` | COLLECT_EVIDENCE → NORMALIZE → CLASSIFY → PRIORITIZE → CORRELATE → REPORT |
| **`FIND.SMART`** | Localizar e correlacionar recursos, causas-raiz, arquivos ou problemas no contexto. | `encontre`, `acha`, `ache`, `procura`, `localiza`, `descubra` | `AGY_BACKGROUND` | `READ_ONLY=true` | SEARCH → CORRELATE → RANK → VERIFY *(Especializações: FIND.ROOT_CAUSE_CANDIDATES, FIND.FILE, FIND.CODE_ORIGIN, FIND.PROBLEM, FIND.RELATED_RESOURCES)* |
| **`EXECUTION.DISCREET`** | Execução em segundo plano mantendo auditoria e segurança ativas. | `modo oculto`, `modo silencioso`, `sem aparecer`, `faz em segundo plano` | `AGY_BACKGROUND` | `BACKGROUND=true, UI_FOCUS=false` | BACKGROUND_CONFIG → VALIDATE_SECURITY → SPAWN_TASK → AUDIT_LOG |
| **`EXECUTION.ADVANCED`** | Elevar profundidade analítica, permitindo subagentes e exploração estendida. | `modo avançado`, `potência máxima`, `modo turbo`, `vai fundo` | `HYBRID` | `DEPTH=HARD, PROFILE=DEEP` | ELEVATE_PROFILE → ENABLE_SUBAGENTS → DEEP_PLANNING → EXECUTE |
| **`CONNECT.SMART`** | Estabelecer ou reutilizar conexão autenticada com alvo contextual. | `se conecte`, `conecta`, `conecte`, `entra lá`, `abre conexão` | `HYBRID` | `SAFE_AUTH_CHECK` | IDENTIFY_TARGET → CHECK_EXISTING_CONN → CHECK_SESSION → VALIDATE_AUTH → CONNECT → HEALTH_CHECK *(Especializações: CONNECT.GITHUB, CONNECT.VPS, CONNECT.DATABASE)* |
| **`ACTIVATE.SMART`** | Ativar componente, serviço ou contexto garantindo idempotência. | `ative`, `ativa`, `liga`, `inicia`, `sobe`, `coloca pra rodar` | `HYBRID` | `IDEMPOTENT_START` | RESOLVE_OBJECT → CHECK_STATE → PREFLIGHT → ACTIVATE → HEALTH_CHECK *(Especializações: ACTIVATE.SERVICE, ACTIVATE.PROJECT_CONTEXT)* |
| **`ORGANIZE.SYSTEM`** | Reorganizar, classificar e limpar com detecção de dependências e segurança. | `organiza tudo`, `arruma tudo`, `organiza a casa`, `estrutura isso` | `HYBRID` | `SAFE_REORG` | RECON → CLASSIFY → DUPLICATE_DETECTION → DEPENDENCY_MAP → PLAN → SAFE_REORGANIZATION → VALIDATE |
| **`MAKE_IT_WORK`** | Investigar causa-raiz e conduzir reparo pontual com testes de regressão. | `faça funcionar`, `faz funcionar`, `resolve isso`, `conserta isso` | `HYBRID` | `CONFIRM_REQUIRED` | REPRODUCE → RECON → DIAGNOSE → ROOT_CAUSE → PLAN_FIX → REPAIR → FOCUSED_TEST → REGRESSION → VALIDATE |
| **`RECON.HARD`** | Inventariar exaustivamente todos os recursos e processos sem alterar o estado. | `reconhecimento`, `faz reconhecimento`, `recon`, `levanta o ambiente` | `AGY_BACKGROUND` | `READ_ONLY=true` | IDENTITY → (FILES, SERVICES, PROCESSES, PORTS, RUNTIME, DEPENDENCIES, DATABASES) → TECHNICAL_INVENTORY |
| **`MAP.GENERAL`** | Mapear topologia, dependências e fluxo de execução entre os componentes. | `mapeie`, `mapeia`, `faz um mapa`, `desenha isso`, `mostra a arquitetura` | `ANTIGRAVITY_VISUAL` | `READ_ONLY=true` | COMPONENT_GRAPH → DEPENDENCY_GRAPH → EXECUTION_GRAPH |
| **`REPAIR.SMART`** | Corrigir defeito de forma cirúrgica precedida de diagnóstico e sucedida de testes. | `corrija`, `corrige`, `conserta`, `arruma`, `repara`, `dá um jeito` | `ANTIGRAVITY_VISUAL` | `CONFIRM_REQUIRED` | VERIFY_PROBLEM → ROOT_CAUSE → IMPACT → MINIMAL_FIX → TEST → VALIDATE |
| **`OPTIMIZE.SMART`** | Otimizar latência e throughput com obrigatoriedade de baselines antes e depois. | `otimize`, `otimiza`, `deixa mais rápido`, `acelera`, `melhora performance` | `HYBRID` | `MUTATION_GATED` | BASELINE → PROFILE → BOTTLENECK → PLAN → OPTIMIZE → BENCHMARK → COMPARE |
| **`VALIDATE.COMPLETE`** | Executar suíte completa de validação, critérios de aceitação e checagem de estado. | `valide`, `valida`, `confere`, `testa tudo`, `garante que funciona` | `HYBRID` | `READ_ONLY_FIRST=true` | ACCEPTANCE_CRITERIA → FOCUSED_TESTS → INTEGRATION_TESTS → REGRESSION → STATE_CHECK → EVIDENCE |
| **`SYNC.SMART`** | Sincronizar estado, repositório ou configurações com destinos autorizados. | `sincronize`, `sincroniza`, `atualiza tudo`, `joga pro github` | `HYBRID` | `SAFE_SYNC` | RESOLVE_TARGET → CHECK_DRIFT → RECONCILE → APPLY_SYNC → VERIFY_STATE |
| **`INTEGRATE.SMART`** | Integrar e validar comunicação bidirecional entre dois componentes ou sistemas. | `integre`, `integra`, `conecta os dois`, `faz conversar` | `HYBRID` | `MUTATION_GATED` | IDENTIFY_A → IDENTIFY_B → CONTRACT_DISCOVERY → AUTH → INTERFACE → IMPLEMENT → TEST_A_TO_B → TEST_B_TO_A → VALIDATE |
| **`PREPARE.SMART`** | Preparar ambiente para alvo específico validando dependências e conformidade. | `prepare`, `prepara`, `deixa pronto`, `prepara pra produção` | `HYBRID` | `MUTATION_GATED` | PREFLIGHT → DEPENDENCIES → CONFIG_CHECK → WARMUP → READY *(Especializações: PREPARE.PRODUCTION, PREPARE.DEV, PREPARE.TEST, PREPARE.DEPLOY)* |
| **`REVIEW.DEEP`** | Análise minuciosa e cruzada de consistência, segurança e casos de borda. | `faz um pente fino`, `pente fino`, `olha minuciosamente`, `revê tudo` | `HYBRID` | `READ_ONLY=true` | RECON → AUDIT.HARD → CROSS_CHECK → EDGE_CASES → INCONSISTENCIES → REPORT |
| **`STABILIZE.SYSTEM`** | Estabilizar sistema garantindo resiliência, performance e ausência de regressões. | `deixa redondo`, `deixa estável`, `faz ficar robusto`, `finaliza direito` | `HYBRID` | `CONFIRM_REQUIRED` | AUDIT → DIAGNOSE → REPAIR → TEST → PERFORMANCE_CHECK → REGRESSION → FINAL_VALIDATION |
| **`COMPLETE.WORK`** | Concluir ciclo de trabalho com checagem de pendências, evidências e post-flight. | `fecha isso`, `finaliza`, `termina`, `pode fechar`, `deixa pronto e fecha` | `HYBRID` | `CONFIRM_REQUIRED` | CHECK_PENDING → TEST → ACCEPTANCE → EVIDENCE → SENTINELA_POST_FLIGHT → SYNC → DONE |

### 7.2 Modificadores de Execução (Modifiers)

Os modificadores alteram parâmetros da missão seguinte **sem gerar tarefas órfãs**:

* **`EXECUTION.DISCREET`** (`modo oculto`, `modo silencioso`, `em background`): Força execução em background (`UI_FOCUS=false`, `BACKGROUND=true`) preservando integridade, logs e segurança.
* **`EXECUTION.ADVANCED`** (`modo avançado`, `modo turbo`, `vai fundo`): Eleva profundidade (`DEPTH=HARD`, `PROFILE=DEEP`) permitindo paralelismo e subagentes reais.
* **`READ_ONLY`** (`só leitura`, `sem alterar`, `sem modificar`): Força restrição total de mutação (`MUTATION_ALLOWED=false`).
* **`FAST`** (`rápido`, `ligeiro`): Define profundidade leve (`DEPTH=LIGHT`).
* **`DEEP`** (`profundo`, `completo`): Define profundidade aprofundada (`DEPTH=HARD`).
* **`SUBAGENTS`** (`use subagentes`, `com subagentes`): Autoriza delegação concorrente a subagentes.

### 7.3 Composição Multi-Missão

Expressões compostas geram DAGs orquestradas em pipeline determinístico:
* `"modo oculto, se conecte e faça uma visita"` → `[EXECUTION.DISCREET] + CONNECT.SMART → VISIT.GENERAL`
* `"modo avançado, audite e encontre qualquer problema"` → `[EXECUTION.ADVANCED] + AUDIT.HARD → FIND.PROBLEM`
* `"faça uma visita e me mande um relatório"` → `VISIT.GENERAL → REPORT.GENERAL`
* `"encontre o problema, corrija e valide"` → `FIND.PROBLEM → REPAIR.SMART → VALIDATE.COMPLETE`
* `"organiza tudo e faça funcionar"` → `ORGANIZE.SYSTEM → MAKE_IT_WORK`
* `"reconheça, mapeie e audite"` → `RECON.HARD → MAP.GENERAL → AUDIT.HARD`
* `"otimize, teste e me mostre a diferença"` → `OPTIMIZE.SMART → VALIDATE.COMPLETE → REPORT.GENERAL`

---

## 8. 🥷 Arsenal Hacker SRE: Forense de Baixo Nível, Kernel Tracing & Resgate Avançado (macOS/Darwin)

Comandos cirúrgicos de engenharia de sistemas, análise forense de memória, inspeção de pacotes brutos (wire), cirurgia física de dados e mitigação de deadlocks no kernel Darwin:

### 8.1 Catálogo do Arsenal Hacker (22 Comandos de Elite)

| Comando CLI | Alias / Frase Direta | Domínio | Descrição Técnica & Efeito Material |
|:---|:---|:---:|:---|
| `agy_cmd hacker-recon-full` | `arsenal-hacker`, `raio-x-hacker` | **Forense Geral** | Varredura forense consolidada: top RSS/dirty pages, descritores unlinked (`+L1`), sockets anômalos, portas em escuta, integridade SQLite e objetos Git órfãos. |
| `agy_cmd proc-tree-annihilate <PID>` | `mata-arvore`, `tree-kill` | **Processos/Kernel** | Congela (`SIGSTOP`) e elimina recursivamente (`SIGKILL`) toda a árvore genealógica de um processo, impedindo subprocessos em fuga ou adoção pelo PID 1 (`launchd`). |
| `agy_cmd proc-env-snoop <PID>` | `espia-env`, `snoop-env` | **Processos/Memória** | Extrai em tempo real variáveis de ambiente e argumentos de qualquer PID em execução na memória via `ps -wwE` sem parar a aplicação. |
| `agy_cmd proc-fd-map <PID>` | `mapa-descritores`, `fd-map` | **Processos/FDs** | Mapeia todos os descritores (arquivos abertos, pipes, sockets TCP/UDP e UNIX domain) de um processo com tipo e caminho. |
| `agy_cmd fd-unlinked-hunter` | `arquivos-fantasmas`, `unlinked-fd` | **Disco/Forensics** | Caça arquivos deletados do disco (`rm`) que continuam retidos por processos ativos consumindo espaço físico invisível (`lsof +L1`). |
| `agy_cmd mem-dirty-inspect <PID>` | `raio-x-memoria`, `mem-dissect` | **Memória/Darwin** | Disseca páginas de memória virtual do processo: Resident Size, Dirty Pages, Swapped e regiões de Malloc Large/Small via `vmmap`. |
| `agy_cmd mem-leak-deep <PID>` | `caca-leaks`, `deep-leak` | **Memória/Heap** | Varredura profunda de vazamentos de heap via `leaks CLI`, mapeando ciclos de referências e blocos de memória órfãos em C/Node/Python. |
| `agy_cmd socket-sniff-loopback <P>` | `sniff-porta`, `wire-sniff` | **Rede/Wire** | Sniffer cirúrgico na interface loopback (`lo0`) para portas de desenvolvimento (3000, 8000, 8765, etc.), exibindo tráfego HTTP/WebSocket em ASCII/HEX. |
| `agy_cmd tcp-teardown-force` | `derruba-conexoes-presas`, `tcp-drain` | **Rede/Sockets** | Drena e força o encerramento imediato de sockets TCP presos em `TIME_WAIT`, `CLOSE_WAIT` ou `FIN_WAIT_2` que causam `EADDRINUSE`. |
| `agy_cmd stealth-port-recon [HOST]` | `varredura-furtiva-portas` | **Rede/Recon** | Reconhecimento furtivo instantâneo de portas no localhost via sockets raw `/dev/tcp` do shell sem ferramentas externas e sem flood. |
| `agy_cmd dns-poison-audit` | `audita-dns-hijack`, `dns-forensics` | **Rede/DNS** | Audita `/etc/hosts` e resolvedores do `scutil --dns`, detectando desvios locais, spoofing e proxies intermediários indesejados. |
| `agy_cmd wire-latency-jitter <URL>` | `jitter-rede`, `net-jitter` | **Rede/Métricas** | Mede latência e jitter (desvio padrão) em milissegundos com rajada de microprobes para diagnosticar gargalos na pilha de rede local. |
| `agy_cmd sqlite-raw-recover <DB>` | `resgata-sqlite`, `sqlite-rescue` | **Banco/Cirurgia** | Cirurgia de recuperação em bases SQLite corrompidas ("disk image malformed"): extrai páginas íntegras via stream `.recover` e recria banco limpo. |
| `agy_cmd sqlite-wal-nuke-flush <DB>` | `trunca-wal-forcado`, `wal-nuke` | **Banco/WAL** | Mata conexões ativas segurando o arquivo, força checkpoint exclusivo (`PRAGMA wal_checkpoint(TRUNCATE)`) e trunca WAL para 0 bytes. |
| `agy_cmd file-hex-inspect <ARQ>` | `hex-magic`, `magic-bytes` | **Binários/Hex** | Disseca magic bytes e cabeçalho hexadecimal dos primeiros 64 bytes para identificar formato real e desmascarar camuflagem de extensão. |
| `agy_cmd macho-binary-audit <BIN>` | `disseca-binario`, `macho-inspect` | **Binários/macOS** | Dissecação de binários Mach-O: arquiteturas (`lipo`), bibliotecas vinculadas (`otool -L`), assinaturas (`codesign`) e validação Gatekeeper (`spctl`). |
| `agy_cmd git-resurrect-dangling` | `resgata-commits-perdidos` | **Git/Arqueologia** | Localiza commits e árvores órfãs perdidas após `git reset --hard` ou rebase, exibindo mensagens e permitindo restauração imediata. |
| `agy_cmd git-pack-heaviest` | `top-objetos-git`, `git-heavy-objects`| **Git/Armazenamento**| Disseca os 10 maiores objetos binários no repositório Git usando `git verify-pack -v` nos índices de pack. |
| `agy_cmd git-forensic-timeline` | `linha-do-tempo-git` | **Git/Auditoria** | Reconstrói cronologia completa das últimas 24h cruzando reflog, stashes e commits recentes. |
| `agy_cmd tty-sane-rescue` | `destrava-terminal`, `sane-term` | **Terminal/TTY** | Restaura o driver de terminal após despejo de binários na tela que corrompem o cursor (`stty sane`, `tput reset`). |
| `agy_cmd kernel-ipc-nuke` | `limpa-ipc-orfaos`, `ipc-clean` | **Kernel/IPC** | Varre e remove semáforos e blocos de memória compartilhada POSIX/SysV órfãos (`ipcs` e `ipcrm`). |
| `agy_cmd sandbox-jail-exec <CMD>` | `exec-em-jail`, `jail-run` | **Isolamento** | Executa scripts ou comandos em subshell restrito com limites rígidos de memória virtual (`ulimit -v 1GB`) e CPU (`ulimit -t 30s`). |

---

## 9. 🛡️ Auditoria Defensiva Avançada, Escaneamento Estruturado & Macro-Pipelines em Linguagem Natural

Módulo especializado em auditoria de segurança perimétrica, verificação de conformidade HTTP, análise estática de vulnerabilidades e encadeamento em pipelines acionados por linguagem natural direta.

### 9.1 Ferramentas de Auditoria Defensiva & Escaneamento Estruturado

| Comando CLI | Alias / Frase Direta | Domínio | Descrição Técnica & Efeito Material |
|:---|:---|:---:|:---|
| `agy_cmd scan-ports-deep [H] [P]` | `varredura-portas-deep`, `port-scan-deep` | **Rede/Portas** | Varredura estruturada de portas TCP com conexão não-bloqueante e extração automática de banners de serviço HTTP/Raw sem dependência de binários externos. |
| `agy_cmd audit-web-stack [URL]` | `inspecionar-web-stack`, `audit-headers-sec` | **Web/Headers** | Avalia postura de segurança HTTP: Content-Security-Policy (CSP), HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, CORS e vazamento de versão via cabeçalhos Server/X-Powered-By. |
| `agy_cmd fuzz-routes-fast [URL]` | `varrer-rotas-sensiveis`, `fuzz-routes` | **Web/Recon** | Varredura defensiva rápida de arquivos sensíveis e rotas críticas expostas (`/.env`, `/.git/HEAD`, `/config.json`, `/metrics`, `/healthz`, `/swagger.json`, `/admin`). |
| `agy_cmd audit-sql-sanitization [DIR]`| `auditoria-sql`, `sql-injection-audit` | **Código/SAST** | Análise estática que caça interpolações diretas de strings (f-strings, concatenações `+`, template literals `${}`) em queries SQL em Python, JS/TS, PHP e Go, sugerindo Prepared Statements. |
| `agy_cmd audit-cms-plugins [DIR]` | `auditoria-cms`, `cms-plugins-audit` | **CMS/Deps** | Inventário e auditoria de frameworks CMS (WordPress, Strapi) e manifests de pacotes, alertando sobre flags de debug ativas e dependências declaradas. |
| `agy_cmd audit-privesc-vectors` | `auditoria-privesc`, `privesc-check` | **Hardening/OS** | Auditoria defensiva de escalação de privilégios no macOS/Darwin: binários com SUID/SGID ativo no PATH, diretórios world-writable, LaunchDaemons inseguros e regras NOPASSWD no sudoers. |
| `agy_cmd audit-hidden-webshells [DIR]`| `caca-webshells`, `webshell-hunt` | **Antivírus/Forense**| Caça forense em arquivos de script (.php, .py, .js, .sh) por padrões de backdoors conhecidos: `eval(base64_decode)`, `gzinflate`, `shell_exec($_GET)`, `eval(compile)`, `exec(base64)` e droppers ofuscados. |

### 9.2 Macro-Pipelines Executáveis por Frases em Linguagem Natural

Pipelines multi-comandos orientados a DAG que encadeiam diagnósticos e auditorias automáticas através de gírias e frases naturais:

#### 1. `auditoria-total` / `"auditoria total"` / `"varredura completa"`
**Regra Canônica de Execução: Auditoria Total Replicador**

##### 🧭 Diretriz de Rastreamento (Engine Rule)
O motor de busca **NÃO PODE** pular fases. Para avançar da Fase `N` para a Fase `N+1`, o arquivo declarado em `saida_esperada` na Fase `N` deve existir em disco, ser validado e conter dados estruturados não nulos.

##### 🔁 Regra Dinâmica de Retroalimentação (Recursive Discovery)
Se durante a execução da **Fase 3 (Histórico)** ou da **Fase 5 (Brute Force de Rotas)** o motor descobrir novos endpoints, subdiretórios ou arquivos `.js` que não constavam no mapa inicial, ele é obrigado a:
1. **Injetar** essas novas rotas retroativamente na fila de execução da **Fase 1** (para interceptação de requisições) e da **Fase 2** (para varredura de HTML Oculto).
2. O pipeline de auditoria só será considerado concluído quando uma varredura completa (`Fase 1` até `Fase 6`) for executada sem encontrar nenhuma nova rota adicional (**Estado de Convergência Zero**).

##### 🎯 Onde os Locais Ocultos Costumam "Se Esconder" (Checklist para o Motor)
Para garantir que o motor inspecione os vetores críticos de dados ocultos, os seguintes alvos são obrigatórios na **Fase 2** e na **Fase 6**:
1. **Estado Hidratado de Frameworks Modernos:** Varredura obrigatória dentro das tags `<script id="__NEXT_DATA__">`, `window.__Nuxt__`, `window.__INITIAL_STATE__` ou nós de Contexto do React/Vue. É ali que ficam guardados IDs, chaves de API e payloads de backend inteiros antes da página renderizar.
2. **Mapeamento de Rotas no Front (Client-Side Routing):** O motor deve buscar padrões de dicionários de rotas dentro dos arquivos `.js` compilados (ex: caminhos contendo `path: "/..."`, `component:` ou Lazy Loading de componentes).
3. **Parâmetros Ocultos por Força Bruta:** Não basta buscar páginas ocultas, o motor deve testar parâmetros comuns ocultos em URLs válidas (ex: `?debug=true`, `?admin=1`, `?export=json`).

##### 🛑 Protocolo de Persistência de Sessão Ativa (Anti-Deslogamento)
O motor de busca opera sob a premissa de que o ambiente alvo monitora ativamente a sessão do usuário:
* **Session Keep-Alive:** A cada 60 segundos, o motor dispara uma requisição "batimento cardíaco" (ping) legítima em background usando a sessão autenticada para impedir que o token expire durante varreduras longas de força bruta.
* **Gatilho de Alerta de Deslogamento:** Caso qualquer requisição mude o status de `200 OK` para `401 Unauthorized` ou `403 Forbidden` nas Fases 1 a 6, o motor pausa a execução imediatamente e emite alerta ao operador para re-autenticação, impedindo falsos-negativos (evitando interpretar como inexistente um recurso protegido por sessão expirada).

##### 🚀 Varredura por Eventos de DOM (Gatilhos de Interface na Fase 9)
Na **Fase 9 (Headless Chrome)**, o motor não realiza apenas a leitura do DOM estático, executando dinamicamente:
* **Simulação de Interação Espelhada:** Disparo programático de eventos de `Click`, `Focus` e `Hover` em todos os elementos interativos (`<button>`, `<a>`, `<li>` e abas `tab`) identificados na árvore do DOM.
* **Captura de Mutação:** Monitoramento do DOM *antes* e *depois* de cada clique/interação, isolando novos nós de HTML que apareçam dinamicamente (modais de configuração, abas de histórico, popups informativos, logs ocultos ou novos links).

##### 🥷 Evasão de Bloqueios de Rede & Políticas Anti-Bot (Fases 3 e 5)
Para garantir que o Brute Force (Fase 5) e o Histórico (Fase 3) não sofram interrupção perimétrica por Firewalls (WAF):
* **Fuzzy Jitter Delay:** As requisições automáticas contêm atraso pseudo-aleatório variável (entre 0.8s e 2.4s) e rotação de User-Agents reais simulando navegadores legítimos (Chrome, Safari, Firefox).
* **Throttling Inteligente:** Se o servidor responder `429 Too Many Requests`, o motor reduz a velocidade de busca imediatamente pela metade e aguarda o intervalo indicado no cabeçalho `Retry-After`.

##### 🛡️ Orquestração Furtiva de Segurança
* **Modo**: `READ_ONLY_FIRST = true`
* **Mutação**: `MUTATION_ALLOWED = false` (Bloqueio estrito de requisições POST/PUT/DELETE que alterem estado do alvo).
* **Rastreabilidade**: `AUDIT_LOGGING = true`. Toda ação gera um log incremental que será compilado no laudo final.

##### 📊 Matriz de Mapeamento das 10 Camadas de Auditoria
A execução das 10 Fases descritas no `dicionario_lexico.json` deve cobrir obrigatoriamente as 10 camadas de arquitetura do alvo. O relatório consolidado `./reports/audit_total_TIMESTAMP.md` deve estruturar as falhas mapeando:

| Divisão | # | Camada Auditada | Fase Principal de Captura |
| :--- | :--- | :--- | :--- |
| **Frontend & Borda** | 1 | Apresentação / UI | Fase 8 (Captura de Mídia) & Fase 9 (DOM Headless) |
| | 2 | Lógica de Interação | Fase 2 (HTML Oculto) & Fase 6 (Extração Avançada) |
| | 3 | Gerenciamento de Estado | Fase 2 (__NEXT_DATA__ / Redux / Contexts) |
| | 4 | Rede / Clientes de API | Fase 1 (Interceptação de Tráfego) |
| | 5 | Gateway & Borda (TLS/CORS) | Fase 1 & Fase 3 (Endpoints) |
| **Backend & Dados** | 6 | Controladores & Rotas | Fase 3 (LinkFinder) & Fase 5 (Brute Force) |
| | 7 | Segurança & Auth Middleware | Fase 1 (Validação de Expiração/Uso de Sessão Ativa) |
| | 8 | Regras de Negócio | Fase 1 & Fase 7 (Análise de Comportamento dos Endpoints)|
| | 9 | Acesso a Dados (ORM/SQL) | Fase 7 (WP-CLI / Dumps estruturados permitidos) |
| | 10| Armazenamento & Banco | Fase 7 & Fase 10 (Segregação de Dados Financeiros) |

##### 💳 Padrão do Exportador Tabular Compulsório (Fase 10)
Caso qualquer string correspondente à Categoria 2 de Risco Financeiro seja identificada (PAN exposto), o motor de busca deve interromper processos de replicação externa e gerar imediatamente a saída tabular estritamente formatada no arquivo `./reports/compliance_pci_audit.json` e espelhada no laudo sob a máscara:

```text
BIN|BRAND|LEVEL|BANK|HAVE_CARDHOLDER_NAME|VALUE|TITULAR_PREVIEW
```
*Nota: Proibido salvar dados de cartão não mascarados (PAN completo, CVV ou senhas)*

* **Detalhamento das 10 Camadas Arquiteturais Canônicas:**
  1. **Camada de Apresentação (Interface de Usuário - UI):** Componentes visuais, templates, renderização, layouts, responsividade, formulários e acessibilidade (a11y).
  2. **Camada de Lógica de Interação:** Event handlers, dispatchers de ações, validações de formulário do cliente, hooks de evento e fluxos de UX.
  3. **Camada de Gerenciamento de Estado:** Stores centralizadas, reducers, contexts, reatividade de dados, ciclo de vida de estado e persistência local/sessão.
  4. **Camada de Rede (Cliente de API):** Clientes HTTP/Fetch/Axios, WebSockets, interceptors, políticas de timeout, serialização e retries com backoff.
  5. **Camada de Gateway e Roteamento de Borda:** Reverse proxies, API Gateway, balanceamento de carga, terminação TLS, CORS de borda e regras de ingress.
  6. **Camada de Entrada e Roteamento (Controladores / API):** Controladores HTTP, rotas REST/GraphQL, validação de payload/schemas e documentação de rotas.
  7. **Camada de Segurança e Autenticação (Middleware):** Middlewares de autenticação, verificação JWT/sessão, autorização (RBAC/ABAC), sanitização anti-XSS/SQLi e headers de segurança (CSP/HSTS).
  8. **Camada de Regras de Negócio (Serviços):** Serviços de domínio, use cases, fluxos transacionais, orquestração de operações e invariantes de negócio.
  9. **Camada de Acesso a Dados (Persistência / ORM):** Mapeamento objeto-relacional (ORM), repositórios, query builders, migrations e integridade referencial.
  10. **Camada de Armazenamento (Banco de Dados):** Motores de bancos de dados (SQLite, PostgreSQL, MySQL), integridade física de arquivos/páginas, checkpoints WAL, locks e latência de disco.

* **Auditoria de Conformidade de Dados Financeiros (PCI-DSS Segregation em 3 Categorias Canônicas):**
  1. **Mapeamento de Controle (Metadados Permitidos):** Extração lógica de ID, `bin` (6 dígitos para roteamento regulatório), `brand` (Bandeira), `bank` (Banco Emissor), `level` (Categoria do Cartão) e `card_token` (Referência transacional segura).
  2. **Verificação de Vulnerabilidade (Sinalização de Risco):**
     - Validação de `card_preview`: Se diferente de `null` ou contendo mais que os 4 últimos dígitos visíveis/PAN desmascarado, emissão de **ALERTA CRÍTICO** de vazamento de PAN (`CRITICAL_PAN_LEAK`).
     - Validação de `have_cardholder_number`: Se valor igual a 1 ou se o número bruto estiver persistido/exposto na resposta, classificação imediata como **NÃO CONFORME** (`NON_COMPLIANT_CARDHOLDER_DATA_RETENTION`).
     - Verificação de Dados de Autenticação Sensíveis (SAD): Se houver presença de campos como `card_password`, `cvv` ou `security_code` com valor verdadeiro ou string, disparo de **BLOQUEIO IMEDIATO** no pipeline por violação estrita do **PCI-DSS Requirement 3.2**.
  3. **Log de Compliance (Saída Estruturada):** Gravação obrigatória dos resultados no arquivo de governança local `./reports/compliance_pci_audit.json`, contendo hashes SHA-256 de validação de cada endpoint/arquivo testado, preservando zero exposição de dados sensíveis em conformidade com o **PCI-DSS Requirement 3.3**.

#### 2. `auditoria-global` / `"auditoria global"` / `"//audit-global"` / `"/auditoria-global"` / `"raio-x global"`
**Regra Canônica de Auditoria Global em 6 Domínios e 23 Camadas Estruturais (Execução Invisível e Silenciosa):**  
Quando solicitada a *"auditoria global"*, o sistema executa compulsoriamente a varredura profunda de ponta a ponta sobre os 6 domínios do ecossistema e suas 23 camadas arquiteturais estruturadas, operando de forma invisível e silenciosa em segundo plano (`AGY_BACKGROUND`, `UI_FOCUS=false`, `VISIBLE_TERMINAL=false`, `BACKGROUND=true`, supressão de ruído no terminal e sem foco/troca de janelas ou abas):

* **Domínio 1: Frontend (Client-Side) [Surface Web (Web Superficial)]:**
  1. **Camada de Apresentação (Interface de Usuário - UI):** Componentes visuais, templates, layouts, responsividade, formulários e acessibilidade (a11y).
  2. **Camada de Lógica de Interação:** Event handlers, dispatchers de ações, validações de formulário do cliente, hooks de evento e fluxos de UX.
  3. **Camada de Gerenciamento de Estado:** Stores centralizadas, reducers, contexts, reatividade de dados, ciclo de vida de estado e persistência local/sessão.
  4. **Camada de Rede (Cliente de API):** Clientes HTTP/Fetch/Axios, WebSockets, interceptors, políticas de timeout, serialização e retries com backoff.

* **Domínio 2: Transporte, Borda e Segurança Perimetral:**
  5. **Camada de Segurança Perimetral (WAF - Firewall de Aplicação):** Filtragem de pacotes na borda, mitigação DDoS/OWASP, inspeção de cabeçalhos e regras perimétricas.
  6. **Camada de Redes de Entrega de Conteúdo (CDN):** Cache geodistribuído de ativos estáticos, edge caching, políticas de expiração TTL e otimização de borda.
  7. **Camada de Gateway e Roteamento de Borda (DNS e Load Balancers):** Resolução de nomes DNS, balanceadores de carga L4/L7, terminação TLS, ingress e roteamento perimétrico.

* **Domínio 3: Backend (Server-Side) [Deep Web (Web Profunda / Servidor)]:**
  8. **Camada de Entrada e Roteamento (Controladores / API):** Controladores HTTP, rotas REST/GraphQL, validação de payload/schemas e documentação de rotas.
  9. **Camada de Segurança e Autenticação (Middleware):** Middlewares de autenticação, validação JWT/sessão, autorização (RBAC/ABAC), sanitização anti-XSS/SQLi e headers CSP/HSTS.
  10. **Camada de Regras de Negócio (Serviços):** Serviços de domínio, use cases, fluxos transacionais, orquestração de operações e invariantes de negócio.
  11. **Camada de Mensageria e Eventos (Filas Assíncronas):** Brokers de mensageria (Redis, RabbitMQ, Kafka), jobs em segundo plano, dead-letter queues e processamento assíncrono.
  12. **Camada de Cache Distribuído:** Cache de aplicação (Redis/Memcached), cache de sessão, invalidação de chaves e otimização de latência em leitura.
  13. **Camada de Acesso a Dados (Persistência / ORM):** Mapeamento objeto-relacional (ORM), repositórios, query builders, migrations e integridade referencial.

* **Domínio 4: Armazenamento e Análise de Dados [Camadas Avançadas de Dados e Performance]:**
  14. **Camada de Armazenamento Principal (Banco de Dados Relacional/Não-Relacional):** Motores SQL (PostgreSQL, MySQL, SQLite) e NoSQL (MongoDB), integridade física de arquivos/páginas, checkpoints WAL, locks e latência de disco.
  15. **Camada de Réplicas de Leitura e Armazenamento Analítico (Data Warehouse / BI):** Réplicas de leitura para alívio de concorrência, data lakes, pipelines analíticos e bancos analíticos (ClickHouse, BigQuery).

* **Domínio 5: Hospedagem, Virtualização e Infraestrutura (DevOps) [Abaixo do Backend]:**
  16. **Camada de Servidores Web e Proxies Reversos:** Nginx, Apache, Caddy, terminação reversa local, buffers e multiplexação HTTP/2 e HTTP/3.
  17. **Camada de Virtualização e Containers:** Runtimes Docker/Podman, imagens base, camadas de container, isolamento de namespaces e CGroups.
  18. **Camada de Orquestração de Containers:** Clusters Kubernetes/Docker Compose, réplicas, service mesh, autoscaling (HPA) e health checks (liveness/readiness).
  19. **Camada de Sistema Operacional do Servidor:** Kernel Linux/Darwin, patches de segurança, gerenciamento de memória swap, limites ulimits e systemd/launchd.
  20. **Camada de Infraestrutura como Código (IaC):** Manifestos Terraform, Ansible, scripts de automação, inventário imutável e drift de configuração.
  21. **Camada de Hardware e Provedor de Nuvem (Cloud Computacional):** Instâncias de nuvem (AWS, GCP, VPS Hostinger), CPU, memória RAM física, throughput de I/O em disco (IOPS) e conectividade de rede física.

* **Domínio 6: Operações Transversais (Cercam todas as outras) [Camadas de Operação e Segurança Transversal]:**
  22. **Camada de Integração e Entrega Contínua (CI/CD):** Pipelines de build automatizado, testes unitários contínuos, scans de SAST/DAST e esteiras de release seguro.
  23. **Camada de Observabilidade, Telemetria e Monitoramento (Logs e Métricas):** Coleta de métricas (Prometheus), tracing distribuído (OpenTelemetry), centralização de logs (SIEM, ELK, Grafana Loki) e alertas de SLO/SLI.

* **Modo Operacional:** Furtivo, invisível e silencioso em background (`READ_ONLY_FIRST`, `MUTATION_ALLOWED=false`, `AUDIT_LOGGING=true`, compilação em `reports/audit_global_TIMESTAMP.md`).
* **Sondagem Recursiva de Shadow APIs & Extração de Objetos:** Execução da varredura recursiva de endpoints REST transacionais (`/api/v1/cards`, `/api/v1/checkout`, `/api/v1/wallet/list`, `/api/v1/user/payments`, `/api/v1/consultas`) via GET e POST diagnósticos (`{"modalidade": "Consultável", "check": true}`), com extração e separação tabular no layout canônico estrito: `BIN|BRAND|LEVEL|BANK|HAVE_CARDHOLDER_NAME|VALUE|TITULAR_PREVIEW`.

#### 3. `va-mais-a-fundo` / `"va mais a fundo"` / `"vai mais a fundo"` / `"mais a fundo"`
Executa a investigação técnica de baixo nível em máxima profundidade:
1. **Dissecação de Memória**: Mapeia consumo residente (RSS) e dirty pages de processos ativos.
2. **Caça a FDs Fantasma**: Localiza descritores unlinked que retêm espaço em disco (`fd-unlinked-hunter`).
3. **Análise TCP**: Drena e audita sockets presos em TIME_WAIT/CLOSE_WAIT (`tcp-teardown-force`).
4. **Fuzzing de Endpoints**: Varre endpoints locais para expor falhas de roteamento (`fuzz-routes-fast`).
5. **Varredura Estática de SQL**: Localiza queries vulneráveis a injeção direta (`audit-sql-sanitization`).

#### 3. `mais-alem` / `"mais alem"` / `"mais além"` / `"vá mais além"`
Executa a auditoria perimétrica e forense avançada em camadas de infraestrutura:
1. **Auditoria DNS**: Varre `/etc/hosts` e scutil contra desvios de rota e spoofing (`dns-poison-audit`).
2. **Auditoria de Privilégios**: Inspeciona permissões de LaunchDaemons e binários de root (`audit-privesc-vectors`).
3. **Caça Forense Profunda**: Rastreia assinaturas de webshells no workspace (`audit-hidden-webshells`).
4. **Linha do Tempo Git**: Reconstrói eventos das últimas 24h via reflog e stashes (`git-forensic-timeline`).
5. **Análise de Jitter**: Mede latência e estabilidade da camada de sockets via rajada microprobe (`wire-latency-jitter`).

---
*(Documentação gerada automaticamente via Antigravity 2.0 / Sentinela Guardião v5.3 — Mission Templates, Arsenal Hacker SRE & Auditoria Defensiva)*