# Auto-Cal Distribution Guide: End-to-End Setup

Thank you for using **Auto-Cal**, the streamlined display calibration wrapper for ArgyllCMS. Follow these steps to get studio-quality color on any display.

---

## 🛠️ Prerequisites
1.  **Colorimeter**: Connect your sensor (Spyder5, i1Display, etc.) to a USB port.
2.  **Display**: Ensure your display has been powered on for at least 30 minutes to stabilize colors.

---

## 🚀 Step 1: Install Dependencies
Open your terminal and run the setup script. This will automatically install ArgyllCMS for your operating system.

```bash
chmod +x setup.sh
./setup.sh
```

---

## 🎨 Step 2: Start Calibration
Launch the interactive menu to choose your calibration depth.

```bash
chmod +x launch-auto-cal.sh
./launch-auto-cal.sh
```

### Which option should I choose?
1.  **Standard (Auto-Ambient)**: Use this if you want the software to decide the best settings based on your current room light. Best for most users.
2.  **Expert Mode (Manual)**: Use this if you need absolute precision. You will be prompted to use the 1-8 menu to match your monitor's hardware buttons (RGB/Brightness) to the target numbers.
3.  **Live Tuner**: Use this for quick visual tweaks (e.g., "Screen looks too blue") without a full 30-minute recalibration.

---

## 📂 Step 3: Locate Your Results
Once finished, the script will automatically apply the new ICC profile to your system. Backups and detailed PDF-ready reports are saved to:

**`~/Documents/Calibration_Reports/`**

---

## 💻 OS Specific Notes
- **macOS**: Dependencies are installed via Homebrew. Profiles are applied using `dispwin -I`.
- **Linux**: Supports `apt`, `dnf`, and `pacman`. Ensure your user has permissions for USB devices (udev rules might be needed for non-root sensor access).
- **Windows**: Install [ArgyllCMS](https://www.argyllcms.com/downloadwin.html) manually and run `python calibrate_new.py`.
