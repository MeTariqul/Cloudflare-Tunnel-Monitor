@echo off
REM Script to update the Chrome path in the tunnel monitor script

REM Check if a Chrome path was provided
if "%~1"=="" (
    echo Error: Please provide the path to Chrome/Chromium
    echo Usage: %0 ^<chrome_path^>
    echo Example: %0 "C:\Program Files\Google\Chrome\Application\chrome.exe"
    exit /b 1
)

REM Get the Chrome path from the command line argument
set CHROME_PATH=%~1

REM Check if the Chrome path exists
if not exist "%CHROME_PATH%" (
    echo Warning: The specified Chrome path does not exist: %CHROME_PATH%
    echo Do you want to continue anyway? (y/n)
    set /p response=
    if /i not "%response%"=="y" (
        echo Operation cancelled.
        exit /b 1
    )
)

echo Updating Chrome path to: %CHROME_PATH%

REM Escape backslashes for PowerShell
set CHROME_PATH_ESCAPED=%CHROME_PATH:\=\\%

REM Update the Chrome path in the script
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(CHROME_PATH = ).*', '$1\"%CHROME_PATH_ESCAPED%\"' | Set-Content 'tunnel_monitor_selenium.py'"

echo Chrome path updated successfully.
echo The tunnel monitor will now use Chrome at: %CHROME_PATH%

pause