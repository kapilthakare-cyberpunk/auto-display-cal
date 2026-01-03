#!/bin/bash

# auto_calibrate.sh - Automated Display Calibration Script for macOS with Spyder5
# This script automatically detects ambient lighting and performs display calibration

# Default values
RED_ADJUSTMENT=0
GREEN_ADJUSTMENT=0
BLUE_ADJUSTMENT=0
BRIGHTNESS_OVERRIDE=""
GAMMA_OVERRIDE=""
WHITE_POINT_OVERRIDE=""
PROFILE_NAME_OVERRIDE=""

# Show usage information
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --red PERCENT        Fine-tune red channel in percentage (-100 to 100)"
    echo "  --green PERCENT      Fine-tune green channel in percentage (-100 to 100)"
    echo "  --blue PERCENT       Fine-tune blue channel in percentage (-100 to 100)"
    echo "  --brightness VALUE   Override brightness setting (cd/m²)"
    echo "  --gamma VALUE        Override gamma setting (e.g., 2.2)"
    echo "  --white-point VALUE  Override white point in Kelvin (e.g., 6500)"
    echo "  --profile-name NAME  Custom profile name"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Standard calibration"
    echo "  $0 --red -5 --green 3        # Reduce red by 5%, increase green by 3%"
    echo "  $0 --blue 10 --brightness 110 # Increase blue by 10%, set brightness to 110"
    echo "  $0 --gamma 2.4 --white-point 6000  # Custom gamma and white point"
    exit 1
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --red)
            RED_ADJUSTMENT="$2"
            shift 2
            ;;
        --green)
            GREEN_ADJUSTMENT="$2"
            shift 2
            ;;
        --blue)
            BLUE_ADJUSTMENT="$2"
            shift 2
            ;;
        --brightness)
            BRIGHTNESS_OVERRIDE="$2"
            shift 2
            ;;
        --gamma)
            GAMMA_OVERRIDE="$2"
            shift 2
            ;;
        --white-point)
            WHITE_POINT_OVERRIDE="$2"
            shift 2
            ;;
        --profile-name)
            PROFILE_NAME_OVERRIDE="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate percentage values
if (( $(echo "$RED_ADJUSTMENT < -100" | bc -l) )) || (( $(echo "$RED_ADJUSTMENT > 100" | bc -l) )); then
    echo "Error: Red adjustment must be between -100 and 100"
    exit 1
fi

if (( $(echo "$GREEN_ADJUSTMENT < -100" | bc -l) )) || (( $(echo "$GREEN_ADJUSTMENT > 100" | bc -l) )); then
    echo "Error: Green adjustment must be between -100 and 100"
    exit 1
fi

if (( $(echo "$BLUE_ADJUSTMENT < -100" | bc -l) )) || (( $(echo "$BLUE_ADJUSTMENT > 100" | bc -l) )); then
    echo "Error: Blue adjustment must be between -100 and 100"
    exit 1
fi

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

# Logging function
log() {
    # Rotate log if needed before logging
    rotate_log_if_needed
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a calibration.log
}

# Check if Spyder5 is connected
check_spyder5() {
    log "Checking for Spyder5 device..."
    if system_profiler SPUSBDataType | grep -i "spyder" > /dev/null; then
        log "Spyder5 device detected"
        return 0
    else
        log "ERROR: Spyder5 device not detected. Please connect your device."
        return 1
    fi
}

# Get ambient light condition (simplified time-based approach)
get_ambient_light() {
    current_hour=$(date +%H)
    
    if [[ $current_hour -ge 6 && $current_hour -lt 9 ]]; then  # Morning
        echo "high"
    elif [[ $current_hour -ge 9 && $current_hour -lt 17 ]]; then  # Daytime
        echo "high"
    elif [[ $current_hour -ge 17 && $current_hour -lt 20 ]]; then  # Evening
        echo "medium"
    else  # Night
        echo "low"
    fi
}

# Get calibration settings based on ambient light
get_calibration_settings() {
    case $1 in
        "low")
            BASE_GAMMA=2.2
            BASE_WHITE_POINT=5500
            BASE_BRIGHTNESS=80
            BASE_PROFILE_NAME="LowLight_Profile"
            ;;
        "medium")
            BASE_GAMMA=2.2
            BASE_WHITE_POINT=6500
            BASE_BRIGHTNESS=100
            BASE_PROFILE_NAME="MediumLight_Profile"
            ;;
        "high")
            BASE_GAMMA=2.2
            BASE_WHITE_POINT=6500
            BASE_BRIGHTNESS=120
            BASE_PROFILE_NAME="HighLight_Profile"
            ;;
        *)
            # Default to medium settings
            BASE_GAMMA=2.2
            BASE_WHITE_POINT=6500
            BASE_BRIGHTNESS=100
            BASE_PROFILE_NAME="Default_Profile"
            ;;
    esac

    # Use overrides if provided, otherwise use base settings
    GAMMA=${GAMMA_OVERRIDE:-$BASE_GAMMA}
    WHITE_POINT=${WHITE_POINT_OVERRIDE:-$BASE_WHITE_POINT}
    BRIGHTNESS=${BRIGHTNESS_OVERRIDE:-$BASE_BRIGHTNESS}
    PROFILE_NAME=${PROFILE_NAME_OVERRIDE:-$BASE_PROFILE_NAME}
}

# Run calibration using ArgyllCMS
run_calibration() {
    log "Starting calibration with settings:"
    log "  Gamma: $GAMMA"
    log "  White Point: $WHITE_POINT"
    log "  Profile Name: $PROFILE_NAME"

    # Include color adjustments in the log if they're not zero
    if [ "$RED_ADJUSTMENT" != "0" ] || [ "$GREEN_ADJUSTMENT" != "0" ] || [ "$BLUE_ADJUSTMENT" != "0" ]; then
        log "  Color adjustments - Red: ${RED_ADJUSTMENT}%, Green: ${GREEN_ADJUSTMENT}%, Blue: ${BLUE_ADJUSTMENT}%"
    fi

    # Generate timestamp for unique profile name
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    UNIQUE_PROFILE_NAME="${PROFILE_NAME}_${TIMESTAMP}"

    # Check if ArgyllCMS is installed
    if ! command -v dispcal &> /dev/null; then
        log "ERROR: ArgyllCMS not found. Please install using setup.sh first."
        exit 1
    fi

    log "Running ArgyllCMS calibration..."

    # Build the dispcal command
    CMD=(dispcal -d1 -t "$WHITE_POINT" -g "$GAMMA" -yl -q m "${UNIQUE_PROFILE_NAME}.cal")

    # Add color adjustments if needed
    if [ "$RED_ADJUSTMENT" != "0" ] || [ "$GREEN_ADJUSTMENT" != "0" ] || [ "$BLUE_ADJUSTMENT" != "0" ]; then
        # Convert percentage adjustments to factors
        RED_FACTOR=$(echo "1 + $RED_ADJUSTMENT/100" | bc -l)
        GREEN_FACTOR=$(echo "1 + $GREEN_ADJUSTMENT/100" | bc -l)
        BLUE_FACTOR=$(echo "1 + $BLUE_ADJUSTMENT/100" | bc -l)

        # Add adjustment flags to command
        CMD+=(-R "$RED_FACTOR" -G "$GREEN_FACTOR" -B "$BLUE_FACTOR")
    fi

    log "Running calibration command: ${CMD[*]}"

    # Run dispcal to measure the display
    if "${CMD[@]}"; then
        log "Calibration measurement completed successfully"

        # Now create the profile using colprof
        PROFILE_CMD=(colprof -D "${UNIQUE_PROFILE_NAME} Profile" -qf -v -A "AutoCal" "${UNIQUE_PROFILE_NAME}.cal")

        log "Creating profile with colprof: ${PROFILE_CMD[*]}"

        if "${PROFILE_CMD[@]}"; then
            log "Profile creation completed successfully"
            return 0
        else
            log "Profile creation failed"
            return 1
        fi
    else
        log "Calibration measurement failed"
        return 1
    fi
}

# Main execution
log "Starting automated display calibration for macOS"
log "Color adjustments - Red: ${RED_ADJUSTMENT}%, Green: ${GREEN_ADJUSTMENT}%, Blue: ${BLUE_ADJUSTMENT}%"

# Check if Spyder5 is connected
if ! check_spyder5; then
    log "Calibration aborted: Spyder5 not connected"
    exit 1
fi

# Determine ambient light condition
AMBIENT_LIGHT=$(get_ambient_light)
log "Ambient light condition: $AMBIENT_LIGHT"

# Get appropriate calibration settings
get_calibration_settings $AMBIENT_LIGHT
log "Using calibration settings - Gamma: $GAMMA, White Point: $WHITE_POINT, Brightness: $BRIGHTNESS"

# Run the calibration
if run_calibration; then
    log "Display calibration completed successfully!"
    echo "Calibration finished. Your display profile has been updated."
else
    log "Display calibration failed!"
    echo "Calibration failed. Check calibration.log for details."
    exit 1
fi