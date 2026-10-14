<#
.SYNOPSIS
    Auditoria e Inspeção Profunda de Hardware ID (HWID) & Pre-Flight Check Gamers Club
.DESCRIPTION
    Coleta e exibe em formato visual os identificadores reais que sistemas operacionais
    e anti-cheats (como Gamers Club Anti-Cheat 2.0) utilizam para fingerprinting da máquina.
#>

[CmdletBinding()]
param(
    [switch]$JsonOutput = $false
)

$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Sentinela - Auditoria Profunda de HWID"

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "  🛡️  SENTINELA HWID AUDIT: $Title" -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Cyan
}

function Write-Item {
    param([string]$Label, [string]$Value, [string]$Status = "INFO")
    $color = "White"
    if ($Status -eq "OK") { $color = "Green" }
    elseif ($Status -eq "WARN") { $color = "Yellow" }
    elseif ($Status -eq "ALERT") { $color = "Red" }
    Write-Host "  [$Status] " -NoNewline -ForegroundColor $color
    Write-Host "$($Label.PadRight(30)): " -NoNewline -ForegroundColor Cyan
    Write-Host "$Value" -ForegroundColor $color
}

$Report = [ordered]@{}

Write-Header "INSPEÇÃO DE IDENTIFICADORES DE HARDWARE"

# 1. Placa-Mãe (Motherboard) & SMBIOS
try {
    $bb = Get-CimInstance Win32_BaseBoard -ErrorAction Stop
    $csp = Get-CimInstance Win32_ComputerSystemProduct -ErrorAction Stop
    $bios = Get-CimInstance Win32_BIOS -ErrorAction Stop

    $Report["Motherboard_Manufacturer"] = $bb.Manufacturer
    $Report["Motherboard_Product"] = $bb.Product
    $Report["Motherboard_Serial"] = $bb.SerialNumber
    $Report["System_UUID"] = $csp.UUID
    $Report["BIOS_Serial"] = $bios.SerialNumber
    $Report["BIOS_Version"] = $bios.SMBIOSBIOSVersion

    Write-Item "Fabricante Placa-Mãe" $bb.Manufacturer "OK"
    Write-Item "Modelo Placa-Mãe" $bb.Product "OK"
    Write-Item "Serial Placa-Mãe (DMI)" $bb.SerialNumber "WARN"
    Write-Item "System UUID (SMBIOS)" $csp.UUID "WARN"
    Write-Item "Serial BIOS" $bios.SerialNumber "WARN"
    Write-Item "Versão BIOS" $bios.SMBIOSBIOSVersion "OK"
} catch {
    Write-Item "Placa-Mãe" "Falha na leitura WMI: $_" "ALERT"
}

# 2. Armazenamento (Storage Disks - NVMe / SATA)
Write-Header "UNIDADES DE ARMAZENAMENTO (DISCOS)"
$DisksList = @()
try {
    $disks = Get-CimInstance Win32_DiskDrive -ErrorAction Stop
    foreach ($d in $disks) {
        $diskInfo = [ordered]@{
            Index        = $d.Index
            Model        = $d.Model
            SerialNumber = $d.SerialNumber.Trim()
            Interface    = $d.InterfaceType
            SizeGB       = [math]::Round($d.Size / 1GB, 2)
        }
        $DisksList += $diskInfo
        Write-Item "Disco $($d.Index) Modelo" $d.Model "OK"
        Write-Item "Disco $($d.Index) Serial Físico" $d.SerialNumber.Trim() "WARN"
        Write-Item "Disco $($d.Index) Interface/Tamanho" "$($d.InterfaceType) - $($diskInfo.SizeGB) GB" "INFO"
    }
    $Report["Disks"] = $DisksList
} catch {
    Write-Item "Discos" "Falha na leitura de discos: $_" "ALERT"
}

# 3. Interfaces de Rede (MAC Address)
Write-Header "INTERFACES DE REDE (MAC ADDRESS)"
$NicsList = @()
try {
    $nics = Get-CimInstance Win32_NetworkAdapterConfiguration -Filter "IPEnabled = True" -ErrorAction Stop
    foreach ($nic in $nics) {
        $nicInfo = [ordered]@{
            Description = $nic.Description
            MACAddress  = $nic.MACAddress
            IPAddress   = ($nic.IPAddress -join ", ")
        }
        $NicsList += $nicInfo
        Write-Item "Adaptador" $nic.Description "OK"
        Write-Item "MAC Address Físico" $nic.MACAddress "WARN"
    }
    $Report["NetworkAdapters"] = $NicsList
} catch {
    Write-Item "Rede" "Falha na leitura de interfaces: $_" "ALERT"
}

# 4. Sistema Operacional & Windows Cryptography GUID
Write-Header "IDENTIDADE DO WINDOWS (REGISTRY GUIDS)"
try {
    $machineGuid = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Cryptography" -Name MachineGuid -ErrorAction SilentlyContinue).MachineGuid
    $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop

    $Report["MachineGuid"] = $machineGuid
    $Report["OS_InstallDate"] = $os.InstallDate
    $Report["OS_SerialNumber"] = $os.SerialNumber

    Write-Item "Cryptography MachineGuid" $machineGuid "WARN"
    Write-Item "Data Instalação Windows" $os.InstallDate "INFO"
    Write-Item "Serial do Windows" $os.SerialNumber "WARN"
} catch {
    Write-Item "Windows Registry" "Falha na leitura do registro: $_" "ALERT"
}

# 5. Pre-Flight Check Gamers Club Anti-Cheat 2.0 (TPM, Secure Boot, VBS)
Write-Header "PRE-FLIGHT CHECK GAMERS CLUB ANTI-CHEAT 2.0"

# Check TPM 2.0
$tpmStatus = "DESCONHECIDO"
$tpmVer = "N/A"
try {
    $tpm = Get-Tpm -ErrorAction SilentlyContinue
    if ($tpm) {
        if ($tpm.TpmPresent -and $tpm.TpmReady) {
            $tpmStatus = "ATIVO E PRONTO"
            Write-Item "TPM 2.0 Status" "Ativado e Operacional (TpmReady: True)" "OK"
        } else {
            $tpmStatus = "DESATIVADO OU INCOMPLETO"
            Write-Item "TPM 2.0 Status" "Presente=$($tpm.TpmPresent), Pronto=$($tpm.TpmReady)" "ALERT"
        }
    } else {
        $tpmStatus = "AUSENTE"
        Write-Item "TPM 2.0 Status" "Módulo TPM não detectado" "ALERT"
    }
} catch {
    Write-Item "TPM 2.0" "Erro ao consultar cmdlet Get-Tpm" "ALERT"
}
$Report["TPM_Status"] = $tpmStatus

# Check Secure Boot
$secureBootStatus = "DESATIVADO"
try {
    $sb = Confirm-SecureBootUEFI -ErrorAction SilentlyContinue
    if ($sb -eq $true) {
        $secureBootStatus = "ATIVADO"
        Write-Item "Secure Boot UEFI" "Ativado em Conformidade com AC 2.0" "OK"
    } else {
        $secureBootStatus = "DESATIVADO"
        Write-Item "Secure Boot UEFI" "Desativado (Gamers Club AC 2.0 bloqueará o acesso)" "ALERT"
    }
} catch {
    Write-Item "Secure Boot" "Não suportado ou modo Legacy BIOS ativo" "ALERT"
}
$Report["SecureBoot_Status"] = $secureBootStatus

# Check Virtualization-Based Security (VBS)
try {
    $dg = Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard -ErrorAction SilentlyContinue
    if ($dg -and $dg.VirtualizationBasedSecurityStatus -eq 2) {
        Write-Item "VBS (Virtualization-Based Security)" "Em Execução (Status 2)" "OK"
        $Report["VBS_Status"] = "ATIVO"
    } else {
        Write-Item "VBS (Virtualization-Based Security)" "Inativo ou Não Configurado" "WARN"
        $Report["VBS_Status"] = "INATIVO"
    }
} catch {
    Write-Item "VBS" "Informação não disponível" "INFO"
}

Write-Header "RESUMO DO DIAGNÓSTICO DE HWID"
Write-Host "  • Todos os seriais listados acima com tag [WARN] compõem a impressão digital da máquina." -ForegroundColor Gray
Write-Host "  • Se os seriais forem idênticos aos de uma máquina banida, a GC associará o hardware." -ForegroundColor Gray
Write-Host "  • Se o TPM 2.0 ou o Secure Boot estiverem em [ALERT], o Anti-Cheat 2.0 recusará o login." -ForegroundColor Yellow
Write-Host ""

if ($JsonOutput) {
    $Report | ConvertTo-Json -Depth 4
}
