@echo off
REM Script to toggle headless mode in the tunnel monitor script

REM Check if the script exists
if not exist "tunnel_monitor_selenium.py" (
    echo Error: tunnel_monitor_selenium.py not found
    exit /b 1
)

REM Check the current headless mode setting
for /f "tokens=3" %%a in ('findstr "HEADLESS_MODE = " tunnel_monitor_selenium.py') do set CURRENT_HEADLESS=%%a

REM Toggle the headless mode
if "%CURRENT_HEADLESS%"=="True" (
    set NEW_HEADLESS=False
    echo Turning HEADLESS MODE OFF
    echo Chrome will now run with a visible browser window
) else (
    set NEW_HEADLESS=True
    echo Turning HEADLESS MODE ON
    echo Chrome will now run in headless mode (no visible window)
)

REM Update the headless mode in the script
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(HEADLESS_MODE = ).*', '$1%NEW_HEADLESS%' | Set-Content 'tunnel_monitor_selenium.py'"

echo Headless mode updated successfully.

if "%NEW_HEADLESS%"=="True" (
    echo IMPORTANT: In headless mode, you'll need to scan the QR code from the saved image.
    echo The QR code will be saved as 'whatsapp_qr.png' in the current directory.
) else (
    echo IMPORTANT: With headless mode off, you'll need to scan the QR code from the browser window.
    echo Make sure you have a display connected if running on a remote system.
)

pause