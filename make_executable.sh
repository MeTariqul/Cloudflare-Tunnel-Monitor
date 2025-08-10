#!/bin/bash

# Script to make all shell scripts executable

echo "Making all shell scripts executable..."

# Find all .sh files in the current directory and make them executable
found=false
for script in *.sh; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "✅ Made executable: $script"
        found=true
    fi
done

if ! $found; then
    echo "No shell scripts found in the current directory."
fi

echo "Done."