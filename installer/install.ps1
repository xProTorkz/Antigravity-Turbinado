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

# ETAPA 3: Instalação e Indexação das Skills e Configurações Turbo
Write-Host "`n[ETAPA 3/5] Configurando Ambiente Turbo, Skills e Permissões..." -ForegroundColor Yellow
$TurboScript = Join-Path $ScriptDir "scripts\configure_turbo_environment.py"
if (Test-Path $TurboScript) {
    python $TurboScript
} else {
    $TempTurboDir = Join-Path $env:TEMP "antigravity_turbo"
    New-Item -ItemType Directory -Path $TempTurboDir -Force | Out-Null
    $TempTurboScript = Join-Path $TempTurboDir "configure_turbo_environment.py"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/xProTorkz/Antigravity-Turbinado/main/scripts/configure_turbo_environment.py" -OutFile $TempTurboScript -UseBasicParsing -ErrorAction SilentlyContinue
    if (Test-Path $TempTurboScript) {
        python $TempTurboScript
        Remove-Item -Recurse -Force $TempTurboDir -ErrorAction SilentlyContinue
    }
}

# ETAPA 4: Permissões de Workspace e Autonomia
Write-Host "`n[ETAPA 4/5] Aplicando Política Otimizada de Permissões..." -ForegroundColor Yellow
Write-Host "• Antigravity configurado em modo: EAGER (Auto-execução contínua de comandos)" -ForegroundColor Green
Write-Host "• Dentro da pasta do projeto: Sempre permitir alterações no workspace" -ForegroundColor Green
Write-Host "• Fora da pasta do projeto: Perguntar sempre / Request Review obrigatório" -ForegroundColor Yellow

# ETAPA 5: Doctor de Integridade
Write-Host "`n[ETAPA 5/5] Executando Doctor de Validação do Ambiente..." -ForegroundColor Yellow
python (Join-Path $ScriptDir "scripts\doctor.py")

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🎉 ANTIGRAVITY TURBINADO INSTALADO COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Sua máquina agora está 100% calibrada e pronta para receber tarefas autônomas."
Write-Host "`n📌 COMO COMEÇAR SEU PRIMEIRO PROJETO:" -ForegroundColor Yellow
Write-Host "1. Abra o ChatGPT e configure as Instruções Personalizadas com o template do kit."
Write-Host "2. Peça sua tarefa em português no ChatGPT: ele criará a Issue no GitHub com a skill ideal."
Write-Host "3. Abra o repositório no Google Antigravity e veja o agente programar e testar sozinho!"
Write-Host "`n💬 Para suporte técnico exclusivo: @xprotorkzdev no Telegram.`n" -ForegroundColor Cyan
