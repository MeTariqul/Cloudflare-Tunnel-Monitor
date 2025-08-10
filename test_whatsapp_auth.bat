@echo off
REM Script to test WhatsApp Web authentication

echo Testing WhatsApp Web authentication...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    
    REM Install dependencies
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo Using existing virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the test script
echo Running WhatsApp Web authentication test...
echo.
python test_whatsapp_auth.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause