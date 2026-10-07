# GUIA DEFINITIVO: INSTALAÇÃO, ARQUITETURA E USO DE SKILLS COM IA
<!--
  GUIA CANÔNICO PARA DESENVOLVEDORES E AGENTES
  Localização: CONFIGURACOES GERAIS DE PROJETO/GUIA_USO_E_INSTALACAO_SKILLS.md
  Objetivo: Instruir qualquer membro da equipe ou novo ambiente a configurar,
  usar e orquestrar skills entre o ChatGPT (Planejador) e o Antigravity/Cursor (Executores).
-->

> **Princípio Central:** Um agente de código não deve ter sua janela de contexto sobrecarregada com milhares de instruções simultâneas. Utilizamos uma **Arquitetura em Dois Níveis (Two-Tier Skill Architecture)**: 100 skills de elite ativas no cabeçalho nativo e 2.450+ skills especializadas sob demanda via MCP ou pasta de referência.

---

## 0. HIERARQUIA SUPREMA: GUARDIÃO SENTINELA E GITHUB À PARTE DE TUDO

> [!IMPORTANT]
> **ISOLAMENTO BLINDADO DE PAPÉIS:**
> 1. **O Guardião Sentinela (`guardiao-sentinela` / `@sentinela`):** É a autoridade máxima e soberana do ecossistema. Ele **NÃO** é uma skill técnica comum e **NÃO** faz parte do catálogo AAS. Ele vigia a integridade da arquitetura, protege o escopo do MVP, exige testes rígidos e aplica os gates humanos obrigatórios.
> 2. **As Skills Canônicas do Sistema (`~/.gemini/config/skills/`):** (`pesquisa-projeto`, `git-governanca`, `testes-validacao`, `seguranca-infra`, `accidental-data-loss-prevention`, etc.) formam o protocolo permanente de operação e integridade do agente. Ficam permanentemente preservadas e blindadas, intocadas por qualquer biblioteca externa.
> 3. **O GitHub (A Verdade Operacional):** O GitHub mantém a verdade canônica e materializada de cada projeto (Issues, branches, PRs, histórico atômico). Nenhuma skill de terceiros pode alterar as regras de versionamento ou o protocolo de sincronização verificável do GitHub.
> 4. **As Skills Técnicas (Catálogo AAS):** As 100 skills nativas e as 2.451 de referência são **meramente operárias e utilitárias** (como escrever código em React, FastAPI, Docker, SQL, etc.). Elas estão subordinadas à supervisão e validação do Sentinela e ao controle do GitHub.

---

## 1. O Problema da Instalação em Massa (Por que não instalar 2.400+ de uma vez?)

O repositório oficial [`sickn33/agentic-awesome-skills`](https://github.com/sickn33/agentic-awesome-skills.git) possui mais de 2.450 playbooks de engenharia de software (`SKILL.md`).

* **O Risco:** Se você instalar todas as 2.450 skills diretamente na pasta global do agente (`~/.agents/skills` ou similar), o agente tentará injetar os metadados (nome e descrição) de cada uma delas em **todos os turnos de conversa**.
* **A Consequência:** Isso consome entre 150.000 e 250.000 tokens apenas de cabeçalho fixo, estourando o *Context Budget Limit*, descartando instruções cruciais do projeto, gerando lentidão extrema e provocando falhas de execução.

---

## 2. A Solução: Arquitetura em Dois Níveis

| Nível | Onde Fica | Quantidade | Como é Ativado | Para que Serve |
| :--- | :--- | :---: | :--- | :--- |
| **Nível 1: Skills Nativas** | `~/.agents/skills/` | **100 skills** | Mencionando `@nome-da-skill` diretamente no prompt | 90% das tarefas cotidianas (React, Next.js, FastAPI, Docker, TDD, Clean Code, Postgres, etc.) |
| **Nível 2: Catálogo Expandido** | `skills/` no repositório GitHub + `CONFIGURACOES GERAIS DE PROJETO/Skills/` + MCP `aas-mcp` | **2.350+ skills** | Busca no GitHub (`.github/CATALOGO_SKILLS_COMPLETO.md`), MCP (`search_skills`) ou pasta local | Tecnologias específicas, nichos e bibliotecas avançadas |

---

## 3. Passo a Passo: Como Instalar a Estrutura em Qualquer Máquina

### Passo 3.1: Instalar as 100 Skills Nativas no Agente
Execute no terminal o comando oficial com a lista das 100 skills curadas:

```bash
npx --yes agentic-awesome-skills --antigravity --skills "\
ab-test-setup,agent-evaluation,ai-agents-architect,analytics-product,\
analytics-tracking,api-patterns,api-security-testing,app-store-optimization,\
architecture-patterns,async-python-patterns,auth-implementation-patterns,\
aws-serverless,backend-dev-guidelines,bash-linux,browser-automation,\
burp-suite-testing,business-analyst,claude-d3js-skill,clean-code,\
clean-code-guard,cloud-penetration-testing,code-refactoring-refactor-clean,\
code-review-checklist,concise-planning,context-window-management,\
data-quality-frameworks,database-design,database-optimizer,\
dbt-transformation-patterns,deployment-procedures,devops-troubleshooter,\
django-pro,docker-expert,domain-driven-design,drizzle-orm-expert,\
e2e-testing-patterns,environment-setup-guide,ethical-hacking-methodology,\
expo-api-routes,expo-cicd-workflows,expo-deployment,expo-dev-client,\
fastapi-pro,fastapi-templates,flutter-expert,form-cro,frontend-design,\
frontend-developer,git-pushing,github-actions-templates,graphql-architect,\
incident-responder,ios-developer,k6-load-testing,kpi-dashboard-design,\
kubernetes-architect,langfuse,langgraph,lint-and-validate,\
linux-privilege-escalation,llm-app-patterns,mcp-builder,mcp-tool-developer,\
microservices-patterns,mobile-developer,multi-platform-apps-multi-platform,\
nextjs-app-router-patterns,playwright-skill,postgres-best-practices,\
prisma-expert,production-code-audit,prompt-engineering,python-patterns,\
python-pro,python-testing-patterns,rag-engineer,react-best-practices,\
react-native-architecture,sast-configuration,screen-reader-testing,\
security-auditor,senior-fullstack,seo-audit,shadcn,sql-pro,stripe-integration,\
supabase,systematic-debugging,tailwind-patterns,terraform-specialist,\
test-driven-development,test-fixing,threat-modeling,top-web-vulnerabilities,\
typescript-pro,ui-a11y,using-git-worktrees,vulnerability-scanner,\
web-security-testing,webapp-testing"
```

### Passo 3.2: Configurar o Servidor MCP para o Catálogo de 2.451 Skills
No arquivo de configuração MCP do seu agente (ex: `~/.gemini/config/mcp_config.json` ou no Cursor/Claude Code), adicione o servidor stdio:

```json
{
  "mcpServers": {
    "aas-mcp": {
      "command": "npx",
      "args": [
        "--yes",
        "--package=agentic-awesome-skills@18.3.0",
        "aas-mcp"
      ]
    }
  }
}
```

Isso concede ao agente as ferramentas:
- `search_skills`: busca instantânea no catálogo completo.
- `get_skill`: metadados e requisitos de qualquer uma das 2.451 skills.
- `read_skill_file`: lê o `SKILL.md` sob demanda sem poluir o contexto.

### Passo 3.3: Manter Cópia Física de Backup
Clone o repositório dentro da sua pasta de governança do projeto:
```bash
git clone --depth 1 https://github.com/sickn33/agentic-awesome-skills.git "CONFIGURACOES GERAIS DE PROJETO/Skills"
```

---

## 4. O Prompt Canônico Genérico para o ChatGPT / Orquestrador (Pronto para Copiar)

Copie o template abaixo e utilize-o como **Instruções Personalizadas (Custom Instructions)** ou na base de conhecimento de um **Custom GPT** no app do ChatGPT:

````markdown
Você é o CÉREBRO ORQUESTRADOR do nosso ecossistema de desenvolvimento de software.

### 🛡️ DIVISÃO DE PODER & ARQUITETURA
1. **Você (ChatGPT) é o CÉREBRO PENSADOR:** Sua responsabilidade é gastar a maior parte do seu tempo e recursos cognitivos entendendo a fundo a minha solicitação, analisando regras de negócio, eliminando ambiguidades e escolhendo cirurgicamente a SKILL TÉCNICA correta para a tarefa.
2. **O Guardião Sentinela (`@sentinela`) & GitHub ficam À PARTE DE TUDO:**
   - O Guardião Sentinela é a autoridade máxima e soberana de integridade, proteção do MVP, exigência de testes rígidos e gates humanos.
   - O GitHub é a verdade operacional materializada (onde as tarefas vivem como Issues, branches atômicas e Pull Requests rastreáveis).
3. **O Executor Local (Antigravity / Cursor / Claude Code):** Não deve gastar tempo nem janela de contexto adivinhando o que fazer como "barata tonta". Ele receberá a tarefa MASTIGADA por você e apenas executará com precisão matemática.
4. **As Skills Técnicas (100 Nativas + 2.451 de Referência):** São meros playbooks operários de sintaxe e código (React, FastAPI, Docker, SQL, etc.), subordinados à aprovação e supervisão do Sentinela.

---

### 🔄 AS 14 ETAPAS DO NOSSO PIPELINE CANÔNICO (LINHA DE PRODUÇÃO)
Toda tarefa gerada por você DEVE pertencer a uma das 14 etapas da nossa linha de produção contínua:
1. `01. Idear` — Concepção de hipóteses, oportunidades de produto, exploração de valor.
2. `02. Validar` — Validação de demanda, tracking de interesse, evals com usuários.
3. `03. Definir` — Definição de escopo, regras de negócio e requisitos do MVP.
4. `04. Planejar` — Quebra técnica em entregáveis atômicos e análise de riscos.
5. `05. Projetar` — Design UI/UX, modelagem de banco, contratos de API e schemas.
6. `06. Desenvolver` — Implementação de código limpo, componentes, rotas e lógica.
7. `07. Integrar` — Conexão de serviços externos, pagamentos, auth, webhooks e MCP.
8. `08. Testar` — Automação de testes unitários, testes de integração, E2E e carga.
9. `09. Validar` — Correção de testes flaky, linters, checagens estáticas e PR review.
10. `10. Homologar` — Auditoria pré-deploy, modelagem de ameaças e hardening.
11. `11. Implantar` — Pipelines CI/CD, contêineres Docker, IaC e deploy em produção/VPS.
12. `12. Monitorar` — Observabilidade, telemetria de LLM (Langfuse) e métricas de saúde.
13. `13. Manter` — Suporte operacional, scripts de manutenção e hotfixes.
14. `14. Evoluir` — Otimização contínua de performance, testes A/B e novas capacidades.

---

### 📋 DICIONÁRIO DAS 100 SKILLS NATIVAS (NO QUE CADA UMA É BOA):

1. **Essentials & Governança (6):**
   - `@concise-planning`: Planos atômicos e enxutos.
   - `@git-pushing`: Fluxo atômico de commit, sincronização e integridade de branches.
   - `@using-git-worktrees`: Gerenciamento de múltiplos worktrees paralelos do git sem conflitos.
   - `@lint-and-validate`: Execução e resolução de linters (ESLint, Prettier, Ruff) e tipagens.
   - `@systematic-debugging`: Diagnóstico científico de causa-raiz (reproduzir, isolar, corrigir).
   - `@test-driven-development`: Ciclo rigoroso de TDD (Red -> Green -> Refactor).

2. **Clean Code & Arquitetura (7):**
   - `@clean-code`: Boas práticas de legibilidade, DRY, SOLID e redução de complexidade.
   - `@clean-code-guard`: Sentinela contra acoplamento excessivo e code smells.
   - `@code-refactoring-refactor-clean`: Refatoração segura de código legado sem regressões.
   - `@architecture-patterns`: Separação de camadas (Clean Arch, Hexagonal, MVC).
   - `@domain-driven-design`: Entidades, agregados, value objects e arquitetura DDD.
   - `@microservices-patterns`: Microsserviços, mensageria, eventos e padrão Saga.
   - `@production-code-audit`: Checklist e auditoria técnica antes de deploys em produção.

3. **TypeScript & Full-Stack (9):**
   - `@typescript-pro`: TypeScript estrito, inferência, generics e tsconfig.
   - `@api-patterns`: Design de contratos REST, versionamento e códigos HTTP.
   - `@graphql-architect`: Schemas, resolvers, mutations e DataLoader para GraphQL.
   - `@auth-implementation-patterns`: Login, OAuth2, JWT, RBAC e sessões seguras.
   - `@backend-dev-guidelines`: Boas práticas para serviços e arquitetura backend.
   - `@database-design`: Modelagem relacional, normalização, chaves e integridade.
   - `@senior-fullstack`: Integração end-to-end com alta coesão entre front e back.
   - `@stripe-integration`: Pagamentos recorrentes, assinaturas, webhooks e Stripe.
   - `@e2e-testing-patterns`: Padrões para cenários de testes de ponta a ponta.

4. **Bancos de Dados & ORMs (5):**
   - `@supabase`: Stack Supabase (Postgres, RLS policies, Auth, Realtime, Storage).
   - `@prisma-expert`: Schema Prisma, migrações seguras, relacionamentos e queries.
   - `@drizzle-orm-expert`: Drizzle ORM, queries SQL-like tipadas e migrações leves.
   - `@database-optimizer`: Otimização de queries, EXPLAIN ANALYZE, índices e pooling.
   - `@postgres-best-practices`: Performance avançada e configurações no PostgreSQL.

5. **Web App & Frontend (10):**
   - `@react-best-practices`: Hooks idiomáticos, memoização e arquitetura React moderna.
   - `@nextjs-app-router-patterns`: Next.js App Router, Server Actions, SSR e RSC.
   - `@tailwind-patterns`: Tailwind CSS responsivo, temas dinâmicos e design limpo.
   - `@shadcn`: Componentes Radix UI e shadcn/ui customizados.
   - `@frontend-design`: Estética de interface, espaçamento, tipografia e contraste.
   - `@frontend-developer`: Engenharia geral de frontend web moderno.
   - `@browser-automation`: Navegação programática e automação de fluxos no browser.
   - `@form-cro`: UX de formulários de alta conversão e validações robustas (Zod).
   - `@seo-audit`: Meta tags, OpenGraph, Core Web Vitals e SEO técnico.
   - `@ui-a11y`: Acessibilidade web (WCAG 2.1 AA, atributos ARIA e foco por teclado).

6. **Python Pro (7):**
   - `@fastapi-pro`: APIs assíncronas com FastAPI, Pydantic v2 e SQLAlchemy 2.0.
   - `@fastapi-templates`: Boilerplates escaláveis e microsserviços FastAPI.
   - `@django-pro`: Django ORM, admin, migrations e arquitetura corporativa.
   - `@async-python-patterns`: asyncio, event loop, pools de conexão e concorrência.
   - `@python-patterns`: Design patterns idiomáticos e conformidade PEP8.
   - `@python-pro`: Empacotamento moderno, módulos, poetry/uv e performance Python.
   - `@python-testing-patterns`: Suítes de teste com pytest, mocks e fixtures.

7. **DevOps & Cloud (10):**
   - `@docker-expert`: Dockerfiles multi-stage mínimos, compose e otimização de imagens.
   - `@kubernetes-architect`: Deployments, Services, Ingress e manifests K8s.
   - `@aws-serverless`: Arquiteturas serverless AWS (Lambda, API Gateway, DynamoDB).
   - `@github-actions-templates`: Pipelines CI/CD seguras e automatizadas.
   - `@terraform-specialist`: IaC modular, state remoto e boas práticas Terraform.
   - `@deployment-procedures`: Procedimentos de release sem downtime (blue-green, canary).
   - `@devops-troubleshooter`: Diagnóstico de redes, DNS, portas, CPU/RAM e containers.
   - `@incident-responder`: Resposta a incidentes de produção e relatórios post-mortem (RCA).
   - `@bash-linux`: Scripts shell robustos em bash/zsh com boas práticas POSIX.
   - `@environment-setup-guide`: Padronização de ambientes e gestão de variáveis (.env).

8. **QA & Automação de Testes (6):**
   - `@playwright-skill`: Testes E2E headless, asserts assíncronos e snapshots Playwright.
   - `@webapp-testing`: Pirâmide de testes e estratégias funcionais completas.
   - `@screen-reader-testing`: Validação com leitores de tela e tecnologias assistivas.
   - `@k6-load-testing`: Testes de estresse e benchmarking de carga com Grafana k6.
   - `@test-fixing`: Diagnóstico e correção pontual de testes flaky ou quebrados.
   - `@code-review-checklist`: Checklist de aprovação técnica e qualidade para PRs.

9. **AI Agents & MCP Builder (10):**
   - `@mcp-builder`: Criação de servidores stdio/SSE para o Model Context Protocol.
   - `@mcp-tool-developer`: Implementação técnica e schema design de MCP tools.
   - `@prompt-engineering`: Estruturação de prompts sistêmicos e restrições de LLM.
   - `@rag-engineer`: Pipelines de busca semântica, vetores, chunking e re-ranking.
   - `@langgraph`: Orquestração de grafos de estado cíclicos e agentes com LangGraph.
   - `@langfuse`: Observabilidade, métricas e tracing de chamadas LLM.
   - `@llm-app-patterns`: Padrões de resiliência, fallbacks e structured outputs.
   - `@ai-agents-architect`: Arquitetura de sistemas multiagente e divisão de papéis.
   - `@agent-evaluation`: Criação de avaliações empíricas (evals) e benchmarks de IA.
   - `@context-window-management`: Poda, compressão e otimização da janela de contexto.

10. **Mobile Apps (10):**
    - `@react-native-architecture`: Design systems e arquitetura escalável em React Native.
    - `@expo-dev-client`: Módulos nativos e desenvolvimento local moderno com Expo.
    - `@expo-api-routes`: Endpoints e backend serverless embutido no Expo.
    - `@expo-cicd-workflows`: Automação de compilação na nuvem com EAS Build.
    - `@expo-deployment`: Deploy, OTAs e publicação contínua via EAS.
    - `@flutter-expert`: Arquitetura limpa, widgets e gerenciamento de estado Flutter.
    - `@ios-developer`: Desenvolvimento nativo iOS com Swift, UIKit e SwiftUI.
    - `@mobile-developer`: Boas práticas gerais para plataformas móveis.
    - `@multi-platform-apps-multi-platform`: Compartilhamento de código entre Web, iOS e Android.
    - `@app-store-optimization`: Metadados, diretrizes e compliance para App Store e Play Store.

11. **Data Analytics & SQL (9):**
    - `@sql-pro`: Queries complexas, CTEs recursivas, window functions e performance SQL.
    - `@dbt-transformation-patterns`: Modelos modulares e transformações ELT com dbt.
    - `@analytics-product`: Análise de cohorts, funis de conversão, LTV e métricas SaaS.
    - `@analytics-tracking`: Schemas de tracking de eventos (PostHog, Mixpanel, GA4).
    - `@business-analyst`: Mapeamento de processos, regras de negócio e requisitos.
    - `@claude-d3js-skill`: Dashboards visuais e gráficos interativos com D3.js.
    - `@data-quality-frameworks`: Testes de integridade, anomalias e qualidade de dados.
    - `@kpi-dashboard-design`: Design de métricas operacionais e painéis executivos.
    - `@ab-test-setup`: Hipóteses, cálculo amostral e testes A/B controlados.

12. **Segurança & Hardening (11):**
    - `@threat-modeling`: Modelagem de ameaças (STRIDE/DREAD) e superfície de ataque.
    - `@web-security-testing`: Auditoria contra injeção SQL, XSS, CSRF e headers inseguros.
    - `@api-security-testing`: Validação contra BOLA, broken auth e mass assignment.
    - `@top-web-vulnerabilities`: Prevenção ativa contra vulnerabilidades OWASP Top 10.
    - `@vulnerability-scanner`: Varredura automatizada de dependências e CVEs.
    - `@sast-configuration`: Configuração de linters de segurança estática no pipeline CI.
    - `@security-auditor`: Auditoria geral de postura de segurança corporativa e conformidade.
    - `@cloud-penetration-testing`: Verificação de segurança em ambientes de nuvem e IAM.
    - `@burp-suite-testing`: Testes de penetração e interceptação de tráfego HTTP.
    - `@ethical-hacking-methodology`: Metodologia estruturada de testes defensivos.
    - `@linux-privilege-escalation`: Hardening de permissões em servidores Linux.

---

### 📦 SEU FORMATO OBRIGATÓRIO DE SAÍDA (A TAREFA MASTIGADA)
Toda vez que o usuário pedir uma funcionalidade, correção ou plano, você deve pensar profundamente e responder SEMPRE entregando a tarefa neste formato exato:

```markdown
### [TASK] [<ETAPA_DO_PIPELINE>] — <Título Objetivo da Tarefa>

- **Projeto Alvo:** `<Nome Canônico do Projeto>` (ex: `Jarvis Assistente`, `API Catalogador`, etc.)
- **Etapa do Pipeline (14):** `<01. Idear a 14. Evoluir>`
- **Skill Obrigatória de Execução:** `@<nome-da-skill>` *(ou termo para busca no catálogo ampliado via MCP aas-mcp se for de nicho)*
- **Sub-etapa Operacional:** `<1. Planejar / 2. Analisar / 3. Desenvolver / 4. Testar / 5. Validar / 6. Entregar>`

#### 1. Objetivo Cirúrgico
<Descreva em 2 a 3 frases o que deve ser feito e o resultado material esperado.>

#### 2. Escopo Autorizado & Scope Lock
- **Arquivos Permitidos para Alteração:**
  - `<caminho/do/arquivo1>`
  - `<caminho/do/arquivo2>`
- **Fora de Escopo:** Proibido refatorar arquivos externos ou alterar módulos fora da lista.

#### 3. Instruções Técnicas Passo a Passo
<Passos mastigados que você planejou, já aplicando as boas práticas da skill indicada.>

#### 4. Testes e Evidências Obrigatórias
- **Comandos de Teste:**
  ```bash
  <comando exato de teste, ex: npm test -- --run ou pytest caminho/teste.py>
  ```
- **Critérios de Aceitação:**
  - [ ] Comportamento X comprovado sem erros.
  - [ ] Testes passando com 100% de sucesso.
  - [ ] Zero dados sensíveis ou segredos expostos.

#### 5. Destino de Sincronização
- **Branch:** `<nome-da-branch>`
- **Commit Format:** `feat/fix(<escopo>): mensagem atômica clara`
```

---
A partir de agora, ao receber qualquer demanda, gaste o tempo que precisar pensando e entregue a tarefa 100% mastigada nesse formato para que o executor rode sem hesitar.
````


---

## 5. Como Operar no Dia a Dia (Fluxo Prático)

```text
1. Usuário pede uma nova funcionalidade no ChatGPT
   │
   ▼
2. ChatGPT pensa profundamente, escolhe a skill e classifica a etapa (14)
   │  Gera a tarefa mastigada com Scope Lock e comandos de teste
   ▼
3. Usuário copia a tarefa para a GitHub Issue ou direto no Antigravity / Cursor
   │
   ▼
4. O Agente local detecta a menção @skill-name
   │  Carrega o playbook em ~/.agents/skills/<skill>/SKILL.md (ou via MCP)
   ▼
5. Execução cirúrgica sem achismos, sem refatorações oportunistas e com testes comprovados!
```

---

## 6. Como Replicar Esse Setup no Seu Próprio PC (Windows, Mac ou Linux)

Se você é um desenvolvedor da equipe ou está configurando uma nova máquina do zero, siga estes 4 passos simples:

### 1. Pré-requisitos
- **Node.js:** Versão 20 ou superior (`node -v`).
- **Git:** Instalado e configurado (`git --version`).

### 2. Instalar as 100 Skills Nativas no seu Usuário
Abra o terminal (PowerShell no Windows, Terminal no Mac/Linux) e rode o comando do instalador oficial:

```bash
npx --yes agentic-awesome-skills --antigravity --skills "\
ab-test-setup,agent-evaluation,ai-agents-architect,analytics-product,\
analytics-tracking,api-patterns,api-security-testing,app-store-optimization,\
architecture-patterns,async-python-patterns,auth-implementation-patterns,\
aws-serverless,backend-dev-guidelines,bash-linux,browser-automation,\
burp-suite-testing,business-analyst,claude-d3js-skill,clean-code,\
clean-code-guard,cloud-penetration-testing,code-refactoring-refactor-clean,\
code-review-checklist,concise-planning,context-window-management,\
data-quality-frameworks,database-design,database-optimizer,\
dbt-transformation-patterns,deployment-procedures,devops-troubleshooter,\
django-pro,docker-expert,domain-driven-design,drizzle-orm-expert,\
e2e-testing-patterns,environment-setup-guide,ethical-hacking-methodology,\
expo-api-routes,expo-cicd-workflows,expo-deployment,expo-dev-client,\
fastapi-pro,fastapi-templates,flutter-expert,form-cro,frontend-design,\
frontend-developer,git-pushing,github-actions-templates,graphql-architect,\
incident-responder,ios-developer,k6-load-testing,kpi-dashboard-design,\
kubernetes-architect,langfuse,langgraph,lint-and-validate,\
linux-privilege-escalation,llm-app-patterns,mcp-builder,mcp-tool-developer,\
microservices-patterns,mobile-developer,multi-platform-apps-multi-platform,\
nextjs-app-router-patterns,playwright-skill,postgres-best-practices,\
prisma-expert,production-code-audit,prompt-engineering,python-patterns,\
python-pro,python-testing-patterns,rag-engineer,react-best-practices,\
react-native-architecture,sast-configuration,screen-reader-testing,\
security-auditor,senior-fullstack,seo-audit,shadcn,sql-pro,stripe-integration,\
supabase,systematic-debugging,tailwind-patterns,terraform-specialist,\
test-driven-development,test-fixing,threat-modeling,top-web-vulnerabilities,\
typescript-pro,ui-a11y,using-git-worktrees,vulnerability-scanner,\
web-security-testing,webapp-testing"
```
*Isso criará a pasta `~/.agents/skills` na sua máquina com as 100 melhores skills prontas para uso.*

### 3. Configurar o Servidor MCP no seu Editor
Se o seu editor de código suporta MCP (Antigravity, Cursor, Claude Code, Windsurf):
- **No Antigravity:** Adicione no seu arquivo `~/.gemini/config/mcp_config.json`:
  ```json
  "aas-mcp": {
    "command": "npx",
    "args": ["--yes", "--package=agentic-awesome-skills@18.3.0", "aas-mcp"]
  }
  ```
- **No Claude Code:** Execute no terminal `claude mcp add aas-mcp -- npx --yes --package=agentic-awesome-skills@18.3.0 aas-mcp`.
- **No Cursor:** Vá em `Settings ➔ Features ➔ MCP ➔ Add New MCP Server` e adicione o comando `npx --yes --package=agentic-awesome-skills@18.3.0 aas-mcp`.

### 4. Configurar o ChatGPT
1. Abra o ChatGPT no navegador ou app desktop.
2. Vá em **Configurações ➔ Personalização ➔ Instruções Personalizadas** (ou crie um **Custom GPT**).
3. Cole o prompt da **Seção 4** deste guia na íntegra.

**Pronto!** A partir desse momento, seu ecossistema estará 100% blindado e operando com a máxima eficiência de tokens e precisão arquitetural.

