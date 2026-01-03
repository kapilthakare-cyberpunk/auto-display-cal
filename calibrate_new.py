#!/usr/bin/env python3
# calibrate_new.py - Manual Display Calibration Wizard
# Runs the full calibration process to generate new ICC profiles.
# Intended to be run manually when setting up the sensor.

import sys
import os
import argparse
import subprocess
from datetime import datetime
from calibration_utils import (
    setup_logging, 
    check_spyder5_connected, 
    get_ambient_light_condition, 
    apply_icc_profile,
    find_binary
)

logger = setup_logging("manual_calibration")

def get_calibration_settings(condition, args):
    """Return appropriate calibration settings based on ambient light and user overrides"""
    # Defaults
    settings = {
        "low": {
            "gamma": 2.2, "white_point": 5500, "brightness": 80, 
            "name": "LowLight_Profile"
        },
        "medium": {
            "gamma": 2.2, "white_point": 6500, "brightness": 100, 
            "name": "MediumLight_Profile"
        },
        "high": {
            "gamma": 2.2, "white_point": 6500, "brightness": 120, 
            "name": "HighLight_Profile"
        }
    }

    base = settings.get(condition, settings["medium"])

    # Overrides
    return {
        "gamma": args.gamma if args.gamma else base["gamma"],
        "white_point": args.white_point if args.white_point else base["white_point"],
        "brightness": args.brightness if args.brightness else base["brightness"],
        "name": args.profile_name if args.profile_name else base["name"],
        "quality": "m", # Medium quality
        "red_adj": args.red,
        "green_adj": args.green,
        "blue_adj": args.blue
    }

def run_calibration_process(settings):
    """Run ArgyllCMS dispcal and colprof"""
    dispcal_bin = find_binary("dispcal")
    colprof_bin = find_binary("colprof")

    if not dispcal_bin or not colprof_bin:
        logger.error("ArgyllCMS binaries (dispcal/colprof) not found.")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{settings['name']}_{timestamp}"
    cal_file = f"{base_name}.cal"
    
    logger.info(f"Starting calibration: {base_name}")
    logger.info(f"Settings: {settings}")
    print("\nIMPORTANT: Interactive calibration starting.")
    print("Follow the on-screen prompts to place your sensor and adjust your monitor.\n")

    # 1. dispcal
    cmd = [
        dispcal_bin,
        "-d1",                      # First display
        "-t", str(settings['white_point']),
        "-g", str(settings['gamma']),
        "-yl",                      # Luminance target
        "-q", settings['quality'],
        base_name
    ]

    # Color Adjustments (Factors)
    if any([settings['red_adj'], settings['green_adj'], settings['blue_adj']]):
        rf = 1.0 + (settings['red_adj'] / 100.0)
        gf = 1.0 + (settings['green_adj'] / 100.0)
        bf = 1.0 + (settings['blue_adj'] / 100.0)
        
        # Insert before filename
        cmd.insert(-1, f"-R{rf:.3f}")
        cmd.insert(-1, f"-G{gf:.3f}")
        cmd.insert(-1, f"-B{bf:.3f}")

    try:
        # We allow stdout/stderr usage here for interaction
        subprocess.check_call(cmd) 
        logger.info("dispcal completed.")
    except subprocess.CalledProcessError:
        logger.error("Calibration failed or aborted.")
        return False

    # 2. colprof
    cmd_prof = [
        colprof_bin,
        "-D", f"{settings['name']} Created {timestamp}",
        "-qf",          # Quality: Fine
        "-v",           # Verbose
        "-A", "AutoCal",
        base_name       # Input .cal/.ti3 -> Output .icc
    ]

    try:
        subprocess.check_call(cmd_prof)
        logger.info("Profile creation completed.")
    except subprocess.CalledProcessError:
        logger.error("Profile creation failed.")
        return False

    # 3. Rename/Link to standard name (Optional but helpers Apply script)
    # We generated `MediumLight_Profile_2024....icc`
    # We might want to save a copy as `MediumLight_Profile.icc` for easy lookup
    target_icc = f"{base_name}.icc"
    standard_name = f"{settings['name']}.icc"
    
    if os.path.exists(target_icc):
        try:
            # We copy it to the standard name so apply_profile.py finds it easily
            import shutil
            shutil.copy2(target_icc, standard_name)
            logger.info(f"Updated standard profile link: {standard_name}")
            
            # Apply it now
            if apply_icc_profile(target_icc):
                print(f"\nSUCCESS: Profile {target_icc} created and applied.")
                return True
        except Exception as e:
            logger.error(f"Error handling profile files: {e}")
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Manual Display Calibration Wizard')
    
    # Overrides
    parser.add_argument('--red', type=float, default=0.0, help='Red adjust %')
    parser.add_argument('--green', type=float, default=0.0, help='Green adjust %')
    parser.add_argument('--blue', type=float, default=0.0, help='Blue adjust %')
    parser.add_argument('--brightness', type=int)
    parser.add_argument('--gamma', type=float)
    parser.add_argument('--white-point', type=int)
    parser.add_argument('--profile-name', help='Custom profile name prefix')
    
    args = parser.parse_args()

    print("--- Manual Calibration Wizard ---")
    
    # 1. Check Device
    if not check_spyder5_connected():
        print("Error: Spyder5 not found. Please connect it.")
        sys.exit(1)

    # 2. Detect Light (or ask user)
    # Since this is manual, maybe we want to force a specific profile type?
    # Or just detect.
    condition = get_ambient_light_condition()
    print(f"Detected Environmental Light: {condition.upper()}")
    
    # Optional: Confirm with user
    # user_input = input(f"Calibrate for {condition} light? [Y/n]: ")
    # if user_input.lower().startswith('n'): ...
    # For now, we trust the detection + args.
    
    settings = get_calibration_settings(condition, args)
    
    if run_calibration_process(settings):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
