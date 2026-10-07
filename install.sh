#!/usr/bin/env bash
# ==============================================================================
# 🚀 Antigravity Ecosystem & SRE Automation Toolkit - Quick Installer
# Compatibilidade: macOS (Darwin) / Linux | Shell: zsh / bash
# ==============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BOLD}${BLUE}====================================================================${NC}"
echo -e "${BOLD}${GREEN}🚀 INSTALADOR DO ECOSSISTEMA ANTIGRAVITY & SRE AUTOMATION TOOLKIT${NC}"
echo -e "${BOLD}${BLUE}====================================================================${NC}"
echo -e "📂 Diretório Base: ${BOLD}${INSTALL_DIR}${NC}\n"

# 1. Checagem de Pré-requisitos
echo -e "${BLUE}🔍 1. Verificando pré-requisitos do sistema...${NC}"

if command -v zsh >/dev/null 2>&1; then
    echo -e "  ✅ Zsh detectado: $(zsh --version)"
else
    echo -e "  ⚠️ Zsh não detectado. Usando bash."
fi

if command -v git >/dev/null 2>&1; then
    echo -e "  ✅ Git detectado: $(git --version)"
else
    echo -e "  ❌ Git não encontrado. Instale o Git antes de prosseguir."
    exit 1
fi

if command -v python3 >/dev/null 2>&1; then
    echo -e "  ✅ Python 3 detectado: $(python3 --version)"
else
    echo -e "  ⚠️ Python 3 não detectado. Recursos de validação de schema podem ser limitados."
fi

# 2. Configuração de Permissões de Segurança (750)
echo -e "\n${BLUE}🛡️ 2. Aplicando permissões de segurança estritas (chmod 750)...${NC}"
chmod -R 750 "$INSTALL_DIR" 2>/dev/null || true
chmod +x "$INSTALL_DIR/4-automacao-e-shell/agy_cmd.sh" 2>/dev/null || true
if [ -f "$INSTALL_DIR/3-instalacao-skills/instalar_skills.sh" ]; then
    chmod +x "$INSTALL_DIR/3-instalacao-skills/instalar_skills.sh" 2>/dev/null || true
fi
echo -e "  ✅ Permissões 750 aplicadas. Apenas o proprietário possui acesso total."

# 3. Configuração do Roteador agy_cmd e Aliases Turbo no Shell (~/.zshrc / ~/.bashrc)
echo -e "\n${BLUE}⚡ 3. Configurando roteador de comandos e aliases turbo no shell...${NC}"
ROUTER_PATH="$INSTALL_DIR/4-automacao-e-shell/agy_cmd.sh"

setup_shell_rc() {
    local rc_file="$1"
    if [ -f "$rc_file" ]; then
        # 3.1 Garantir PATH para agy e scripts locais
        if ! grep -q '\.local/bin' "$rc_file"; then
            echo -e '\n# === Antigravity PATH ===\nexport PATH="$HOME/.local/bin:$PATH"' >> "$rc_file"
            echo -e "  ✅ PATH ~/.local/bin adicionado a ${rc_file}."
        fi

        # 3.2 Aliases Turbo do Antigravity (Modo Turbo idêntico)
        if ! grep -q 'alias google-cli=' "$rc_file"; then
            echo -e '\n# === Antigravity Turbo Aliases ===' >> "$rc_file"
            echo -e 'alias google-cli="agy --dangerously-skip-permissions --model gemini-3.8-flash-high --effort high"' >> "$rc_file"
            echo -e 'alias google="agy --dangerously-skip-permissions --model gemini-3.8-flash-high --effort high"' >> "$rc_file"
            echo -e 'alias agy="agy --dangerously-skip-permissions --model gemini-3.8-flash-high --effort high"' >> "$rc_file"
            echo -e "  ✅ Aliases turbo (google-cli, google, agy) adicionados a ${rc_file}."
        fi

        # 3.3 Registro do Roteador de Comandos SRE
        if grep -q "agy_cmd.sh" "$rc_file"; then
            echo -e "  ℹ️ Roteador já registrado em ${rc_file}."
        else
            echo -e "\n# === Antigravity SRE Command Router ===" >> "$rc_file"
            echo -e "[ -f \"$ROUTER_PATH\" ] && source \"$ROUTER_PATH\"" >> "$rc_file"
            echo -e "  ✅ Roteador adicionado com sucesso a ${rc_file}."
        fi
    fi
}

setup_shell_rc "$HOME/.zshrc"
setup_shell_rc "$HOME/.bashrc"

# 3.4 Sincronização do Dicionário Léxico Canônico
mkdir -p "$HOME/.gemini/config"
if [ -f "$INSTALL_DIR/4-automacao-e-shell/dicionario_lexico.json" ]; then
    cp -f "$INSTALL_DIR/4-automacao-e-shell/dicionario_lexico.json" "$HOME/.gemini/config/dicionario_lexico.json"
    echo -e "  ✅ Dicionário léxico v3.8 instalado em ~/.gemini/config/dicionario_lexico.json."
fi

# 4. Validação de Integridade e Schema
echo -e "\n${BLUE}🧪 4. Validando integridade dos arquivos e schemas JSON...${NC}"
if command -v python3 >/dev/null 2>&1; then
    SCHEMA_FILE="$INSTALL_DIR/4-automacao-e-shell/system_core_architecture_schema.json"
    if [ -f "$SCHEMA_FILE" ]; then
        python3 -c "import json; json.load(open('$SCHEMA_FILE')); print('  ✅ Schema de arquitetura validado sintaticamente.')"
    fi
fi

# 5. Conclusão e Instruções de Uso
echo -e "\n${BOLD}${GREEN}====================================================================${NC}"
echo -e "${BOLD}${GREEN}🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
echo -e "${BOLD}${GREEN}====================================================================${NC}"
echo -e "\n${BOLD}Para começar a usar imediatamente:${NC}"
echo -e "1️⃣ Recarregue o seu terminal executando:"
echo -e "   ${YELLOW}source ~/.zshrc${NC}  (ou ${YELLOW}source ~/.bashrc${NC})"
echo -e "\n2️⃣ Teste o roteador de comandos digitando:"
echo -e "   ${YELLOW}agy_cmd help${NC}"
echo -e "\n3️⃣ Para instalar as 100 skills essenciais de engenharia, execute:"
echo -e "   ${YELLOW}cd $INSTALL_DIR/3-instalacao-skills && ./instalar_skills.sh${NC}"
echo -e "\n4️⃣ Para configurar o ChatGPT como orquestrador, copie o conteúdo de:"
echo -e "   ${YELLOW}$INSTALL_DIR/2-prompts-chatgpt/CHATGPT_BRAIN_ORCHESTRATOR.md${NC}"
echo -e "   para as Instruções Personalizadas (Custom Instructions) do seu ChatGPT.\n"
