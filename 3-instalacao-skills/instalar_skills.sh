#!/usr/bin/env bash
# ==============================================================================
# SCRIPT DE INSTALAÇÃO AUTOMATIZADA: SKILLS DO ECOSSISTEMA CANÔNICO
# ==============================================================================
# Executa a instalação das 100 skills essenciais em ~/.agents/skills/
# Mantém o limite de tokens seguro e prepara a máquina para qualquer agente IA.
# ==============================================================================

set -e

echo "🚀 Iniciando configuração do ecossistema de Skills..."

# 1. Verificar pré-requisitos
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Erro: Node.js não foi encontrado. Por favor, instale o Node.js v18+ antes de prosseguir."
    exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
    echo "❌ Erro: npx não foi encontrado."
    exit 1
fi

echo "✅ Node.js e npx verificados."

# 2. Criar diretório padrão de skills se não existir
SKILLS_DIR="$HOME/.agents/skills"
mkdir -p "$SKILLS_DIR"
echo "📂 Diretório de destino: $SKILLS_DIR"

# 3. Lista curada das 100 skills essenciais (Zero Overhead / Máxima Eficiência)
SKILLS_LIST="ab-test-setup,agent-evaluation,ai-agents-architect,analytics-product,\
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
fastapi-pro,figma-implement,flutter-expert,form-cro,frontend-design,\
full-stack-governance,github-actions-templates,golang-patterns,\
graphql-architect,incident-responder,interview-prep,k6-load-testing,\
kpi-dashboard-design,kubernetes-architect,langfuse,lint-and-validate,\
mcp-builder,microservices-patterns,mobile-app-analytics,mobile-design-system,\
mobile-security-testing,multi-agent-orchestrator,network-security-auditor,\
nextjs-app-router-patterns,nextjs-seo,node-service-patterns,\
owasp-security-checks,penetration-testing-playbook,performance-profiling,\
playwright-skill,poker-probability,post-incident-review,postgresql-ha,\
prisma-expert,production-code-audit,python-testing-patterns,rag-engineer,\
react-best-practices,react-native-architecture,redis-caching-patterns,\
sast-configuration,screen-reader-testing,security-auditor,senior-fullstack,\
seo-audit,shadcn,sql-pro,stripe-integration,supabase,systematic-debugging,\
tailwind-patterns,terraform-specialist,test-driven-development,test-fixing,\
threat-modeling,top-web-vulnerabilities,typescript-pro,ui-a11y,\
using-git-worktrees,vulnerability-scanner,web-security-testing,webapp-testing"

echo "📦 Instalando as 100 skills curadas via npx agentic-awesome-skills..."
npx --yes agentic-awesome-skills --antigravity --skills "$SKILLS_LIST"

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo "✨ Total de skills nativas instaladas em $SKILLS_DIR: $(ls -1 "$SKILLS_DIR" | wc -l | tr -d ' ')"
echo ""
echo "💡 Dica: Para consultar o catálogo completo com 2.480+ skills sob demanda:"
echo "   Execute: npx agentic-awesome-skills mcp"
