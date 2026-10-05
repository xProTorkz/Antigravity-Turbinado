# CONFIGURAÇÃO DE ALTA PERFORMANCE DO GOOGLE ANTIGRAVITY

Este documento define a configuração do ambiente de execução do **Antigravity** para eliminar interrupções desnecessárias, manter a velocidade máxima de engenharia e blindar o sistema operacional contra alterações acidentais.

---

## 1. POLÍTICA DE PERMISSÕES CIRÚRGICA (INSIDE VS. OUTSIDE WORKSPACE)

Para garantir autonomia sem perder a segurança, o Antigravity opera com uma política bifurcada de permissões:

```text
┌────────────────────────────────────────────────────────┐
│              SISTEMA OPERACIONAL DO CLIENTE            │
│                                                        │
│   ┌────────────────────────────────────────────────┐   │
│   │        DENTRO DA PASTA DO PROJETO              │   │
│   │       (/Users/.../projetos/meu-projeto)        │   │
│   │                                                │   │
│   │   • Modo: "Sempre Permitir & Proceder"         │   │
│   │   • Leitura e escrita em allowed_scope: AUTO   │   │
│   │   • Execução de testes (pytest, vitest): AUTO  │   │
│   │   • Git add / commit local auditado: AUTO      │   │
│   │   • ZERO prompts repetitivos para cada edição  │   │
│   └────────────────────────────────────────────────┘   │
│                                                        │
│   ┌────────────────────────────────────────────────┐   │
│   │        FORA DA PASTA DO PROJETO                │   │
│   │           (Qualquer outro diretório)           │   │
│   │                                                │   │
│   │   • Modo: "Request Review / Perguntar Sempre"  │   │
│   │   • Bloqueio automático fail-closed            │   │
│   │   • Intervenção humana explícita obrigatória   │   │
│   │   • Impede mutações em outros projetos do Mac  │   │
│   └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

---

## 2. APLICAÇÃO DA CONFIGURAÇÃO NO ANTIGRAVITY

### Passo 1: Ajuste de Permissões nas Configurações da Sessão
No Antigravity (IDE ou CLI):
1. Acesse **Settings → Workspace Permissions**.
2. Para o workspace do projeto ativo, defina:
   - **File Read & Write:** `Auto-Approve (In Workspace)`
   - **Terminal Commands:** `Auto-Approve for Safe Tools (git, npm, python, tests)`
   - **Outside Workspace Access:** `Strict Prompt / Request Review`

### Passo 2: Regra de Comportamento Injetada (`~/.gemini/antigravity/`)
O instalador do Antigravity Turbinado adiciona automaticamente ao diretório de configuração do Antigravity a regra canônica que instrui o agente:
- "Ao executar dentro de um workspace registrado, execute as alterações e testes diretamente sem pausar para pedir autorização a cada linha de código."
- "Se qualquer operação tentar ler ou escrever em caminhos fora da raiz do projeto, pare imediatamente e solicite revisão humana com justificativa."

---

## 3. SESSÃO PERSISTENTE POR PROJETO

- Cada projeto cadastrado no `PROJECT_REGISTRY.json` possui uma sessão persistente associada.
- Isso preserva o contexto operacional, histórico recente de commits e baseline sem poluir o contexto com tarefas de outros projetos.
- O Antigravity mantém isolamento completo de cache e dependências entre projetos diferentes.

---

## 4. DICIONÁRIO CANÔNICO DE AUTOMAÇÃO & GATILHOS DE ALTA POTÊNCIA (v3.2)

O Antigravity Turbinado inclui o Dicionário Canônico de Automação (`estruturas/dicionario_automacao_core.md`) e o roteador executável `agy_cmd.sh`, permitindo acionar tarefas administrativas complexas por frases curtas e `//comandos` padronizados sob a taxonomia de **Engenharia de Sistemas, SRE e DevOps**:
- **Processos & CPU:** `//foco-ativo`, `//kill-zombies`, `//realtime-cpu`, `//kill-port`, `//watchdog-cpu`
- **I/O & Buffers:** `//purgar-buffers`, `//clean-scratch`, `//deep-clean`, `//rotacionar-logs`
- **Git & Resiliência:** `//quick-push`, `//snapshot-force`, `//reset-clean`, `//sync-upstream`, `//bypass-hooks`
- **Redes & Sockets:** `//portas-ativas`, `//check-endpoint`, `//check-net`, `//cert-check`
- **Telemetria:** `//telemetria-full`, `//check-health`, `//disk-usage`, `//varrer-grandes`
- **Background & Silêncio:** `//exec-raw`, `//run-daemon`, `//run-idle`, `//quiet-mode`
- **Segurança & Permissões:** `//audit-perms`, `//blindar` (`//harden-workspace`), `//audit-secrets`
- **Amostragem & DR:** `//export-db-sample`, `//backup-quick`, `//leak-check`, `//sync-remote`
- **Sandbox & Chaos:** `//sandbox-run`, `//stress-test`, `//mock-traffic`, `//audit-compliance`
