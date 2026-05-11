import os
import platform
import queue
import re
import shutil
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import PhotoImage, filedialog, messagebox, scrolledtext, ttk
import ttkbootstrap as tb
from PIL import Image, ImageTk
from ttkbootstrap.constants import *

from python.benchmark.main_window import start_benchmark
from python.clocks import monitor_clock_speed, update_clock_speed
from python.core_picker import open_core_picker
from python.dependencies import install_dependencies
from python.styling import apply_theme_on_load, toggle_dark_mode
from python.temperature import monitor_temperature, update_temperature
from python.errors import (
    clear_error_log,
    monitor_error_status,
    show_error_log,
    toggle_error_log,
    update_error_log,
    update_error_status,
)
from python.logs import (
    clear_current_test,
    clear_output,
    export_log,
    log_message,
    monitor_current_test,
    open_output_window,
    process_log_queue,
    set_current_test,
)
from python.options import (
    parse_settings_options,
    register_settings_traces,
    save_settings,
    update_settings_content,
)
from python.system import (
    detect_cpu_topology,
    full_reset,
    on_close,
    refresh_system_info,
    reset_button,
    check_browser_dependency,
)
from python.ui import (
    make_section,
    configure_numeric_spinbox,
    setup_styles,
    build_header,
    build_info_row,
    build_error_section,
    build_settings,
    build_controls,
)
from python.timers import (
    start_timer,
    stop_timer,
    reset_timer,
    monitor_process_status,
)
from python.testing import (
    run_stress_test,
    start_stress_test,
    stop_stress_test,
    on_process_stop,
)

class StressTestGUI:

    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", lambda: on_close(self))
        self.root.title("Thread Stepper (3.10)")
        self.root.geometry("700x958")
        self.process = None
        self.is_running = False
        self.benchmark_mode = False
        self.benchmark_window_open = False
        self.log_queue = queue.Queue()
        self.output_windows = []
        self.error_status = False
        self.error_log_visible = False
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_thread = None
        self.setup_ui()
        self.start_monitors()
        full_reset(self)
        update_settings_content(self)
        register_settings_traces(self)
        clear_current_test(self)

    def open_benchmark_window(self):
        if self.benchmark_window_open:
            return
        if self.is_running:
            log_message(self, "Cannot open benchmark while tests are running", "warning")
            return
        self.benchmark_window_open = True
        start_benchmark(self)

    def setup_ui(self):
        # Vars
        self.loops_var = tk.IntVar(value=1)
        self.browsers_var = tk.IntVar(value=1)
        self.light_time_var = tk.IntVar(value=1)
        self.medium_time_var = tk.IntVar(value=1)
        self.heavy_time_var = tk.IntVar(value=1)
        self.all_core_time_var = tk.IntVar(value=1)
        self.all_core_tests_var = tk.IntVar(value=1)
        self.rapid_tests_var = tk.IntVar(value=1)
        self.rapid_time_var = tk.IntVar(value=1)
        self.random_tests_var = tk.IntVar(value=1)
        self.random_time_var = tk.IntVar(value=1)
        self.rest_time_var = tk.IntVar(value=1)
        self.core_blacklist_var = tk.StringVar()
        self.max_ram_var = tk.IntVar(value=1)
        self.advanced_visible = False
        self.all_cores_enabled_var = tk.BooleanVar(value=True)
        self.low_load_enabled_var = tk.BooleanVar(value=True)
        self.single_core_enabled_var = tk.BooleanVar(value=True)
        self.webgl_enabled_var = tk.BooleanVar(value=True)
        # Map test groups
        self.group_vars = {
            "all_cores": [self.all_core_time_var, self.all_core_tests_var],
            "low_load": [self.rapid_tests_var, self.rapid_time_var, self.random_tests_var, self.random_time_var],
            "single_core": [self.light_time_var, self.medium_time_var, self.heavy_time_var],
            "webgl": [self.browsers_var],
        }
        # Layout
        main_container = ttk.Frame(self.root, padding=10)
        main_container.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        for i in range(10):
            main_container.rowconfigure(i, weight=1 if i == 6 else 0)
        build_header(self, main_container)
        build_info_row(self, main_container)
        build_error_section(self, main_container)
        build_settings(self, main_container)
        build_controls(self, main_container)
        setup_styles(self)
        apply_theme_on_load(self)

    def start_monitors(self):
        threading.Thread(target=monitor_error_status, args=(self,), daemon=True).start()
        threading.Thread(target=monitor_clock_speed, args=(self,), daemon=True).start()
        threading.Thread(target=process_log_queue, args=(self,), daemon=True).start()
        threading.Thread(target=monitor_process_status, args=(self,), daemon=True).start()
        threading.Thread(target=monitor_current_test, args=(self,), daemon=True).start()
        threading.Thread(target=monitor_temperature, args=(self,), daemon=True).start()
        threading.Thread(target=self.periodic_rank_killer, daemon=True).start()

    def periodic_rank_killer(self):
        while True:
            if not self.benchmark_window_open:
                result = subprocess.run(["pgrep", "-f", "rank.sh"], capture_output=True)
                if result.returncode == 0:
                    subprocess.run(["pkill", "-9", "-f", "rank.sh"], stderr=subprocess.DEVNULL)
            time.sleep(1)

    def kill_rank_processes(self):
        while not self.benchmark_window_open:
            subprocess.run(["pkill", "-9", "-f", "./functions/benchmark/rank.sh"], stderr=subprocess.DEVNULL)
            time.sleep(0.1)

# Entry point
def main():
    os.makedirs("./logs", exist_ok=True)
    if not os.path.exists("./config/user.settings"):
        with open("./config/user.settings", "w") as f:
            f.write("#!/bin/bash\n\n# Test Configuration\nTHREADS=4\nDURATION=60\nINTENSITY=high\n")
    detect_cpu_topology()
    if not os.path.exists("./logs/clock.log"):
        with open("./logs/clock.log", "w") as f:
            f.write("0")
    if not os.path.exists("./logs/errors.log"):
        with open("./logs/errors.log", "w") as f:
            f.write("false")
    if not os.path.exists("./logs/current.log"):
        with open("./logs/current.log", "w") as f:
            f.write("Waiting...")
    if not os.path.exists("./logs/benchmark.log"):
        with open("./logs/current.log", "w") as f:
            f.write("")
    if not os.path.exists("./logs/output.log"):
        with open("./logs/current.log", "w") as f:
            f.write("")
    if not os.path.exists("./logs/threads.log"):
        with open("./logs/threads.log", "w") as f:
            f.write("0, 0")
    root = tb.Window(themename="flatly")
    root.resizable(False, False)
    icon = PhotoImage(file="favicon.png")
    root.iconphoto(True, icon)
    app = StressTestGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()