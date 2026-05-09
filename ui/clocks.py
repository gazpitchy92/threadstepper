import os
import time
import tkinter as tk
from tkinter import messagebox

def reset_clock_speed(self):
    try:
        with open("./logs/clock.log", 'w') as f:
            f.write("0")
        update_clock_speed(self)
        self.status_bar.config(text="Clock speed reset to 0")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to reset clock speed: {str(e)}")

def monitor_clock_speed(self):
    last_mtime = 0
    while True:
        try:
            if os.path.exists("./logs/clock.log"):
                current_mtime = os.path.getmtime("./logs/clock.log")
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    self.root.after(0, lambda: update_clock_speed(self))
        except:
            pass
        time.sleep(0.5)

def update_clock_speed(self):
    try:
        if os.path.exists("./logs/clock.log"):
            with open("./logs/clock.log", "r") as f:
                clock_speed = f.read().strip()

            if clock_speed:
                self.clock_label_top.config(
                    text=clock_speed,
                    fg="#17a2b8",
                    bg="#e8f4f8"
                )
            else:
                self.clock_label_top.config(
                    text="No data",
                    fg="#6c757d",
                    bg="#f8f9fa"
                )
        else:
            self.clock_label_top.config(
                text="No clock.log file",
                fg="#6c757d",
                bg="#f8f9fa"
            )

    except:
        self.clock_label_top.config(
            text="Error reading",
            fg="#721c24",
            bg="#f8d7da"
        )