@echo off
:: GP800 Windows Setup — dubbelklik om te starten
:: Werkt op Windows 10 32-bit
title GP800 Setup

echo.
echo === GP800 Windows Setup ===
echo.

:: PowerShell script starten met juiste rechten
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0setup.ps1'"

if errorlevel 1 (
    echo.
    echo Setup mislukt. Controleer de foutmelding hierboven.
    pause
)
