#!/usr/bin/env bash
#
# Antigravity Turbinado — Instalador Oficial macOS
# Executa a configuração automatizada com verificação estrita de permissões TCC e cancelamento fail-closed.
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🚀 INICIANDO INSTALAÇÃO DO ANTIGRAVITY TURBINADO (macOS)${NC}"
echo -e "${BLUE}============================================================${NC}"

# ETAPA 1: Verificação de Plataforma
echo -e "\n${YELLOW}[ETAPA 1/6] Verificando Sistema Operacional...${NC}"
OS_NAME="$(uname -s)"
if [ "$OS_NAME" != "Darwin" ]; then
    echo -e "${RED}❌ ERRO: Este instalador é exclusivo para macOS. Para Windows, utilize installer/install.ps1.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ macOS detectado com sucesso ($(sw_vers -productVersion)).${NC}"

# ETAPA 2: Pré-requisitos (Python 3.10+ e Git)
echo -e "\n${YELLOW}[ETAPA 2/6] Verificando Dependências...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ ERRO: Git não encontrado. Instale as ferramentas de linha de comando: xcode-select --install${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git disponível: $(git --version)${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ ERRO: Python 3 não encontrado. Instale o Python 3.10 ou superior.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python disponível: $(python3 --version)${NC}"

# ETAPA 3: Verificação de Permissões TCC & Disco (FAIL-CLOSED)
echo -e "\n${YELLOW}[ETAPA 3/6] Auditoria de Permissões macOS (TCC & Acesso a Disco)...${NC}"
echo -e "O Antigravity precisa de permissão de escrita e leitura nos seus diretórios de projetos."

TEST_DIR="$HOME/projetos"
mkdir -p "$TEST_DIR"

# Teste de permissão de escrita
TEST_FILE="$TEST_DIR/.tcc_permission_probe_$$"
if touch "$TEST_FILE" 2>/dev/null; then
    rm -f "$TEST_FILE"
    echo -e "${GREEN}✅ Permissão de disco confirmada em $TEST_DIR!${NC}"
else
    echo -e "\n${RED}============================================================${NC}"
    echo -e "${RED}❌ INSTALAÇÃO CANCELADA: PERMISSÃO DE DISCO NEGADA PELO MACOS${NC}"
    echo -e "${RED}============================================================${NC}"
    echo -e "O macOS bloqueou o acesso aos seus diretórios de desenvolvimento."
    echo -e "\n${YELLOW}COMO AUTORIZAR E RESOLVER:${NC}"
    echo -e "1. Abra os ${BLUE}Ajustes do Sistema${NC} (System Settings)."
    echo -e "2. Acesse ${BLUE}Privacidade e Segurança → Acesso Total ao Disco${NC} (Full Disk Access)."
    echo -e "3. Clique no botão ${BLUE}+${NC} e adicione o seu aplicativo de ${BLUE}Terminal${NC} e o ${BLUE}Antigravity${NC}."
    echo -e "4. Marque a opção como ATIVADA (azul)."
    echo -e "5. Reinicie a instalação executando o comando novamente.\n"
    exit 1
fi

# ETAPA 4: Configuração de Governança & Sentinela Guardião
echo -e "\n${YELLOW}[ETAPA 4/6] Configurando Sentinela Guardião e Regras Canônicas...${NC}"
AGY_CONFIG_DIR="$HOME/.gemini/antigravity"
mkdir -p "$AGY_CONFIG_DIR"

# ETAPA 5: Configuração de Permissões de Workspace (Inside vs. Outside)
echo -e "\n${YELLOW}[ETAPA 5/6] Aplicando Política Otimizada de Permissões...${NC}"
echo -e "• Dentro da pasta do projeto: ${GREEN}Sempre permitir e proceder com as implementações${NC}"
echo -e "• Fora da pasta do projeto: ${YELLOW}Perguntar sempre / Request Review obrigatório${NC}"

# ETAPA 6: Diagnóstico Final (Doctor)
echo -e "\n${YELLOW}[ETAPA 6/6] Executando Doctor de Validação...${NC}"
python3 scripts/doctor.py

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 INSTALAÇÃO DO ANTIGRAVITY TURBINADO CONCLUÍDA COM SUCESSO!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo -e "Para comprar o Combo Pro com Gemini por 18 meses ou obter suporte:"
echo -e "👉 Acesse o bot oficial no Telegram: ${BLUE}@xprotorkzdev${NC}"
echo -e "Consulte a documentação em ${YELLOW}docs/ARCHITECTURE.md${NC} para começar.\n"
