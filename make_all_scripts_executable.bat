@echo off
REM This batch script creates a simple shell script that will make all .sh files executable
REM Useful when transferring files from Windows to Linux systems

echo Creating make_all_scripts_executable.sh...

echo #!/bin/bash > make_all_scripts_executable.sh
echo # Script to make all shell scripts executable >> make_all_scripts_executable.sh
echo. >> make_all_scripts_executable.sh
echo echo "Making all shell scripts executable..." >> make_all_scripts_executable.sh
echo. >> make_all_scripts_executable.sh
echo # Find all .sh files in the current directory and make them executable >> make_all_scripts_executable.sh
echo find . -type f -name "*.sh" -exec chmod +x {} \; >> make_all_scripts_executable.sh
echo. >> make_all_scripts_executable.sh
echo echo "Done! All shell scripts are now executable." >> make_all_scripts_executable.sh

echo Created make_all_scripts_executable.sh
echo.
echo When you transfer files to a Linux system, run this batch file first
echo to create the make_all_scripts_executable.sh script, then run:
echo chmod +x make_all_scripts_executable.sh
echo ./make_all_scripts_executable.sh

pause