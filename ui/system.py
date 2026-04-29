import os
import platform

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


def update_clock_speed(self):
    try:
        if os.path.exists("./logs/clock.log"):
            with open("./logs/clock.log", "r") as f:
                clock_speed = f.read().strip()

            if clock_speed:
                self.clock_label.config(
                    text=clock_speed,
                    fg="#17a2b8",
                    bg="#e8f4f8"
                )
            else:
                self.clock_label.config(
                    text="No data",
                    fg="#6c757d",
                    bg="#f8f9fa"
                )
        else:
            self.clock_label.config(
                text="No clock.log file",
                fg="#6c757d",
                bg="#f8f9fa"
            )

    except:
        self.clock_label.config(
            text="Error reading",
            fg="#721c24",
            bg="#f8d7da"
        )