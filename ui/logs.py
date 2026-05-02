import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, PhotoImage
import subprocess
import threading
import time
import os
import queue
from datetime import datetime
import platform
import re
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

def export_log(self):
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

def log_message(self, message, tag="info"):
    import re
    
    timestamp = datetime.now().strftime("[%H:%M:%S] ")
    message = re.sub(r'\x1b\(B|\033\(B', '', message)
    
    ansi_color_map = {
        '30': 'black', '31': 'red', '32': 'green', '33': 'yellow',
        '34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white',
        '90': 'bright_black', '91': 'bright_red', '92': 'bright_green',
        '93': 'bright_yellow', '94': 'bright_blue', '95': 'bright_magenta',
        '96': 'bright_cyan', '97': 'bright_white'
    }
    
    for code, color_name in ansi_color_map.items():
        tag_name = f"ansi_{color_name}"
        if tag_name not in self.output_text.tag_names():
            color_hex = {
                'black': '#000000', 'red': '#cd0000', 'green': '#00cd00', 'yellow': '#cdcd00',
                'blue': '#0000ee', 'magenta': '#cd00cd', 'cyan': '#00cdcd', 'white': '#e5e5e5',
                'bright_black': '#7f7f7f', 'bright_red': '#ff0000', 'bright_green': '#00ff00',
                'bright_yellow': '#ffff00', 'bright_blue': '#5c5cff', 'bright_magenta': '#ff00ff',
                'bright_cyan': '#00ffff', 'bright_white': '#ffffff'
            }.get(color_name, '#000000')
            self.output_text.tag_config(tag_name, foreground=color_hex)
    
    self.output_text.insert(tk.END, timestamp, tag)
    
    ansi_pattern = r'\x1b\[([0-9;]+)m|\033\[([0-9;]+)m|\[([0-9;]+)m'
    reset_pattern = r'\(B\[m|\[m|\x1b\[m|\033\[m'
    
    current_tag = tag
    last_pos = 0
    
    full_message = message
    full_message = re.sub(reset_pattern, '\x00RESET\x00', full_message)
    
    for match in re.finditer(ansi_pattern, full_message):
        text_before = full_message[last_pos:match.start()]
        if text_before:
            parts = text_before.split('\x00RESET\x00')
            for i, part in enumerate(parts):
                if part:
                    self.output_text.insert(tk.END, part, current_tag)
                if i < len(parts) - 1:
                    current_tag = tag
        
        code = match.group(1) or match.group(2) or match.group(3)
        if code == '0' or code == '':
            current_tag = tag 
        else:
            codes = code.split(';')
            for c in codes:
                if c in ansi_color_map:
                    current_tag = f"ansi_{ansi_color_map[c]}"
                    break
        
        last_pos = match.end()
    
    remaining = full_message[last_pos:]
    if remaining:
        parts = remaining.split('\x00RESET\x00')
        for i, part in enumerate(parts):
            if part:
                self.output_text.insert(tk.END, part, current_tag)
            if i < len(parts) - 1:
                current_tag = tag
    
    self.output_text.insert(tk.END, "\n", tag)
    self.output_text.see(tk.END)
    self.output_text.update_idletasks()

def clear_output(self):
    clear_current_test(self)
    self.output_text.delete(1.0, tk.END)
    self.reset_timer()

def clear_current_test(self):
    try:
        if os.path.exists("./logs/current.log"):
            with open("./logs/current.log", "w") as f:
                f.write("Waiting...")
            update_current_test(self)

    except Exception as e:
        log_message(self, f"Error clearing test: {str(e)}", "error")

def set_current_test(self, test):
    try:
        if os.path.exists("./logs/current.log"):
            with open("./logs/current.log", "w") as f:
                f.write(test)
            update_current_test(self)

    except Exception as e:
        log_message(self, f"Error setting current test: {str(e)}", "error")

def monitor_current_test(self):
    last_mtime = 0
    while True:
        try:
            if os.path.exists("./logs/current.log"):
                current_mtime = os.path.getmtime("./logs/current.log")
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    self.root.after(0, lambda: update_current_test(self))
        except:
            pass
        time.sleep(0.5)

def update_current_test(self):
    try:
        if os.path.exists("./logs/current.log"):
            with open("./logs/current.log", "r") as f:
                lines = f.readlines()
            
            if lines:
                # Get first line (test name) and second line (progress)
                test_name = lines[0].strip() if len(lines) > 0 else ""
                progress = lines[1].strip() if len(lines) > 1 else ""
                
                # Combine with newline for multi-line display
                display_text = f"{test_name}\n{progress}"
                
                if test_name == "Starting...":
                    self.clock_label_bottom.config(
                        text="⚠️ " + test_name + "\n" + progress,
                        fg="#856404",
                        bg="#fff3cd"
                    )
                elif test_name == "Waiting...":
                    self.clock_label_bottom.config(
                        text="💤 " + test_name + "\n" + progress,
                        fg="#343a40",
                        bg="#e9ecef",
                    )
                elif test_name == "Failed!":
                    self.clock_label_bottom.config(
                        text="😤 " + test_name + "\n" + progress,
                        fg="#ffffff",
                        bg="#dc3545",
                    )
                elif test_name == "Rapid Tests":
                    self.clock_label_bottom.config(
                        text="🌀 " + test_name + "\n" + progress,
                        fg="#28a745",
                        bg="#d4edda",
                    )
                elif test_name == "Random Tests":
                    self.clock_label_bottom.config(
                        text="🌀 " + test_name + "\n" + progress,
                        fg="#28a745",
                        bg="#d4edda",
                    )
                elif test_name == "Random Tests":
                    self.clock_label_bottom.config(
                        text="🌀 " + test_name + "\n" + progress,
                        fg="#28a745",
                        bg="#d4edda",
                    )
                elif test_name == "Single Core Tests":
                    self.clock_label_bottom.config(
                        text="🎯 " + test_name + "\n" + progress,
                        fg="#28a745",
                        bg="#d4edda",
                    )
                else:
                    self.clock_label_bottom.config(
                        text="🔥 " + test_name + "\n" + progress,
                        fg="#28a745",
                        bg="#d4edda"
                    )
            else:
                self.clock_label_bottom.config(
                    text="No data",
                    fg="#6c757d",
                    bg="#f8f9fa"
                )
        else:
            self.clock_label_bottom.config(
                text="No current.log file",
                fg="#6c757d",
                bg="#f8f9fa"
            )

    except Exception as e:
        self.clock_label_bottom.config(
            text="Error reading",
            fg="#721c24",
            bg="#f8d7da"
        )