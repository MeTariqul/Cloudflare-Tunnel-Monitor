@echo off
REM Script to update the WhatsApp message template in the tunnel monitor script

REM Check if a message template was provided
if "%~1"=="" (
    echo Error: Please provide a message template
    echo Usage: %0 ^<message_template^>
    echo Example: %0 "Your tunnel link is: {link}"
    echo Note: Use {link} as a placeholder for the tunnel URL
    exit /b 1
)

REM Get the message template from the command line arguments
set MESSAGE_TEMPLATE=%*

REM Check if the template contains the {link} placeholder
echo %MESSAGE_TEMPLATE% | findstr /C:"{link}" > nul
if errorlevel 1 (
    echo Warning: Your message template does not contain the {link} placeholder.
    echo The tunnel URL will not be included in the message.
    echo Do you want to continue? (y/n)
    set /p response=
    if /i not "%response%"=="y" (
        echo Operation cancelled.
        exit /b 1
    )
)

echo Updating WhatsApp message template to: %MESSAGE_TEMPLATE%

REM Update the message template in the script
powershell -Command "$template = '%MESSAGE_TEMPLATE%'; $template = $template -replace '\\', '\\\\'; (Get-Content 'tunnel_monitor_selenium.py') -replace '(MESSAGE_TEMPLATE = ).*', ('$1"' + $template + '"') | Set-Content 'tunnel_monitor_selenium.py'"

echo WhatsApp message template updated successfully.
echo The tunnel monitor will now send messages with the template: %MESSAGE_TEMPLATE%

pause