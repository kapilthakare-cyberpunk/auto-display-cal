#!/usr/bin/env bash
set -euo pipefail

# Enhanced script to run display calibration from scratch with ArgyllCMS
# Supports dry-run mode and configuration file

# Set up error handling
trap 'echo "Error occurred at line $LINENO. Check calibration.log for details." >&2; exit 1' ERR

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

# Start logging
exec 1> >(tee -a calibration.log) 2>&1

# Check for dry-run flag
DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]] || [[ "${1:-}" == "-n" ]]; then
    DRY_RUN=1
    echo "DRY RUN MODE: Commands will be displayed but not executed"
    echo "To run calibration normally, execute without --dry-run flag"
    echo ""
fi

echo "Starting display calibration setup and execution..."

# Make sure we're in the right directory
cd /Users/kapilthakare/Projects/auto-cal

# Ensure all scripts have execute permissions
chmod +x setup.sh auto_calibrate.sh auto_calibrate.py calibration_gui.py

echo "Step 1: Installing dependencies (if not already installed)..."
./setup.sh

echo "Step 2: Checking for Spyder5 device..."
if system_profiler SPUSBDataType | grep -i "spyder" > /dev/null; then
    echo "✓ Spyder5 device detected"
else
    echo "⚠ Warning: Spyder5 device not detected. Please connect your device."
    if [ $DRY_RUN -eq 0 ]; then
        echo "Connect your Spyder5 device and press Enter to continue..."
        read -r
    else
        echo "DRY RUN: Would wait for device connection"
    fi
fi

# Check if ArgyllCMS is installed
if ! command -v dispcal &> /dev/null; then
    echo "ArgyllCMS not found. Installing..."
    if [ $DRY_RUN -eq 0 ]; then
        HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_ENV_HINTS=1 brew install argyll-cms
    else
        echo "DRY RUN: Would execute: HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_ENV_HINTS=1 brew install argyll-cms"
    fi
fi

# Source configuration file if it exists
if [ -f "$HOME/.displaycalrc" ]; then
    source "$HOME/.displaycalrc"
    echo "Configuration loaded from ~/.displaycalrc"
elif [ -f ".displaycalrc" ]; then
    source ".displaycalrc"
    echo "Configuration loaded from .displaycalrc"
else
    # Set default values
    DEFAULT_DISPLAY="-d1"
    DEFAULT_WHITE_POINT="6500"
    DEFAULT_GAMMA="2.2"
    DEFAULT_QUALITY="m"
    DEFAULT_AUTHOR="AutoCal"
    DEFAULT_RED_FACTOR="1.0"
    DEFAULT_GREEN_FACTOR="1.0"
    DEFAULT_BLUE_FACTOR="1.0"
    echo "No configuration file found. Using default values."
fi

echo "Step 3: Running calibration..."

# Define options array
options=("Auto-Instant-Cal (fast, ambient-aware)"
         "Auto-Instant-Cal (3 variations: Standard, Warm, Cool)"
         "Apply Best Profile (Instant, no calibration)"
         "Launch GUI for manual adjustment")

# Set custom prompt
PS3="Enter your choice (1-4): "

# Use select for menu with validation
while true; do
    select choice in "${options[@]}"; do
        case $REPLY in
            1)
                echo "Running Auto-Instant-Cal (fast, ambient-aware)..."
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 auto_calibrate.py"
                else
                    python3 auto_calibrate.py
                fi
                break 2
                ;;
            2)
                echo "Running Auto-Instant-Cal (3 variations)..."
                
                # Variation 1: Standard (Auto Ambient)
                echo "--- Variation 1: Standard ---"
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 auto_calibrate.py --profile-name Variation_Standard"
                else
                    python3 auto_calibrate.py --profile-name Variation_Standard
                fi

                # Variation 2: Warm (5000K)
                echo "--- Variation 2: Warm (5000K) ---"
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 auto_calibrate.py --white-point 5000 --profile-name Variation_Warm"
                else
                    python3 auto_calibrate.py --white-point 5000 --profile-name Variation_Warm
                fi

                # Variation 3: Cool (7500K)
                echo "--- Variation 3: Cool (7500K) ---"
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 auto_calibrate.py --white-point 7500 --profile-name Variation_Cool"
                else
                    python3 auto_calibrate.py --white-point 7500 --profile-name Variation_Cool
                fi
                
                echo "All variations completed."
                break 2
                ;;
            3)
                echo "Applying Best Profile..."
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 auto_calibrate.py --apply-only"
                else
                    python3 auto_calibrate.py --apply-only
                fi
                break 2
                ;;
            4)
                echo "Launching GUI..."
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 calibration_gui.py"
                else
                    python3 calibration_gui.py
                fi
                break 2
                ;;
            *)
                echo "Invalid option. Please select 1-4."
                break  # Break only the select loop, continue while loop
                ;;
        esac
    done
done

echo "Calibration completed. For visual fine-tuning and final acceptance, run: python3 calibration_gui.py"
echo "Check calibration.log for details."