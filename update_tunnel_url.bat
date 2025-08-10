@echo off
REM Script to update the tunnel URL in the tunnel monitor script

REM Check if a URL was provided
if "%~1"=="" (
    echo Error: Please provide a URL to tunnel
    echo Usage: %0 ^<url^>
    echo Example: %0 http://localhost:8080
    exit /b 1
)

REM Get the URL from the command line argument
set URL=%~1

echo Updating tunnel URL to: %URL%

REM Update the URL in the script
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(TUNNEL_URL = ).*', '$1\"%URL%\"' | Set-Content 'tunnel_monitor_selenium.py'"
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(\[cloudflared_cmd, \"tunnel\", \"--url\", ).*\]', '$1\"%URL%\"]' | Set-Content 'tunnel_monitor_selenium.py'"

echo Tunnel URL updated successfully.
echo The tunnel monitor will now create a tunnel to: %URL%

pause