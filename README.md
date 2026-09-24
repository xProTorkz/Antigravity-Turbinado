# 🚀 Antigravity Turbinado (AI Orchestration Kit)

> **A infraestrutura profissional de agentes autônomos que une ChatGPT, GitHub, Sentinela e Google Antigravity em um fluxo produtivo de nível enterprise.**

[![Version](https://img.shields.io/badge/version-v0.1.0-blue.svg)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()
[![OS](https://img.shields.io/badge/OS-macOS%20%7C%20Windows-lightgrey.svg)]()
[![Security](https://img.shields.io/badge/Security-Zero--Spyware%20Verified-success.svg)](SECURITY.md)

---

## 📌 Visão Geral & Proposta de Valor

O **Antigravity Turbinado** é um kit de orquestração autônoma e governança distribuída pronto para produção. Ele transforma o desenvolvimento orientado por IA em uma esteira determinística, auditável e sem retrabalho, reproduzindo com fidelidade a divisão canônica de responsabilidades:

```text
       ┌──────────────────────────┐
       │         USUÁRIO          │ (Comando em linguagem natural / Requisito)
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │    CHATGPT / PLANNER     │ (Planeja, decompõe, seleciona a Skill canônica
       └────────────┬─────────────┘  e gera o Execution Packet com Scope Lock)
                    │
                    ▼
       ┌──────────────────────────┐
       │   GITHUB ISSUES (SOT)    │ (Fonte Única da Verdade operacional;
       └────────────┬─────────────┘  nenhum código roda sem contrato registrado)
                    │ Execution Packet (agent_task v5)
                    ▼
       ┌──────────────────────────┐
       │   CONTROL PLANE / ROUTER │ (Resolve o workspace local canônico,
       └──────┬────────────┬──────┘  gerencia lock de execução e fila)
              │            │
              ▼            ▼
  ┌───────────────┐   ┌───────────────────────┐
  │ SKILL ROUTER  │   │  SENTINELA GUARDIÃO   │ (Governança transversal: Scope Lock,
  │   (Curator)   │   │ (Segurança & Escopo)  │  Zero Segredos, Human Gates e Validação)
  └───────────────┘   └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │      ANTIGRAVITY      │ (ÚNICO executor de código autorizado.
                      └───────────┬───────────┘  Modo autônomo total no workspace)
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │    TESTES & COMMIT    │ (Metodologia: Test Before / Test After)
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │   GITHUB STATE SYNC   │ (Atualização de Issue, Recibo e Push)
                      └───────────────────────┘
```

---

## 💎 Modelos Comerciais & Planos de Acesso

O produto é distribuído e comercializado via gateway automatizado integrado com **Sharkbot** e canal de atendimento oficial no Telegram:

👉 **Bot Oficial de Vendas & Suporte:** [@xprotorkzdev](https://t.me/xprotorkzdev)

### Tabela de Ofertas

| Plano | Valor | O que está incluso |
|---|---|---|
| **Plano Core** | **R$ 299,00** | • Instalador automático (macOS e Windows)<br>• Sentinela Guardião v2.0 pré-configurado<br>• Catálogo nativo com 100 skills essenciais prontas<br>• Skill Router dinâmico com acesso ao acervo de 2.488 skills<br>• Integração ChatGPT (Web + Desktop App) com perfil Planner<br>• Templates canônicos de Issue e Governança |
| **Combo Pro (Recomendado)** | **R$ 399,00** | • **Tudo do Plano Core**<br>• **Conta Google Gemini Pro/Ultra configurada por 18 meses**<br>• Suporte prioritário via Telegram [@xprotorkzdev](https://t.me/xprotorkzdev)<br>• Setup guiado one-on-one com onboarding de primeiro projeto |

> **Fluxo de Compra Interativo:** Ao acessar [@xprotorkzdev](https://t.me/xprotorkzdev), o cliente navega por um menu dinâmico com navegação estruturada (botões de opções e botão "Voltar") para selecionar o plano ideal, efetuar o pagamento via Sharkbot e receber a chave de liberação/onboarding imediatamente.

---

## ⚙️ Arquitetura dos 4 Pilares Fundamentais

### 1. ChatGPT = Planejador e Orquestrador (Não Executa Código)
- O ChatGPT atua com Custom Instructions / Behavior Profile estrito.
- Ele **não** altera arquivos locais diretamente, não armazena senhas e não inventa etapas fora do contrato.
- Ao receber uma demanda do usuário, ele:
  1. Identifica o projeto canônico.
  2. Consulta a fonte da verdade no GitHub.
  3. Consulta o **Skill Router** para selecionar a skill exata.
  4. Gera o **Execution Packet** (bloco YAML `agent_task` v5) em uma nova Issue no GitHub.

### 2. GitHub = Fonte Única de Verdade (State of Truth - SOT)
- Nada é verdade no ecossistema se não estiver registrado no GitHub.
- Todas as decisões, branches, baseline SHAs, escopos permitidos (`allowed_scope`) e critérios de aceite residem na Issue.
- As tarefas utilizam taxonomia de labels estrita: `project:*`, `priority:*`, `type:*`, `ag:*`.

### 3. Antigravity = Único Executor Local Autorizado
- O Google Antigravity executa os passos com foco cirúrgico no workspace do projeto.
- **Configuração de Permissões Otimizada:**
  - **Dentro da pasta do projeto (`Workspace Policy`):** Modo autônomo com política de *Sempre permitir e proceder* com ferramentas seguras e implementações, eliminando interrupções redundantes.
  - **Fora da pasta do projeto (`Outside-of-project Policy`):** Política estrita de *Request Review / Confirmar sempre*, bloqueando mutações acidentais no sistema operacional.

### 4. Sentinela Guardião = Camada Transversal Permanente
- A Sentinela **não é uma skill comum**; é o protocolo de governança que protege o projeto.
- Governa:
  - *Scope Lock:* Bloqueia modificações fora do `allowed_scope`.
  - *Zero Segredos:* Impede o commit de chaves de API, PATs, `.env` ou dados privados.
  - *Human Gates:* Exige aprovação humana expressa para deploy de produção, destruição de dados (`rm -rf`, `DROP`) ou gastos financeiros.
  - *Isolamento Estrito:* Falha imediatamente fechado se qualquer agente tentar modificar outro projeto.

---

## 🛠️ Instalação Rápida (Multiplataforma)

O instalador foi projetado para exigir o **mínimo de Human Gates possível**, com validação transparente e segurança contra falhas.

### Requisitos Prévios
- **macOS** (Apple Silicon ou Intel com macOS 13+) ou **Windows 10/11** (com PowerShell 5.1+).
- **Git** instalado e configurado.
- **Python 3.10+** no PATH.

---

### 📦 Como Obter o Instalador Oficial

> [!IMPORTANT]
> **Acesso Exclusivo & Protegido por Licença:**  
> Por motivos de segurança contra pirataria e controle de versão, o instalador e o link de download **não são públicos**. O instalador autenticado e a sua chave exclusiva de ativação (vinculada ao seu Hardware UUID / HWID) são entregues **diretamente pelo bot oficial no Telegram [@xProTorkzbot](https://t.me/xProTorkzbot)** após a confirmação do plano.

---

### 🧰 As 3 Ferramentas Obrigatórias Antes da Instalação

Antes de rodar o instalador recebido no Telegram, certifique-se de que as 3 ferramentas base estão prontas na sua máquina:

1. **GitHub (Conta & Git CLI):**
   - Tenha uma conta ativa em [github.com](https://github.com).
   - Tenha o Git instalado (`git --version` no terminal).
   - Recomendado: GitHub CLI oficial instalado (`gh auth login`).
2. **Google Antigravity:**
   - Tenha o Google Antigravity instalado no seu computador.
   - Configure a permissão de workspace para *"Sempre permitir e proceder com as implementações"* na pasta de projetos.
3. **ChatGPT (Web ou Desktop App):**
   - Conta no [chatgpt.com](https://chatgpt.com) ou aplicativo oficial para Mac/Windows.
   - Aplique o perfil comportamental do **Planner** disponibilizado na documentação para que ele orquestre as tarefas diretamente no GitHub.


---

## 🧠 Configuração do ChatGPT (Web & Desktop App)

Para garantir que o ChatGPT gere Issues inteligentes com a seleção exata de skills, configure o seguinte perfil de comportamento nas **Instruções Personalizadas (Custom Instructions)** ou no Perfil do Projeto:

```text
Você é o ChatGPT Planner & Orchestrator da arquitetura Antigravity Turbinado.
Seu papel exclusivo é planejar, analisar requisitos e gerar o Execution Packet canônico para o GitHub.
Você NUNCA executa código local, nunca manipula credenciais e nunca inventa escopos fora do contrato.

Ao receber uma demanda:
1. Identifique o projeto canônico e verifique a Issue correspondente no GitHub.
2. Consulte o catálogo de skills e indique estritamente:
   - SKILL_PRIMARY: [skill indispensável para a tarefa]
   - SKILL_SUPPORT: [skill de apoio, somente se estritamente necessária]
3. Estruture o Execution Packet no formato TASK_PROTOCOL v5 (YAML delimitado) contendo:
   - target_project, target_repo, priority, type, execution: auto
   - allowed_scope: caminhos exatos de arquivos autorizados para alteração
   - baseline_sha: SHA de commit atual
4. Mantenha os limites de escopo e oriente o Antigravity a executar em modo autônomo dentro do workspace.
```

---

## 🔍 Skill Router: Inteligência na Seleção de Skills

O ecossistema conta com um roteador dinâmico (`scripts/skill_router.py`) que analisa a tarefa e seleciona a ferramenta correta sem sobrecarregar o contexto da IA:

- **100 Skills Nativas Essenciais** instaladas em `~/.agents/skills/`.
- **Catálogo de Referência com mais de 2.400 Skills** especializadas em frontend, backend, devops, segurança, cloud e data science.
- **Score de Confiança:** Se a tarefa não atingir 80% de precisão semântica na escolha da skill, o roteador abre um `HUMAN_REVIEW` transparente.

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
python3 scripts/doctor.py
```

Para dúvidas, ativação do Combo Pro com Gemini 18 meses ou integração corporativa, fale com nosso time de engenharia:
💬 **Telegram Oficial:** [@xprotorkzdev](https://t.me/xprotorkzdev)
