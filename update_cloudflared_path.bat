@echo off
REM Script to update the cloudflared path in the tunnel monitor script

REM Check if a cloudflared path was provided
if "%~1"=="" (
    echo Error: Please provide the path to cloudflared
    echo Usage: %0 ^<cloudflared_path^>
    echo Example: %0 "C:\Users\username\cloudflared.exe"
    exit /b 1
)

REM Get the cloudflared path from the command line argument
set CLOUDFLARED_PATH=%~1

REM Check if the cloudflared path exists
if not exist "%CLOUDFLARED_PATH%" (
    echo Warning: The specified cloudflared path does not exist: %CLOUDFLARED_PATH%
    echo Do you want to continue anyway? (y/n)
    set /p response=
    if /i not "%response%"=="y" (
        echo Operation cancelled.
        exit /b 1
    )
)

echo Updating cloudflared path to: %CLOUDFLARED_PATH%

REM Escape backslashes for PowerShell
set CLOUDFLARED_PATH_ESCAPED=%CLOUDFLARED_PATH:\=\\%

REM Update the cloudflared path in the script
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(CLOUDFLARED_PATH = ).*', '$1\"%CLOUDFLARED_PATH_ESCAPED%\"' | Set-Content 'tunnel_monitor_selenium.py'"

echo cloudflared path updated successfully.
echo The tunnel monitor will now use cloudflared at: %CLOUDFLARED_PATH%

pause