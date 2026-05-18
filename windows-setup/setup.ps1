# GP800 Windows Setup Script
# Uitvoeren via setup.bat (dubbelklik)
$ErrorActionPreference = "Stop"
$REPO_DIR = Split-Path -Parent $PSScriptRoot
$TOOL_DIR = Join-Path $REPO_DIR "gp800-tool"
$VENV_DIR = Join-Path $REPO_DIR ".venv"
$LOG_DIR = "$env:USERPROFILE\gp800-logs"
$DESKTOP = "$env:USERPROFILE\Desktop"

Write-Host "=== GP800 Windows Setup ===" -ForegroundColor Cyan
Write-Host "Repo:  $REPO_DIR"
Write-Host "Venv:  $VENV_DIR"
Write-Host "Logs:  $LOG_DIR"
Write-Host ""

# --- Python controleren ---
Write-Host "Python controleren..." -ForegroundColor Yellow
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.([0-9]+)") {
            $python = $cmd
            Write-Host "  Gevonden: $ver" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host "Python 3.10+ niet gevonden!" -ForegroundColor Red
    Write-Host "Installeer Python van python.org en vink 'Add Python to PATH' aan."
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

# --- 32-bit check ---
$arch = & $python -c "import struct; print(struct.calcsize('P') * 8)"
Write-Host "  Architectuur: $arch-bit"

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

$pip  = Join-Path $VENV_DIR "Scripts\pip.exe"
$tool = Join-Path $VENV_DIR "Scripts\gp800-tool.exe"

# --- gp800-tool installeren ---
Write-Host ""
Write-Host "gp800-tool installeren..." -ForegroundColor Yellow
& $pip install --only-binary :all: -e "$TOOL_DIR[api,kline]" -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Volledige installatie mislukt, installeren zonder dashboard..." -ForegroundColor Yellow
    & $pip install -e "$TOOL_DIR[kline]" -q
    Write-Host "  Geinstalleerd (zonder dashboard)" -ForegroundColor Yellow
    Write-Host "  CLI commando's werken wel: validate, quickcheck, compare, dtc" -ForegroundColor Green
} else {
    $ver = & $tool --version
    Write-Host "  Geinstalleerd: $ver" -ForegroundColor Green
}

# --- Log directory ---
Write-Host ""
Write-Host "Log directory aanmaken..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
Write-Host "  $LOG_DIR" -ForegroundColor Green

# --- Startscript naar bureaublad kopiëren ---
Write-Host ""
Write-Host "Startscript naar bureaublad..." -ForegroundColor Yellow
$src = Join-Path $PSScriptRoot "start-dashboard.bat"
$dst = Join-Path $DESKTOP "GP800-Start.bat"
Copy-Item $src $dst -Force
Write-Host "  Gekopieerd naar: $dst" -ForegroundColor Green

# --- Beschikbare COM poorten ---
Write-Host ""
Write-Host "=== Beschikbare COM poorten ===" -ForegroundColor Cyan
Add-Type -AssemblyName System.IO.Ports
$ports = [System.IO.Ports.SerialPort]::GetPortNames()
if ($ports) {
    foreach ($p in $ports) { Write-Host "  $p" -ForegroundColor Green }
} else {
    Write-Host "  Geen COM poorten gevonden (USB-KKL nog niet aangesloten?)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Klaar! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Volgende stappen:" -ForegroundColor Yellow
Write-Host "  1. Sluit USB-KKL adapter aan op laptop"
Write-Host "  2. Open Apparaatbeheer, kijk bij Poorten welk COM nummer"
Write-Host "  3. Pas het COM nummer aan in GP800-Start.bat op je bureaublad"
Write-Host "  4. Dubbelklik GP800-Start.bat"
Write-Host ""
Read-Host "Druk Enter om af te sluiten"
