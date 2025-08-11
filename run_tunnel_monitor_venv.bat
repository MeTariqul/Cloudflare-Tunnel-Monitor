@echo off
echo Starting Cloudflare Tunnel Monitor...

:: Check if virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo Using existing virtual environment...
    call venv\Scripts\activate.bat
)

:: Run the tunnel monitor
echo Running tunnel monitor...
echo.
echo Starting the monitoring process...
echo The tunnel URL will be displayed in the console when available.
echo.
python tunnel_monitor_selenium.py

:: Deactivate virtual environment when done
call venv\Scripts\deactivate.bat