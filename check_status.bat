@echo off
REM Script to check the status of the tunnel monitor on Windows

echo Checking Cloudflare Tunnel Monitor status...

REM Check if running as a background process
if exist "tunnel_monitor.pid" (
    set /p PID=<tunnel_monitor.pid
    
    REM Check if the process is running
    tasklist /FI "PID eq %PID%" 2>nul | find "%PID%" >nul
    if not errorlevel 1 (
        echo ✅ Tunnel monitor is running as a background process with PID: %PID%
        
        REM Try to get process start time
        for /f "tokens=1,2" %%a in ('wmic process where "ProcessId=%PID%" get CreationDate /format:list ^| findstr "="') do (
            echo    Started: %%b
        )
    ) else (
        echo ❌ Tunnel monitor is not running, but PID file exists.
        echo    The process with PID %PID% is no longer active.
        echo    You may want to remove the stale PID file: del tunnel_monitor.pid
    )
)

REM Check for running Python processes
echo.
echo Checking for Python processes running tunnel_monitor_selenium.py...
tasklist /FI "IMAGENAME eq python.exe" /FO LIST | findstr /i "python"

REM Check for running cloudflared processes
echo.
echo Checking for cloudflared processes...
tasklist /FI "IMAGENAME eq cloudflared.exe" /FO LIST | findstr /i "cloudflared"

REM Check for recent log files
if exist "logs" (
    echo.
    echo Checking for recent log files...
    
    REM List the most recent log files
    dir /b /o-d /a-d "logs\tunnel_monitor_*.log" 2>nul
    
    if not errorlevel 1 (
        echo ✅ Recent log files found:
        for /f "delims=" %%i in ('dir /b /o-d /a-d "logs\tunnel_monitor_*.log" 2^>nul') do (
            echo    %%i
            echo    Last few lines:
            powershell -Command "Get-Content 'logs\%%i' -Tail 5 | ForEach-Object { '     ' + $_ }"
            echo.
            goto :found_logs
        )
        :found_logs
    ) else (
        echo ❌ No recent log files found in the logs directory
    )
)

REM If nothing is running, provide instructions
tasklist /FI "IMAGENAME eq python.exe" | find "python.exe" >nul
if errorlevel 1 (
    tasklist /FI "IMAGENAME eq cloudflared.exe" | find "cloudflared.exe" >nul
    if errorlevel 1 (
        echo.
        echo ❌ Tunnel monitor is not running
        echo.
        echo To start it, use one of these methods:
        echo 1. Run directly: run_tunnel_monitor_venv.bat
        echo 2. Run with custom URL: run_with_custom_url.bat http://localhost:8080
    )
)

echo.
echo Status check completed.

pause