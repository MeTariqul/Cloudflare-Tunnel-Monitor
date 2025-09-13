@echo off
echo Starting Cloudflare Tunnel Monitor Web UI...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

:: Check if app.py exists
if not exist "app.py" (
    echo app.py not found. Please make sure you're running this script from the correct location.
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
:: Set auto_open_browser flag to true
set FLASK_AUTO_OPEN_BROWSER=1
python app.py

:: Deactivate virtual environment when done
call venv\Scripts\deactivate.bat

pause