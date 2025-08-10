@echo off
echo Starting Cloudflare Tunnel Monitor GUI...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.6 or higher.
    pause
    exit /b 1
)

:: Check if virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if requirements are installed
pip show selenium >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install selenium undetected-chromedriver requests
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies.
        pause
        exit /b 1
    )
)

:: Run the GUI application
echo Starting GUI application...
python tunnel_monitor_gui.py

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause