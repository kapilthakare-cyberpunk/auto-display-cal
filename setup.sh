#!/bin/bash

# macOS ArgyllCMS and Spyder5 Setup Script
# This script installs ArgyllCMS for Spyder5 calibration

# Function to rotate log file if it exceeds 10MB
rotate_log_if_needed() {
    local log_file="calibration.log"
    if [[ -f "$log_file" ]]; then
        local log_size
        log_size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo 0)
        if (( log_size > 10485760 )); then  # 10MB in bytes
            echo "Rotating log file (size: $log_size bytes)..."
            mv "$log_file" "${log_file}.old" 2>/dev/null || true
        fi
    fi
}

# Rotate log if needed before starting
rotate_log_if_needed

echo "Starting ArgyllCMS and Spyder5 setup for macOS..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install ArgyllCMS
echo "Installing ArgyllCMS..."
HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_ENV_HINTS=1 brew install argyll-cms

# Check if ArgyllCMS is available
if ! command -v dispcal &> /dev/null; then
    echo "ArgyllCMS installation failed."
    exit 1
fi

echo "ArgyllCMS installed successfully!"

# Check for Spyder5 device
echo "Checking for Spyder5 device..."
if system_profiler SPUSBDataType | grep -i "spyder"; then
    echo "✓ Spyder5 device detected!"
else
    echo "⚠ Warning: Spyder5 device not detected. Please ensure it is connected."
fi

echo "Setup complete! You can now run automated calibration."
echo ""
echo "To run automated calibration, use one of these commands:"
echo "  ./run_calibration.sh          # Simple interactive setup"
echo "  python3 auto_calibrate.py     # Standard calibration"
echo "  python3 auto_calibrate.py --red -5   # With red reduction"
echo "  python3 calibration_gui.py    # Launch the GUI"
echo ""