#!/usr/bin/env python3
# apply_profile.py - Lightweight script to apply display profiles based on ambient light
# Safe for scheduling (non-interactive)

import sys
import os
import argparse
from calibration_utils import setup_logging, get_ambient_light_condition, apply_icc_profile

logger = setup_logging("apply_profile")

# Configuration - Assumes profiles are in the same directory or standard system paths
PROFILES = {
    "low": "LowLight_Profile.icc",
    "medium": "MediumLight_Profile.icc",
    "high": "HighLight_Profile.icc"
}

def main():
    parser = argparse.ArgumentParser(description='Apply display profile based on ambient light found.')
    parser.add_argument('--force-condition', choices=['low', 'medium', 'high'], 
                        help='Force specific lighting condition')
    parser.add_argument('--profile-dir', default=os.getcwd(),
                        help='Directory containing the .icc profiles')
    args = parser.parse_args()

    logger.info("--- Starting Auto-Apply Profile ---")

    # Determine condition
    if args.force_condition:
        condition = args.force_condition
        logger.info(f"Using forced condition: {condition}")
    else:
        condition = get_ambient_light_condition()
        logger.info(f"Detected condition: {condition}")

    # Select profile
    profile_filename = PROFILES.get(condition)
    if not profile_filename:
        logger.error(f"No profile mapping for condition: {condition}")
        sys.exit(1)

    # Resolve full path
    # 1. Check provided dir (default: CWD)
    # 2. Check standard macOS ColorSync folder
    
    candidates = [
        os.path.join(args.profile_dir, profile_filename),
        os.path.expanduser(f"~/Library/ColorSync/Profiles/{profile_filename}"),
        f"/Library/ColorSync/Profiles/{profile_filename}"
    ]

    found_profile = None
    for path in candidates:
        if os.path.exists(path):
            found_profile = path
            break
            
    if found_profile:
        logger.info(f"Found profile: {found_profile}")
        if apply_icc_profile(found_profile):
            print(f"Applied {condition} profile: {found_profile}")
            sys.exit(0)
        else:
            logger.error("Failed to apply profile.")
            sys.exit(1)
    else:
        logger.warning(f"Profile {profile_filename} not found in search paths.")
        logger.info("Please run 'calibrate_new.py' to generate these profiles first.")
        sys.exit(1)

if __name__ == "__main__":
    main()
