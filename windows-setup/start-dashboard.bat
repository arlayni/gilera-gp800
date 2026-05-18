@echo off
:: GP800 Dashboard starten — dubbelklik na setup
title GP800 Dashboard

set REPO_DIR=%~dp0..
set VENV=%REPO_DIR%\.venv\Scripts

:: COM poort instellen — pas aan indien nodig
set PORT=COM3

echo.
echo === GP800 Dashboard ===
echo Poort: %PORT%
echo.

:: IP adres tonen voor iPhone
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%
echo Open op iPhone: http://%IP%:8000
echo Stoppen: Ctrl+C
echo.

call "%VENV%\activate.bat"
gp800-tool serve %PORT%

pause
