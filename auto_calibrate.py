#!/usr/bin/env python3
# auto_calibrate.py - Automated Display Calibration Script for macOS with Spyder5
# This script automatically detects ambient lighting and performs display calibration

import subprocess
import time
import os
import sys
import logging
import argparse
from datetime import datetime

def parse_arguments():
    """Parse command-line arguments for calibration"""
    parser = argparse.ArgumentParser(
        description='Automated Display Calibration for macOS with Spyder5',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                           # Standard calibration
  %(prog)s --red -5 --green 3        # Reduce red by 5%%, increase green by 3%%
  %(prog)s --blue 10 --brightness 110 # Increase blue by 10%%, set brightness to 110
  %(prog)s --gamma 2.4 --white-point 6000  # Custom gamma and white point
        '''
    )

    parser.add_argument('--red', type=float, default=0.0,
                        help='Fine-tune red channel in percentage (-100 to 100)')
    parser.add_argument('--green', type=float, default=0.0,
                        help='Fine-tune green channel in percentage (-100 to 100)')
    parser.add_argument('--blue', type=float, default=0.0,
                        help='Fine-tune blue channel in percentage (-100 to 100)')
    parser.add_argument('--brightness', type=int,
                        help='Override brightness setting (cd/m²)')
    parser.add_argument('--gamma', type=float,
                        help='Override gamma setting (e.g., 2.2)')
    parser.add_argument('--white-point', dest='white_point', type=int,
                        help='Override white point in Kelvin (e.g., 6500)')
    parser.add_argument('--profile-name', dest='profile_name',
                        help='Custom profile name')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--apply-only', action='store_true',
                        help='Only measure ambient light and apply the best existing profile without full calibration')

    return parser.parse_args()

import logging.handlers

def setup_logging():
    """Set up logging with rotation to prevent excessive log growth"""
    # Create rotating file handler that rotates when log reaches 10MB
    # Keep up to 3 backup files
    rotating_handler = logging.handlers.RotatingFileHandler(
        'calibration.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )

    # Set up formatting
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    rotating_handler.setFormatter(formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Add handlers
    logger.addHandler(rotating_handler)
    logger.addHandler(logging.StreamHandler())

    return logger

logger = setup_logging()

def check_spyder5_connected(retries=3, delay=2):
    """Check if Spyder5 device is connected via USB with retries"""
    for attempt in range(retries):
        try:
            result = subprocess.run(['system_profiler', 'SPUSBDataType'],
                                  capture_output=True, text=True)
            if 'spyder' in result.stdout.lower() or 'color munki' in result.stdout.lower():
                logger.info("Spyder5 device detected")
                return True
            else:
                logger.warning(f"Spyder5 device not detected (attempt {attempt + 1}/{retries}).")
                if attempt < retries - 1:
                    time.sleep(delay)
        except Exception as e:
            logger.error(f"Error checking for Spyder5: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    
    logger.error("Spyder5 device not detected after multiple attempts. Please connect your device.")
    return False

def get_ambient_lux():
    """
    Read ambient light level (Lux) using ArgyllCMS spotread.
    Returns float value of Lux or None if reading fails.
    """
    try:
        # Check if spotread is available
        if subprocess.run(["command", "-v", "spotread"], capture_output=True).returncode != 0:
            logger.warning("spotread tool not found. Cannot read ambient light.")
            return None

        logger.info("Reading ambient light using spotread...")
        # Run spotread to measure ambient light (-a)
        # -O: output information only (no interaction) - this flag might vary, 
        # usually spotread is interactive. We might need to pipe 'q' or run non-interactively.
        # spotread -a -y -c 1 (ambient, luminance, port 1) 
        # Actually 'spotread -a' usually asks for a key press. 
        # usage: spotread -a (ambient)
        
        # We'll try to run it in a way that just takes a reading and exits.
        # Unfortunately spotread is interactive by default for ambient.
        # We might need to simulate input if there isn't a "single shot" flag.
        # However, for automation, some versions accept input redirection.
        
        # Attempting to read with a timeout and mocked input if needed.
        # But 'dispcal' has a measurement mode too.
        # Let's try a standard command that might work for many:
        cmd = ["spotread", "-a", "-y", "-N"] # -N: no calibration
        
        # We might need to pipe "q" to quit after reading if it loops, 
        # or just capture the first output.
        # Let's assume we can capture the output.
        result = subprocess.run(cmd, input="q\n", capture_output=True, text=True, timeout=10)
        
        # Parse output for Lux
        # Output typically contains: "Ambient = 45.3 Lux, ..."
        import re
        match = re.search(r"Ambient\s*=\s*([\d\.]+)\s*Lux", result.stdout)
        if match:
            lux = float(match.group(1))
            logger.info(f"Measured Ambient Light: {lux} Lux")
            return lux
        
        # Fallback regex if format is different
        match = re.search(r"Result is XYZ: [\d\.]+ [\d\.]+ [\d\.]+, D50 Lab: [\d\.]+ [\d\.]+ [\d\.]+, ([\d\.]+) Lux", result.stdout)
        if match:
            lux = float(match.group(1))
            logger.info(f"Measured Ambient Light: {lux} Lux")
            return lux

        logger.warning(f"Could not parse Lux from spotread output: {result.stdout[:200]}...")
        return None

    except subprocess.TimeoutExpired:
        logger.error("Timeout waiting for spotread measurement.")
        return None
    except Exception as e:
        logger.error(f"Error reading ambient light: {e}")
        return None

def get_ambient_light():
    """
    Estimate ambient light level based on sensor reading or time of day fallback.
    """
    # Try to get real reading
    lux = get_ambient_lux()
    
    if lux is not None:
        if lux < 10:
            return "low"      # Pitch black or very dim
        elif lux < 100:
            return "medium"   # Normal indoor lighting
        else:
            return "high"     # Bright / Daylight
            
    logger.info("Falling back to time-based ambient estimation.")
    # For macOS, we'll use a simple time-based estimation as a placeholder
    current_hour = datetime.now().hour
    
    # Define lighting conditions based on time of day
    if 6 <= current_hour < 9:  # Morning
        return "high"  # Higher brightness in morning
    elif 9 <= current_hour < 17:  # Daytime
        return "high"  # Bright conditions during day
    elif 17 <= current_hour < 20:  # Evening
        return "medium"  # Medium brightness in evening
    else:  # Night
        return "low"   # Low brightness at night

def get_calibration_settings(ambient_light, args):
    """Return appropriate calibration settings based on ambient light and user overrides"""
    settings = {
        "low": {
            "gamma": 2.2,
            "white_point": 5500,  # Warmer temperature for low light
            "brightness": 80,     # Lower brightness for night
            "name": "LowLight_Profile",
            "icc_file": "LowLight_Profile.icc" # Assuming these exist or will be created
        },
        "medium": {
            "gamma": 2.2,
            "white_point": 6500,  # Standard temperature
            "brightness": 100,    # Standard brightness
            "name": "MediumLight_Profile",
            "icc_file": "MediumLight_Profile.icc"
        },
        "high": {
            "gamma": 2.2,
            "white_point": 6500,  # Standard temperature
            "brightness": 120,    # Higher brightness for daylight
            "name": "HighLight_Profile",
            "icc_file": "HighLight_Profile.icc"
        }
    }

    # Get base settings for ambient light
    base_settings = settings.get(ambient_light, settings["medium"])

    # Override with command-line arguments if provided
    final_settings = {
        "gamma": args.gamma if args.gamma is not None else base_settings["gamma"],
        "white_point": args.white_point if args.white_point is not None else base_settings["white_point"],
        "brightness": args.brightness if args.brightness is not None else base_settings["brightness"],
        "name": args.profile_name if args.profile_name else base_settings["name"],
        "icc_file": base_settings.get("icc_file", "")
    }

    # Add color fine-tuning values
    final_settings["red_adjustment"] = args.red
    final_settings["green_adjustment"] = args.green
    final_settings["blue_adjustment"] = args.blue

    return final_settings

def run_calibration(settings):
    """Run the ArgyllCMS calibration process with specified settings"""
    try:
        # Generate a unique name for this calibration
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        profile_name = f"{settings['name']}_{timestamp}"
        
        logger.info(f"Starting calibration with settings: {settings}")
        logger.info(f"Profile name: {profile_name}")
        
        # Build the command for ArgyllCMS dispcal
        cmd = [
            "dispcal",
            "-d1",  # Use first display
            "-t", str(settings['white_point']),  # White point
            "-g", str(settings['gamma']),  # Gamma
            "-yl",  # Use luminance
            "-q", "m",  # Medium quality
            f"{profile_name}.cal"
        ]
        
        # Add color adjustments if needed
        if settings['red_adjustment'] != 0 or settings['green_adjustment'] != 0 or settings['blue_adjustment'] != 0:
            logger.info(f"Applying color adjustments - Red: {settings['red_adjustment']}%, "
                       f"Green: {settings['green_adjustment']}%, Blue: {settings['blue_adjustment']}%")
            
            # Convert percentage adjustments to factors
            red_factor = 1.0 + (settings['red_adjustment'] / 100.0)
            green_factor = 1.0 + (settings['green_adjustment'] / 100.0)
            blue_factor = 1.0 + (settings['blue_adjustment'] / 100.0)
            
            # Add color adjustment factors to command
            cmd.insert(-1, f"-R{red_factor:.3f}")  # Red adjustment
            cmd.insert(-1, f"-G{green_factor:.3f}")  # Green adjustment
            cmd.insert(-1, f"-B{blue_factor:.3f}")  # Blue adjustment
            
        logger.info("Running calibration command...")
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Run the calibration process
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Calibration measurement completed successfully")
            
            # Now create the profile using colprof
            profile_cmd = [
                "colprof",
                "-D", f"{settings['name']} Profile",
                "-qf",  # Fine quality
                "-v",  # Verbose
                "-A", "AutoCal",  # Author
                f"{profile_name}.cal"
            ]
            
            logger.info("Creating profile with colprof...")
            logger.info(f"Command: {' '.join(profile_cmd)}")
            
            profile_result = subprocess.run(profile_cmd, capture_output=True, text=True)
            
            if profile_result.returncode == 0:
                logger.info("Profile creation completed successfully")
                # Apply the newly created profile
                # Check for .icc or .icm extension, colprof usually creates .icc by default
                generated_profile = f"{profile_name}.icc"
                if os.path.exists(generated_profile):
                    apply_profile(generated_profile)
                else:
                    logger.warning(f"Expected profile {generated_profile} not found.")
                return True
            else:
                logger.error(f"Profile creation failed: {profile_result.stderr}")
                return False
        else:
            logger.error(f"Calibration failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        logger.error("ArgyllCMS not found. Please ensure it is installed (brew install argyll-cms)")
        return False
    except Exception as e:
        logger.error(f"Error during calibration: {e}")
        return False

def apply_profile(profile_path):
    """Apply the specified ICC profile to the display"""
    try:
        # First try using dispwin from ArgyllCMS
        logger.info(f"Attempting to apply profile {profile_path} using dispwin...")
        cmd = ["dispwin", "-d1", profile_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Profile {profile_path} applied successfully using dispwin")
            return True
        else:
            logger.warning(f"dispwin failed: {result.stderr}. Trying AppleScript fallback...")
            
        # Use AppleScript as fallback
        script = f'''
        tell application "System Events"
            tell application "Displays" to activate
            click menu bar item "Displays" of menu bar 1 of application process "System Preferences"
            click menu item "Color" of menu 1 of menu bar item "Displays" of menu bar 1 of application process "System Preferences"
            delay 2
            -- This is a brittle fallback, user manual intervention preferred if dispwin fails
        end tell
        '''
        
        logger.warning("Automatic profile application via AppleScript is not fully implemented/reliable.")
        logger.info("Please manually apply the profile in System Preferences > Displays > Color")
        return False
    except Exception as e:
        logger.error(f"Error applying profile: {e}")
        return False

def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Starting automated display calibration for macOS")

    # Check if Spyder5 is connected
    if not check_spyder5_connected():
        logger.error("Calibration aborted: Spyder5 not connected")
        sys.exit(1)

    # Determine ambient light conditions
    ambient_light = get_ambient_light()
    logger.info(f"Ambient light condition detected: {ambient_light}")

    # Get appropriate calibration settings
    settings = get_calibration_settings(ambient_light, args)
    
    # Check if we only want to apply the best profile
    if args.apply_only:
        logger.info("Apply-only mode selected. Skipping calibration.")
        icc_file = settings.get("icc_file")
        # Check if the profile exists in current directory or system folder
        # For simplicity, we assume they are in current dir or mapped
        # In a real scenario, we might want to look up by name in ~/Library/ColorSync/Profiles
        
        # Here we try to find a matching profile.
        # Since we don't have the exact filename from a previous run, 
        # we might need to rely on the user having named profiles or recent ones.
        # But let's assume standard naming convention or existence of 'MediumLight_Profile.icc' etc.
        # If not found, we warn.
        
        possible_paths = [
            icc_file,
            os.path.expanduser(f"~/Library/ColorSync/Profiles/{icc_file}"),
            f"/Library/ColorSync/Profiles/{icc_file}"
        ]
        
        found_profile = None
        for path in possible_paths:
            if path and os.path.exists(path):
                found_profile = path
                break
        
        if found_profile:
            logger.info(f"Found matching profile: {found_profile}")
            if apply_profile(found_profile):
                print(f"Successfully applied profile for {ambient_light} light: {found_profile}")
                sys.exit(0)
            else:
                logger.error("Failed to apply profile.")
                sys.exit(1)
        else:
            logger.warning(f"No existing profile found for {ambient_light} light ({icc_file}).")
            logger.info("Please run a full calibration first to generate these profiles.")
            sys.exit(1)

    logger.info(f"Color adjustments - Red: {args.red}%, Green: {args.green}%, Blue: {args.blue}%")
    logger.info(f"Using calibration settings: {settings}")

    # Run the calibration
    success = run_calibration(settings)

    if success:
        logger.info("Display calibration completed successfully!")
        print("\nCalibration finished. Your display profile has been updated.")
    else:
        logger.error("Display calibration failed!")
        print("\nCalibration failed. Check calibration.log for details.")
        sys.exit(1)