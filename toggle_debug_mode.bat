@echo off
REM Script to toggle debug mode in the tunnel monitor script

REM Check if the script exists
if not exist "tunnel_monitor_selenium.py" (
    echo Error: tunnel_monitor_selenium.py not found
    exit /b 1
)

REM Check the current debug mode setting
for /f "tokens=3" %%a in ('findstr "DEBUG_MODE = " tunnel_monitor_selenium.py') do set CURRENT_DEBUG=%%a

REM Toggle the debug mode
if "%CURRENT_DEBUG%"=="True" (
    set NEW_DEBUG=False
    echo Turning DEBUG MODE OFF
) else (
    set NEW_DEBUG=True
    echo Turning DEBUG MODE ON
)

REM Update the debug mode in the script
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(DEBUG_MODE = ).*', '$1%NEW_DEBUG%' | Set-Content 'tunnel_monitor_selenium.py'"

echo Debug mode updated successfully.

if "%NEW_DEBUG%"=="True" (
    echo The tunnel monitor will now run in debug mode with additional logging.
    echo This will help diagnose issues but may generate larger log files.
) else (
    echo The tunnel monitor will now run in normal mode with standard logging.
)

pause