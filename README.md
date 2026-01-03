# Auto-Cal: macOS Display Calibration Automation

A streamlined, robust wrapper around **ArgyllCMS** for macOS. This ecosystem manages your color calibration lifecycle—from deep monthly calibration to daily automated adjustments and real-time visual fine-tuning—without the bloat of GUI applications.

## 🌟 Features

*   **Automated Daily Application**: Silently detects ambient light (or uses equivalent time-of-day logic) to apply the correct ICC profile (`Low`, `Medium`, or `High` light). Safe for `launchd`/`cron`.
*   **Manual Calibration Wizard**: A simplified interactive CLI wrapper for `dispcal` to generate studio-quality, timestamped ICC profiles.
*   **Real-Time Live Tuner**: **Exclusive Feature.** A TUI (Text User Interface) that lets you "paint" your screen tint and brightness in real-time using keyboard shortcuts. Great for visually matching reference displays.

---

## � Quick Start

The easiest way to interact with the suite is the main menu:

```bash
./run_calibration.sh
```

This provides quick access to all tools.

---

## 🛠️ Tools Reference

### 1. Daily Automation (`apply_profile.py`)
*   **Purpose**: Run this in the background (e.g., every hour or at login).
*   **Logic**: Checks if Spyder sensor is attached.
    *   *If Yes*: Reads room lux.
    *   *If No*: Estimates light based on current hour.
    *   Applies the matching `LowLight_Profile.icc`, `Medium...`, or `High...`.
*   **Usage**:
    ```bash
    python3 apply_profile.py
    ```

### 2. Live Display Tuner (`tune_display.py`)
*   **Purpose**: Instant visual adjustment without re-calibrating.
*   **How it works**: Generates a temporary lookup table (LUT) and typically pushes it to the GPU in <100ms.
*   **Controls**:
    *   `R` / `r`: Increase/Decrease **Red** Tint
    *   `G` / `g`: Increase/Decrease **Green** Tint
    *   `B` / `b`: Increase/Decrease **Blue** Tint
    *   `W` / `w`: Increase/Decrease **Brightness** (Gain)
    *   `q`: Quit (Keep changes active)
    *   `x`: Cancel (Revert to original state)
*   **Usage**:
    ```bash
    python3 tune_display.py
    ```

### 3. Monthly Calibration (`calibrate_new.py`)
*   **Purpose**: Generate NEW baseline profiles.
*   **Requirement**: Spyder5 sensor must be connected and hanging on the screen.
*   **Usage**:
    ```bash
    python3 calibrate_new.py
    ```

---

## ⚙️ Installation / Setup

1.  **Dependencies**:
    Ensure `ArgyllCMS` is installed. The setup script handles this for you (via Homebrew).
    ```bash
    ./setup.sh
    ```

2.  **Scheduling (Optional)**:
    To make `apply_profile.py` run automatically, add it to your `crontab` or `launchd`.
    *Example Crontab (every hour)*:
    ```bash
    0 * * * * /usr/bin/python3 /Users/yourname/Projects/auto-cal/apply_profile.py >> /tmp/autocal.log 2>&1
    ```

---

## 📂 File Structure

*   `apply_profile.py`: Automation script.
*   `calibrate_new.py`: Calibration wizard.
*   `tune_display.py`: Real-time tuner.
*   `calibration_utils.py`: Shared logic (logging, binary detection).
*   `run_calibration.sh`: Main menu.

## 📄 License
MIT License.