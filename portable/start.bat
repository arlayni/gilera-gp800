@echo off
REM GP800 Tool — Start Session (Windows)
REM Opens Claude Code in the GP800 project directory.
REM Claude Code can then run gp800-tool commands directly.

echo ============================================
echo  GP800 Tool - Live Session
echo ============================================
echo.

REM Detect USB-KKL adapter
echo Detecting serial ports...
python -c "import serial.tools.list_ports; [print(f'  {p.device}: {p.description}') for p in serial.tools.list_ports.comports()]" 2>nul
if errorlevel 1 (
    echo   [Could not list ports — pyserial may not be installed]
)
echo.

REM Check if Claude Code is available
claude --version >nul 2>&1
if errorlevel 1 (
    echo Claude Code is not installed — starting in manual mode.
    echo You can run gp800-tool commands directly:
    echo.
    echo   gp800-tool connect COM3
    echo   gp800-tool read COM3 backup.bin
    echo   gp800-tool dtc COM3
    echo   gp800-tool live COM3
    echo   gp800-tool flash COM3 modified.bin
    echo.
    cd /d "%~dp0"
    cmd /k "echo Ready. Type gp800-tool --help for all commands."
) else (
    echo Starting Claude Code...
    echo Claude can run gp800-tool commands, analyze ECU data,
    echo and guide you through diagnostics in real-time.
    echo.
    cd /d "%~dp0"
    claude
)
