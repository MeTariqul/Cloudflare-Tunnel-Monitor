@echo off
REM Script to update the WhatsApp contact name in the tunnel monitor script

REM Check if a contact name was provided
if "%~1"=="" (
    echo Error: Please provide a WhatsApp contact name
    echo Usage: %0 ^<contact_name^>
    echo Example: %0 "John Doe"
    exit /b 1
)

REM Get the contact name from the command line argument
set CONTACT_NAME=%~1

echo Updating WhatsApp contact name to: %CONTACT_NAME%

REM Update the contact name in the script
powershell -Command "(Get-Content 'tunnel_monitor_selenium.py') -replace '(WHATSAPP_CONTACT = ).*', '$1\"%CONTACT_NAME%\"' | Set-Content 'tunnel_monitor_selenium.py'"

echo WhatsApp contact name updated successfully.
echo The tunnel monitor will now send messages to: %CONTACT_NAME%

pause