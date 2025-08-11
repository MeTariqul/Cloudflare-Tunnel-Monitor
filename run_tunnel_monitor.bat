@echo off
echo ===================================================
echo    Cloudflare Tunnel Monitor - One-Click Starter
echo ===================================================
echo.

:: Delete unnecessary Ubuntu/Linux files
echo Cleaning up unnecessary files...

:: Delete all shell scripts
if exist "*.sh" (
    del /q *.sh
    echo Deleted shell scripts.
)

:: Delete Linux service files
if exist "tunnel-monitor.service" (
    del /q tunnel-monitor.service
    echo Deleted systemd service file.
)

:: Delete Linux binary files
if exist "cloudflared-linux-amd64.deb" (
    del /q cloudflared-linux-amd64.deb
    echo Deleted Linux Cloudflared package.
)

if exist "cloudflared-linux-amd64" (
    del /q cloudflared-linux-amd64
    echo Deleted Linux Cloudflared binary.
)

:: Delete any other Linux-specific files
if exist "install_selenium.sh" (
    del /q install_selenium.sh
    echo Deleted Linux installation script.
)

echo.
echo ===================================================
echo Starting Cloudflare Tunnel Monitor Web UI...
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

:: Check if cloudflared is available in PATH or exists in current directory
where cloudflared >nul 2>&1
if %errorlevel% equ 0 (
    echo Cloudflared found in PATH. Using system installation.
) else (
    if exist "cloudflared.exe" (
        echo Cloudflared found in current directory.
    ) else (
        echo Cloudflared not found. Downloading...
        if exist "download_cloudflared_windows.bat" (
            call download_cloudflared_windows.bat
        ) else (
            echo Warning: download_cloudflared_windows.bat not found. Please download cloudflared manually.
            echo You can download it from: https://github.com/cloudflare/cloudflared/releases/latest
            pause
        )
    )
)

:: Check if web_ui directory exists
if not exist "web_ui" (
    echo web_ui directory not found. Please make sure you're running this script from the correct location.
    pause
    exit /b 1
)

:: Check if virtual environment exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

:: Start the web UI
echo Starting web UI...
cd web_ui

:: The app.py script will automatically find an available port
echo The web UI will start on the first available port (starting from 5000)...
python app.py

:: Deactivate virtual environment when done
cd ..
call venv\Scripts\deactivate.bat

pause