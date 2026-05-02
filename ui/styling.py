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

def toggle_dark_mode(self):
    if self.dark_mode_btn.cget("text") == "🌙 Dark Mode":
        # Switch to Dark Mode
        self.dark_mode_btn.config(text="☀️ Light Mode")
        
        # Dark mode colors
        bg_dark = "#1e1e1e"
        fg_dark = "#ffffff"
        entry_bg = "#2d2d2d"
        frame_bg = "#2d2d2d"
        
        # Change main container background
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                style = ttk.Style()
                style.configure("TFrame", background=bg_dark)
                style.configure("TLabel", background=bg_dark, foreground=fg_dark)
                style.configure("TLabelframe", background=bg_dark, foreground=fg_dark)
                style.configure("TLabelframe.Label", background=bg_dark, foreground=fg_dark)
        
        # Change specific widgets
        self.root.configure(bg=bg_dark)
        self.timer_label.configure(bg=entry_bg, fg=fg_dark)
        
    else:
        # Switch to Light Mode (original colors)
        self.dark_mode_btn.config(text="🌙 Dark Mode")
        
        # Light mode colors (your original)
        bg_light = "#f0f0f0"
        fg_light = "#000000"
        entry_bg = "#ffffff"
        
        # Reset styles
        style = ttk.Style()
        style.configure("TFrame", background=bg_light)
        style.configure("TLabel", background=bg_light, foreground=fg_light)
        style.configure("TLabelframe", background=bg_light, foreground=fg_light)
        style.configure("TLabelframe.Label", background=bg_light, foreground=fg_light)
        
        # Reset specific widgets
        self.root.configure(bg=bg_light)
        self.output_text.configure(bg=entry_bg, fg=fg_light, insertbackground=fg_light)
        self.error_text.configure(bg=entry_bg, fg=fg_light, insertbackground=fg_light)
        self.clock_label_top.configure(bg="#e8f4f8", fg="#17a2b8")
        self.clock_label_bottom.configure(bg="#e8f4f8", fg="#17a2b8")
        self.error_indicator.configure(bg="#d4edda", fg="#155724")
        self.timer_label.configure(bg="#f0f0f0", fg="#28a745")