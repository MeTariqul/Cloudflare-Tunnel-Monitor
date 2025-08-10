@echo off
REM Script to update the Chrome user data directory

echo Updating Chrome user data directory...

REM Check if a directory was provided
if "%~1"=="" (
    echo No directory provided. Will use default or prompt for input.
    set DIR_PATH=
) else (
    echo Using provided directory: %~1
    set DIR_PATH=%~1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Using existing virtual environment...
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the update script
if "%DIR_PATH%"=="" (
    python update_user_data_dir.py
) else (
    python update_user_data_dir.py "%DIR_PATH%"
)

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause