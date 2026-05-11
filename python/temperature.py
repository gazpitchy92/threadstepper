import time
from tkinter import messagebox
from python.clocks import update_clock_speed

TEMP_LOG = "./logs/temperature.log"
POLL_INTERVAL = 2


def read_temperature():
    try:
        with open(TEMP_LOG, "r") as f:
            raw = f.read().strip()
        if not raw:
            return "N/A"
        val = float(raw)
        return f"{val:.0f}°C"
    except (FileNotFoundError, ValueError):
        return "N/A"


def update_temperature(app):
    temp_str = read_temperature()
    if temp_str == "N/A":
        fg, bg = "#17a2b8", "#e8f4f8"
    else:
        val = float(temp_str.replace("°C", ""))
        if val >= 95:
            fg, bg = "#ffffff", "#dc3545"
        elif val >= 80:
            fg, bg = "#ffffff", "#e67e00"
        elif val >= 65:
            fg, bg = "#856404", "#fff3cd"
        else:
            fg, bg = "#155724", "#d4edda"

    app.root.after(0, lambda: app.temp_label_top.config(text=temp_str, fg=fg, bg=bg))


def monitor_temperature(app):
    while True:
        update_temperature(app)
        time.sleep(POLL_INTERVAL)


def reset_temperature(self):
    try:
        with open(TEMP_LOG, "w") as f:
            f.write("0.0")
        update_clock_speed(self)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to reset clock speed: {str(e)}")
