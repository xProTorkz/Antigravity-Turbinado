# Antigravity Turbinado — Instalador Neutro e Onboarding Oficial (Windows)
# Arquitetura: ChatGPT (Planejador) → GitHub (Fonte da Verdade) → Antigravity (Executor)
#

param (
    [string]$License = "",
    [string]$ProjectsDir = "",
    [switch]$NonInteractive
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 INSTALADOR OFICIAL DO ANTIGRAVITY TURBINADO (WINDOWS)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $PSScriptRoot
$LicenseGuard = Join-Path $ScriptDir "scripts\license_guard.py"

# ETAPA 1: Verificação de Licença e HWID (se informada)
if ($License -and (Test-Path $LicenseGuard)) {
    Write-Host "`n[ETAPA 1/6] Verificando Licença e Vinculação de Hardware (HWID)..." -ForegroundColor Yellow
    $VerifyOutput = python $LicenseGuard --verify $License 2>&1
    if ($LASTEXITCODE -ne 0 -or $VerifyOutput -match '"ok": false') {
        Write-Host "`n============================================================" -ForegroundColor Red
        Write-Host "❌ ACESSO NEGADO: LICENÇA INVÁLIDA OU COMPARTILHADA" -ForegroundColor Red
        Write-Host "============================================================" -ForegroundColor Red
        Write-Host $VerifyOutput
        Write-Host "`nEsta licença é exclusiva desta máquina. Suporte: <support-url>" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Licença autenticada com sucesso e vinculada a este hardware!" -ForegroundColor Green
} else {
    Write-Host "`n[ETAPA 1/6] Modo de Instalação Padrão / Licença Local" -ForegroundColor Yellow
}

# ETAPA 2: Pré-requisitos (Git, Python)
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

# ETAPA 3: Instalação e Indexação das Skills e Configurações de Autonomia
Write-Host "`n[ETAPA 3/5] Configurando Ambiente Turbo, Skills e Permissões..." -ForegroundColor Yellow
$TurboScript = Join-Path $ScriptDir "scripts\configure_turbo_environment.py"
if (Test-Path $TurboScript) {
    python $TurboScript
}

# ETAPA 4: Permissões de Workspace e Autonomia
Write-Host "`n[ETAPA 4/5] Aplicando Política Otimizada de Permissões..." -ForegroundColor Yellow
Write-Host "• Antigravity configurado em modo: EAGER (Auto-execução de comandos no workspace)" -ForegroundColor Green
Write-Host "• Dentro da pasta do projeto: Sempre permitir alterações no workspace" -ForegroundColor Green
Write-Host "• Fora da pasta do projeto: Perguntar sempre / Request Review obrigatório" -ForegroundColor Yellow

# ETAPA 5: Doctor de Integridade
Write-Host "`n[ETAPA 5/5] Executando Doctor de Validação do Ambiente..." -ForegroundColor Yellow
python (Join-Path $ScriptDir "scripts\doctor.py")

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🎉 ANTIGRAVITY TURBINADO INSTALADO COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Sua máquina agora está configurada e pronta para receber tarefas autônomas."
Write-Host "`n📌 COMO COMEÇAR SEU PRIMEIRO PROJETO:" -ForegroundColor Yellow
Write-Host "1. Abra o ChatGPT e configure as Instruções Personalizadas com o template do kit."
Write-Host "2. Peça sua tarefa no ChatGPT: ele criará a Issue no GitHub com a skill ideal."
Write-Host "3. Abra o repositório no Google Antigravity e veja o agente programar e testar sozinho!"
Write-Host "`n💬 Para suporte e documentação: consulte <support-url>`n" -ForegroundColor Cyan
