# PIPELINE CANÔNICO & MATRIZ DE SKILLS DO ECOSSISTEMA
<!--
  MATRIZ DEFINITIVA: 14 ETAPAS DO PIPELINE x 100 SKILLS NATIVAS x 2.451 CATALOGADAS
  Utilizado por: GitHub Issues, GitHub Copilot, ChatGPT (Orquestrador) e Antigravity (Executor)
-->

## 1. Visão Geral da Linha de Produção
Nosso ciclo de vida de produto e engenharia opera sob um pipeline unificado e contínuo de 14 etapas:

```text
Idear ➔ Validar ➔ Definir ➔ Planejar ➔ Projetar ➔ Desenvolver ➔ Integrar ➔ Testar ➔ Validar ➔ Homologar ➔ Implantar ➔ Monitorar ➔ Manter ➔ Evoluir
```

---

## 2. Matriz de Atribuição de Skills por Etapa

| # | Etapa do Pipeline | Foco Operacional | Skills Nativas Recomendadas (`@skill`) |
| :---: | :--- | :--- | :--- |
| **01** | **Idear** | Brainstorming de produto, hipóteses de valor, concepção de features | `@ab-test-setup`, `@analytics-product`, `@business-analyst` |
| **02** | **Validar** | Validação de demanda, tracking de interesse, evals com usuários | `@analytics-tracking`, `@form-cro`, `@agent-evaluation` |
| **03** | **Definir** | Definição de escopo, regras de negócio e requisitos funcionais | `@business-analyst`, `@concise-planning` |
| **04** | **Planejar** | Arquitetura técnica, decomposição em tasks atômicas e mitigação | `@concise-planning`, `@architecture-patterns`, `@systematic-debugging` |
| **05** | **Projetar** | Design UI/UX, modelagem de banco, contratos de API e schemas | `@frontend-design`, `@ui-a11y`, `@shadcn`, `@tailwind-patterns`, `@database-design`, `@graphql-architect`, `@domain-driven-design` |
| **06** | **Desenvolver** | Implementação de código limpo, componentes, lógica de negócio e rotas | `@clean-code`, `@clean-code-guard`, `@typescript-pro`, `@react-best-practices`, `@nextjs-app-router-patterns`, `@fastapi-pro`, `@django-pro`, `@senior-fullstack`, `@supabase`, `@prisma-expert`, `@drizzle-orm-expert`, `@react-native-architecture` |
| **07** | **Integrar** | Conexão de serviços externos, gateways de pagamento, auth e MCP | `@api-patterns`, `@stripe-integration`, `@auth-implementation-patterns`, `@microservices-patterns`, `@mcp-builder`, `@using-git-worktrees` |
| **08** | **Testar** | Automação de testes unitários, testes de integração e ponta a ponta | `@test-driven-development`, `@playwright-skill`, `@webapp-testing`, `@python-testing-patterns`, `@k6-load-testing`, `@screen-reader-testing`, `@e2e-testing-patterns` |
| **09** | **Validar** | Resolução de testes quebrados, linters, checagens estáticas e PR review | `@test-fixing`, `@lint-and-validate`, `@code-review-checklist`, `@code-refactoring-refactor-clean` |
| **10** | **Homologar** | Auditoria pré-produção, modelagem de ameaças e hardening | `@production-code-audit`, `@threat-modeling`, `@web-security-testing`, `@sast-configuration`, `@vulnerability-scanner`, `@database-optimizer` |
| **11** | **Implantar** | Provisionamento IaC, pipelines CI/CD, contêineres e deploy seguro | `@deployment-procedures`, `@docker-expert`, `@kubernetes-architect`, `@terraform-specialist`, `@github-actions-templates`, `@aws-serverless`, `@environment-setup-guide` |
| **12** | **Monitorar** | Métricas de telemetria, observabilidade de LLM e painéis de saúde | `@langfuse`, `@incident-responder`, `@devops-troubleshooter`, `@kpi-dashboard-design` |
| **13** | **Manter** | Resolução de bugs em produção, scripts de manutenção e patches | `@incident-responder`, `@bash-linux`, `@database-optimizer`, `@git-pushing` |
| **14** | **Evoluir** | Otimização de performance, testes A/B e expansão contínua | `@ab-test-setup`, `@analytics-product`, `@context-window-management`, `@rag-engineer` |

---

## 3. Catálogo Completo no Repositório (2.350+ Skills)
Quando uma tarefa exigir conhecimentos além das skills primárias recomendadas acima (ex: bibliotecas específicas, banco de dados especializado, segurança ofensiva, scraping, mobile avançado, etc.):
1. **Consulte o Catálogo Completo:** Acesse `skills/` ou o índice detalhado em `[.github/CATALOGO_SKILLS_COMPLETO.md](file:///Users/lucasvinicius/projetos/project-blueprint/.github/CATALOGO_SKILLS_COMPLETO.md)`.
2. **Defina a Skill Exata:** Preencha o campo `required_skill` da Issue ou comando com a `@skill` específica.
3. **Execução Cirúrgica:** O Antigravity consulta diretamente o playbook em `skills/<skill-name>/SKILL.md` ou invoca via MCP `aas-mcp`, executando sem desvios.
