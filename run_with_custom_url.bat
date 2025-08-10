@echo off
REM Script to run the tunnel monitor with a custom URL

REM Check if a URL was provided
if "%~1"=="" (
    echo Error: Please provide a URL to tunnel
    echo Usage: %0 ^<url^>
    echo Example: %0 http://localhost:8080
    exit /b 1
)

REM Get the URL from the command line argument
set URL=%~1

echo Starting Cloudflare Tunnel Monitor with custom URL: %URL%

REM Create a temporary copy of the script with the custom URL
set TEMP_SCRIPT=tunnel_monitor_custom.py

REM Copy the original script
copy tunnel_monitor_selenium.py "%TEMP_SCRIPT%" > nul

REM Update the URL in the script
powershell -Command "(Get-Content '%TEMP_SCRIPT%') -replace '(TUNNEL_URL = ).*', '$1\"%URL%\"' | Set-Content '%TEMP_SCRIPT%'"
powershell -Command "(Get-Content '%TEMP_SCRIPT%') -replace '(\[cloudflared_cmd, \"tunnel\", \"--url\", ).*\]', '$1\"%URL%\"]' | Set-Content '%TEMP_SCRIPT%'"

echo Updated script with custom URL

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

REM Run the modified script
echo Running tunnel monitor with custom URL...
echo.
echo IMPORTANT: You will need to scan the QR code to authenticate WhatsApp Web
echo when the browser window opens.
echo.
python "%TEMP_SCRIPT%"

REM Clean up
del "%TEMP_SCRIPT%"

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause