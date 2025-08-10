#!/bin/bash

# Script to download the latest version of cloudflared

echo "Downloading the latest version of cloudflared..."

# Determine the operating system
if [ "$(uname)" == "Linux" ]; then
    OS="linux"
elif [ "$(uname)" == "Darwin" ]; then
    OS="darwin"
else
    echo "Unsupported operating system: $(uname)"
    echo "This script supports Linux and macOS only."
    echo "For Windows, please download manually from:"
    echo "https://github.com/cloudflare/cloudflared/releases/latest"
    exit 1
fi

# Determine the architecture
ARCH=$(uname -m)
if [ "$ARCH" == "x86_64" ]; then
    ARCH="amd64"
elif [ "$ARCH" == "aarch64" ] || [ "$ARCH" == "arm64" ]; then
    ARCH="arm64"
else
    echo "Unsupported architecture: $ARCH"
    echo "This script supports x86_64 (amd64) and arm64 only."
    exit 1
fi

# Download the executable
echo "Downloading cloudflared for $OS-$ARCH..."
if [ "$OS" == "linux" ]; then
    # For Linux, download both the .deb package and the executable
    echo "Downloading .deb package..."
    curl -L --output cloudflared-${OS}-${ARCH}.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-${OS}-${ARCH}.deb
    
    echo "Downloading executable..."
    curl -L --output cloudflared-${OS}-${ARCH} https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-${OS}-${ARCH}
    chmod +x cloudflared-${OS}-${ARCH}
    
    echo "Downloaded:"
    echo "- cloudflared-${OS}-${ARCH}.deb (package for system-wide installation)"
    echo "- cloudflared-${OS}-${ARCH} (executable)"
    
    echo "\nTo install system-wide:"
    echo "sudo dpkg -i cloudflared-${OS}-${ARCH}.deb"
    
    echo "\nOr use the executable directly:"
    echo "./cloudflared-${OS}-${ARCH} tunnel --url http://localhost:8080"
else
    # For macOS, just download the executable
    curl -L --output cloudflared-${OS}-${ARCH} https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-${OS}-${ARCH}
    chmod +x cloudflared-${OS}-${ARCH}
    
    echo "Downloaded: cloudflared-${OS}-${ARCH}"
    echo "\nTo use the executable:"
    echo "./cloudflared-${OS}-${ARCH} tunnel --url http://localhost:8080"
fi

echo "\nDownload completed successfully."