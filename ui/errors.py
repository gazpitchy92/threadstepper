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

def clear_error_log(self):
    try:
        if os.path.exists("./logs/errors.log"):

            with open("./logs/errors.log", "w") as f:
                f.write("false")

            update_error_status(self)
            update_error_log(self)
            self.log_message("Error log cleared", "info")

    except Exception as e:
        self.log_message(f"Error clearing log: {str(e)}", "error")

def monitor_error_status(self):
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
        time.sleep(5)

def update_error_log(self):
    try:
        if os.path.exists("./logs/errors.log"):
            with open("./logs/errors.log", 'r') as f:
                lines = f.readlines()
                
                if len(lines) > 1:
                    content = ''.join(lines[1:])
                else:
                    content = "(No error details)"
                    
                self.error_text.delete(1.0, tk.END)
                self.error_text.insert(1.0, content)
                
                highlight_error_log(self)
                
                self.error_text.see(tk.END)
        else:
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(1.0, "Error log file not found")
            
    except Exception as e:
        self.error_text.delete(1.0, tk.END)
        self.error_text.insert(1.0, f"Error reading error log: {str(e)}")

def highlight_error_log(self):
    content = self.error_text.get(1.0, tk.END)
    
    for tag in ["error_highlight", "warning_highlight", "info_highlight"]:
        self.error_text.tag_remove(tag, 1.0, tk.END)
    
    self.error_text.tag_config("error_highlight", background="#f8d7da", foreground="#721c24")
    self.error_text.tag_config("warning_highlight", background="#fff3cd", foreground="#856404")
    self.error_text.tag_config("info_highlight", background="#d1ecf1", foreground="#0c5460")
    
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
    if self.error_log_visible:
        hide_error_log(self)
    else:
        show_error_log(self)

def show_error_log(self):
    self.error_log_container.grid()
    self.error_log_visible = True
    self.toggle_error_btn.config(text="👆 Hide Logs")
    update_error_log(self)
    self.root.update()

def hide_error_log(self):
    self.error_log_container.grid_remove()
    self.error_log_visible = False
    self.toggle_error_btn.config(text="👇 Show Logs")
    self.bootstyle="success-outline"
    self.root.update()

def update_error_status(self):
    try:
        status = False
        if os.path.exists("./logs/errors.log"):
            with open("./logs/errors.log", 'r') as f:
                first_line = f.readline().strip()
                status = first_line.lower() == "true"

        self.error_status = status

        if self.error_status:
            self.error_indicator.config(
                text="ERRORS DETECTED 😤", 
                bg='#f8d7da',
                fg='#721c24'
            )

            if self.is_running:
                self.stop_stress_test()
                try:
                    subprocess.run(["pkill", "-f", "threadstepper"])
                    subprocess.run(["pkill", "-f", "logger.sh"])
                except Exception as e:
                    self.log_message(f"Error killing logger.sh: {str(e)}", "error")

            if not self.error_log_visible:
                self.show_error_log()

        else:
            self.error_indicator.config(
                text="NO ERRORS 🙂",
                bg='#d4edda',
                fg='#155724'
            )

        self.toggle_error_btn.config(
            text="👆 Hide Logs" if self.error_log_visible else "👇 Show Logs"
        )

        return self.error_status

    except Exception as e:
        self.error_status = False
        self.error_indicator.config(
            text="ERROR READING STATUS",
            bg='#f8d7da',
            fg='#721c24'
        )
        return False