# 🚀 Antigravity Turbinado (AI Orchestration Kit)

> **A infraestrutura profissional de desenvolvimento autônomo que conecta ChatGPT, GitHub e Google Antigravity em uma esteira de engenharia de software de alta performance.**

[![Version](https://img.shields.io/badge/version-v0.1.0-blue.svg)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()
[![OS](https://img.shields.io/badge/OS-macOS%20%7C%20Windows-lightgrey.svg)]()
[![Security](https://img.shields.io/badge/Security-Zero--Spyware%20Verified-success.svg)](SECURITY.md)

---

## 📌 Visão Geral & Proposta de Valor

O **Antigravity Turbinado** é um kit de engenharia e orquestração autônoma pronto para produção. Ele transforma o desenvolvimento assistido por IA em uma esteira determinística, auditável e sem retrabalho manual, estabelecendo a divisão canônica de responsabilidades:

```text
       ┌──────────────────────────┐
       │         USUÁRIO          │ (Comando em linguagem natural / Requisito)
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │    CHATGPT / PLANNER     │ (Planeja, decompõe, seleciona a Skill
       └────────────┬─────────────┘  e gera o Execution Packet com Scope Lock)
                    │
                    ▼
       ┌──────────────────────────┐
       │   GITHUB ISSUES (SOT)    │ (Fonte Única da Verdade operacional;
       └────────────┬─────────────┘  backlog estruturado e organizador de tarefas v5)
                    │ Execution Packet (agent_task v5)
                    ▼
       ┌──────────────────────────┐
       │    ANTIGRAVITY LOCAL     │ (ÚNICO executor de código autorizado;
       └────────────┬─────────────┘  autonomia máxima dentro do workspace do projeto)
                    │
                    ▼
       ┌──────────────────────────┐
       │     TESTES & COMMIT      │ (Metodologia: Test Before / Test After;
       └────────────┬─────────────┘  verificação de regressões e diff limpo)
                    │
                    ▼
       ┌──────────────────────────┐
       │    GITHUB STATE SYNC     │ (Recibo de entrega, SHA e fechamento da Issue)
       └──────────────────────────┘
```

---

## 💎 Modelos Comerciais & Planos de Acesso

O produto é distribuído e suportado através do nosso canal oficial de atendimento:

👉 **Canal Oficial de Atendimento & Suporte:** `<support-url>`

### Tabela de Ofertas

| Plano | Valor | O que está incluso |
|---|---|---|
| **Plano Core** | **R$ 299,00** | • Instaladores automáticos (macOS e Windows)<br>• Autonomia no Workspace com política de Scope Lock<br>• Catálogo nativo com 100 skills essenciais prontas<br>• Skill Router dinâmico com acervo ampliado de 2.492 skills<br>• Integração ChatGPT (Web + Desktop App) com perfil Planner<br>• Templates canônicos de Issue v5, Governança e AGENTS.md |
| **Combo Pro (Recomendado)** | **R$ 399,00** | • **Tudo do Plano Core**<br>• **Conta Google Gemini Pro/Ultra configurada por 18 meses**<br>• Suporte prioritário via canal oficial: `<support-url>`<br>• Setup guiado one-on-one com onboarding do primeiro projeto |

---

## ⚙️ Arquitetura dos 3 Pilares Fundamentais

### 1. ChatGPT = Planejador e Orquestrador (Não Executa Código)
- O ChatGPT atua com perfil comportamental padronizado (Custom Instructions).
- Ele **não** altera arquivos locais, não abre terminais e não manipula senhas.
- Ao receber uma solicitação do usuário, ele:
  1. Identifica o projeto e lê o contexto do repositório GitHub selecionado pelo cliente.
  2. Consulta o catálogo de skills técnicas e sugere a skill indispensável.
  3. Gera o **Execution Packet** estruturado (bloco YAML `agent_task` v5) em uma nova Issue no GitHub.
  4. Define explicitamente o objetivo, critérios de aceite e os caminhos permitidos em `allowed_scope`.

### 2. GitHub = Fonte Única de Verdade (State of Truth - SOT)
- Nada é verdade no ecossistema se não estiver registrado e versionado no GitHub.
- Todas as decisões, branches, baseline SHAs, escopos permitidos (`allowed_scope`) e critérios de aceite residem na Issue.
- As tarefas utilizam taxonomia de labels estrita: `priority:*`, `type:*`, `execution:auto`.
- O GitHub do próprio cliente funciona como o backlog transparente de engenharia.

### 3. Antigravity = Único Executor Local Autorizado
- O Google Antigravity executa os passos com foco cirúrgico no workspace do projeto.
- **Configuração de Permissões Turbo & Blindagem do SO:**
  - **Dentro da pasta do projeto:** Autonomia máxima Turbo com execução contínua de comandos, ferramentas e testes sem travamentos (`CASCADE_COMMANDS_AUTO_EXECUTION_EAGER`).
  - **Fora da pasta do projeto (Espaço do Usuário):** Autonomia estendida no escopo do usuário (`AGENT_SETTING_POLICY_ALLOW` para `$HOME` e `/tmp`), viabilizando leitura de dependências globais e caches sem paradas redundantes no IDE.
  - **Recursos do Sistema & Hardware:** Blindados nativamente pelo sistema operacional (macOS SIP/TCC para Câmera/Microfone/Tela; Windows UAC/ACLs para System32/HKLM).
- **Auditoria de Escopo & Zero Segredos:** Commits são cancelados imediatamente caso arquivos fora de `allowed_scope` ou padrões de chaves/tokens sensíveis sejam detectados.

---

## 📂 Arquitetura Modular Unificada

O ecossistema está consolidado em 4 módulos canônicos, estruturados e testados:

```text
ANTIGRAVITY TURBINADO/
├── 1-governanca-e-regras/    # Regras inegociáveis: menor diff, test before/after, Sentinela Guardião
├── 2-prompts-chatgpt/        # Prompts Mestres: Chatgpt Sentinela Orchestrator, Cloud-First e Capabilities
├── 3-instalacao-skills/      # Instalador de skills e catálogo das 100 essenciais + acervo de 2.450+
├── 4-automacao-e-shell/       # Motor Semântico v5.2, agy_cmd.sh, dicionário canônico e suíte de 52 testes
├── apresentacao/             # Materiais executivos de apresentação (HTML, PDF, Markdown)
├── install.sh                # Instalador mestre automatizado em 1 comando (macOS / Linux)
└── installer/                # Instaladores dedicados (macOS / Windows PowerShell)
```

---

## 🛠️ Instalação Rápida & Onboarding Limpo

O instalador foi projetado para configurar exclusivamente os dados fornecidos pelo próprio cliente em ambiente neutro:

### Requisitos Prévios
- **macOS** (macOS 13+) ou **Windows 10/11** (PowerShell 5.1+).
- **Git** instalado e configurado com credenciais do cliente.
- **Python 3.10+** no PATH.
- **Google Antigravity** instalado.

---

### Execução da Instalação

#### No macOS / Linux (Instalador Mestre Unificado):
```bash
chmod +x install.sh
./install.sh
```

#### No Windows:
```powershell
powershell -ExecutionPolicy Bypass -File .\installer\install.ps1
```

O assistente de onboarding executa transparentemente:
1. Detecção do sistema operacional.
2. Definição da pasta de projetos do cliente (`<workspace>`).
3. Verificação da autenticação GitHub do cliente (`<github-user>`).
4. Seleção ou criação do repositório de trabalho (`<github-user>/<github-repo>`).
5. Confirmação do Google Antigravity.
6. Aplicação consentida e transparente de permissões no workspace.
7. Instalação do acervo de skills distribuíveis.
8. Exibição do Planner Profile neutro para o ChatGPT.
9. Disponibilização dos templates de Issue v5.
10. Inicialização de um workspace sandbox neutro de demonstração.

---

## 🧠 Configuração do ChatGPT (Web & Desktop App)

Para transformar o ChatGPT no planejador da esteira, copie o bloco abaixo nas **Instruções Personalizadas (Custom Instructions)** ou nas Instruções do Projeto:

```text
Você é o ChatGPT Planner & Orchestrator da arquitetura Antigravity Turbinado.
Seu papel exclusivo é entender os requisitos do cliente, planejar soluções e gerar o Execution Packet canônico para registro em GitHub Issues.
Você NUNCA executa código local, nunca manipula credenciais ou chaves privadas e nunca cria escopos fora do autorizado.

Ao receber uma solicitação:
1. Mapeie o projeto para o repositório GitHub selecionado pelo cliente (<github-user>/<github-repo>).
2. Sugira a skill técnica primária ideal do catálogo oficial (@nome-da-skill).
3. Estruture o Execution Packet no formato TASK_PROTOCOL v5 (YAML delimitado) contendo:
   - target_project, target_repo, priority, type, execution: auto
   - allowed_scope: caminhos relativos estritos autorizados para alteração
   - baseline_sha: SHA de commit atual
   - skills: primary: "@nome-da-skill"
4. Especifique critérios de aceite objetivos e oriente o Antigravity a executar com foco autônomo dentro do workspace.
```

---

## 🔍 Skill Router: Seleção Inteligente de Skills

O ecossistema conta com um roteador dinâmico (`scripts/skill_router.py`) que analisa a tarefa e seleciona a ferramenta correta sem sobrecarregar o contexto da IA:

- **100 Skills Nativas Essenciais** instaladas em `~/.agents/skills/`.
- **Catálogo de Referência com 2.492 Skills** especializadas em frontend, backend, devops, segurança, cloud e dados.
- **Roteamento Heurístico:** Ativação sob demanda sem poluir o prompt com milhares de tokens desnecessários.

---

## 🔒 Compromisso Anti-Spyware & Modelo de Confiança

O Antigravity Turbinado foi construído com respeito irrestrito à soberania da sua máquina:

- ❌ **Sem Keyloggers** ou monitoramento de teclado.
- ❌ **Sem Captura Contínua de Tela** ou espionagem de área de transferência.
- ❌ **Sem Dumps de Keychain / Senhas do Sistema**.
- ❌ **Sem Túneis Ocultos** ou telemetria invasiva.
- ✅ **Manifesto de Rede Transparente:** Todas as conexões externas são declaradas em [docs/NETWORK_MANIFEST.md](docs/NETWORK_MANIFEST.md).
- ✅ **Manifesto de Permissões:** Detalhamento exato de cada permissão em [docs/PERMISSION_MANIFEST.md](docs/PERMISSION_MANIFEST.md).
- ✅ **Desinstalação Limpa:** Script `scripts/uninstall.py` remove completamente os componentes sem deixar rastros.

---

## 📋 Diagnóstico & Suporte

Para verificar a saúde de toda a instalação a qualquer momento:

```bash
# macOS / Linux
python3 scripts/doctor.py

# Windows
python scripts\doctor.py
```

Para dúvidas, contratação e suporte técnico oficial:
💬 **Canal de Atendimento:** `<support-url>`
