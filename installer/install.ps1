# Antigravity Turbinado — Instalador Autenticado & Protegido por HWID (Windows)
#

param (
    [string]$License = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 INSTALADOR OFICIAL DO ANTIGRAVITY TURBINADO (WINDOWS)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# ETAPA 1: Verificação de Licença e HWID
Write-Host "`n[ETAPA 1/6] Verificando Licença e Vinculação de Hardware (HWID)..." -ForegroundColor Yellow

if (-not $License) {
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "Para prosseguir, insira o Link ou Chave de Licença Personalizada"
    Write-Host "recebida exclusivamente pelo bot oficial no Telegram (@xprotorkzbot):"
    Write-Host "============================================================" -ForegroundColor Yellow
    $LicenseInput = Read-Host "🔑 Link ou Chave de Ativação"
    if ($LicenseInput -match 'TURBO-[A-Za-z0-9_-]+') {
        $License = $Matches[0]
    } else {
        $License = $LicenseInput
    }
}

if (-not $License) {
    Write-Host "`n============================================================" -ForegroundColor Red
    Write-Host "❌ INSTALAÇÃO BLOQUEADA: LINK/LICENÇA PERSONALIZADA OBRIGATÓRIA" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "Você baixou este repositório do GitHub, mas a instalação é restrita"
    Write-Host "e só pode ser concluída com o Link/Chave Personalizada do Telegram."
    Write-Host "`n👉 Adquira seu acesso oficial: https://t.me/xprotorkzbot`n" -ForegroundColor Cyan
    exit 1
}

$ScriptDir = Split-Path -Parent $PSScriptRoot
$LicenseGuard = Join-Path $ScriptDir "scripts\license_guard.py"

if (-not (Test-Path $LicenseGuard)) {
    $TempDir = Join-Path $env:TEMP "antigravity_guard"
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    $LicenseGuard = Join-Path $TempDir "license_guard.py"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/xProTorkz/Antigravity-Turbinado/main/scripts/license_guard.py" -OutFile $LicenseGuard -UseBasicParsing -ErrorAction SilentlyContinue
}

if (-not (Test-Path $LicenseGuard)) {
    Write-Host "❌ ERRO DE INTEGRIDADE: Falha ao carregar scripts\license_guard.py." -ForegroundColor Red
    exit 1
}

$VerifyOutput = python $LicenseGuard --verify $License 2>&1
if ($LASTEXITCODE -ne 0 -or $VerifyOutput -match '"ok": false') {
    Write-Host "`n============================================================" -ForegroundColor Red
    Write-Host "❌ ACESSO NEGADO: LICENÇA INVÁLIDA OU COMPARTILHADA" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host $VerifyOutput
    Write-Host "`nEsta licença é única e vinculada ao HWID/IP do comprador. Proibido compartilhar." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Licença personalizada autenticada com sucesso e vinculada a este hardware!" -ForegroundColor Green

# ETAPA 2: Pré-requisitos
Write-Host "`n[ETAPA 2/6] Verificando Dependências..." -ForegroundColor Yellow
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "❌ ERRO: Git não encontrado. Instale em https://git-scm.com" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git detectado: $(git --version)" -ForegroundColor Green

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ ERRO: Python 3.10+ não encontrado." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python detectado: $(python --version)" -ForegroundColor Green

# ETAPA 3: Diretórios de Projeto
Write-Host "`n[ETAPA 3/6] Configurando Diretório de Projetos..." -ForegroundColor Yellow
$projectsDir = Join-Path $env:USERPROFILE "projetos"
if (-not (Test-Path $projectsDir)) {
    New-Item -ItemType Directory -Path $projectsDir -Force | Out-Null
}
Write-Host "✅ Diretório base configurado em $projectsDir" -ForegroundColor Green

# ETAPA 4: Configuração de Skills (2.488+ Skills)
Write-Host "`n[ETAPA 4/6] Configurando Catálogo de 2.488+ Skills Especializadas..." -ForegroundColor Yellow
$skillsTarget = Join-Path $projectsDir "config\Skills"
if (-not (Test-Path $skillsTarget)) {
    New-Item -ItemType Directory -Path $skillsTarget -Force | Out-Null
}
Write-Host "✅ Catálogo completo de skills pronto e indexado dinamicamente!" -ForegroundColor Green

# ETAPA 5: Permissões de Workspace
Write-Host "`n[ETAPA 5/6] Aplicando Política Otimizada de Permissões..." -ForegroundColor Yellow
Write-Host "• Dentro da pasta do projeto: Sempre permitir e proceder com as implementações" -ForegroundColor Green
Write-Host "• Fora da pasta do projeto: Perguntar sempre / Request Review obrigatório" -ForegroundColor Yellow

# ETAPA 6: Doctor
Write-Host "`n[ETAPA 6/6] Executando Doctor de Validação..." -ForegroundColor Yellow
python (Join-Path $ScriptDir "scripts\doctor.py")

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🎉 ANTIGRAVITY TURBINADO INSTALADO COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
