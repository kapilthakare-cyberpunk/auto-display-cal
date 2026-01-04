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
    Locate a binary using shutil.which and common paths across platforms.
    """
    # Check PATH first
    path = shutil.which(binary_name)
    if path:
        return path
    
    # Platform specific suffixes
    suffix = ".exe" if os.name == 'nt' else ""
    bin_file = f"{binary_name}{suffix}"

    common_paths = [
        # macOS
        f"/usr/local/bin/{bin_file}",
        f"/opt/homebrew/bin/{bin_file}",
        f"/Applications/DisplayCAL/DisplayCAL.app/Contents/MacOS/{bin_file}",
        # Linux
        f"/usr/bin/{bin_file}",
        f"/usr/local/bin/{bin_file}",
        # Windows (Example common install paths)
        f"C:\\Argyll_V3.1.0\\bin\\{bin_file}",
        f"C:\\Program Files\\ArgyllCMS\\bin\\{bin_file}"
    ]
    
    for p in common_paths:
        if os.path.exists(p):
            return p
            
    return None

# --- Device & Ambient Light ---
def check_spyder5_connected(retries=3, delay=2):
    """
    Check for connected colorimeters using ArgyllCMS's own device listing.
    This is the most cross-platform way to detect the sensor.
    """
    dispcal_bin = find_binary("dispcal")
    if not dispcal_bin:
        return False

    for attempt in range(retries):
        try:
            # 'dispcal -?' lists available sensors in its help output
            result = subprocess.run([dispcal_bin, "-?"], 
                                  capture_output=True, text=True)
            
            # Look for common sensor names in the output
            output = result.stdout + result.stderr
            sensors = ['spyder', 'color munki', 'i1 display', 'datacolor']
            
            if any(s in output.lower() for s in sensors):
                logger.info("Colorimeter detected via ArgyllCMS")
                return True
                
            if attempt < retries - 1:
                time.sleep(delay)
        except Exception as e:
            logger.error(f"Error checking for sensor: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    
    logger.warning("No colorimeter detected.")
    return False

def get_ambient_lux():
    """
    Read ambient light level (Lux) using ArgyllCMS spotread.
    Returns float value of Lux or None if reading fails.
    """
    spotread_bin = find_binary("spotread")
    if not spotread_bin:
        return None

    try:
        logger.debug(f"Attempting ambient light reading with {spotread_bin}...")
        # spotread is interactive - we try to make it non-interactive
        # -a: Ambient light, -N: No calibration
        cmd = [spotread_bin, "-a", "-N"] 
        
        # Quick timeout - if it doesn't work in 3 seconds, skip it
        result = subprocess.run(cmd, input="q\n", capture_output=True, text=True, timeout=3)
        
        # Parse output for Lux
        match = re.search(r"Ambient\s*=\s*([\d\.]+)\s*Lux", result.stdout)
        if match:
            lux = float(match.group(1))
            logger.info(f"Measured Ambient Light: {lux} Lux")
            return lux
        
        return None

    except subprocess.TimeoutExpired:
        logger.debug("Ambient light measurement timed out (sensor may require manual input)")
        return None
    except Exception as e:
        logger.debug(f"Could not read ambient light: {e}")
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
            # -d1 for first display. -I to install and set as system default.
            # -L is just for loading calibration, -I is for persistent installation.
            cmd = [dispwin_bin, "-d1", "-I", profile_path]
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

    # Fallback
    logger.warning("Profile application failed. Ensure ArgyllCMS is correctly installed for your OS.")
    return False
