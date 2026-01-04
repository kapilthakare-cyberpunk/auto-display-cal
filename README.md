# Auto-Cal: Professional Display Calibration for macOS, Linux, and Windows

A streamlined, professional wrapper around **ArgyllCMS**. Auto-Cal provides studio-quality color calibration with an intuitive interface—no bloated GUI applications required. Works on macOS, Linux, and Windows.

## 🌟 Features

*   **Standard Calibration**: One-click ambient-aware calibration. Measures room light → selects optimal profile → calibrates → exports ICC + Report.
*   **Detailed Manual Calibration**: Expert mode with full ArgyllCMS interactive menu (Black Level, White Point, etc.).
*   **Real-Time Live Tuner**: Visual tint/brightness adjustment with keyboard shortcuts. Export calibrated settings instantly.
*   **Cross-Platform**: Automatic dependency installation for macOS (Homebrew) and Linux (apt, dnf, pacman).

---

## 🚀 Quick Start

### macOS & Linux:
Launch the Auto-Cal menu:
```bash
./launch-auto-cal.sh
```

### Windows:
Ensure [ArgyllCMS](https://www.argyllcms.com/downloadwin.html) is installed and in your PATH, then run:
```powershell
python calibrate_new.py
```

### Menu Options:
1.  **Standard Calibration (Auto-Ambient)** → 20-30 mins → ICC + Report
2.  **Detailed Manual Calibration (Expert Mode)** → 30-45 mins → Full Control  
3.  **Live Tuner (Visual Adjust + Export)** → Real-time → Quick Tweaks

---

## 🛠️ Tools Reference

### 1. Standard / Detailed Calibration (`calibrate_new.py`)
*   **Purpose**: Generate accurate ICC profiles with ambient light optimization.
*   **Modes**:
    *   **Standard**: Auto-detects settings based on ambient light sensor.
    *   **Detailed**: Full ArgyllCMS interactive menu (1-8 options).
*   **Output**:
    *   ICC Profile applied to system
    *   Backup copy → `~/Documents/Calibration_Reports/`
    *   Detailed report with before/after metrics
*   **Usage**:
    ```bash
    python3 calibrate_new.py
    # OR for manual control:
    python3 calibrate_new.py --manual
    ```

### 2. Live Display Tuner (`tune_display.py`)
*   **Purpose**: Real-time visual adjustment without full recalibration.
*   **How it works**: Generates temporary LUT and applies to GPU in <100ms.
*   **Controls**:
    *   `R` / `r`: Increase/Decrease **Red** Tint
    *   `G` / `g`: Increase/Decrease **Green** Tint
    *   `B` / `b`: Increase/Decrease **Blue** Tint
    *   `W` / `w`: Increase/Decrease **Brightness** (Gain)
    *   `S` / `s`: **EXPORT** current settings to file & Report
    *   `q`: Quit (Keep changes active)
    *   `x`: Cancel (Revert to original state)
*   **Usage**:
    ```bash
    python3 tune_display.py
    ```

---

## ⚙️ Installation

1.  **Install Dependencies**:
    ```bash
    ./setup.sh
    ```
    This installs ArgyllCMS for your detected OS.

2.  **Connect Sensor**: Plug in your Spyder5, i1Display, or other supported colorimeter.

3.  **Launch**: `./launch-auto-cal.sh`

---

## 📂 Output Files

All calibration outputs are saved to `~/Documents/Calibration_Reports/`:
*   `ProfileName_YYYYMMDD_HHMMSS.icc` - ICC color profile
*   `Report_ProfileName_YYYYMMDD_HHMMSS.txt` - Detailed calibration report

---

## 📄 License
MIT License.