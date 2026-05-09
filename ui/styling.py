import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import re
from PIL import Image, ImageTk

# apply theme on load
def apply_theme_on_load(self, settings_path="./settings"):
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                content = f.read()
            match = re.search(r"^dark_mode=(\d+)", content, re.MULTILINE)
            if match:
                mode = int(match.group(1))
                if mode == 1:
                    dark_mode(self)
                else:
                    light_mode(self)
    except Exception:
        pass

# Save topology
def save_dark_mode(self, mode, settings_path="./settings"):
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                content = f.read()
            if re.search(r"^dark_mode=", content, re.MULTILINE):
                content = re.sub(r"^dark_mode=.*", f"dark_mode={mode}", content, flags=re.MULTILINE)
            else:
                content += f"\ndark_mode={mode}"
            with open(settings_path, "w") as f:
                f.write(content)
    except Exception:
        pass

# Toggle between dark and light
def toggle_dark_mode(self):
    if self.dark_mode_btn.cget("text") == "☾ Dark Mode":
        dark_mode(self)
    else:
        light_mode(self)

# Switch to light mode
def light_mode(self):
    self.dark_mode_btn.config(text="☾ Dark Mode")
    
    # Colors
    bg_light = "#f0f0f0"
    fg_light = "#000000"
    entry_bg = "#ffffff"
    
    # Update elements
    style = ttk.Style()
    style.configure("TFrame", background=bg_light)
    style.configure("TLabel", background=bg_light, foreground=fg_light)
    style.configure("TLabelframe", background=bg_light, foreground=fg_light)
    style.configure("TLabelframe.Label", background=bg_light, foreground=fg_light)
    
    self.root.configure(bg=bg_light)
    self.output_text.configure(bg=entry_bg, fg=fg_light, insertbackground=fg_light)
    self.clock_label_top.configure(bg="#e8f4f8", fg="#17a2b8")
    self.timer_label.configure(bg="#f0f0f0", fg="#28a745")
    self.header_label.configure(bg=bg_light, fg=fg_light)

    # Save
    for lbl in getattr(self, '_section_labels', []):
        lbl.configure(foreground="#000000")
    save_dark_mode(self, 0)

# Switch to dark Mode
def dark_mode(self):
    self.dark_mode_btn.config(text="◌ Light Mode")
    
    # Colors
    bg_dark = "#1e1e1e"
    fg_dark = "#ffffff"
    entry_bg = "#2d2d2d"
    frame_bg = "#2d2d2d"
    
    # Update elements
    for widget in self.root.winfo_children():
        if isinstance(widget, ttk.Frame):
            style = ttk.Style()
            style.configure("TFrame", background=bg_dark)
            style.configure("TLabel", background=bg_dark, foreground=fg_dark)
            style.configure("TLabelframe", background=bg_dark, foreground=fg_dark)
            style.configure("TLabelframe.Label", background=bg_dark, foreground=fg_dark)
    
    self.root.configure(bg=bg_dark)
    self.timer_label.configure(bg=entry_bg, fg=fg_dark)
    self.header_label.configure(bg=bg_dark, fg=fg_dark)

    # Save to settings
    for lbl in getattr(self, '_section_labels', []):
        lbl.configure(foreground="#ffffff")
    save_dark_mode(self, 1)
