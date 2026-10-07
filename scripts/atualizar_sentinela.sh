#!/usr/bin/env bash
# ==============================================================================
# 🚀 Atualizador Canônico do Sentinela & Dicionário Léxico (Antigravity Turbinado)
# Disparado automaticamente ao dizer no Antigravity:
#   "baixa a nova atualizacao sentinela"
# ==============================================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$HOME/.gemini/config"
SKILLS_DIR="$CONFIG_DIR/skills"

echo -e "${BOLD}${BLUE}====================================================================${NC}"
echo -e "${BOLD}${GREEN}🔄 ATUALIZADOR DO SENTINELA & DICIONÁRIO LÉXICO (ANTIGRAVITY)${NC}"
echo -e "${BOLD}${BLUE}====================================================================${NC}"
echo -e "📂 Repositório: ${BOLD}${REPO_DIR}${NC}\n"

# 1. Puxar as novidades do Git
echo -e "${BLUE}📥 1. Puxando as últimas atualizações do GitHub (git pull origin main)...${NC}"
if [ -d "$REPO_DIR/.git" ]; then
    git -C "$REPO_DIR" pull origin main || echo -e "  ⚠️ git pull finalizado com avisos ou já sincronizado."
else
    echo -e "  ⚠️ Diretório .git não encontrado em $REPO_DIR."
fi

# 2. Criar diretórios de destino se não existirem
mkdir -p "$CONFIG_DIR"
mkdir -p "$SKILLS_DIR/guardiao-sentinela"
mkdir -p "$SKILLS_DIR/menu-comandos-rapidos"
mkdir -p "$SKILLS_DIR/sentinela"

# 3. Sincronizar o Dicionário Léxico (~/.gemini/config/dicionario_lexico.json)
echo -e "\n${BLUE}📚 2. Sincronizando Dicionário Léxico Canônico...${NC}"
if [ -f "$REPO_DIR/4-automacao-e-shell/dicionario_lexico.json" ]; then
    cp -f "$REPO_DIR/4-automacao-e-shell/dicionario_lexico.json" "$CONFIG_DIR/dicionario_lexico.json"
    echo -e "  ✅ Dicionário atualizado em: ${BOLD}$CONFIG_DIR/dicionario_lexico.json${NC}"
elif [ -f "$REPO_DIR/templates/dicionario_lexico.template.json" ]; then
    cp -f "$REPO_DIR/templates/dicionario_lexico.template.json" "$CONFIG_DIR/dicionario_lexico.json"
    echo -e "  ✅ Dicionário copiado do template em: ${BOLD}$CONFIG_DIR/dicionario_lexico.json${NC}"
fi

# 4. Sincronizar Skills do Sentinela
echo -e "\n${BLUE}🛡️ 3. Sincronizando Skills da Sentinela & Menu de Comandos Rápidos...${NC}"
if [ -f "$REPO_DIR/1-governanca-e-regras/GUARDIAO_DE_PROJETOS_SENTINELA.md" ]; then
    cp -f "$REPO_DIR/1-governanca-e-regras/GUARDIAO_DE_PROJETOS_SENTINELA.md" "$SKILLS_DIR/sentinela/SKILL.md"
    cp -f "$REPO_DIR/1-governanca-e-regras/GUARDIAO_DE_PROJETOS_SENTINELA.md" "$SKILLS_DIR/guardiao-sentinela/SKILL.md"
    echo -e "  ✅ Skill @sentinela e @guardiao-sentinela sincronizadas."
fi
if [ -f "$REPO_DIR/skills/native/menu-comandos-rapidos/SKILL.md" ]; then
    cp -f "$REPO_DIR/skills/native/menu-comandos-rapidos/SKILL.md" "$SKILLS_DIR/menu-comandos-rapidos/SKILL.md"
    echo -e "  ✅ Skill @menu-comandos-rapidos sincronizada."
fi

# 5. Validação da versão instalada
if command -v python3 >/dev/null 2>&1 && [ -f "$CONFIG_DIR/dicionario_lexico.json" ]; then
    VERSION=$(python3 -c "import json; print(json.load(open('$CONFIG_DIR/dicionario_lexico.json')).get('versao', 'Desconhecida'))" 2>/dev/null || echo "3.9")
    echo -e "\n${BOLD}${GREEN}✨ Sentinela e Dicionário atualizados com sucesso para a versão v${VERSION}!${NC}"
    echo -e "🎯 Recursos Ativos:"
    echo -e "  • Espelhamento estático recursivo via wget com destino em /projetos/<PASTA>"
    echo -e "  • Suíte DevTools de Inspeção Irrestrita de Interface & Depuração DOM (Menu 10)"
    echo -e "  • Desmascaramento de senhas, remoção de travas CSS/blur, overlays e extração de cache"
    echo -e "  • Gatilho rápido de atualização: 'baixa a nova atualizacao sentinela'"
fi

echo -e "\n${BOLD}${BLUE}====================================================================${NC}\n"
