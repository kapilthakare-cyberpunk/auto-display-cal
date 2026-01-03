# macOS Display Calibration with Spyder5

This project provides automated display calibration for macOS using DisplayCAL and a Spyder5 colorimeter. The scripts automatically detect ambient lighting conditions and calibrate your display accordingly.

## 📋 Requirements

- macOS (10.14 or later recommended)
- X-Rite Spyder5 colorimeter
- USB port to connect the device

## 🚀 Quick Start - Simple One-Command Setup

For the simplest way to run calibration from scratch, use the automated script:

```bash
cd /Users/kapilthakare/Projects/auto-cal
chmod +x run_calibration.sh
./run_calibration.sh
```

This script will:
1. Install dependencies (DisplayCAL and ArgyllCMS) if needed
2. Check for your Spyder5 device
3. Present an interactive menu with calibration options
4. Run the calibration with your chosen settings using ArgyllCMS CLI

### Advanced Options

The script supports additional features:

```bash
# Dry run mode - shows commands without executing them
./run_calibration.sh --dry-run

# Or using the short form
./run_calibration.sh -n
```

### Configuration File

Create a configuration file at `~/.displaycalrc` to set default values:

```bash
# Display settings
DEFAULT_DISPLAY="-d1"

# White point (in Kelvin)
DEFAULT_WHITE_POINT="6500"

# Gamma value
DEFAULT_GAMMA="2.2"

# Quality setting (h=high, m=medium, l=low)
DEFAULT_QUALITY="m"

# Author name for profiles
DEFAULT_AUTHOR="AutoCal"

# Default color adjustments (as factors, not percentages)
DEFAULT_RED_FACTOR="1.0"
DEFAULT_GREEN_FACTOR="1.0"
DEFAULT_BLUE_FACTOR="1.0"
```

## 🛠️ Manual Setup (Alternative)

If you prefer to set up manually:

1. **Navigate to the project directory:**
   ```bash
   cd /Users/kapilthakare/Projects/auto-cal
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x setup.sh auto_calibrate.sh auto_calibrate.py calibration_gui.py
   ```

3. **Install dependencies:**
   ```bash
   ./setup.sh
   ```

4. **Run the calibration:**
   ```bash
   # Using Python script (recommended)
   python3 auto_calibrate.py

   # Or using bash script
   ./auto_calibrate.sh
   ```

## 🔧 ArgyllCMS Integration

The system now uses ArgyllCMS for direct CLI calibration, which provides:
- Full command-line automation
- Direct instrument control (Spyder5 via -I flag)
- More reliable operation than GUI-based tools
- Better error handling for USB disconnections
- Direct access to calibration tools without GUI overhead

## ⚙️ How It Works

The automation works in the following steps:

1. **Device Detection**: Checks if Spyder5 is connected to your Mac
2. **Ambient Light Estimation**: Determines lighting conditions based on time of day
3. **Profile Selection**: Chooses optimal calibration settings:
   - **Low Light** (evening/night): 5500K, 80 cd/m² - warmer, dimmer profile
   - **Medium Light** (morning/normal): 6500K, 100 cd/m² - standard profile
   - **High Light** (daylight): 6500K, 120 cd/m² - brighter profile
4. **Calibration**: Runs DisplayCAL with selected parameters
5. **Profile Application**: Applies the calibrated profile to your display

## 🔧 Customization

### Python Script (`auto_calibrate.py`)
- Modify the `get_ambient_light()` function to use actual ambient light sensor data if available
- Adjust the time ranges or lighting conditions in the function
- Change gamma, white point, and brightness values in `get_calibration_settings()`

### Bash Script (`auto_calibrate.sh`)
- Similar customization options as the Python script
- Easier to modify if you prefer shell scripting

## 🎨 Color Fine-Tuning

Both scripts now support command-line options to fine-tune colors when you notice color tints:

### Python Script Usage
```bash
# Reduce red by 5%, increase green by 3%
python3 auto_calibrate.py --red -5 --green 3

# Increase blue by 10%, set brightness to 110
python3 auto_calibrate.py --blue 10 --brightness 110

# Custom gamma and white point with color adjustments
python3 auto_calibrate.py --gamma 2.4 --white-point 6000 --red -2 --blue 5

# Use a custom profile name
python3 auto_calibrate.py --red -3 --profile-name "MyCustomProfile"
```

### Bash Script Usage
```bash
# Reduce red by 5%, increase green by 3%
./auto_calibrate.sh --red -5 --green 3

# Increase blue by 10%, set brightness to 110
./auto_calibrate.sh --blue 10 --brightness 110

# Custom gamma and white point with color adjustments
./auto_calibrate.sh --gamma 2.4 --white-point 6000 --red -2 --blue 5

# Use a custom profile name
./auto_calibrate.sh --red -3 --profile-name "MyCustomProfile"
```

### Available Options
- `--red PERCENT`: Fine-tune red channel in percentage (-100 to 100)
- `--green PERCENT`: Fine-tune green channel in percentage (-100 to 100)
- `--blue PERCENT`: Fine-tune blue channel in percentage (-100 to 100)
- `--brightness VALUE`: Override brightness setting (cd/m²)
- `--gamma VALUE`: Override gamma setting (e.g., 2.2)
- `--white-point VALUE`: Override white point in Kelvin (e.g., 6500)
- `--profile-name NAME`: Custom profile name
- `--verbose` or `-v`: Enable verbose logging (Python script only)

### Fine-Tuning Guidelines
- **Red Tint**: Reduce red value (e.g., `--red -5`)
- **Green Tint**: Reduce green value (e.g., `--green -5`)
- **Blue Tint**: Reduce blue value (e.g., `--blue -5`)
- **Yellow Tint**: Reduce red and green slightly (e.g., `--red -3 --green -3`)
- **Purple Tint**: Reduce red and blue slightly (e.g., `--red -3 --blue -3`)
- **Too Cool (Blue) Tint**: Reduce blue and increase red/green
- **Too Warm (Yellow/Orange) Tint**: Reduce red/green and increase blue

Start with small adjustments (±2% to ±5%) and gradually increase if needed.

## 🖥️ Real-Time GUI Application

The system now includes a real-time GUI application that provides visual controls for calibration:

### Launch the GUI
```bash
python3 calibration_gui.py
```

### GUI Features
- **Device Status**: Shows whether your Spyder5 device is connected
- **Calibration Settings**:
  - Ambient light condition selection
  - Gamma adjustment
  - White point setting (Kelvin)
  - Brightness setting (cd/m²)
- **Color Fine-Tuning**:
  - Real-time RGB adjustment sliders (-100% to +100%)
  - Visual color preview
  - Full-screen preview mode
- **Profile Management**:
  - Custom profile naming
  - Save/load presets
- **Calibration Process**:
  - Start/Cancel buttons
  - Progress bar
  - Real-time log output

### Using the GUI
1. Connect your Spyder5 device
2. Launch the GUI with `python3 calibration_gui.py`
3. Adjust settings using the sliders and input fields
4. Use the "Preview Color Changes" button to see adjustments on your screen
5. Click "Start Calibration" to begin the process
6. Monitor progress in the log output

The GUI provides an intuitive way to visualize and adjust your display calibration settings before running the actual calibration process.

### Troubleshooting "Instrument Access Failed" Error
If you encounter the "Instrument Access Failed" error:
1. Ensure your Spyder5 device is properly connected to your Mac
2. Close any other applications that might be using the device (like other calibration software)
3. Try unplugging and reconnecting the Spyder5 device
4. Restart your Mac if the device is still not accessible

## 📊 Calibration Profiles

The system creates different profiles based on lighting conditions:

- **LowLight_Profile**: For evening/night use (warmer, dimmer)
- **MediumLight_Profile**: For normal indoor lighting
- **HighLight_Profile**: For bright daylight conditions

Each profile is timestamped to maintain a history of calibrations.

## 📁 Log Files

All calibration attempts are logged to `calibration.log` in the same directory. Check this file if you encounter issues:

```bash
tail -f calibration.log  # Monitor calibration in real-time
```

## 🔄 Scheduling Automatic Calibration

You can schedule automatic calibration using macOS's `launchd`:

1. Create a plist file in `~/Library/LaunchAgents/`:
   ```bash
   nano ~/Library/LaunchAgents/com.user.displaycal.plist
   ```

2. Add the following content (modify paths as needed):
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.user.displaycal</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>/Users/yourusername/Projects/auto-cal/auto_calibrate.py</string>
       </array>
       <key>StartCalendarInterval</key>
       <array>
           <dict>
               <key>Hour</key>
               <integer>8</integer>
               <key>Minute</key>
               <integer>0</integer>
           </dict>
           <dict>
               <key>Hour</key>
               <integer>13</integer>
               <key>Minute</key>
               <integer>0</integer>
           </dict>
           <dict>
               <key>Hour</key>
               <integer>19</integer>
               <key>Minute</key>
               <integer>0</integer>
           </dict>
       </array>
       <key>StandardOutPath</key>
       <string>/tmp/displaycal.out</string>
       <key>StandardErrorPath</key>
       <string>/tmp/displaycal.err</string>
   </dict>
   </plist>
   ```

3. Load the job:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.user.displaycal.plist
   ```

## 🆘 Troubleshooting

### Common Issues:

1. **"Spyder5 device not detected"**:
   - Ensure the device is properly plugged in
   - Check if other applications can access the device
   - Try a different USB port

2. **"DisplayCAL not found"**:
   - Run `./setup.sh` again to ensure proper installation
   - Verify DisplayCAL is installed in `/Applications`

3. **Calibration fails during measurement**:
   - Ensure the Spyder5 sensor is properly positioned on the screen
   - Make sure nothing is blocking the sensor
   - Ensure the display brightness is not set too low

### Manual Calibration:

If automation fails, you can still use DisplayCAL manually:
1. Open DisplayCAL from Applications
2. Follow the on-screen instructions to calibrate your display
3. Use the same lighting-appropriate settings as defined in this script

## 📚 Additional Resources

- [DisplayCAL Documentation](https://displaycal.net/)
- [X-Rite Spyder5 Manual](https://www.xrite.com/service-support/product-documentation/color-management-devices/spyder/spyder5)
- [macOS Accessibility Display Settings](https://support.apple.com/guide/mac-help/change-display-settings-mchl4fb32d64/mac)

## 🤝 Contributing

If you have improvements for the macOS automation:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request with a clear description

## 📄 License

This project is available for personal and commercial use. See the LICENSE file for more details.