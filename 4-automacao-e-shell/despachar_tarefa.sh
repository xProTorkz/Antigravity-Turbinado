#!/usr/bin/env bash
# ==============================================================================
# despachar_tarefa.sh — Despachador Autônomo de Tarefas para GitHub Issues
# Criado para o ecossistema Sentinela Guardião / Gemini Orquestrador
# ==============================================================================
set -e

# Injetar token das variáveis de ambiente
export GITHUB_TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
export GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"

if ! command -v gh &> /dev/null; then
    echo "❌ Erro: GitHub CLI (gh) não está instalado ou no PATH."
    exit 1
fi

PROJETO=""
TITULO=""
ETAPA="06. Desenvolver"
SKILL="@sentinela"
SCOPE_LOCK=""
CORPO=""
REPOSITORIO=""

# Parse de argumentos
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -p|--projeto) PROJETO="$2"; shift ;;
        -t|--titulo) TITULO="$2"; shift ;;
        -e|--etapa) ETAPA="$2"; shift ;;
        -s|--skill) SKILL="$2"; shift ;;
        --scope) SCOPE_LOCK="$2"; shift ;;
        -b|--corpo) CORPO="$2"; shift ;;
        -r|--repo) REPOSITORIO="$2"; shift ;;
        -h|--help)
            echo "Uso: $0 --projeto <Nome> --titulo <Descricao> [--etapa <14 Etapas>] [--skill <@skill>] [--scope <arquivos>] [--corpo <detalhes>]"
            exit 0
            ;;
        *) echo "Parâmetro desconhecido: $1"; exit 1 ;;
    esac
    shift
done

if [ -z "$PROJETO" ] || [ -z "$TITULO" ]; then
    echo "❌ Erro: --projeto e --titulo são obrigatórios."
    exit 1
fi

# Mapeamento dinâmico de projetos para repositórios GitHub
declare -A REPO_MAP=(
    ["Zentinel"]="xProTorkz/Zentinel"
    ["Dados Bacbo"]="xProTorkz/Dados-Bacbo"
    ["Atende Ai"]="xProTorkz/Atende-Ai"
    ["Jarvis Assistente"]="xProTorkz/Jarvis-Assistente"
    ["Buy Station"]="xProTorkz/Buy-Station"
    ["Minha Agenda"]="xProTorkz/Minha-Agenda"
    ["Arena Beach"]="xProTorkz/gestao-arena"
    ["Nu Bank"]="xProTorkz/Nu-Bank"
    ["Premium Car"]="xProTorkz/PremiumCar"
    ["Skills Catalog"]="xProTorkz/Skills-Catalog"
    ["Chama Oferta"]="xProTorkz/Chama-Oferta"
    ["Whaticket Meta"]="xProTorkz/Whaticket-Meta"
    ["Deriv Bot"]="xProTorkz/Deriv-Bot"
    ["Config Bot"]="xProTorkz/Config-Bot"
    ["Antigravity Turbinado"]="xProTorkz/Antigravity-Turbinado"
)

TARGET_REPO="${REPOSITORIO:-${REPO_MAP[$PROJETO]}}"

if [ -z "$TARGET_REPO" ]; then
    # Tenta descobrir o remote git local se a pasta existir
    for CAT in "SISTEMAS" "APLICAÇÕES" "SITES" "BOTS"; do
        LOCAL_PATH="/Users/lucasvinicius/projetos/$CAT/$PROJETO"
        if [ -d "$LOCAL_PATH/.git" ]; then
            TARGET_REPO=$(git -C "$LOCAL_PATH" remote get-url origin 2>/dev/null | sed -E 's/.*github.com[:\/]([^\/]+\/[^\/\.]+).*/\1/' || true)
            break
        fi
    done
fi

if [ -z "$TARGET_REPO" ]; then
    echo "❌ Erro: Não foi possível determinar o repositório GitHub para o projeto '$PROJETO'."
    exit 1
fi

# Formatar Título Canônico Universal: [Projeto - Sistema] Descrição
ISSUE_TITLE="[$PROJETO] $TITULO"

# Construir Corpo Padronizado agent_task v5
DATA_HORA_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FINAL_BODY=$(cat <<EOF
\`\`\`yaml
agent_task:
  version: 5.0
  target_project: "$PROJETO"
  target_repo: "$TARGET_REPO"
  pipeline_stage: "$ETAPA"
  required_skill: "$SKILL"
  priority: "P1_HIGH"
  type: "FEATURE_OU_FIX"
  execution: "AUTONOMOUS_LOCAL"
  created_at_utc: "$DATA_HORA_UTC"
  assigned_agent: "antigravity-local"
  write_permission: true
\`\`\`

## 🎯 Contexto e Justificativa Arquitetural
${CORPO:-"Execução técnica planejada pelo Cérebro Orquestrador (Gemini) sob a governança do Sentinela Guardião."}

## 🔒 Scope Lock Cirúrgico (Arquivos Autorizados)
${SCOPE_LOCK:-"- Modificar estritamente os arquivos necessários para esta tarefa sem refatoração oportunista."}

## 📋 Critérios de Aceitação (DoD)
- [ ] Alterações implementadas fielmente conforme a especificação.
- [ ] Sem quebra de funcionalidades pré-existentes (regressão zero).
- [ ] Test Before / Test After executado e validado.
- [ ] Ausência de credenciais ou chaves hardcoded no código.

## 🧪 Protocolo de Testes Mandatório
1. **Baseline (Antes):** Validar se o ambiente e os testes atuais estão verdes.
2. **Execução:** Aplicar minimal necessary diff.
3. **Validação (Depois):** Rodar testes automatizados ou verificação local do componente.
EOF
)

echo "🚀 Despachando Issue para o GitHub..."
echo "  Repositório: $TARGET_REPO"
echo "  Título: $ISSUE_TITLE"

ISSUE_URL=$(gh issue create --repo "$TARGET_REPO" --title "$ISSUE_TITLE" --body "$FINAL_BODY")

echo "✅ SUCESSO! Issue criada no GitHub:"
echo "👉 $ISSUE_URL"
