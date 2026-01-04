#!/bin/bash

# setup.sh - Install dependencies for Auto-Cal
# This script installs ArgyllCMS across different platforms (macOS/Linux)

OS_TYPE="$(uname -s)"
echo "Detected OS: $OS_TYPE"

case "${OS_TYPE}" in
    Darwin*)
        echo "Installing for macOS..."
        if ! command -v brew &> /dev/null; then
            echo "Error: Homebrew not found. Install it from https://brew.sh/"
            exit 1
        fi
        HOMEBREW_NO_AUTO_UPDATE=1 brew install argyll-cms
        ;;
    Linux*)
        echo "Installing for Linux..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y argyll
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y argyllcms
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm argyllcms
        else
            echo "Error: Unsupported Linux distribution. Please install 'argyll' manually."
            exit 1
        fi
        ;;
    CYGWIN*|MINGW32*|MSYS*|MINGW*)
        echo "Windows detected. Please download and install ArgyllCMS from:"
        echo "https://www.argyllcms.com/downloadwin.html"
        echo "Ensure 'bin' folder is in your PATH."
        exit 0
        ;;
    *)
        echo "Error: Unsupported OS type: ${OS_TYPE}"
        exit 1
        ;;
esac

if command -v dispcal &> /dev/null; then
    echo "✓ ArgyllCMS ready"
else
    echo "✗ Failed to verify ArgyllCMS installation."
    exit 1
fi

echo "✓ Setup complete"