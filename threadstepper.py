import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import threading
import time
import os
import queue
from datetime import datetime
import platform

class StressTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Thread Stepper")
        self.root.geometry("800x800")
        
        # Process tracking
        self.process = None
        self.is_running = False
        self.log_queue = queue.Queue()
        
        # Error tracking
        self.error_status = False
        self.error_log_visible = False
        
        # Setup UI
        self.setup_ui()
        
        # Start monitoring threads
        self.start_monitors()
        
        # Check existing files
        self.update_settings_content()
        self.update_error_status()
        self.update_error_log()
        self.update_clock_speed()

    def setup_ui(self):
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=0)
        main_container.rowconfigure(2, weight=0)  # Error log panel row
        main_container.rowconfigure(3, weight=1)
        
        # Top Section: Settings File Editor
        settings_frame = ttk.LabelFrame(main_container, text="Settings File Editor (./settings.sh)", padding="10")
        settings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.rowconfigure(0, weight=1)
        
        # Settings text area with scrollbar
        self.settings_text = scrolledtext.ScrolledText(settings_frame, width=60, height=15, wrap=tk.NONE, font=('Consolas', 10))
        self.settings_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Settings buttons
        settings_btn_frame = ttk.Frame(settings_frame)
        settings_btn_frame.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
        
        ttk.Button(settings_btn_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(settings_btn_frame, text="Reload", command=self.update_settings_content).pack(side=tk.LEFT, padx=2)
        
        # Middle Section: Status Indicators
        middle_frame = ttk.Frame(main_container)
        middle_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.columnconfigure(1, weight=1)
        
        # Left: Error Status Indicator
        error_status_frame = ttk.LabelFrame(middle_frame, text="Error Status", padding="10")
        error_status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Error status display with large indicator
        self.error_indicator_frame = ttk.Frame(error_status_frame)
        self.error_indicator_frame.pack(fill=tk.BOTH, expand=True)
        
        self.error_indicator = tk.Label(
            self.error_indicator_frame, 
            text="NO ERRORS", 
            font=('Arial', 16, 'bold'),
            bg='#d4edda',
            fg='#155724',
            relief=tk.RAISED,
            padx=20,
            pady=10
        )
        self.error_indicator.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Error status buttons
        error_btn_frame = ttk.Frame(error_status_frame)
        error_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.toggle_error_btn = ttk.Button(
            error_btn_frame, 
            text="Show Error Log", 
            command=self.toggle_error_log
        )
        self.toggle_error_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(error_btn_frame, text="Refresh Status", command=self.update_error_status).pack(side=tk.LEFT, padx=2)
        
        # Right: CPU Clock Speed
        clock_frame = ttk.LabelFrame(middle_frame, text="Highest Recorded CPU Clock Speed", padding="10")
        clock_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Clock speed display
        clock_display_frame = ttk.Frame(clock_frame)
        clock_display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.clock_label = tk.Label(
            clock_display_frame, 
            text="N/A", 
            font=('Arial', 24, 'bold'), 
            fg='#17a2b8',
            bg='#e8f4f8',
            relief=tk.RAISED,
            padx=20,
            pady=15
        )
        self.clock_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        clock_btn_frame = ttk.Frame(clock_frame)
        clock_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(clock_btn_frame, text="Refresh", command=self.update_clock_speed).pack(side=tk.LEFT, padx=2)
        
        # Collapsible Error Log Section
        self.error_log_container = ttk.LabelFrame(main_container, text="Error Log Details", padding="5")
        self.error_log_container.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        self.error_log_container.grid_remove()  # Hidden by default
        
        # Error log text area
        self.error_text = scrolledtext.ScrolledText(
            self.error_log_container, 
            width=80, 
            height=8, 
            wrap=tk.WORD, 
            font=('Consolas', 9)
        )
        self.error_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.error_log_container.columnconfigure(0, weight=1)
        self.error_log_container.rowconfigure(0, weight=1)
        
        # Error log buttons
        error_log_btn_frame = ttk.Frame(self.error_log_container)
        error_log_btn_frame.grid(row=1, column=0, sticky=tk.E, pady=(0, 5))
        ttk.Button(error_log_btn_frame, text="Clear Log", command=self.clear_error_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(error_log_btn_frame, text="Refresh", command=self.update_error_log).pack(side=tk.LEFT, padx=2)
        
        # Bottom Section: Output and Controls
        output_frame = ttk.LabelFrame(main_container, text="Stress Test Output", padding="10")
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=(0, 5))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, width=80, height=15, wrap=tk.WORD, font=('Consolas', 10))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(main_container)
        control_frame.grid(row=4, column=0, columnspan=2, sticky=tk.E, pady=(0, 10))
        
        # Add Install Dependencies button first
        ttk.Button(control_frame, text="📦 Install Dependencies", 
                  command=self.install_dependencies,
                  style="Install.TButton").pack(side=tk.LEFT, padx=2)
        
        self.start_button = ttk.Button(control_frame, text="▶ Start Thread Stepper", 
                                      command=self.start_stress_test, 
                                      style="Start.TButton")
        self.start_button.pack(side=tk.LEFT, padx=2)
        
        self.stop_button = ttk.Button(control_frame, text="■ Stop", 
                                     command=self.stop_stress_test, 
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(control_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Export Log...", command=self.export_log).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_bar = ttk.Label(main_container, text="Ready", relief=tk.SUNKEN)
        self.status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Configure styles
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Start.TButton", foreground="green", font=('Arial', 10, 'bold'))
        style.configure("Install.TButton", foreground="blue", font=('Arial', 10, 'bold'))
        
        # Configure tags for text highlighting
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("warning", foreground="orange")
        self.output_text.tag_config("info", foreground="blue")

    def install_dependencies(self):
        """Open install.sh in a new terminal window"""
        install_script = "./install.sh"
        
        if not os.path.exists(install_script):
            messagebox.showerror("File Not Found", 
                f"install.sh not found in current directory.\n\n"
                f"Current directory: {os.getcwd()}\n"
                f"Expected at: {install_script}")
            return
        
        # Make sure install.sh is executable
        try:
            os.chmod(install_script, 0o755)
        except:
            pass  # Ignore permission errors
        
        # Determine terminal command based on platform
        system = platform.system()
        
        try:
            if system == "Linux":
                # Try various Linux terminals
                terminals = [
                    ["x-terminal-emulator", "-e", f"bash -c '{install_script}; echo \"Press Enter to close...\"; read'"],
                    ["gnome-terminal", "--", "bash", "-c", f"{install_script}; echo 'Press Enter to close...'; read"],
                    ["konsole", "-e", "bash", "-c", f"{install_script}; echo 'Press Enter to close...'; read"],
                    ["xterm", "-e", "bash", "-c", f"{install_script}; echo 'Press Enter to close...'; read"],
                    ["terminator", "-e", f"bash -c '{install_script}; echo \"Press Enter to close...\"; read'"],
                    ["xfce4-terminal", "-e", f"bash -c '{install_script}; echo \"Press Enter to close...\"; read'"]
                ]
                
                for terminal_cmd in terminals:
                    try:
                        subprocess.Popen(terminal_cmd, start_new_session=True)
                        self.log_message(f"Opening terminal to run install.sh...", "info")
                        self.log_message("Follow installation steps in the terminal window.", "info")
                        return
                    except:
                        continue
                
                # If no terminal worked, try with bash directly
                subprocess.Popen(["bash", install_script], start_new_session=True)
                self.log_message("Running install.sh in background...", "info")
                
            elif system == "Darwin":  # macOS
                apple_script = f'''
                tell application "Terminal"
                    do script "cd '{os.getcwd()}' && ./install.sh"
                    activate
                end tell
                '''
                subprocess.Popen(["osascript", "-e", apple_script])
                self.log_message("Opening Terminal to run install.sh...", "info")
                
            elif system == "Windows":
                # Windows - use PowerShell or CMD
                try:
                    subprocess.Popen(["powershell", "-Command", f"Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"{os.getcwd()}\"; .\\install.sh'"], 
                                   shell=True)
                except:
                    subprocess.Popen(["cmd", "/k", install_script], shell=True)
                self.log_message("Opening PowerShell to run install.sh...", "info")
            
            self.status_bar.config(text="Running install.sh in new terminal...")
            
        except Exception as e:
            error_msg = f"Failed to open terminal: {str(e)}"
            self.log_message(error_msg, "error")
            messagebox.showerror("Error", error_msg)

    # [ALL THE REST OF THE METHODS REMAIN EXACTLY THE SAME AS YOUR PROVIDED CODE]
    # I'll keep them here for completeness, but they're identical to what you provided
    
    def start_monitors(self):
        """Start background threads for monitoring files"""
        # Monitor error status
        threading.Thread(target=self.monitor_error_status, daemon=True).start()
        
        # Monitor clock speed
        threading.Thread(target=self.monitor_clock_speed, daemon=True).start()
        
        # Process log queue
        threading.Thread(target=self.process_log_queue, daemon=True).start()

    def update_settings_content(self):
        """Load settings.sh content"""
        try:
            if os.path.exists("./settings.sh"):
                with open("./settings.sh", 'r') as f:
                    content = f.read()
                    self.settings_text.delete(1.0, tk.END)
                    self.settings_text.insert(1.0, content)
                self.status_bar.config(text="Settings loaded successfully")
            else:
                self.settings_text.delete(1.0, tk.END)
                self.settings_text.insert(1.0, "# settings.sh not found\n# Create this file to configure your stress test")
                self.status_bar.config(text="settings.sh not found - create it to configure your test")
        except Exception as e:
            self.log_message(f"Error loading settings: {str(e)}", "error")

    def save_settings(self):
        """Save settings.sh content"""
        try:
            content = self.settings_text.get(1.0, tk.END)
            with open("./settings.sh", 'w') as f:
                f.write(content)
            self.status_bar.config(text="Settings saved successfully")
            self.log_message("Settings saved", "success")
        except Exception as e:
            self.log_message(f"Error saving settings: {str(e)}", "error")

    def update_error_status(self):
        """Update error status from the first line of error log"""
        try:
            if os.path.exists("./logs/errors.log"):
                with open("./logs/errors.log", 'r') as f:
                    first_line = f.readline().strip()
                    
                self.error_status = (first_line.upper() == "TRUE")
                
                # Update indicator
                if self.error_status:
                    self.error_indicator.config(
                        text="ERRORS DETECTED!",
                        bg='#f8d7da',
                        fg='#721c24'
                    )
                    self.toggle_error_btn.config(text="Hide Error Log")
                    
                    # Auto-show error log if errors detected
                    if not self.error_log_visible:
                        self.show_error_log()
                else:
                    self.error_indicator.config(
                        text="NO ERRORS",
                        bg='#d4edda',
                        fg='#155724'
                    )
                    self.toggle_error_btn.config(text="Show Error Log")
                    
                    # Auto-hide error log if no errors
                    if self.error_log_visible:
                        self.hide_error_log()
                        
                return self.error_status
            else:
                self.error_status = False
                self.error_indicator.config(
                    text="NO ERROR LOG FILE",
                    bg='#fff3cd',
                    fg='#856404'
                )
                return False
                
        except Exception as e:
            self.error_status = False
            self.error_indicator.config(
                text="ERROR READING STATUS",
                bg='#f8d7da',
                fg='#721c24'
            )
            return False

    def monitor_error_status(self):
        """Monitor error status for changes"""
        last_mtime = 0
        while True:
            try:
                if os.path.exists("./logs/errors.log"):
                    current_mtime = os.path.getmtime("./logs/errors.log")
                    if current_mtime > last_mtime:
                        last_mtime = current_mtime
                        self.root.after(0, self.update_error_status)
                        self.root.after(0, self.update_error_log)
            except:
                pass
            time.sleep(1)

    def update_error_log(self):
        """Update error log display (skip first line)"""
        try:
            if os.path.exists("./logs/errors.log"):
                with open("./logs/errors.log", 'r') as f:
                    lines = f.readlines()
                    
                    # Skip first line (True/False status line)
                    if len(lines) > 1:
                        content = ''.join(lines[1:])
                    else:
                        content = "(No error details)"
                        
                    self.error_text.delete(1.0, tk.END)
                    self.error_text.insert(1.0, content)
                    
                    # Apply color coding
                    self.highlight_error_log()
                    
                    # Scroll to end
                    self.error_text.see(tk.END)
            else:
                self.error_text.delete(1.0, tk.END)
                self.error_text.insert(1.0, "Error log file not found")
                
        except Exception as e:
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(1.0, f"Error reading error log: {str(e)}")

    def highlight_error_log(self):
        """Apply syntax highlighting to error log"""
        content = self.error_text.get(1.0, tk.END)
        
        # Clear existing tags
        for tag in ["error_highlight", "warning_highlight", "info_highlight"]:
            self.error_text.tag_remove(tag, 1.0, tk.END)
        
        # Configure tags
        self.error_text.tag_config("error_highlight", background="#f8d7da", foreground="#721c24")
        self.error_text.tag_config("warning_highlight", background="#fff3cd", foreground="#856404")
        self.error_text.tag_config("info_highlight", background="#d1ecf1", foreground="#0c5460")
        
        # Simple highlighting based on keywords
        lines = content.split('\n')
        line_num = 1
        for line in lines:
            lower_line = line.lower()
            
            if any(word in lower_line for word in ['error', 'failed', 'fatal', 'exception', 'crash']):
                start_pos = f"{line_num}.0"
                end_pos = f"{line_num}.{len(line)}"
                self.error_text.tag_add("error_highlight", start_pos, end_pos)
            elif any(word in lower_line for word in ['warning', 'alert', 'notice']):
                start_pos = f"{line_num}.0"
                end_pos = f"{line_num}.{len(line)}"
                self.error_text.tag_add("warning_highlight", start_pos, end_pos)
            elif any(word in lower_line for word in ['info', 'debug', 'trace']):
                start_pos = f"{line_num}.0"
                end_pos = f"{line_num}.{len(line)}"
                self.error_text.tag_add("info_highlight", start_pos, end_pos)
            
            line_num += 1

    def toggle_error_log(self):
        """Toggle error log visibility"""
        if self.error_log_visible:
            self.hide_error_log()
        else:
            self.show_error_log()

    def show_error_log(self):
        """Show the error log panel"""
        self.error_log_container.grid()
        self.error_log_visible = True
        self.toggle_error_btn.config(text="Hide Error Log")
        self.update_error_log()
        # Adjust row weights to accommodate the new panel
        self.root.update()

    def hide_error_log(self):
        """Hide the error log panel"""
        self.error_log_container.grid_remove()
        self.error_log_visible = False
        self.toggle_error_btn.config(text="Show Error Log")
        # Reset row weights
        self.root.update()

    def update_clock_speed(self):
        """Update CPU clock speed display"""
        try:
            if os.path.exists("./logs/clock.log"):
                with open("./logs/clock.log", 'r') as f:
                    clock_speed = f.read().strip()
                    if clock_speed:
                        # Format display text
                        display_text = clock_speed
                        self.clock_label.config(text=display_text)
                        
                        # Change color based on value
                        try:
                            # Extract numeric value
                            import re
                            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", clock_speed)
                            if numbers:
                                value = float(numbers[0])
                                if "GHz" in clock_speed.upper():
                                    if value > 4.0:
                                        self.clock_label.config(fg='#dc3545', bg='#f8d7da')  # Red
                                    elif value > 3.0:
                                        self.clock_label.config(fg='#fd7e14', bg='#fff3cd')  # Orange
                                    else:
                                        self.clock_label.config(fg='#28a745', bg='#d4edda')  # Green
                                else:
                                    # Assume MHz or other unit
                                    self.clock_label.config(fg='#17a2b8', bg='#e8f4f8')  # Teal
                        except:
                            # If parsing fails, use default color
                            self.clock_label.config(fg='#17a2b8', bg='#e8f4f8')
                    else:
                        self.clock_label.config(text="No data", fg='#6c757d', bg='#f8f9fa')
            else:
                self.clock_label.config(text="No clock.log file", fg='#6c757d', bg='#f8f9fa')
        except Exception as e:
            self.clock_label.config(text="Error reading", fg='#721c24', bg='#f8d7da')

    def monitor_clock_speed(self):
        """Monitor clock speed file for changes"""
        last_mtime = 0
        while True:
            try:
                if os.path.exists("./logs/clock.log"):
                    current_mtime = os.path.getmtime("./logs/clock.log")
                    if current_mtime > last_mtime:
                        last_mtime = current_mtime
                        self.root.after(0, self.update_clock_speed)
            except:
                pass
            time.sleep(0.5)

    def clear_error_log(self):
        """Clear the error log file (preserve status line)"""
        try:
            if os.path.exists("./logs/errors.log"):
                with open("./logs/errors.log", 'r') as f:
                    lines = f.readlines()
                
                # Keep only the first line (True/False status)
                if lines:
                    with open("./logs/errors.log", 'w') as f:
                        f.write(lines[0])
                else:
                    # If file is empty, write default False status
                    with open("./logs/errors.log", 'w') as f:
                        f.write("False\n")
                
                self.update_error_status()
                self.update_error_log()
                self.log_message("Error log cleared", "info")
        except Exception as e:
            self.log_message(f"Error clearing log: {str(e)}", "error")

    def start_stress_test(self):
        """Start the stress test process"""
        if self.is_running:
            return
            
        # Clear previous output
        self.clear_output()
        
        # Check if script exists
        if not os.path.exists("./threadstepper"):
            self.log_message("Error: ./threadstepper not found!", "error")
            return
        
        # Update UI state
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start the process in a separate thread
        self.log_message(f"Starting stress test at {datetime.now().strftime('%H:%M:%S')}", "info")
        self.status_bar.config(text="Stress test running...")
        
        threading.Thread(target=self.run_stress_test, daemon=True).start()

    def run_stress_test(self):
        """Run the stress test process"""
        try:
            # Make script executable
            os.chmod("./threadstepper", 0o755)
            
            # Run the process
            self.process = subprocess.Popen(
                ["./threadstepper"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in real-time
            for line in self.process.stdout:
                if line:
                    self.log_queue.put(line.strip())
            
            # Get return code
            return_code = self.process.wait()
            
            # Process completed
            self.log_queue.put(f"\nProcess completed with return code: {return_code}")
            
        except Exception as e:
            self.log_queue.put(f"Error running stress test: {str(e)}")
        finally:
            self.process = None
            self.is_running = False
            self.root.after(0, self.on_process_stop)

    def on_process_stop(self):
        """Update UI when process stops"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_bar.config(text="Stress test stopped")
        self.log_message(f"Stress test stopped at {datetime.now().strftime('%H:%M:%S')}", "info")

    def stop_stress_test(self):
        """Stop the running stress test"""
        if self.process and self.is_running:
            self.process.terminate()
            self.log_message("Stopping stress test...", "warning")
            self.status_bar.config(text="Stopping stress test...")

    def process_log_queue(self):
        """Process messages from the log queue"""
        while True:
            try:
                message = self.log_queue.get_nowait()
                self.root.after(0, lambda msg=message: self.log_message(msg))
            except queue.Empty:
                time.sleep(0.1)

    def log_message(self, message, tag="info"):
        """Add a message to the output text area"""
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.output_text.insert(tk.END, timestamp + message + "\n", tag)
        self.output_text.see(tk.END)
        self.output_text.update_idletasks()

    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)

    def export_log(self):
        """Export the output log to a file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                content = self.output_text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(content)
                self.log_message(f"Log exported to {filename}", "success")
        except Exception as e:
            self.log_message(f"Error exporting log: {str(e)}", "error")

def main():
    # Create directories if they don't exist
    os.makedirs("./logs", exist_ok=True)
    
    # Create sample files if they don't exist
    if not os.path.exists("./settings.sh"):
        with open("./settings.sh", 'w') as f:
            f.write("#!/bin/bash\n\n# Stress Test Configuration\nTHREADS=4\nDURATION=60\nINTENSITY=high\n")
    
    if not os.path.exists("./logs/clock.log"):
        with open("./logs/clock.log", 'w') as f:
            f.write("4.2 GHz (Highest Recorded)")
    
    if not os.path.exists("./logs/errors.log"):
        with open("./logs/errors.log", 'w') as f:
            f.write("False\n")
    
    # Create a dummy threadstepper script if it doesn't exist
    if not os.path.exists("./threadstepper"):
        with open("./threadstepper", 'w') as f:
            f.write("""#!/bin/bash
echo "Starting stress test..."
echo "Using configuration:"
cat ./settings.sh
echo ""
for i in {1..10}; do
    echo "Stress test iteration $i/10"
    echo "$((i * 10))% complete"
    sleep 1
done
echo "Stress test complete!"
""")
    
    # Start the GUI
    root = tk.Tk()
    app = StressTestGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()