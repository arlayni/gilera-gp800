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
    Write-Host "Installeer Python van python.org en vink Add Python to PATH aan."
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

# --- 32-bit of 64-bit ---
$arch = & $python -c "import struct; print(struct.calcsize('P') * 8)"
Write-Host "  Architectuur: $arch bit"

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

# --- gp800-tool core installeren ---
Write-Host ""
Write-Host "gp800-tool installeren..." -ForegroundColor Yellow
& $pip install -e "$TOOL_DIR" -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installatie mislukt!" -ForegroundColor Red
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}
Write-Host "  Core geinstalleerd" -ForegroundColor Green

# --- Dashboard dependencies ---
Write-Host ""
if ($arch -eq "64") {
    Write-Host "64-bit systeem - FastAPI installeren..." -ForegroundColor Yellow
    & $pip install "fastapi>=0.110" "uvicorn[standard]>=0.29" "python-multipart>=0.0.9" "pyserial>=3.5" "flask>=2.0" -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  FastAPI mislukt, terugvallen op Flask..." -ForegroundColor Yellow
        & $pip install "flask>=2.0" "python-multipart>=0.0.9" "pyserial>=3.5" -q
        Write-Host "  Flask geinstalleerd" -ForegroundColor Green
    } else {
        Write-Host "  FastAPI geinstalleerd" -ForegroundColor Green
    }
} else {
    Write-Host "32-bit systeem - Flask installeren..." -ForegroundColor Yellow
    & $pip install "flask>=2.0" "python-multipart>=0.0.9" "pyserial>=3.5" -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Flask installatie mislukt!" -ForegroundColor Red
    } else {
        Write-Host "  Flask geinstalleerd" -ForegroundColor Green
    }
}

$ver = & $tool --version 2>$null
if ($ver) { Write-Host "  gp800-tool: $ver" -ForegroundColor Green }

# --- Log directory ---
Write-Host ""
Write-Host "Log directory aanmaken..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
Write-Host "  $LOG_DIR" -ForegroundColor Green

# --- Startscript op bureaublad ---
Write-Host ""
Write-Host "Startscript naar bureaublad..." -ForegroundColor Yellow
$dst = Join-Path $DESKTOP "GP800-Start.bat"
$toolExe = Join-Path $VENV_DIR "Scripts\gp800-tool.exe"
$activateCmd = Join-Path $VENV_DIR "Scripts\activate.bat"
$content = "@echo off`r`ntitle GP800 Dashboard`r`necho.`r`necho === GP800 Dashboard ===`r`necho Poort: COM3`r`necho.`r`nfor /f `"tokens=2 delims=:`" %%a in ('ipconfig ^| findstr /i `"IPv4`"') do (set IP=%%a & goto :found)`r`n:found`r`nset IP=%IP: =%`r`necho Open op iPhone: http://%IP%:8000`r`necho Stoppen: Ctrl+C`r`necho.`r`ncall `"$activateCmd`"`r`n`"$toolExe`" serve COM3`r`npause"
Set-Content -Path $dst -Value $content -Encoding ASCII
Write-Host "  Aangemaakt: $dst" -ForegroundColor Green

# --- COM poorten ---
Write-Host ""
Write-Host "=== Beschikbare COM poorten ===" -ForegroundColor Cyan
$ports = Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -match "COM\d+" } | ForEach-Object { $_.Name }
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
Write-Host "  3. Pas COM nummer aan in GP800-Start.bat op bureaublad"
Write-Host "  4. Dubbelklik GP800-Start.bat"
Write-Host ""
Read-Host "Druk Enter om af te sluiten"
