@echo off
REM Script to download the latest cloudflared executable for Windows

echo Downloading the latest cloudflared for Windows...

REM Create a temporary directory for downloads
if not exist "temp" mkdir temp

REM Get the latest release URL
echo Fetching the latest release information...
powershell -Command "$latestRelease = Invoke-RestMethod -Uri 'https://api.github.com/repos/cloudflare/cloudflared/releases/latest'; $asset = $latestRelease.assets | Where-Object { $_.name -like '*windows-amd64.exe' } | Select-Object -First 1; $asset.browser_download_url | Out-File -FilePath 'temp\download_url.txt'"

REM Read the download URL from the file
set /p DOWNLOAD_URL=<temp\download_url.txt

if "%DOWNLOAD_URL%"=="" (
    echo Failed to get download URL. Please check your internet connection.
    goto :cleanup
)

echo Download URL: %DOWNLOAD_URL%

REM Download the executable
echo Downloading cloudflared...
powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile 'temp\cloudflared.exe'"

if not exist "temp\cloudflared.exe" (
    echo Download failed. Please try again or download manually from:
    echo https://github.com/cloudflare/cloudflared/releases/latest
    goto :cleanup
)

REM Copy to the project directory
echo Copying cloudflared to the project directory...
copy "temp\cloudflared.exe" "cloudflared.exe" /Y

echo.
echo cloudflared has been downloaded successfully!
echo Location: %CD%\cloudflared.exe

REM Update the cloudflared path in the script
echo Updating the cloudflared path in the tunnel monitor script...
powershell -Command "$path = '%CD%\cloudflared.exe'; $path = $path -replace '\\', '\\\\'; (Get-Content 'tunnel_monitor_selenium.py') -replace '(CLOUDFLARED_PATH = ).*', ('$1"' + $path + '"') | Set-Content 'tunnel_monitor_selenium.py'"

echo The tunnel monitor script has been updated to use the downloaded cloudflared.

:cleanup
REM Clean up temporary files
echo Cleaning up temporary files...
if exist "temp\download_url.txt" del "temp\download_url.txt"
if exist "temp\cloudflared.exe" del "temp\cloudflared.exe"
if exist "temp" rmdir "temp"

pause