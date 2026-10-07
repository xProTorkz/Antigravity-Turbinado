#!/usr/bin/env bash
# ==============================================================================
# 🚀 Iniciar Runtime Local para Google Colab & Antigravity
# Permite conectar o Google Colab diretamente aos arquivos e terminal locais
# ==============================================================================

PORT=8888
ORIGIN="https://colab.research.google.com"

echo "===================================================================="
echo "🚀 INICIANDO SERVIDOR LOCAL PARA GOOGLE COLAB"
echo "===================================================================="

if ! command -v jupyter >/dev/null 2>&1; then
    echo "⚠️ Jupyter não encontrado no ambiente global."
    echo "Instalando jupyter e jupyter_http_over_ws..."
    python3 -m pip install --user jupyter jupyter_http_over_ws
    python3 -m jupyter serverextension enable --py jupyter_http_over_ws
fi

echo "Iniciando servidor na porta $PORT permitindo origem Colab..."
echo "Cole a URL exibida abaixo com o token na opção 'Conectar a um ambiente de execução local' do Google Colab."
echo "===================================================================="

python3 -m jupyter notebook \
  --NotebookApp.allow_origin="$ORIGIN" \
  --port="$PORT" \
  --NotebookApp.port_retries=0 \
  --no-browser
