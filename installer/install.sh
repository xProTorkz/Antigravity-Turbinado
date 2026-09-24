#!/usr/bin/env bash
#
# Antigravity Turbinado — Instalador Neutro e Onboarding Oficial (macOS)
# Arquitetura: ChatGPT (Planejador) → GitHub (Fonte da Verdade) → Antigravity (Executor)
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🚀 INSTALADOR OFICIAL DO ANTIGRAVITY TURBINADO (macOS)${NC}"
echo -e "${BLUE}============================================================${NC}"

# Parse argumentos
LICENSE_KEY=""
NON_INTERACTIVE=false
PROJECTS_DIR_ARG=""

for arg in "$@"; do
    case $arg in
        --license=*)
        LICENSE_KEY="${arg#*=}"
        shift
        ;;
        --projects-dir=*)
        PROJECTS_DIR_ARG="${arg#*=}"
        shift
        ;;
        --non-interactive|--ci)
        NON_INTERACTIVE=true
        shift
        ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." 2>/dev/null && pwd || echo "")"
GUARD_SCRIPT="$SCRIPT_DIR/scripts/license_guard.py"

# ETAPA 1: Autenticação de Licença e Vinculação de Hardware (se licença fornecida ou exigida)
if [ -n "$LICENSE_KEY" ] && [ -f "$GUARD_SCRIPT" ]; then
    echo -e "\n${YELLOW}[ETAPA 1/7] Verificando Licença e Vinculação de Hardware (HWID)...${NC}"
    VERIFY_RES=$(python3 "$GUARD_SCRIPT" --verify="$LICENSE_KEY" 2>&1)
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ] || echo "$VERIFY_RES" | grep -q '"ok": false'; then
        echo -e "\n${RED}============================================================${NC}"
        echo -e "${RED}❌ ACESSO NEGADO: LICENÇA INVÁLIDA OU COMPARTILHADA${NC}"
        echo -e "${RED}============================================================${NC}"
        echo -e "$VERIFY_RES"
        echo -e "\n${YELLOW}Esta licença só pode ser executada na máquina física autorizada.${NC}"
        echo -e "Para suporte técnico: consulte <support-url>\n"
        exit 1
    fi
    echo -e "${GREEN}✅ Licença autenticada com sucesso e vinculada a este hardware!${NC}"
else
    echo -e "\n${YELLOW}[ETAPA 1/7] Modo de Instalação Padrão / Licença Local${NC}"
fi

# ETAPA 2: Verificação do Sistema Operacional
echo -e "\n${YELLOW}[ETAPA 2/7] Verificando Sistema Operacional...${NC}"
if [ "$(uname -s)" != "Darwin" ]; then
    echo -e "${RED}❌ ERRO: Este instalador é exclusivo para macOS. Para Windows use install.ps1.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ macOS detectado ($(sw_vers -productVersion)).${NC}"

# ETAPA 3: Pré-requisitos (Git, Python 3.10+, Antigravity)
echo -e "\n${YELLOW}[ETAPA 3/7] Verificando Ferramentas Pré-Requisito...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ ERRO: Git não encontrado. Instale com: xcode-select --install${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git disponível: $(git --version)${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ ERRO: Python 3 não encontrado. Instale Python 3.10 ou superior.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python disponível: $(python3 --version)${NC}"

# ETAPA 4: Permissões Transparentes TCC e Acesso a Disco (FAIL-CLOSED)
echo -e "\n${YELLOW}[ETAPA 4/7] Auditoria de Permissões macOS (TCC & Acesso a Disco no Workspace)...${NC}"
if [ -n "$PROJECTS_DIR_ARG" ]; then
    TEST_DIR="$PROJECTS_DIR_ARG"
elif [ -d "$HOME/projects" ]; then
    TEST_DIR="$HOME/projects"
else
    TEST_DIR="$HOME/projetos"
fi
mkdir -p "$TEST_DIR"
TEST_FILE="$TEST_DIR/.tcc_probe_$$"
if touch "$TEST_FILE" 2>/dev/null; then
    rm -f "$TEST_FILE"
    echo -e "${GREEN}✅ Permissão de disco confirmada em $TEST_DIR.${NC}"
else
    echo -e "\n${RED}============================================================${NC}"
    echo -e "${RED}❌ INSTALAÇÃO CANCELADA: PERMISSÃO DE DISCO NEGADA PELO MACOS${NC}"
    echo -e "${RED}============================================================${NC}"
    echo -e "O macOS bloqueou o acesso às suas pastas de desenvolvimento."
    echo -e "\n${YELLOW}COMO HABILITAR COM CONSENTIMENTO TRANSPARENTE:${NC}"
    echo -e "1. Abra os ${BLUE}Ajustes do Sistema${NC} → ${BLUE}Privacidade e Segurança${NC}."
    echo -e "2. Selecione ${BLUE}Acesso Total ao Disco${NC}."
    echo -e "3. Adicione o seu ${BLUE}Terminal${NC} e o ${BLUE}Antigravity${NC} e marque como ATIVADO."
    echo -e "4. Reinicie a instalação executando o comando novamente.\n"
    exit 1
fi

# ETAPA 5: Instalação e Indexação das Skills e Configurações de Autonomia
echo -e "\n${YELLOW}[ETAPA 5/7] Configurando Ambiente de Autonomia e Catálogo de Skills...${NC}"
TURBO_SCRIPT="$SCRIPT_DIR/scripts/configure_turbo_environment.py"
if [ -f "$TURBO_SCRIPT" ]; then
    python3 "$TURBO_SCRIPT"
fi

# ETAPA 6: Política de Permissões do Workspace e Autonomia
echo -e "\n${YELLOW}[ETAPA 6/7] Aplicando Diretrizes de Workspace e Autonomia...${NC}"
echo -e "• Antigravity configurado em modo: ${GREEN}EAGER (Auto-execução de comandos seguros no workspace)${NC}"
echo -e "• Dentro da pasta de projeto: ${GREEN}Sempre permitir alterações no workspace${NC}"
echo -e "• Fora da pasta de projeto: ${YELLOW}Perguntar sempre / Request Review obrigatório${NC}"

# ETAPA 7: Doctor de Integridade
echo -e "\n${YELLOW}[ETAPA 7/7] Executando Doctor de Diagnóstico do Ambiente...${NC}"
python3 "$SCRIPT_DIR/scripts/doctor.py"

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 ANTIGRAVITY TURBINADO INSTALADO COM SUCESSO!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo -e "Sua máquina agora está configurada e pronta para receber tarefas autônomas."
echo -e "\n📌 ${YELLOW}COMO COMEÇAR SEU PRIMEIRO PROJETO:${NC}"
echo -e "1. Abra o ChatGPT e configure as ${BLUE}Instruções Personalizadas${NC} com o template do kit."
echo -e "2. Peça sua tarefa no ChatGPT: ele criará a Issue no GitHub com a skill técnica ideal."
echo -e "3. Abra o repositório no Google Antigravity e veja o agente programar e testar com foco!"
echo -e "\n💬 Para suporte e documentação: consulte <support-url>\n"
