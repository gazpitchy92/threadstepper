import os
import platform

from ui.logs import log_message, clear_output, clear_current_test
from ui.errors import clear_error_log, update_error_log, update_error_status
from ui.clocks import update_clock_speed

def refresh_system_info(self):
    import psutil

    self.os_label.config(text=f"OS: {platform.system()} {platform.release()}")

    try:
        freq = psutil.cpu_freq()
        min_ghz = freq.min / 1000
        max_ghz = freq.max / 1000
        ram_gb = psutil.virtual_memory().total / 1024**3

        self.cores_label.config(text=f"CPU Cores: {psutil.cpu_count(logical=False)}")
        self.threads_label.config(text=f"CPU Threads: {psutil.cpu_count(logical=True)}")
        self.cpu_freq.config(text=f"CPU Freq.: {min_ghz:.3f}-{max_ghz:.3f} GHz")
        self.ram_label.config(text=f"Total RAM: {ram_gb:.1f} GB")

    except ImportError:
        self.cores_label.config(text="CPU Cores: N/A (install psutil)")
        self.threads_label.config(text="CPU Threads: N/A")
        self.cpu_freq.config(text="CPU Freq.: N/A")
        self.ram_label.config(text="Total RAM: N/A (install psutil)")

    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
            governor = f.read().strip()
    except:
        governor = "N/A"

    self.governor_label.config(text=f"CPU Governor: {governor}")

def full_reset(self):
    try:
        subprocess.run(["pkill", "-f", "threadstepper"])
        subprocess.run(["pkill", "-f", "logger.sh"])
    except Exception as e:
        log_message(self, f"Error killing logger.sh: {str(e)}", "error")
        
    with open("./logs/errors.log", "w") as f:
        f.write("false")
    with open("./logs/clock.log", "w") as f:
        f.write("0")
    with open("./logs/output.log", "w") as f:
        f.write("-- STARTUP --")

    clear_current_test(self)
    clear_error_log(self)
    clear_output(self)
    refresh_system_info(self)
    update_clock_speed(self)
    update_error_log(self)
    update_error_status(self)