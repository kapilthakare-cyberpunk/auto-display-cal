#!/usr/bin/env python3
# tune_display.py - Real-time Display Color Tuner
# Allows live adjustment of R/G/B/Brightness using ArgyllCMS dispwin

import sys
import os
import subprocess
import time
import tempfile
from datetime import datetime
from calibration_utils import find_binary, setup_logging

logger = setup_logging("live_tuner")

# --- Configuration ---
STEP_SIZE = 0.01  # 1% increment
TEMP_CAL_NAME = "live_tune.cal"

def get_temp_cal_path():
    return os.path.join(tempfile.gettempdir(), TEMP_CAL_NAME)

# Current State (1.0 = 100% = Neutral)
state = {
    'red': 1.0,
    'green': 1.0,
    'blue': 1.0,
    'gain': 1.0
}

def getch():
    """Read single character from stdin without waiting for enter (Cross-platform)."""
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode('utf-8', errors='ignore')
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def generate_cal_file(filename, s):
    """Generates a simple ArgyllCMS .cal file based on current state."""
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
        f"NUMBER_OF_SETS 256",
        "BEGIN_DATA"
    ]

    for i in range(256):
        x = i / 255.0
        r_val = min(1.0, max(0.0, x * s['gain'] * s['red']))
        g_val = min(1.0, max(0.0, x * s['gain'] * s['green']))
        b_val = min(1.0, max(0.0, x * s['gain'] * s['blue']))
        content.append(f"{x:.6f} {r_val:.6f} {g_val:.6f} {b_val:.6f}")

    content.append("END_DATA")
    
    with open(filename, 'w') as f:
        f.write('\n'.join(content))

def apply_tuning(dispwin_bin):
    """Applies the current state to the display instantly."""
    path = get_temp_cal_path()
    generate_cal_file(path, state)
    
    if dispwin_bin:
        # -d1: First display
        subprocess.run([dispwin_bin, "-d1", path], capture_output=True)

def print_status():
    print(f"\r\033[KSTATUS | Red: {state['red']:.2f} | Green: {state['green']:.2f} | Blue: {state['blue']:.2f} | Gain: {state['gain']:.2f} (S to Export)", end="", flush=True)

def main():
    dispwin_bin = find_binary("dispwin")
    if not dispwin_bin:
        print("Error: 'dispwin' from ArgyllCMS not found. Please run setup.sh first.")
        sys.exit(1)

    print("\n╔════════════════════════════════════════╗")
    print("║       REAL-TIME DISPLAY TUNER          ║")
    print("╚════════════════════════════════════════╝")
    print("Adjust your monitor's look with shortcuts:")
    print("  r/R : Red -/+")
    print("  g/G : Green -/+")
    print("  b/B : Blue -/+")
    print("  w/W : Brightness Gain -/+")
    print("  s   : EXPORT & SAVE settings")
    print("  q   : Quit and Keep")
    print("  x   : Cancel and Revert")
    print("------------------------------------------")

    apply_tuning(dispwin_bin)
    print_status()

    while True:
        char = getch()
        
        if char == 'q':
            print(f"\n\n[INFO] Tuning session ended. Changes kept.")
            break
        elif char == 'x':
            print("\n\n[REVERTING] Defaulting video LUT...")
            subprocess.run([dispwin_bin, "-d1", "-c"], capture_output=True)
            break
        elif char.lower() == 's':
            print("\n")
            name = input("Enter name for exported visual profile: ").strip()
            if not name:
                name = f"LiveTune_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            docs_path = os.path.expanduser("~/Documents/Calibration_Reports")
            if not os.path.exists(docs_path):
                os.makedirs(docs_path)
            
            cal_file = os.path.join(docs_path, f"{name}.cal")
            report_file = os.path.join(docs_path, f"Report_{name}.txt")
            
            generate_cal_file(cal_file, state)
            
            with open(report_file, 'w') as f:
                f.write(f"Display Visual Tuning Report\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Red:   {state['red']:.2f}\n")
                f.write(f"Green: {state['green']:.2f}\n")
                f.write(f"Blue:  {state['blue']:.2f}\n")
                f.write(f"Gain:  {state['gain']:.2f}\n")
                f.write("-" * 40 + "\n")
                f.write(f"To reload this in the future: dispwin -d1 {cal_file}\n")

            print(f"\n" + "═"*50)
            print(f" ✅ SUCCESS: SETTINGS EXPORTED")
            print(f"" + "═"*50)
            print(f" 📂 LOCATION  : {docs_path}")
            print(f" 📄 CAL FILE   : {name}.cal")
            print(f" 📝 REPORT     : Report_{name}.txt")
            print(f"═"*50 + "\n")
            break

        # Adjustments
        if char == 'r': state['red'] -= STEP_SIZE
        elif char == 'R': state['red'] += STEP_SIZE
        elif char == 'g': state['green'] -= STEP_SIZE
        elif char == 'G': state['green'] += STEP_SIZE
        elif char == 'b': state['blue'] -= STEP_SIZE
        elif char == 'B': state['blue'] += STEP_SIZE
        elif char == 'w': state['gain'] -= STEP_SIZE
        elif char == 'W': state['gain'] += STEP_SIZE
        
        apply_tuning(dispwin_bin)
        print_status()

if __name__ == "__main__":
    main()
