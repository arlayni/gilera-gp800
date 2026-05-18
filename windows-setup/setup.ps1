# GP800 Windows Setup Script
# Uitvoeren als Administrator in PowerShell
# Klik rechts op PowerShell → "Als administrator uitvoeren"
# Dan: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#      .\setup.ps1

$ErrorActionPreference = "Stop"
$REPO_DIR = Split-Path -Parent $PSScriptRoot
$TOOL_DIR = Join-Path $REPO_DIR "gp800-tool"
$VENV_DIR = Join-Path $REPO_DIR ".venv"
$LOG_DIR = "$env:USERPROFILE\gp800-logs"

Write-Host "=== GP800 Windows Setup ===" -ForegroundColor Cyan
Write-Host "Repo:  $REPO_DIR"
Write-Host "Tool:  $TOOL_DIR"
Write-Host "Venv:  $VENV_DIR"
Write-Host "Logs:  $LOG_DIR"
Write-Host ""

# --- Python controleren ---
Write-Host "Python controleren..." -ForegroundColor Yellow
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(1[0-9])") {
            $python = $cmd
            Write-Host "  Gevonden: $ver ($cmd)" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host ""
    Write-Host "Python 3.10+ niet gevonden!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installeer Python 3.12 (32-bit):" -ForegroundColor Yellow
    Write-Host "  1. Ga naar: https://www.python.org/downloads/windows/"
    Write-Host "  2. Kies: Python 3.12.x - Windows installer (32-bit)"
    Write-Host "  3. Vink aan: 'Add Python to PATH'"
    Write-Host "  4. Installeer, herstart dit script"
    Write-Host ""
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

# --- 32-bit check ---
$arch = & $python -c "import struct; print(struct.calcsize('P') * 8)"
Write-Host "  Architectuur: $arch-bit"
if ($arch -eq "32") {
    Write-Host "  32-bit Python — goed voor deze laptop" -ForegroundColor Green
}

# --- Pip bijwerken ---
Write-Host ""
Write-Host "Pip bijwerken..." -ForegroundColor Yellow
& $python -m pip install --upgrade pip -q

# --- Virtuele omgeving ---
Write-Host ""
Write-Host "Virtuele omgeving aanmaken..." -ForegroundColor Yellow
if (-not (Test-Path $VENV_DIR)) {
    & $python -m venv $VENV_DIR
    Write-Host "  Aangemaakt: $VENV_DIR" -ForegroundColor Green
} else {
    Write-Host "  Bestaat al: $VENV_DIR" -ForegroundColor Green
}

$pip = Join-Path $VENV_DIR "Scripts\pip.exe"
$gp800 = Join-Path $VENV_DIR "Scripts\gp800-tool.exe"

# --- gp800-tool installeren ---
Write-Host ""
Write-Host "gp800-tool installeren..." -ForegroundColor Yellow
& $pip install -e "$TOOL_DIR[api,kline]" -q
Write-Host "  Geinstalleerd: $(& $gp800 --version)" -ForegroundColor Green

# --- Log directory ---
Write-Host ""
Write-Host "Log directory aanmaken..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
Write-Host "  $LOG_DIR" -ForegroundColor Green

# --- Startscript aanmaken ---
Write-Host ""
Write-Host "Startscript aanmaken op bureaublad..." -ForegroundColor Yellow
$desktopScript = Join-Path $env:USERPROFILE "Desktop\GP800-Start.bat"
@"
@echo off
title GP800 Tool
cd /d "$REPO_DIR"
call "$VENV_DIR\Scripts\activate.bat"
echo.
echo === GP800 Dashboard starten ===
echo Open op je iPhone: http://%COMPUTERNAME%:8000
echo Stoppen: Ctrl+C
echo.
gp800-tool serve COM3
pause
"@ | Set-Content $desktopScript
Write-Host "  Bureaublad: GP800-Start.bat" -ForegroundColor Green

# --- CH340 driver instructie ---
Write-Host ""
Write-Host "=== USB-KKL Driver ===" -ForegroundColor Cyan
Write-Host "Als je USB-KKL adapter een CH340 chip heeft:"
Write-Host "  1. Sluit de adapter aan"
Write-Host "  2. Open Apparaatbeheer (devmgmt.msc)"
Write-Host "  3. Zoek 'USB-SERIAL CH340' onder Poorten (COM & LPT)"
Write-Host "  4. Onthoud het COM-poortnummer (bijv. COM3)"
Write-Host "  5. Pas het poortnummer aan in GP800-Start.bat op je bureaublad"
Write-Host ""

# --- Poorten tonen ---
Write-Host "=== Beschikbare COM poorten ===" -ForegroundColor Cyan
$ports = [System.IO.Ports.SerialPort]::GetPortNames()
if ($ports) {
    $ports | ForEach-Object { Write-Host "  $_" -ForegroundColor Green }
} else {
    Write-Host "  Geen COM poorten gevonden (USB-KKL nog niet aangesloten?)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Klaar! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wat nu:" -ForegroundColor Yellow
Write-Host "  1. Sluit USB-KKL aan op laptop"
Write-Host "  2. Check COM poortnummer in Apparaatbeheer"
Write-Host "  3. Dubbelklik 'GP800-Start.bat' op bureaublad"
Write-Host "  4. Open http://<laptop-ip>:8000 op iPhone"
Write-Host ""
Read-Host "Druk Enter om af te sluiten"
