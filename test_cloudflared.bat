@echo off
REM Script to test cloudflared functionality

echo Testing cloudflared functionality...

REM Check if a URL was provided
if "%~1"=="" (
    echo Using default URL: http://localhost:8080
    set URL=http://localhost:8080
) else (
    echo Using provided URL: %~1
    set URL=%~1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    
    REM Install dependencies
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install requests
) else (
    echo Using existing virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the test script
echo Running cloudflared test...
echo.
python test_cloudflared.py "%URL%"

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause