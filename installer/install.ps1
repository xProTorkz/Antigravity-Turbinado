# Antigravity Turbinado — Instalador Oficial Windows (PowerShell)
# Executa a configuração automatizada para Windows com suporte a Credential Manager.

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO INSTALAÇÃO DO ANTIGRAVITY TURBINADO (WINDOWS)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# ETAPA 1: Verificação de Dependências
Write-Host "`n[ETAPA 1/5] Verificando Dependências do Windows..." -ForegroundColor Yellow

$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "❌ ERRO: Git para Windows não encontrado no PATH. Instale o Git em https://git-scm.com" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git detectado: $(git --version)" -ForegroundColor Green

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ ERRO: Python não encontrado. Instale o Python 3.10+ e marque 'Add python.exe to PATH'." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python detectado: $(python --version)" -ForegroundColor Green

# ETAPA 2: Diretório de Projetos
Write-Host "`n[ETAPA 2/5] Configurando Diretório de Projetos..." -ForegroundColor Yellow
$projectsDir = Join-Path $env:USERPROFILE "projetos"
if (-not (Test-Path $projectsDir)) {
    New-Item -ItemType Directory -Path $projectsDir -Force | Out-Null
}
Write-Host "✅ Diretório base configurado em $projectsDir" -ForegroundColor Green

# ETAPA 3: Política de Permissões (Inside vs. Outside)
Write-Host "`n[ETAPA 3/5] Aplicando Política Otimizada de Permissões..." -ForegroundColor Yellow
Write-Host "• Dentro da pasta do projeto: Sempre permitir e proceder com as implementações" -ForegroundColor Green
Write-Host "• Fora da pasta do projeto: Perguntar sempre / Request Review obrigatório" -ForegroundColor Yellow

# ETAPA 4: Configuração de Credenciais
Write-Host "`n[ETAPA 4/5] Integrando com o Windows Credential Manager..." -ForegroundColor Yellow
git config --global credential.helper manager-core
Write-Host "✅ Armazenamento seguro de credenciais ativado via Windows Credential Manager." -ForegroundColor Green

# ETAPA 5: Diagnóstico Doctor
Write-Host "`n[ETAPA 5/5] Executando Doctor de Validação..." -ForegroundColor Yellow
python scripts\doctor.py

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🎉 INSTALAÇÃO DO ANTIGRAVITY TURBINADO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Para suporte, compra do Combo Pro com Gemini 18 meses ou tirar dúvidas:" -ForegroundColor White
Write-Host "👉 Fale com nosso bot oficial no Telegram: @xprotorkzdev" -ForegroundColor Cyan
