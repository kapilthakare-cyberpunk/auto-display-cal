#!/usr/bin/env bash
set -euo pipefail

# Auto-Cal Launcher
# Provides a clean menu interface for display calibration

# Check for dry-run flag
DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]] || [[ "${1:-}" == "-n" ]]; then
    DRY_RUN=1
    echo "DRY RUN MODE: Commands will be displayed but not executed"
    echo ""
fi

echo "╔════════════════════════════════════════╗"
echo "║        Auto-Cal Display Manager        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Ensure scripts are executable
chmod +x setup.sh calibrate_new.py tune_display.py 2>/dev/null || true

# Install dependencies if needed
if ! command -v dispcal &> /dev/null; then
    echo "→ Installing dependencies..."
    ./setup.sh
    echo ""
fi

# Check for Spyder5 device using cross-platform Python helper
echo "→ Checking for colorimeter..."
if python3 -c "from calibration_utils import check_spyder5_connected; exit(0 if check_spyder5_connected(retries=1) else 1)" 2>/dev/null; then
    echo "✓ Device detected"
else
    echo "⚠ No device detected"
    if [ $DRY_RUN -eq 0 ]; then
        echo "Connect your device and press Enter to continue..."
        read
    fi
fi

echo ""

# Define options array with enhanced descriptions
options=(
    "Standard Calibration (Auto-Ambient) → 20-30 mins → ICC + Report"
    "Detailed Manual Calibration (Expert Mode) → 30-45 mins → Full Control"
    "Live Tuner (Visual Adjust + Export) → Real-time → Quick Tweaks"
)

# Set custom prompt
PS3="Select option (1-3): "

# Use select for menu with validation
while true; do
    select choice in "${options[@]}"; do
        case $REPLY in
            1)
                echo "Running Standard Calibration (Ambient-Aware)..."
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 calibrate_new.py"
                else
                    python3 calibrate_new.py
                fi
                break 2
                ;;
            2)
                echo "Running Detailed Manual Calibration..."
                echo "This will launch the interactive calibration menu."
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 calibrate_new.py --manual --profile-name Custom_Detailed"
                else
                    python3 calibrate_new.py --manual --profile-name Custom_Detailed
                fi
                break 2
                ;;
            3)
                echo "Launching Live Tuner..."
                if [ $DRY_RUN -eq 1 ]; then
                    echo "DRY RUN: Would execute: python3 tune_display.py"
                else
                    python3 tune_display.py
                fi
                break 2
                ;;
            *)
                echo "Invalid option. Please select 1-3."
                break  # Break only the select loop, continue while loop
                ;;
        esac
    done
done

echo "Calibration completed. For visual fine-tuning and final acceptance, run: python3 calibration_gui.py"
echo "Check calibration.log for details."