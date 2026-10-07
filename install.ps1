# ==============================================================================
# 🚀 Antigravity Ecosystem & SRE Automation Toolkit - Instalador Windows
# Compatibilidade: Windows 10/11 | Shell: PowerShell 5.1+ / PowerShell Core (pwsh)
# ==============================================================================

[CmdletBinding()]
param (
    [switch]$Force = $false,
    [switch]$AllUsers = $false
)

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "🚀 INSTALADOR DO ECOSSISTEMA ANTIGRAVITY & SRE TOOLKIT (WINDOWS)" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Cyan

$InstallDir = $PSScriptRoot
Write-Host "📂 Diretório Base: $InstallDir`n" -ForegroundColor Gray

# ------------------------------------------------------------------------------
# Passo 1: Liberar a Política de Execução do PowerShell (ExecutionPolicy)
# ------------------------------------------------------------------------------
Write-Host "🔓 1. Configurando política de execução do PowerShell..." -ForegroundColor Yellow

try {
    if ($AllUsers) {
        Set-ExecutionPolicy Bypass -Scope LocalMachine -Force -ErrorAction Stop
        Write-Host "  ✅ ExecutionPolicy definida como 'Bypass' (LocalMachine)." -ForegroundColor Green
    } else {
        Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force -ErrorAction Stop
        Write-Host "  ✅ ExecutionPolicy definida como 'RemoteSigned' (CurrentUser)." -ForegroundColor Green
    }
} catch {
    Write-Warning "  ⚠️ Não foi possível alterar a política automaticamente: $_"
    Write-Warning "  👉 Execute o PowerShell como Administrador e rode: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
}

# Conferir políticas atuais
Write-Host "  📋 Políticas ativas:" -ForegroundColor Gray
Get-ExecutionPolicy -List | Format-Table -AutoSize | Out-String | Write-Host -ForegroundColor DarkGray

# ------------------------------------------------------------------------------
# Passo 2: Desbloquear Scripts/Arquivos Baixados (Unblock-File)
# ------------------------------------------------------------------------------
Write-Host "`n🔓 2. Removendo trava SmartScreen/Zone.Identifier dos arquivos..." -ForegroundColor Yellow
try {
    Get-ChildItem -Path $InstallDir -Recurse -File -ErrorAction SilentlyContinue | Unblock-File
    Write-Host "  ✅ Todos os arquivos e scripts foram desbloqueados com sucesso." -ForegroundColor Green
} catch {
    Write-Warning "  ⚠️ Falha ao desbloquear alguns arquivos: $_"
}

# ------------------------------------------------------------------------------
# Passo 3: Configurar Terminal Integrado do Antigravity / VS Code
# ------------------------------------------------------------------------------
Write-Host "`n⚙️ 3. Otimizando configurações de terminal integrado no VS Code / Antigravity..." -ForegroundColor Yellow

$VscodeSettingsPaths = @(
    "$env:APPDATA\Code\User\settings.json",
    "$env:APPDATA\Antigravity\User\settings.json",
    "$env:USERPROFILE\.gemini\settings.json"
)

foreach ($path in $VscodeSettingsPaths) {
    if (Test-Path (Split-Path $path -Parent)) {
        try {
            $settings = @{}
            if (Test-Path $path) {
                $rawContent = Get-Content -Path $path -Raw
                if (![string]::IsNullOrWhiteSpace($rawContent)) {
                    $settings = $rawContent | ConvertFrom-Json -AsHashtable
                }
            }
            
            # Recomendar Git Bash se instalado, ou configurar PowerShell sem trava
            $gitBashPath = "C:\Program Files\Git\bin\bash.exe"
            if (Test-Path $gitBashPath) {
                $settings["terminal.integrated.defaultProfile.windows"] = "Git Bash"
                Write-Host "  ✅ Git Bash configurado como terminal padrão em $path" -ForegroundColor Green
            } else {
                # Configurar PowerShell com bypass automático
                if (-not $settings.ContainsKey("terminal.integrated.profiles.windows")) {
                    $settings["terminal.integrated.profiles.windows"] = @{}
                }
                $settings["terminal.integrated.profiles.windows"]["PowerShell"] = @{
                    "source" = "PowerShell";
                    "icon" = "terminal-powershell";
                    "args" = @("-NoExit", "-ExecutionPolicy", "Bypass")
                }
                Write-Host "  ✅ PowerShell com Bypass configurado em $path" -ForegroundColor Green
            }
            
            # Salvar JSON formatado
            $settings | ConvertTo-Json -Depth 10 | Set-Content -Path $path -Encoding UTF8
        } catch {
            Write-Warning "  ⚠️ Não foi possível atualizar $path automaticamente: $_"
        }
    }
}

Write-Host "`n====================================================================" -ForegroundColor Cyan
Write-Host "🎉 INSTALAÇÃO NO WINDOWS CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "💡 Dica: Se o Antigravity / VS Code já estava aberto, feche e abra novamente." -ForegroundColor Gray
