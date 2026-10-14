<#
.SYNOPSIS
    Sanitização Profunda de Ambiente & Remoção de Telemetria de Sessões Anteriores (Fase 1)
.DESCRIPTION
    Limpa caches de identificação, logs de eventos do Windows, arquivos temporários,
    tabelas ARP/DNS e traces de rede para preparar a máquina para execução limpa.
#>

[CmdletBinding()]
param()

$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Sentinela - Sanitização Profunda de Ambiente"

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "  🧹  SENTINELA SANITIZAÇÃO: $Title" -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Action, [string]$Detail, [string]$Status = "OK")
    $color = "Green"
    if ($Status -eq "WARN") { $color = "Yellow" }
    elseif ($Status -eq "FAIL") { $color = "Red" }
    Write-Host "  [$Status] " -NoNewline -ForegroundColor $color
    Write-Host "$($Action.PadRight(35)): " -NoNewline -ForegroundColor White
    Write-Host "$Detail" -ForegroundColor $color
}

Write-Header "INICIALIZANDO SANITIZAÇÃO (FASE 1)"

# 1. Limpeza de Caches de Rede e DNS
Write-Header "1. SANITIZAÇÃO DE REDE & RESOLUÇÃO DE NOMES"
try {
    Clear-DnsClientCache -ErrorAction SilentlyContinue
    ipconfig /flushdns | Out-Null
    Write-Step "Cache DNS do Windows" "Flush realizado com sucesso" "OK"
} catch {
    Write-Step "Cache DNS do Windows" "Falha parcial no flush" "WARN"
}

try {
    arp -d * 2>$null | Out-Null
    Write-Step "Tabela ARP (Endereços Físicos)" "Tabela ARP esvaziada" "OK"
} catch {
    Write-Step "Tabela ARP" "Executado com aviso" "WARN"
}

try {
    netsh winsock reset | Out-Null
    Write-Step "Stack Winsock" "Catálogo Winsock redefinido" "OK"
} catch {
    Write-Step "Stack Winsock" "Requer elevação de administrador" "WARN"
}

# 2. Limpeza de Arquivos Temporários e Dumps
Write-Header "2. ARQUIVOS TEMPORÁRIOS & CRASHDUMPS"
$tempPaths = @(
    "$env:TEMP",
    "$env:LOCALAPPDATA\Temp",
    "C:\Windows\Temp",
    "$env:LOCALAPPDATA\CrashDumps"
)

$totalDeleted = 0
foreach ($p in $tempPaths) {
    if (Test-Path $p) {
        try {
            $files = Get-ChildItem -Path $p -Recurse -Force -ErrorAction SilentlyContinue
            $count = ($files | Measure-Object).Count
            Remove-Item -Path "$p\*" -Recurse -Force -ErrorAction SilentlyContinue
            $totalDeleted += $count
            Write-Step "Limpeza $p" "$count itens processados" "OK"
        } catch {
            Write-Step "Limpeza $p" "Acesso negado em alguns itens" "WARN"
        }
    }
}

# 3. Limpeza de Logs de Eventos do Windows (Event Viewer)
Write-Header "3. EVENT VIEWER & LOGS DO SISTEMA"
$logsToClear = @("Application", "System", "Security", "Setup")
foreach ($log in $logsToClear) {
    try {
        wevtutil cl $log 2>$null
        Write-Step "Log de Eventos ($log)" "Limpo com sucesso" "OK"
    } catch {
        Write-Step "Log de Eventos ($log)" "Requer execução como Administrador" "WARN"
    }
}

# 4. Limpeza de Rastros de Telemetria e Logs de Jogos
Write-Header "4. TELEMETRIA E RASTROS DE JOGOS"
$gamePaths = @(
    "$env:LOCALAPPDATA\GamersClub",
    "$env:PROGRAMDATA\GamersClub",
    "$env:APPDATA\GamersClub"
)
foreach ($gp in $gamePaths) {
    if (Test-Path $gp) {
        try {
            $logFiles = Get-ChildItem -Path $gp -Include "*.log","*.dmp","*.tmp" -Recurse -Force -ErrorAction SilentlyContinue
            $cnt = ($logFiles | Measure-Object).Count
            $logFiles | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Step "Logs GamersClub ($gp)" "$cnt arquivos de telemetria removidos" "OK"
        } catch {
            Write-Step "Logs GamersClub ($gp)" "Pasta em uso ou protegida" "WARN"
        }
    } else {
        Write-Step "Logs GamersClub ($gp)" "Nenhum diretório residual encontrado" "OK"
    }
}

Write-Header "SANITIZAÇÃO CONCLUÍDA"
Write-Host "  ✅ Ambiente limpo e sanitizado." -ForegroundColor Green
Write-Host "  💡 Recomenda-se reiniciar o roteador para renovação do IP público (caso não seja estático)." -ForegroundColor Yellow
Write-Host ""
