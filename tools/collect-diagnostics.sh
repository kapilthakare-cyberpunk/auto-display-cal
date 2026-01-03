#!/bin/bash
# collect-diagnostics.sh - Gather logs and config for debugging

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="diagnostics_${TIMESTAMP}.tar.gz"

echo "Collecting diagnostics into $OUTPUT_FILE..."

# Create a temporary directory
TEMP_DIR=$(mktemp -d)

# Copy logs
cp calibration.log* "$TEMP_DIR/" 2>/dev/null || echo "No logs found."

# Copy config
cp .displaycalrc "$TEMP_DIR/" 2>/dev/null || echo "No .displaycalrc found."
cp ~/.displaycalrc "$TEMP_DIR/user_displaycalrc" 2>/dev/null || echo "No ~/.displaycalrc found."

# System info
echo "Gathering system info..."
system_profiler SPDisplaysDataType > "$TEMP_DIR/system_info.txt"
system_profiler SPUSBDataType >> "$TEMP_DIR/system_info.txt"
sw_vers >> "$TEMP_DIR/system_info.txt"

# Create archive
tar -czf "$OUTPUT_FILE" -C "$TEMP_DIR" .

# Cleanup
rm -rf "$TEMP_DIR"

echo "Diagnostics bundle created: $OUTPUT_FILE"
