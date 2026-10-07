# ==============================================================================
# 🚀 Antigravity Ecosystem & SRE Automation Toolkit - Instalador Windows
# Compatibilidade: Windows 10/11 | Shell: PowerShell 5.1+ / PowerShell Core (pwsh)
# Modelo de Credenciais: BYOK (Bring Your Own Key) - 100% Isolado por Usuário
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

# ------------------------------------------------------------------------------
# Passo 2: Desbloquear Scripts/Arquivos Baixados (Unblock-File)
# ------------------------------------------------------------------------------
Write-Host "`n🔓 2. Removendo trava SmartScreen/Zone.Identifier dos scripts..." -ForegroundColor Yellow
try {
    Get-ChildItem -Path $InstallDir -Recurse -File -ErrorAction SilentlyContinue | Unblock-File
    Write-Host "  ✅ Todos os arquivos e scripts foram desbloqueados com sucesso." -ForegroundColor Green
} catch {
    Write-Warning "  ⚠️ Falha ao desbloquear alguns arquivos: $_"
}

# ------------------------------------------------------------------------------
# Passo 3: Destravar o Terminal Integrado no Antigravity / VS Code
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
            
            $gitBashPath = "C:\Program Files\Git\bin\bash.exe"
            if (Test-Path $gitBashPath) {
                $settings["terminal.integrated.defaultProfile.windows"] = "Git Bash"
                Write-Host "  ✅ Git Bash configurado como terminal padrão em $path" -ForegroundColor Green
            } else {
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
            
            $settings | ConvertTo-Json -Depth 10 | Set-Content -Path $path -Encoding UTF8
        } catch {
            Write-Warning "  ⚠️ Não foi possível atualizar $path: $_"
        }
    }
}

# ------------------------------------------------------------------------------
# Passo 4: Onboarding Pessoal — Google AI Studio & Google Colab (BYOK)
# ------------------------------------------------------------------------------
Write-Host "`n🌐 4. Configuração Pessoal de Inteligência Artificial (BYOK)..." -ForegroundColor Yellow
Write-Host "  ⚠️ Atenção: Para sua total segurança, suas credenciais são 100% isoladas." -ForegroundColor DarkYellow
Write-Host "  Você utilizará sua própria conta gratuita do Google (sem risco de compartilhamento)." -ForegroundColor DarkYellow

$KeyDir = "$env:USERPROFILE\.gemini"
$KeyFile = "$KeyDir\ai_studio_key.txt"

if (-not (Test-Path $KeyDir)) {
    New-Item -ItemType Directory -Path $KeyDir -Force | Out-Null
}

if (Test-Path $KeyFile) {
    Write-Host "  ✅ Chave pessoal do Google AI Studio já configurada em: $KeyFile" -ForegroundColor Green
} else {
    Write-Host "`n  👉 Passo para obter sua chave gratuita do Google AI Studio:" -ForegroundColor Cyan
    Write-Host "     1. Acesse o link oficial: https://aistudio.google.com/app/apikey" -ForegroundColor White
    Write-Host "     2. Faça login com sua conta Google e clique em 'Create API Key'." -ForegroundColor White
    Write-Host "     3. Cole sua chave abaixo (ou aperte Enter para configurar depois):" -ForegroundColor White
    
    $UserKey = Read-Host "     Sua API Key do Google AI Studio"
    if (![string]::IsNullOrWhiteSpace($UserKey)) {
        Set-Content -Path $KeyFile -Value $UserKey.Trim() -Encoding UTF8
        Write-Host "     🎉 Chave salva com sucesso em $KeyFile!" -ForegroundColor Green
    } else {
        Write-Host "     ℹ️ Chave não informada no momento. Quando quiser ativar, acesse:" -ForegroundColor DarkGray
        Write-Host "        https://aistudio.google.com/app/apikey e salve com: python 4-automacao-e-shell\ai_studio_cli.py --set-key <chave>" -ForegroundColor DarkGray
    }
}

Write-Host "`n  👉 Integração com Google Colab:" -ForegroundColor Cyan
Write-Host "     1. Acesse seus notebooks em: https://colab.research.google.com/" -ForegroundColor White
Write-Host "     2. Para rodar células usando o poder do seu PC local:" -ForegroundColor White
Write-Host "        Execute no terminal: bash 4-automacao-e-shell/iniciar_colab_local.sh (ou use o menu agy_cmd)" -ForegroundColor White
Write-Host "     3. No Colab, clique em 'Conectar a um ambiente de execução local' e cole a URL exibida." -ForegroundColor White

Write-Host "`n====================================================================" -ForegroundColor Cyan
Write-Host "🎉 INSTALAÇÃO NO WINDOWS CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "💡 Dica: Reinicie o terminal ou o Antigravity para carregar todas as políticas." -ForegroundColor Gray
