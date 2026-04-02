@echo off
REM =============================================
REM  GP800 Tool — Dubbelklik en klaar!
REM  Installeert automatisch, opent GUI + Claude Code
REM =============================================

title GP800 Tool - Starting...
cd /d "%~dp0"

REM Fix PATH voor Python Scripts
set "PATH=%APPDATA%\Python\Python312\Scripts;%APPDATA%\Python\Python311\Scripts;%APPDATA%\Python\Python310\Scripts;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo =============================================
    echo  Python is niet geinstalleerd!
    echo  Download van: https://www.python.org/downloads/
    echo  BELANGRIJK: Vink "Add Python to PATH" aan!
    echo =============================================
    pause
    exit /b 1
)

REM Auto-install als gp800-tool nog niet werkt
python -m gp800_tool.cli --version >nul 2>&1
if errorlevel 1 (
    echo Eerste keer? Installeren...
    cd /d "%~dp0gp800-tool"
    pip install --user -e ".[kline]" --quiet --no-warn-script-location 2>nul
    if errorlevel 1 pip install -e ".[kline]" --quiet --no-warn-script-location 2>nul
    cd /d "%~dp0"
    echo Installatie compleet!
)

REM Start GUI op de achtergrond
echo Starting GP800 GUI...
start "" pythonw -m gp800_tool.gui 2>nul
if errorlevel 1 start "" python -m gp800_tool.gui

REM Start Claude Code in terminal
echo.
echo =============================================
echo  GP800 Tool draait!
echo  GUI: geopend in apart venster
echo  Claude Code: hieronder (als geinstalleerd)
echo =============================================
echo.

claude --version >nul 2>&1
if errorlevel 1 (
    echo Claude Code is niet geinstalleerd op deze PC.
    echo Je kunt gp800-tool gebruiken via de GUI of deze terminal:
    echo   gp800-tool --help
    echo.
    cmd /k "title GP800 Terminal"
) else (
    title GP800 + Claude Code
    claude
)
