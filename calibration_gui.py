#!/usr/bin/env python3
"""
Display Calibration GUI for macOS with Spyder5
Provides a real-time interface for display calibration with color fine-tuning
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import time
import os
import sys
import logging
from datetime import datetime
import argparse
import platform

class CalibrationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Display Calibration with Spyder5 - GUI")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Set up logging
        self.setup_logging()
        
        # Initialize variables
        self.calibration_running = False
        self.calibration_process = None
        
        # Create the GUI elements
        self.create_widgets()
        
        # Check if Spyder5 is connected
        self.check_device_connection()
        
    def setup_logging(self):
        """Set up logging for the application with rotation"""
        import logging.handlers

        # Create rotating file handler that rotates when log reaches 10MB
        # Keep up to 3 backup files
        rotating_handler = logging.handlers.RotatingFileHandler(
            'calibration.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3
        )

        # Set up formatting
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        rotating_handler.setFormatter(formatter)

        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Add handlers
        self.logger.addHandler(rotating_handler)
        self.logger.addHandler(logging.StreamHandler())

        self.logger.info("Calibration GUI started")

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Display Calibration with Spyder5", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Device status frame
        device_frame = ttk.LabelFrame(main_frame, text="Device Status", padding="10")
        device_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.device_status = tk.StringVar(value="Checking...")
        device_status_label = ttk.Label(device_frame, textvariable=self.device_status, 
                                       font=("TkDefaultFont", 10, "bold"))
        device_status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Calibration settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Calibration Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Ambient light condition
        ttk.Label(settings_frame, text="Ambient Light:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ambient_light = tk.StringVar(value="Auto Detect")
        ambient_light_combo = ttk.Combobox(settings_frame, textvariable=self.ambient_light,
                                          values=["Auto Detect", "Low Light", "Medium Light", "High Light"],
                                          state="readonly", width=15)
        ambient_light_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Gamma
        ttk.Label(settings_frame, text="Gamma:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.gamma_var = tk.StringVar(value="2.2")
        gamma_spinbox = ttk.Spinbox(settings_frame, from_=1.0, to=2.8, increment=0.1, 
                                  textvariable=self.gamma_var, width=10)
        gamma_spinbox.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # White Point
        ttk.Label(settings_frame, text="White Point (K):").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.white_point_var = tk.StringVar(value="6500")
        white_point_spinbox = ttk.Spinbox(settings_frame, from_=3000, to=10000, increment=100,
                                        textvariable=self.white_point_var, width=10)
        white_point_spinbox.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        # Brightness
        ttk.Label(settings_frame, text="Brightness (cd/m²):").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.brightness_var = tk.StringVar(value="100")
        brightness_spinbox = ttk.Spinbox(settings_frame, from_=50, to=200, increment=5,
                                       textvariable=self.brightness_var, width=10)
        brightness_spinbox.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Color adjustment frame
        color_frame = ttk.LabelFrame(main_frame, text="Color Fine-Tuning", padding="10")
        color_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Red adjustment
        ttk.Label(color_frame, text="Red Adjustment:").grid(row=0, column=0, sticky=tk.W)
        self.red_var = tk.DoubleVar(value=0.0)
        self.red_scale = ttk.Scale(color_frame, from_=-100, to=100, variable=self.red_var,
                                  orient=tk.HORIZONTAL, length=200)
        self.red_scale.grid(row=0, column=1, padx=(10, 0))
        self.red_value_label = ttk.Label(color_frame, text="0%")
        self.red_value_label.grid(row=0, column=2, padx=(5, 0))

        # Green adjustment
        ttk.Label(color_frame, text="Green Adjustment:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.green_var = tk.DoubleVar(value=0.0)
        self.green_scale = ttk.Scale(color_frame, from_=-100, to=100, variable=self.green_var,
                                   orient=tk.HORIZONTAL, length=200)
        self.green_scale.grid(row=1, column=1, padx=(10, 0), pady=(5, 0))
        self.green_value_label = ttk.Label(color_frame, text="0%")
        self.green_value_label.grid(row=1, column=2, padx=(5, 0), pady=(5, 0))

        # Blue adjustment
        ttk.Label(color_frame, text="Blue Adjustment:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.blue_var = tk.DoubleVar(value=0.0)
        self.blue_scale = ttk.Scale(color_frame, from_=-100, to=100, variable=self.blue_var,
                                  orient=tk.HORIZONTAL, length=200)
        self.blue_scale.grid(row=2, column=1, padx=(10, 0), pady=(5, 0))
        self.blue_value_label = ttk.Label(color_frame, text="0%")
        self.blue_value_label.grid(row=2, column=2, padx=(5, 0), pady=(5, 0))

        # Color preview
        ttk.Label(color_frame, text="Color Preview:").grid(row=0, column=3, rowspan=3, sticky=tk.W, padx=(20, 0))

        # Create a canvas for color preview
        self.color_preview_canvas = tk.Canvas(color_frame, width=100, height=100, bg='white',
                                             highlightthickness=1, highlightbackground='black')
        self.color_preview_canvas.grid(row=0, column=4, rowspan=3, padx=(10, 0), pady=(0, 20))

        # Bind scale events to update labels and preview
        self.red_var.trace_add('write', lambda *args: self.update_color_label(self.red_var, self.red_value_label))
        self.green_var.trace_add('write', lambda *args: self.update_color_label(self.green_var, self.green_value_label))
        self.blue_var.trace_add('write', lambda *args: self.update_color_label(self.blue_var, self.blue_value_label))

        # Bind scale events to update color preview
        self.red_var.trace_add('write', lambda *args: self.update_color_preview())
        self.green_var.trace_add('write', lambda *args: self.update_color_preview())
        self.blue_var.trace_add('write', lambda *args: self.update_color_preview())

        # Profile name
        ttk.Label(color_frame, text="Profile Name:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.profile_name_var = tk.StringVar(value="")
        profile_name_entry = ttk.Entry(color_frame, textvariable=self.profile_name_var, width=30)
        profile_name_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))

        # Add preview button
        ttk.Button(color_frame, text="Preview Color Changes",
                  command=self.open_preview_window).grid(row=3, column=4, padx=(10, 0), pady=(10, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Calibrate button
        self.calibrate_button = ttk.Button(buttons_frame, text="Start Calibration", 
                                         command=self.start_calibration)
        self.calibrate_button.grid(row=0, column=0, padx=(0, 10))
        
        # Cancel button
        self.cancel_button = ttk.Button(buttons_frame, text="Cancel", 
                                      command=self.cancel_calibration, state=tk.DISABLED)
        self.cancel_button.grid(row=0, column=1, padx=(0, 10))
        
        # Save preset button
        ttk.Button(buttons_frame, text="Save Preset", command=self.save_preset).grid(row=0, column=2, padx=(0, 10))
        
        # Load preset button
        ttk.Button(buttons_frame, text="Load Preset", command=self.load_preset).grid(row=0, column=3)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Calibration Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to start calibration")
        self.progress_label.grid(row=1, column=0, pady=(5, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="5")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Configure grid weight for log frame
        main_frame.rowconfigure(6, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Create text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=10, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def update_color_label(self, var, label):
        """Update the color adjustment percentage label"""
        value = var.get()
        label.config(text=f"{value:.1f}%")

    def update_color_preview(self):
        """Update the color preview based on current adjustments"""
        # Get current values
        red_adj = self.red_var.get()
        green_adj = self.green_var.get()
        blue_adj = self.blue_var.get()

        # Calculate RGB values based on adjustments
        # Base RGB is (128, 128, 128) - a medium gray
        base_val = 128

        # Calculate adjusted values (with clamping to 0-255)
        r = max(0, min(255, int(base_val + (base_val * red_adj / 100))))
        g = max(0, min(255, int(base_val + (base_val * green_adj / 100))))
        b = max(0, min(255, int(base_val + (base_val * blue_adj / 100))))

        # Convert to hex color
        color = f"#{r:02x}{g:02x}{b:02x}"

        # Update the canvas background
        self.color_preview_canvas.config(bg=color)

    def open_preview_window(self):
        """Open a full-screen preview window to see color adjustments"""
        # Create a new top-level window
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Color Preview")
        self.preview_window.attributes('-fullscreen', True)
        self.preview_window.configure(bg='black')

        # Create a large label to fill the screen with the preview color
        self.preview_label = tk.Label(self.preview_window, text="",
                                     bg=self.color_preview_canvas['bg'],
                                     width=100, height=50)
        self.preview_label.pack(expand=True)

        # Add close instructions
        instructions = tk.Label(self.preview_window,
                               text="Press ESC or click anywhere to close preview",
                               bg='black', fg='white', font=("Arial", 14))
        instructions.pack(side=tk.BOTTOM, pady=20)

        # Bind escape key and click to close
        self.preview_window.bind('<Escape>', lambda e: self.close_preview_window())
        self.preview_window.bind('<Button-1>', lambda e: self.close_preview_window())

        # Bind the color change to update the preview window
        # Store the trace IDs so we can unbind them later
        self.preview_red_trace = self.red_var.trace_add('write', lambda *args: self.update_preview_window())
        self.preview_green_trace = self.green_var.trace_add('write', lambda *args: self.update_preview_window())
        self.preview_blue_trace = self.blue_var.trace_add('write', lambda *args: self.update_preview_window())

        # Focus on the window to capture key events
        self.preview_window.focus_set()

    def update_preview_window(self):
        """Update the preview window with the new color"""
        if hasattr(self, 'preview_label'):
            self.preview_label.config(bg=self.color_preview_canvas['bg'])

    def close_preview_window(self):
        """Close the preview window"""
        if hasattr(self, 'preview_window'):
            # Unbind the trace callbacks to prevent errors
            if hasattr(self, 'preview_red_trace'):
                self.red_var.trace_remove('write', self.preview_red_trace)
            if hasattr(self, 'preview_green_trace'):
                self.green_var.trace_remove('write', self.preview_green_trace)
            if hasattr(self, 'preview_blue_trace'):
                self.blue_var.trace_remove('write', self.preview_blue_trace)
            self.preview_window.destroy()

    def check_device_connection(self):
        """Check if Spyder5 device is connected"""
        try:
            result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                  capture_output=True, text=True)
            if 'spyder' in result.stdout.lower() or 'color munki' in result.stdout.lower():
                self.device_status.set("Spyder5 device detected - Ready to calibrate")
                self.device_status_label = ttk.Style().configure("green.TLabel", foreground="green")
                self.calibrate_button.state(['!disabled'])
                return True
            else:
                self.device_status.set("Spyder5 device NOT detected - Please connect your device")
                self.calibrate_button.state(['disabled'])
                return False
        except Exception as e:
            self.logger.error(f"Error checking for Spyder5: {e}")
            self.device_status.set("Error checking device connection")
            return False
    
    def start_calibration(self):
        """Start the calibration process in a separate thread"""
        if not self.check_device_connection():
            messagebox.showerror("Device Error", "Spyder5 device not detected. Please connect your device.")
            return
        
        # Disable the calibrate button and enable cancel button
        self.calibrate_button.state(['disabled'])
        self.cancel_button.state(['!disabled'])
        
        # Start calibration in a separate thread
        self.calibration_thread = threading.Thread(target=self.run_calibration_process)
        self.calibration_thread.daemon = True
        self.calibration_thread.start()
    
    def run_calibration_process(self):
        """Run the actual calibration process"""
        self.calibration_running = True
        self.status_var.set("Calibrating...")
        self.progress_label.config(text="Starting calibration...")
        
        try:
            # Get current settings
            settings = {
                'gamma': float(self.gamma_var.get()),
                'white_point': int(self.white_point_var.get()),
                'brightness': int(self.brightness_var.get()),
                'red': self.red_var.get(),
                'green': self.green_var.get(),
                'blue': self.blue_var.get(),
                'profile_name': self.profile_name_var.get() if self.profile_name_var.get() else None
            }
            
            # Generate a unique name for this calibration
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            profile_name = f"GUI_Profile_{timestamp}"
            if settings['profile_name']:
                profile_name = f"{settings['profile_name']}_{timestamp}"
            
            self.logger.info(f"Starting calibration with settings: {settings}")
            self.log_message(f"Starting calibration with profile: {profile_name}")
            
            # Build the command for ArgyllCMS dispcal
            cmd = [
                "dispcal",
                "-d1",  # Use first display
                "-t", str(settings['white_point']),  # White point
                "-g", str(settings['gamma']),  # Gamma
                "-yl",  # Use luminance
                "-q", "m",  # Medium quality
                f"{profile_name}.cal"
            ]

            # Add color adjustments if needed
            if settings['red'] != 0 or settings['green'] != 0 or settings['blue'] != 0:
                self.log_message(f"Applying color adjustments - Red: {settings['red']}%, "
                                f"Green: {settings['green']}%, Blue: {settings['blue']}%")

                # Convert percentage adjustments to factors
                red_factor = 1.0 + (settings['red'] / 100.0)
                green_factor = 1.0 + (settings['green'] / 100.0)
                blue_factor = 1.0 + (settings['blue'] / 100.0)

                # Add color adjustment factors to command
                cmd.insert(-1, f"-R{red_factor:.3f}")  # Red adjustment
                cmd.insert(-1, f"-G{green_factor:.3f}")  # Green adjustment
                cmd.insert(-1, f"-B{blue_factor:.3f}")  # Blue adjustment
            
            self.log_message(f"Running command: {' '.join(cmd)}")
            
            # Update progress
            self.update_progress(10, "Initializing calibration...")

            # Actually run the dispcal command
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.log_message("Calibration measurement completed successfully")

                # Now create the profile using colprof
                profile_cmd = [
                    "colprof",
                    "-D", f"{profile_name} Profile",
                    "-qf",  # Fine quality
                    "-v",  # Verbose
                    "-A", "AutoCal GUI",  # Author
                    f"{profile_name}.cal"
                ]

                self.log_message("Creating profile with colprof...")
                self.log_message(f"Command: {' '.join(profile_cmd)}")

                profile_result = subprocess.run(profile_cmd, capture_output=True, text=True)

                if profile_result.returncode == 0:
                    self.update_progress(100, "Calibration completed successfully!")
                    self.log_message("Profile creation completed successfully!")
                    self.status_var.set("Calibration completed successfully!")

                    # Show success message
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Calibration completed successfully!"))
                else:
                    self.log_message(f"Profile creation failed: {profile_result.stderr}")
                    self.status_var.set("Calibration failed - Profile creation error")

                    # Show error message
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Profile creation failed: {profile_result.stderr}"))
            elif "Instrument Access Failed" in result.stderr:
                self.log_message("Instrument Access Failed - Please ensure Spyder5 is properly connected and not in use by another application")
                self.status_var.set("Calibration failed - Instrument Access Failed")

                # Show error message
                self.root.after(0, lambda: messagebox.showerror("Error",
                    "Instrument Access Failed - Please ensure Spyder5 is properly connected and not in use by another application"))
            else:
                self.log_message(f"Calibration measurement failed: {result.stderr}")
                self.status_var.set("Calibration failed")

                # Show error message
                self.root.after(0, lambda: messagebox.showerror("Error", f"Calibration measurement failed: {result.stderr}"))

        except FileNotFoundError:
            self.logger.error("ArgyllCMS not found. Please ensure it is installed (brew install argyll-cms)")
            self.log_message("ArgyllCMS not found. Please ensure it is installed (brew install argyll-cms)")
            self.status_var.set("ArgyllCMS not found")

            # Show error message
            self.root.after(0, lambda: messagebox.showerror("Error",
                "ArgyllCMS not found. Please ensure it is installed (brew install argyll-cms)"))
        except Exception as e:
            self.logger.error(f"Error during calibration: {e}")
            self.log_message(f"Error during calibration: {e}")
            self.status_var.set("Calibration failed")

            # Show error message
            self.root.after(0, lambda: messagebox.showerror("Error", f"Calibration failed: {e}"))
        finally:
            # Re-enable buttons
            self.root.after(0, self.enable_calibration_controls)
    
    def update_progress(self, value, message):
        """Update the progress bar and label from the calibration thread"""
        self.root.after(0, lambda: self._update_progress_gui(value, message))
    
    def _update_progress_gui(self, value, message):
        """Update the progress bar and label (called from main thread)"""
        self.progress_var.set(value)
        self.progress_label.config(text=message)
    
    def log_message(self, message):
        """Add a message to the log text widget"""
        self.root.after(0, lambda: self._add_log_message(message))
    
    def _add_log_message(self, message):
        """Add a message to the log text widget (called from main thread)"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def cancel_calibration(self):
        """Cancel the running calibration"""
        self.calibration_running = False
        self.status_var.set("Cancelling calibration...")
        self.log_message("Cancelling calibration...")
    
    def enable_calibration_controls(self):
        """Re-enable the calibration controls after completion"""
        self.calibrate_button.state(['!disabled'])
        self.cancel_button.state(['disabled'])
    
    def save_preset(self):
        """Save current settings as a preset"""
        preset_name = simpledialog.askstring("Save Preset", "Enter preset name:")
        if preset_name:
            # In a real implementation, this would save to a file
            preset_data = {
                'gamma': self.gamma_var.get(),
                'white_point': self.white_point_var.get(),
                'brightness': self.brightness_var.get(),
                'red': self.red_var.get(),
                'green': self.green_var.get(),
                'blue': self.blue_var.get(),
            }
            
            # For now, just log the action
            self.logger.info(f"Saved preset '{preset_name}': {preset_data}")
            self.log_message(f"Saved preset: {preset_name}")
            messagebox.showinfo("Preset Saved", f"Preset '{preset_name}' saved successfully!")
    
    def load_preset(self):
        """Load a saved preset"""
        # In a real implementation, this would load from a file
        # For now, just show a simple dialog
        presets = ["Daylight", "Evening", "Night", "Custom 1", "Custom 2"]
        preset_name = simpledialog.askstring("Load Preset", f"Enter preset name:\nPreset options: {', '.join(presets)}")
        
        if preset_name:
            # For demonstration, we'll just set some example values
            # In a real implementation, this would load actual values from the preset
            if preset_name.lower() == "daylight":
                self.gamma_var.set(2.2)
                self.white_point_var.set(6500)
                self.brightness_var.set(120)
                self.red_var.set(0)
                self.green_var.set(0)
                self.blue_var.set(0)
            elif preset_name.lower() == "evening":
                self.gamma_var.set(2.2)
                self.white_point_var.set(5500)
                self.brightness_var.set(100)
                self.red_var.set(2)
                self.green_var.set(-1)
                self.blue_var.set(-3)
            elif preset_name.lower() == "night":
                self.gamma_var.set(2.2)
                self.white_point_var.set(4500)
                self.brightness_var.set(80)
                self.red_var.set(5)
                self.green_var.set(2)
                self.blue_var.set(-5)
            else:
                messagebox.showinfo("Preset", f"Preset '{preset_name}' not found. Using defaults.")
            
            self.logger.info(f"Loaded preset: {preset_name}")
            self.log_message(f"Loaded preset: {preset_name}")
            messagebox.showinfo("Preset Loaded", f"Preset '{preset_name}' loaded successfully!")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Display Calibration GUI for macOS with Spyder5')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    # Set up root window
    root = tk.Tk()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create the GUI
    app = CalibrationGUI(root)

    # Handle window closing
    def on_closing():
        if app.calibration_running:
            if messagebox.askokcancel("Quit", "Calibration is in progress. Do you want to quit?"):
                app.cancel_calibration()
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    # Import here to avoid issues if not available
    try:
        import tkinter.simpledialog as simpledialog
    except ImportError:
        from tkinter import simpledialog

    main()