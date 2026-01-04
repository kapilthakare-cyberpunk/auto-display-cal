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

def generate_report(settings, log_output, output_path):
    """Generate a detailed calibration report"""
    report = []
    report.append(f"Display Calibration Report")
    report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Profile Name: {settings['name']}")
    report.append("-" * 40)
    report.append(f"Target Settings:")
    report.append(f"  White Point: {settings['white_point']}K")
    report.append(f"  Gamma: {settings['gamma']}")
    report.append(f"  Brightness: {settings['brightness']} cd/m^2")
    report.append("-" * 40)
    report.append("Calibration Results:")
    
    # Extract key metrics from log output if possible
    # This is a basic extraction, Argyll output varies
    found_metrics = False
    for line in log_output.split('\n'):
        if "Black level" in line or "White level" in line or "Brightness" in line:
            report.append(f"  {line.strip()}")
            found_metrics = True
    
    if not found_metrics:
        report.append("  (Detailed metrics available in calibration.log)")

    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    return output_path

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

    # Color Adjustments
    if any([settings['red_adj'], settings['green_adj'], settings['blue_adj']]):
        rf = 1.0 + (settings['red_adj'] / 100.0)
        gf = 1.0 + (settings['green_adj'] / 100.0)
        bf = 1.0 + (settings['blue_adj'] / 100.0)
        cmd.insert(-1, f"-R{rf:.3f}")
        cmd.insert(-1, f"-G{gf:.3f}")
        cmd.insert(-1, f"-B{bf:.3f}")

    # Execution with TTY preservation (Critical for 1-8 menu on Unix)
    import tempfile
    temp_dir = tempfile.gettempdir()
    session_log = os.path.join(temp_dir, f"{base_name}.log")
    
    # Use 'script' for Unix-like systems to capture interactive sessions
    # For Windows, we run directly and accept that logging might be limited
    if os.name != 'nt' and shutil.which("script"):
        shell_cmd = ["script", "-q", session_log] + cmd
    else:
        shell_cmd = cmd
        session_log = None # Cannot capture full interactive session easily on Win
    
    print(f"Executing: {' '.join(cmd)}")
    try:
        # We run this directly to inherit the terminal (stdin/stdout)
        retcode = subprocess.call(shell_cmd)
        
        if retcode != 0:
            logger.error("Calibration failed or aborted.")
            return False
            
        logger.info("dispcal completed successfully.")
        
        # Read the captured log for the report if it exists
        calibration_log = ""
        if session_log and os.path.exists(session_log):
            with open(session_log, 'r', errors='ignore') as f:
                calibration_log = f.read()
        else:
            calibration_log = "Detailed interactive log not available on this platform."
            
    except Exception as e:
        logger.error(f"Error executing calibration session: {e}")
        return False

    # 2. colprof
    cmd_prof = [
        colprof_bin,
        "-D", f"{settings['name']} Created {timestamp}",
        "-qf",          # Quality: Fine
        "-v",           # Verbose
        "-A", "AutoCal",
        base_name
    ]

    try:
        subprocess.check_call(cmd_prof)
        logger.info("Profile creation completed.")
    except subprocess.CalledProcessError:
        logger.error("Profile creation failed.")
        return False

    # 3. Finalize: Copy to Documents and Generate Report
    documents_path = os.path.expanduser("~/Documents/Calibration_Reports")
    if not os.path.exists(documents_path):
        os.makedirs(documents_path)
    
    generated_icc = f"{base_name}.icc"
    
    if os.path.exists(generated_icc):
        try:
            # Copy ICC to Documents
            import shutil
            dest_icc = os.path.join(documents_path, generated_icc)
            shutil.copy2(generated_icc, dest_icc)
            logger.info(f"Backup ICC profile saved to: {dest_icc}")
            
            # Generate Report
            report_file = os.path.join(documents_path, f"Report_{base_name}.txt")
            generate_report(settings, calibration_log, report_file)
            logger.info(f"Calibration report saved to: {report_file}")
            
            # Apply profile
            if apply_icc_profile(dest_icc):
                print(f"\n" + "═"*50)
                print(f" ✅ SUCCESS: PROFILES CREATED AND APPLIED")
                print(f"" + "═"*50)
                print(f" 📂 LOCATION  : {documents_path}")
                print(f" 📄 ICC PROFILE: {generated_icc}")
                print(f" 📝 REPORT     : Report_{base_name}.txt")
                print(f"═"*50 + "\n")
                return True
        except Exception as e:
            logger.error(f"Error handling final files: {e}")
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Display Calibration Standard Process')
    parser.add_argument('--red', type=float, default=0.0)
    parser.add_argument('--green', type=float, default=0.0)
    parser.add_argument('--blue', type=float, default=0.0)
    parser.add_argument('--brightness', type=int)
    parser.add_argument('--gamma', type=float)
    parser.add_argument('--white-point', type=int)
    parser.add_argument('--profile-name', help='Custom profile name prefix')
    parser.add_argument('--manual', action='store_true', help='Skip ambient sensing and use defaults/args')
    
    args = parser.parse_args()

    print("--- Standard Calibration Process ---")
    
    # 1. Check Device
    if not check_spyder5_connected():
        print("Error: Spyder5 not found. Please connect it.")
        sys.exit(1)

    # 2. Detect Light & Auto-Configure
    if args.manual:
        print("Manual Mode: Skipping ambient light measurement.")
        condition = "medium" # Default to medium if manual and no args
    else:
        print("Measuring ambient light to determine optimal settings...")
        condition = get_ambient_light_condition()
        print(f"Detected Condition: {condition.upper()}")
    
    settings = get_calibration_settings(condition, args)
    
    # Run
    if run_calibration_process(settings):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
