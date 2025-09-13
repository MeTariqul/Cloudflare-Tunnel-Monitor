@echo off
:: Cloudflare Tunnel Monitor - Universal Launcher
:: This script handles all setup and execution tasks

setlocal enabledelayedexpansion

echo ================================
echo Cloudflare Tunnel Monitor v2.0
echo ================================

:MENU
echo.
echo Choose an option:
echo [1] Start Web UI
echo [2] Download Cloudflared
echo [3] Check Status
echo [4] Run Monitor (Command Line)
echo [5] Install Dependencies
echo [6] Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto START_WEB
if "%choice%"=="2" goto DOWNLOAD_CF
if "%choice%"=="3" goto CHECK_STATUS
if "%choice%"=="4" goto RUN_MONITOR
if "%choice%"=="5" goto INSTALL_DEPS
if "%choice%"=="6" goto EXIT

echo Invalid choice. Please try again.
goto MENU

:START_WEB
echo Starting Web UI...
python app.py
goto MENU

:DOWNLOAD_CF
echo Downloading Cloudflared...
curl -L --output cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
echo Cloudflared downloaded successfully!
goto MENU

:CHECK_STATUS
echo Checking tunnel status...
tasklist /fi "imagename eq cloudflared.exe" /fo table | find /i "cloudflared.exe" >nul
if %errorlevel% equ 0 (
    echo Cloudflared is RUNNING
) else (
    echo Cloudflared is NOT RUNNING
)
goto MENU

:RUN_MONITOR
echo Starting command line monitor...
python tunnel_monitor.py
goto MENU

:INSTALL_DEPS
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo Dependencies installed!
goto MENU

:EXIT
echo Goodbye!
exit /b 0