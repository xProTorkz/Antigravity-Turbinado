# 🛡️ Sentinela — Ecossistema Operacional & AI Control Plane

> **Arquitetura de Desenvolvimento Autônomo e Governança Canônica Unificada.**  
> Princípio Supremo: **ONE RULE → ONE CANONICAL SOURCE (`SENTINELA.md`).**

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()
[![Governance](https://img.shields.io/badge/governance-sentinela--v5-blue.svg)]()
[![Security](https://img.shields.io/badge/security-zero--token--guard-success.svg)]()

---

## 📌 A Visão Sentinela

O **Sentinela** é o guardião operacional supremo e a infraestrutura técnica que conecta o raciocínio estratégico, o versionamento no GitHub e a execução local autônoma do **Google Antigravity** em uma esteira contínua, isolada e determinística.

Toda a governança, integridade, restrições e regras do ecossistema residem em uma **única autoridade viva**: [`SENTINELA.md`](SENTINELA.md).

```text
       ┌──────────────────────────┐
       │     LUCAS (Comando)      │ (Visão, decisão e prioridade soberana)
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │    CHATGPT (Brain)       │ (Planejador e orquestrador; gera tarefas com Scope Lock)
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │   GITHUB (Single Truth)  │ (Backlog oficial, issues, branches, PRs e comprovantes)
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │   ANTIGRAVITY (Sentinela)│ (Único executor local autorizado; Scope Lock + Test Before/After)
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │  ENTREGA & FECHAMENTO    │ (Validação comprovada, commit SHA limpo e fechamento no GitHub)
       └──────────────────────────┘
```

---

## 🏛️ Os Pilares da Arquitetura

### 1. Uma Skill Global & Uma Governança Canônica
* **Skill Global Canônica:** `@sentinela` (`~/.gemini/config/skills/sentinela/SKILL.md`), espelhada diretamente de [`SENTINELA.md`](SENTINELA.md).
* **Contrato Mestre Injetado:** `~/.gemini/GEMINI.md` opera como injeção permanente `<RULE[user_global]>`.
* **Zero Fragmentação:** Proibida a multiplicação de arquivos de governança, prompts dispersos ou regras concorrentes.

### 2. Soberania da Pasta Física & Mapeamento 1:1
Todos os projetos da máquina residem compulsoriamente sob o diretório principal `/Users/lucasvinicius/projetos/`, distribuídos estritamente em **3 categorias canônicas**:
```text
PROJETOS/
├── SITES/           (Sites institucionais, landing pages e portais web)
├── APLICACOES/      (Aplicações desktop, utilitários, automações e mobile)
└── SISTEMAS/        (Backends, microsserviços, bots e control-plane)
```
* **Padrão Estrito "Nome Sobrenome":** Nome da Pasta = Nome do Projeto = Repositório GitHub (ex: `Atende Ai`, `Dados Bacbo`, `Buy Station`, `Jarvis Assistente`).
* **Symlinks de Compatibilidade:** A raiz mantém symlinks diretos para retrocompatibilidade instantânea com terminais e ferramentas.

### 3. Trio Fixo de Skills Locais por Projeto
Cada repositório de projeto mantém exclusivamente **3 skills locais** em `.skills/`:
1. `frontend`: Interface, componentes visuais, DOM e acessibilidade (a11y).
2. `backend`: APIs, microsserviços, controladores, lógica de negócio e persistência.
3. `seguranca`: AppSec defensivo, conformidade OWASP, proteção de segredos e sanitização.

### 4. Zero-Token Guard Permanente (Proteção Anti-Cobrança)
* Todas as APIs externas tarifadas por token operam permanentemente travadas no socket local nulo:
  `http://127.0.0.1:0/token-lock`.
* Todo o raciocínio profundo e execução técnica operam em **Modo Potência Máxima Local** (`gemini-3.8-flash-high` / High Effort), com zero consumo de tokens pagos.

---

## 📂 Estrutura do Repositório

O repositório é intencionalmente enxuto, minimalista e direto ao ponto:

```text
Antigravity Turbinado/
├── SENTINELA.md               # O Contrato Operacional Universal & Skill Canônica
├── README.md                  # Este manifesto arquitetural
├── control-plane/             # Motor Python do Dispatcher Daemon e GitHub Client
├── 4-automacao-e-shell/       # Motor SRE Zsh (agy_cmd.sh, dicionário léxico e atualizador)
└── .skills/                   # Trio local canônico (frontend, backend, seguranca)
```

---

## ⚡ Comandos Rápidos de Terminal

Os atalhos do terminal Zsh (disponíveis via `agy_cmd.sh` no `~/.zshrc`):

| Comando | Função |
| :--- | :--- |
| `google` / `agy` | Executa o Antigravity CLI com autonomia turbo e alta capacidade. |
| `agy atualizar-sentinela` | Sincroniza `SENTINELA.md` e o dicionário léxico na máquina. |
| `agy kill-port <porta>` | Libera portas TCP ocupadas imediatamente. |
| `agy status` | Exibe a telemetria do sistema, daemons e uso de recursos. |

---

## 🔒 Segurança e Integridade

* **Zero Segredos:** Proibida a inclusão de tokens, senhas ou arquivos `.env` em commits.
* **Scope Lock Cirúrgico:** Toda tarefa executada altera estritamente os arquivos autorizados na Issue.
* **Test Before / Test After:** Nenhuma tarefa é encerrada sem comprovação de testes e ausência de regressão.
