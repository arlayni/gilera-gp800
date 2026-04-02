@echo off
REM GP800 Tool — Windows Setup (run once on laptop)
REM This installs Python dependencies and Claude Code.

echo ============================================
echo  GP800 Tool - Setup for Windows
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Download from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during install!
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Install dependencies
echo.
echo Installing gp800-tool dependencies...
cd /d "%~dp0gp800-tool"
pip install -e ".[kline]" --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
cd /d "%~dp0"

echo [OK] gp800-tool installed

REM Verify
echo.
echo Verifying installation...
gp800-tool --version
if errorlevel 1 (
    echo [ERROR] gp800-tool not found in PATH.
    echo Try: python -m gp800_tool --help
    pause
    exit /b 1
)

echo [OK] gp800-tool works!

REM Check Claude Code
echo.
claude --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Claude Code is not installed.
    echo To install Claude Code:
    echo   npm install -g @anthropic-ai/claude-code
    echo Or download from: https://claude.ai/download
    echo.
    echo You can still use gp800-tool without Claude Code,
    echo but live debugging assistance won't be available.
) else (
    echo [OK] Claude Code found
)

echo.
echo ============================================
echo  Setup complete!
echo  Run start.bat to begin a session.
echo ============================================
pause
