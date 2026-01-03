#!/usr/bin/env python3
# tune_display.py - Real-time Display Color Tuner
# Allows live adjustment of R/G/B/Brightness/Gamma using ArgyllCMS dispwin
#
# USAGE:
#   python3 tune_display.py
#
# CONTROLS:
#   r/R : Red -/+ (Tint)
#   g/G : Green -/+ (Tint)
#   b/B : Blue -/+ (Tint)
#   w/W : Brightness -/+ (Global Gain)
#   q   : Quit (Keep changes)
#   x   : Cancel (Revert to start)

import sys
import os
import subprocess
import termios
import tty
import time
from datetime import datetime

# --- Configuration ---
STEP_SIZE = 0.01  # 1% increment
TEMP_CAL_FILE = "/tmp/live_tune.cal"

# Current State (1.0 = 100% = Neutral)
state = {
    'red': 1.0,
    'green': 1.0,
    'blue': 1.0,
    'gain': 1.0
}

def getch():
    """Read single character from stdin without waiting for enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def generate_cal_file(filename, s):
    """
    Generates a simple ArgyllCMS .cal file (RAMP) based on current state.
    This modifies the Video Card Gamma Table (VCGT).
    """
    # Header for Argyll .cal file
    content = [
        "CAL",
        "DESCRIPTOR \"Real-time Tuning\"",
        "ORIGINATOR \"AutoCal Tuner\"",
        "DEVICE_CLASS \"DISPLAY\"",
        "COLOR_REP \"RGB\"",
        "NUMBER_OF_FIELDS 4",
        "BEGIN_DATA_FORMAT",
        "RGB_I RGB_R RGB_G RGB_B",
        "END_DATA_FORMAT",
        "NUMBER_OF_SETS 256",
        "BEGIN_DATA"
    ]

    # Generate 256 steps (0-1.0 mapping)
    for i in range(256):
        x = i / 255.0
        
        # Apply Gain * Channel Tint
        # Simple linear scaling (Gamma 1.0 relative modification)
        # We could apply gamma power here, but linear gain is safer for "tinting"
        # on top of an existing HW calibration if the display handles it.
        # BUT: dispwin loads this INTO the LUT, replacing the current LUT.
        # So this is a "Visual Override".
        
        r_val = min(1.0, x * s['gain'] * s['red'])
        g_val = min(1.0, x * s['gain'] * s['green'])
        b_val = min(1.0, x * s['gain'] * s['blue'])
        
        content.append(f"{x:.6f} {r_val:.6f} {g_val:.6f} {b_val:.6f}")

    content.append("END_DATA")
    
    with open(filename, 'w') as f:
        f.write('\n'.join(content))

def apply_tuning():
    """Applies the current state to the display instantly."""
    generate_cal_file(TEMP_CAL_FILE, state)
    
    # Run dispwin to load the .cal file
    # -d1: First display
    cmd = ["dispwin", "-d1", TEMP_CAL_FILE]
    subprocess.run(cmd, capture_output=True)

def print_status():
    print(f"\r\033[KSTATUS | Red: {state['red']:.2f} | Green: {state['green']:.2f} | Blue: {state['blue']:.2f} | Brightness: {state['gain']:.2f}", end="", flush=True)

def main():
    print("--- REAL-TIME DISPLAY TUNER ---")
    print("WARNING: This replaces your current active calibration LUT while running.")
    print("Controls:")
    print("  r/R : Red -/+")
    print("  g/G : Green -/+")
    print("  b/B : Blue -/+")
    print("  w/W : Brightness -/+")
    print("  q   : Quit and Keep")
    print("  x   : Cancel and Revert")
    print("-------------------------------")

    # Initial apply
    apply_tuning()
    print_status()

    while True:
        char = getch()
        
        if char == 'q':
            print("\nValues kept. To make permanent, you might need to save the Generated .cal file.")
            print(f"File cached at: {TEMP_CAL_FILE}")
            break
        elif char == 'x':
            print("\nReverting...")
            subprocess.run(["dispwin", "-d1", "-c"]) # Clear/Reset
            break
        
        # Logic
        if char == 'r': state['red'] -= STEP_SIZE
        elif char == 'R': state['red'] += STEP_SIZE
        elif char == 'g': state['green'] -= STEP_SIZE
        elif char == 'G': state['green'] += STEP_SIZE
        elif char == 'b': state['blue'] -= STEP_SIZE
        elif char == 'B': state['blue'] += STEP_SIZE
        elif char == 'w': state['gain'] -= STEP_SIZE
        elif char == 'W': state['gain'] += STEP_SIZE
        
        # Apply & Update UI
        apply_tuning()
        print_status()

if __name__ == "__main__":
    main()
