# Primes & Zooms Display Calibration Runbook

This document guides the technical team on maintaining color accuracy for our editing and client review displays.

## 1. Routine Calibration

### When to run what?

| Method | When to use | Command |
| :--- | :--- | :--- |
| **Instant Auto-Cal** | Daily morning startup. Adapts to current light. | `./auto_calibrate.py --apply-only` |
| **Standard Calibration** | Weekly, or if the "Instant" result looks wrong. | `./run_calibration.sh` (Select Option 1) |
| **Fine-Tune (GUI)** | If a specific client needs a warmer/cooler look. | `./run_calibration.sh` (Select Option 4) |
| **Client Review Mode** | Before a client sits down to review footage. | `./pz-profile switch client-review` |

### Quick Switching

Use the `pz-profile` tool to quickly switch display modes without running a calibration:

```bash
./pz-profile switch editing        # Standard bright profile
./pz-profile switch client-review  # Standardized for accurate color preview
./pz-profile switch dark-room      # Low brightness for night work
```

## 2. Troubleshooting ("This looks off")

If a display looks too red, too green, or too bright:

1.  **Check Ambient Light:** Is direct sunlight hitting the sensor? Cover the sensor and run `./auto_calibrate.py --apply-only`.
2.  **Verify Profile:** Check System Preferences > Displays > Color to see which profile is active.
3.  **Run Diagnostics:** Use the diagnostic tool to gather info for the engineering team.

```bash
./tools/collect-diagnostics.sh
```

Send the resulting `diagnostics_YYYYMMDD.tar.gz` to the lead technician.

## 3. Logs & Maintenance

*   **Logs Location:** `calibration.log` in the project root.
*   **Rotation:** Logs are automatically rotated. Old logs are compressed weekly.

### Error Messages

*   **"Spyder5 device not detected"**: Unplug and replug the USB. Try a different port.
*   **"Instrument Access Failed"**: Close any other software (Spyder utility, etc.) that might be grabbing the device.

## 4. Contact

For persistent issues, contact: Kapil Thakare (kapil@primesandzooms.com)
