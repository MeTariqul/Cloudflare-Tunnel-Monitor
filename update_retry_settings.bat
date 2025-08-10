@echo off
REM Script to update the retry settings in the tunnel monitor script

REM Check if arguments were provided
if "%~1"=="" (
    echo Error: Please provide both retry count and retry delay
    echo Usage: %0 ^<retry_count^> ^<retry_delay_seconds^>
    echo Example: %0 3 5
    exit /b 1
)

if "%~2"=="" (
    echo Error: Please provide both retry count and retry delay
    echo Usage: %0 ^<retry_count^> ^<retry_delay_seconds^>
    echo Example: %0 3 5
    exit /b 1
)

REM Get the retry count and delay from the command line arguments
set RETRY_COUNT=%~1
set RETRY_DELAY=%~2

REM Validate that the retry count is a positive number
echo %RETRY_COUNT%| findstr /r "^[0-9]*$" >nul
if errorlevel 1 (
    echo Error: Retry count must be a positive number
    exit /b 1
)

REM Validate that the retry delay is a positive number
echo %RETRY_DELAY%| findstr /r "^[0-9]*$" >nul
if errorlevel 1 (
    echo Error: Retry delay must be a positive number
    exit /b 1
)

echo Updating retry settings to: %RETRY_COUNT% attempts with %RETRY_DELAY% seconds delay

REM Update the retry settings in the script
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(MAX_RETRIES = ).*', '$1%RETRY_COUNT%' | Set-Content 'tunnel_monitor_selenium.py'"
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(RETRY_DELAY = ).*', '$1%RETRY_DELAY%' | Set-Content 'tunnel_monitor_selenium.py'"

echo Retry settings updated successfully.
echo The tunnel monitor will now retry %RETRY_COUNT% times with %RETRY_DELAY% seconds delay between attempts

pause