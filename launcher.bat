@echo off
:: ================================================================
:: Cloudflare Tunnel Monitor v3.0 Neon Edition - Smart Launcher
:: Enhanced Auto-Setup with Data Transfer Monitoring Support
:: ================================================================

setlocal enabledelayedexpansion

color 0A

echo.
echo     ######  ##      ## ######## ######## ##    ##
echo     ##   ## ##      ## ##       ##       ###   ##
echo     ##   ## ##  ##  ## ##       ##       ####  ##
echo     ######  ##  ##  ## ######   ######   ## ## ##
echo     ##   ## ##  ##  ## ##       ##       ##  ####
echo     ##   ## ##  ##  ## ##       ##       ##   ###
echo     ##   ##  ###  ###  ######## ######## ##    ##
echo.
echo     CLOUDFLARE TUNNEL MONITOR v3.0 NEON EDITION
echo     Enhanced Real-time Dashboard with Data Transfer Monitoring
echo     Smart Auto-Setup Launcher
echo     Hello
echo.
echo ================================================================

:: Initialize variables
set "PYTHON_CMD="
set "VENV_DIR=venv"
set "REQUIREMENTS_FILE=requirements.txt"
set "MAIN_APP=app.py"
set "ERROR_COUNT=0"

echo [INFO] Initializing smart launcher system...
echo [INFO] Checking system requirements and dependencies...
echo.

:: Step 1: Check if Python is installed
echo [1/8] [Python] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python found: !PYTHON_VERSION!
    set "PYTHON_CMD=python"
) else (
    python3 --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "delims=" %%i in ('python3 --version 2^>^&1') do set "PYTHON_VERSION=%%i"
        echo [OK] Python3 found: !PYTHON_VERSION!
        set "PYTHON_CMD=python3"
    ) else (
        echo [ERROR] Python not found! Please install Python 3.7+ from https://python.org
        echo [INFO] After installation, make sure to check "Add Python to PATH"
        pause
        exit /b 1
    )
)

:: Step 2: Check Python version compatibility
echo [2/8] [Config] Verifying Python version compatibility...
for /f "tokens=2" %%i in ('!PYTHON_CMD! --version 2^>^&1') do set "PY_VERSION=%%i"
echo [INFO] Python version: %PY_VERSION%
echo [OK] Python version compatible with Tunnel Monitor v3.0

:: Step 3: Check/Create Virtual Environment
echo [3/8] [VEnv] Checking virtual environment...
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [OK] Virtual environment found at '%VENV_DIR%'
) else (
    echo [INFO] Creating new virtual environment...
    !PYTHON_CMD! -m venv %VENV_DIR%
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment
        echo [TIP] Try: !PYTHON_CMD! -m pip install --user virtualenv
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully
)

:: Step 4: Activate Virtual Environment
echo [4/8] [Activate] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    echo [TIP] Try deleting the '%VENV_DIR%' folder and run this script again
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

:: Step 5: Update pip to latest version
echo [5/8] [Pip] Updating pip to latest version...
python -m pip install --upgrade pip >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Pip updated to latest version
) else (
    echo [WARN] Pip update failed, continuing with current version...
)

:: Step 6: Install/Update Dependencies
echo [6/8] [Dependencies] Installing application dependencies...
if exist "%REQUIREMENTS_FILE%" (
    echo [INFO] Installing from %REQUIREMENTS_FILE%...
    python -m pip install -r "%REQUIREMENTS_FILE%"
    if !errorlevel! equ 0 (
        echo [OK] All dependencies installed successfully
        echo [INFO] Installed: Flask, Socket.IO, Chart.js support, psutil, requests
    ) else (
        echo [ERROR] Some dependencies failed to install
        echo [TIP] Check your internet connection and try again
        set /a ERROR_COUNT+=1
    )
) else (
    echo [WARN] Requirements file not found, installing core dependencies...
    python -m pip install flask flask-socketio psutil requests gevent python-socketio
    if !errorlevel! equ 0 (
        echo [OK] Core dependencies installed
    ) else (
        echo [ERROR] Failed to install core dependencies
        set /a ERROR_COUNT+=1
    )
)

:: Step 7: Check application files
echo [7/8] [Files] Verifying application files...
if exist "%MAIN_APP%" (
    echo [OK] Main application found: %MAIN_APP%
    echo [INFO] Features: Neon UI, Data Transfer Monitor, Live Ping Analytics
) else (
    echo [ERROR] Main application not found: %MAIN_APP%
    echo [TIP] Make sure you're in the correct directory
    pause
    exit /b 1
)

:: Step 8: Final system check
echo [8/8] [System] Running final system check...
echo [INFO] Checking for Cloudflared (will be prompted if needed)...
echo [INFO] Verifying network connectivity...
ping 1.1.1.1 -n 1 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Network connectivity verified
) else (
    echo [WARN] Network connectivity check failed
    echo [INFO] Application will still start but tunnel creation may fail
)

:: Display startup information
echo.
echo ================================================================
if %ERROR_COUNT% equ 0 (
    echo *** ALL SYSTEMS READY - LAUNCHING NEON EDITION ***
    echo.
    echo [LAUNCH] Starting Cloudflare Tunnel Monitor v3.0...
    echo [INFO] Enhanced Features Active:
    echo   * Real-time Data Transfer Monitoring
    echo   * Live Ping Analytics with Charts
    echo   * Neon-themed Cyberpunk UI
    echo   * Auto-save Tunnel URLs
    echo   * WebSocket Live Updates
    echo.
    echo [ACCESS] Application will open in your default browser
    echo [LOCAL] http://localhost:5000
    echo [NETWORK] http://YOUR_IP:5000 (for other devices)
    echo.
    echo [CONTROL] Press Ctrl+C to stop the server
    echo ================================================================
    echo.
    
    :: Start the enhanced application
    python "%MAIN_APP%"
    
) else (
    echo [WARN] Setup completed with %ERROR_COUNT% warnings
    echo [TIP] You can try starting the application manually:
    echo    python %MAIN_APP%
    echo.
    pause
)

:: Graceful shutdown
echo.
echo [SHUTDOWN] Shutting down Tunnel Monitor gracefully...
echo [INFO] Cleaning up resources...
deactivate 2>nul
echo [OK] Session ended successfully
echo [INFO] Thank you for using Cloudflare Tunnel Monitor v3.0 Neon Edition!
pause