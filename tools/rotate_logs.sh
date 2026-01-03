#!/bin/bash
# rotate_logs.sh - Compress old logs and cleanup

LOG_DIR="."
RETENTION_DAYS=30

echo "Running log maintenance..."

# 1. Compress rotated logs (calibration.log.1, .2, etc.)
# We assume the python RotatingFileHandler produces .1, .2 etc. 
# or our shell script produces .old.
# Let's compress any calibration.log.* that isn't already compressed.

find "$LOG_DIR" -name "calibration.log.*" -type f ! -name "*.gz" -exec gzip {} \;

# 2. Delete logs older than RETENTION_DAYS
find "$LOG_DIR" -name "calibration.log.*.gz" -mtime +$RETENTION_DAYS -delete

echo "Log maintenance complete."
