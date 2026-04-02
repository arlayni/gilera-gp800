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

REM Add Python user Scripts to PATH for this session
for /f "delims=" %%i in ('python -c "import site; print(site.getusersitepackages().replace(chr(92)+chr(39)lib'+chr(92)+'site-packages','Scripts'))"') do set "PYSCRIPTS=%%i"
if not defined PYSCRIPTS (
    for /f "delims=" %%i in ('python -c "import os,sys; print(os.path.join(os.path.dirname(sys.executable),'Scripts'))"') do set "PYSCRIPTS=%%i"
)
set "PATH=%PYSCRIPTS%;%APPDATA%\Python\Python312\Scripts;%APPDATA%\Python\Python311\Scripts;%APPDATA%\Python\Python310\Scripts;%PATH%"
echo [OK] Python Scripts added to PATH

REM Install dependencies
echo.
echo Installing gp800-tool dependencies...
cd /d "%~dp0gp800-tool"
pip install --user -e ".[kline]" --quiet --no-warn-script-location
if errorlevel 1 (
    pip install -e ".[kline]" --quiet --no-warn-script-location
)
cd /d "%~dp0"

echo [OK] gp800-tool installed

REM Verify
echo.
echo Verifying installation...
gp800-tool --version >nul 2>&1
if errorlevel 1 (
    python -m gp800_tool --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] gp800-tool not found.
        pause
        exit /b 1
    )
    echo [OK] gp800-tool works (via python -m gp800_tool)
    echo.
    echo NOTE: Use "python -m gp800_tool" instead of "gp800-tool"
) else (
    echo [OK] gp800-tool works!
)

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
