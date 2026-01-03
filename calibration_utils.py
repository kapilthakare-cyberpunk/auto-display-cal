import logging
import logging.handlers
import subprocess
import time
import os
import shutil
import re
from datetime import datetime

# --- Logging Setup ---
def setup_logging(name="calibration"):
    """Set up logging with rotation to prevent excessive log growth"""
    # Create rotating file handler that rotates when log reaches 10MB
    # Keep up to 3 backup files
    log_filename = f'{name}.log'
    rotating_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )

    # Set up formatting
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    rotating_handler.setFormatter(formatter)

    # Configure root logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Add handlers
    if not logger.handlers:
        logger.addHandler(rotating_handler)
        logger.addHandler(logging.StreamHandler())

    return logger

logger = setup_logging()

# --- Path Safety ---
def find_binary(binary_name):
    """
    Locate a binary using shutil.which and common paths.
    Returns absolute path or None if not found.
    """
    path = shutil.which(binary_name)
    if path:
        return path
    
    # Check common locations for ArgyllCMS on macOS
    common_paths = [
        f"/usr/local/bin/{binary_name}",
        f"/opt/homebrew/bin/{binary_name}",
        f"/usr/bin/{binary_name}",
        f"/Applications/DisplayCAL/DisplayCAL.app/Contents/MacOS/{binary_name}", # sometimes bundled
        f"/Library/Frameworks/ArgyllCMS.framework/Resources/bin/{binary_name}"
    ]
    
    for p in common_paths:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
            
    return None

# --- Device & Ambient Light ---
def check_spyder5_connected(retries=3, delay=2):
    """Check if Spyder5 device is connected via USB with retries"""
    for attempt in range(retries):
        try:
            # Method 1: system_profiler (detailed but sometimes slow/flaky)
            result = subprocess.run(['system_profiler', 'SPUSBDataType'],
                                  capture_output=True, text=True)
            if 'spyder' in result.stdout.lower() or 'color munki' in result.stdout.lower():
                logger.info("Spyder5 device detected (via system_profiler)")
                return True
                
            # Method 2: ioreg (faster, lower level)
            result_ioreg = subprocess.run(['ioreg', '-p', 'IOUSB', '-w0'], 
                                        capture_output=True, text=True)
            if 'spyder' in result_ioreg.stdout.lower() or 'datacolor' in result_ioreg.stdout.lower():
                logger.info("Spyder5 device detected (via ioreg)")
                return True
                
            # If neither found...
            if attempt < retries - 1:
                time.sleep(delay)
        except Exception as e:
            logger.error(f"Error checking for Spyder5: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    
    logger.warning("Spyder5 device not detected.")
    return False

def get_ambient_lux():
    """
    Read ambient light level (Lux) using ArgyllCMS spotread.
    Returns float value of Lux or None if reading fails.
    """
    spotread_bin = find_binary("spotread")
    if not spotread_bin:
        logger.warning("spotread tool not found. Cannot read ambient light.")
        return None

    try:
        logger.info(f"Reading ambient light using {spotread_bin}...")
        # -a: Ambient light, -N: No calibration (just read)
        # spotread usually needs a keypress or interactive mode. 
        # We try feeding 'q' and capture output.
        cmd = [spotread_bin, "-a"] 
        
        # We pipe "q" to quit immediately after reading if possible, or wait for output
        # Some versions output continuously, so we might need to handle that.
        # This is a best-effort attempt for automation.
        
        result = subprocess.run(cmd, input="q\n", capture_output=True, text=True, timeout=10)
        
        # Parse output for Lux
        match = re.search(r"Ambient\s*=\s*([\d\.]+)\s*Lux", result.stdout)
        if match:
            lux = float(match.group(1))
            logger.info(f"Measured Ambient Light: {lux} Lux")
            return lux
        
        match = re.search(r"Result is.*?([\d\.]+)\s*Lux", result.stdout, re.DOTALL)
        if match:
            lux = float(match.group(1))
            logger.info(f"Measured Ambient Light: {lux} Lux")
            return lux

        logger.debug(f"Could not parse Lux from spotread output: {result.stdout[:200]}...")
        return None

    except subprocess.TimeoutExpired:
        logger.error("Timeout waiting for spotread measurement.")
        return None
    except Exception as e:
        logger.error(f"Error reading ambient light: {e}")
        return None

def get_ambient_light_condition():
    """
    Estimate ambient light level based on sensor reading or time of day fallback.
    Returns: 'low', 'medium', 'high'
    """
    # Simply detecting if device is connected is fast; taking reading takes time.
    # If we are in "Apply Fast" mode, maybe we skip sensor if not present immediately?
    # For now, we try sensor if connected.
    
    if check_spyder5_connected(retries=1):
        lux = get_ambient_lux()
        if lux is not None:
            if lux < 10:
                return "low"
            elif lux < 100:
                return "medium"
            else:
                return "high"
            
    logger.info("Falling back to time-based ambient estimation.")
    current_hour = datetime.now().hour
    
    if 6 <= current_hour < 9:
        return "high"
    elif 9 <= current_hour < 17:
        return "high"
    elif 17 <= current_hour < 20: 
        return "medium"
    else:
        return "low"

# --- Profile Application ---
def apply_icc_profile(profile_path):
    """Apply the specified ICC profile to the display"""
    dispwin_bin = find_binary("dispwin")
    
    if dispwin_bin:
        try:
            logger.info(f"Attempting to apply profile {profile_path} using {dispwin_bin}...")
            # -d1 for first display. -I to install (if needed) or just apply. 
            # Usually just passing the filename applies it. 
            # -L loads the calibration from the profile to the video LUT.
            cmd = [dispwin_bin, "-d1", "-L", profile_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Profile {profile_path} applied successfully")
                return True
            else:
                logger.warning(f"dispwin failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error executing dispwin: {e}")
    else:
        logger.warning("dispwin binary not found in PATH or common locations.")

    # Fallback to AppleScript
    logger.warning("Attempting fallback to AppleScript (System Preferences)...")
    try:
        # Note: This is brittle and depends on macOS version/language
        # It's better to just rely on dispwin or 'color' command line tools if available
        logger.info("AppleScript fallback skipped (unreliable). Please install ArgyllCMS.")
        return False
    except Exception as e:
        logger.error(f"Error applying profile via fallback: {e}")
        return False
