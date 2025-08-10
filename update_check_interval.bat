@echo off
REM Script to update the internet check interval in the tunnel monitor script

REM Check if an interval was provided
if "%~1"=="" (
    echo Error: Please provide a check interval in seconds
    echo Usage: %0 ^<interval_seconds^>
    echo Example: %0 30
    exit /b 1
)

REM Get the interval from the command line argument
set INTERVAL=%~1

REM Validate that the interval is a positive number
echo %INTERVAL%| findstr /r "^[0-9]*$" >nul
if errorlevel 1 (
    echo Error: Interval must be a positive number
    exit /b 1
)

echo Updating internet check interval to: %INTERVAL% seconds

REM Update the interval in the script
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(CHECK_INTERVAL = ).*', '$1%INTERVAL%' | Set-Content 'tunnel_monitor_selenium.py'"

echo Internet check interval updated successfully.
echo The tunnel monitor will now check internet connectivity every %INTERVAL% seconds

pause