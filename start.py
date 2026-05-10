import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, PhotoImage
import subprocess
import threading
import time
import shutil
import os
import queue
from datetime import datetime
import platform
import re
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

from ui.system import (
    refresh_system_info,
    full_reset,
    on_close,
    detect_cpu_topology,
    reset_button
)
from ui.options import (
    parse_settings_options,
    update_settings_content,
    save_settings,
    register_settings_traces
)
from ui.errors import (
    clear_error_log,
    monitor_error_status,
    update_error_log,
    toggle_error_log,
    show_error_log,
    update_error_status
)
from ui.clocks import (
    monitor_clock_speed,
    update_clock_speed
)
from ui.logs import (
    export_log,
    log_message,
    clear_output,
    monitor_current_test,
    clear_current_test,
    set_current_test,
    process_log_queue,
    open_output_window
)
from ui.temperature import (
    monitor_temperature,
    update_temperature
)
from ui.dependencies import install_dependencies
from ui.styling import toggle_dark_mode, apply_theme_on_load
from ui.core_picker import open_core_picker
from ui.benchmark import start_benchmark

class StressTestGUI:

    def __init__(self, root):
        
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", lambda: on_close(self))
        self.root.title("Thread Stepper (3.8)")
        self.root.geometry("700x915")
        
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

    def check_browser_dependency(self):
        result = subprocess.run(
            "compgen -c | grep '^electron[0-9]' | sort -V | tail -1",
            shell=True, executable='/bin/bash',
            capture_output=True, text=True
        )
        return bool(result.stdout.strip())

    def open_benchmark_window(self):
        if self.benchmark_window_open:
            return

        if self.is_running:
            log_message(self, "Cannot open benchmark while tests are running", "warning")
            return

        self.benchmark_window_open = True
        start_benchmark(self)
            
    def setup_ui(self):

        def make_section(parent, title, **kwargs):
            outer = ttk.Frame(parent, **kwargs)
            header = ttk.Frame(outer)
            header.pack(fill="x", pady=(0, 6))
            lbl = ttk.Label(
                header, text=title,
                font=("Segoe UI", 11, "bold"),
                foreground="#000000"
            )
            lbl.pack(side="left")
            ttk.Separator(header, orient="horizontal").pack(
                side="left", fill="x", expand=True, padx=(6, 0), pady=1
            )
            inner = ttk.Frame(outer)
            inner.pack(fill="both", expand=True)
            if not hasattr(self, '_section_labels'):
                self._section_labels = []
            self._section_labels.append(lbl)
            return outer, inner

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

        main_container = ttk.Frame(self.root, padding=10)
        main_container.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        for i in range(10):
            main_container.rowconfigure(i, weight=1 if i == 6 else 0)

        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        img = Image.open("favicon.png").resize((45, 45))
        icon_img = ImageTk.PhotoImage(img)
        self.header_label = tk.Label(header_frame, text=" Thread Stepper", font=("Segoe UI", 18, "bold"), image=icon_img, compound="left")
        self.header_label.pack(side="left")
        self.header_label.image = icon_img

        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side="right")

        self.dark_mode_btn = ttk.Button(button_frame, text="☾ Dark Mode", bootstyle="info-outline", command=lambda: toggle_dark_mode(self))
        self.dark_mode_btn.pack(side="left", padx=(0, 10))

        self.install_dep_btn = ttk.Button(button_frame, text="⌂ Install Dependencies", bootstyle="info", 
            command=lambda: install_dependencies(self))
        self.install_dep_btn.pack(side="left")

        if self.check_browser_dependency():
            self.install_dep_btn.pack_forget()

        info_row = ttk.Frame(main_container)
        info_row.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 0))
        info_row.columnconfigure(0, weight=1)
        info_row.columnconfigure(1, weight=1)
        info_row.rowconfigure(0, weight=1)
        info_row.rowconfigure(1, weight=1)

        system_frame, system_inner = make_section(info_row, "⌕ System Information", padding=10)
        system_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 0))
        system_inner.columnconfigure(0, weight=1)

        top_info_frame = ttk.Frame(system_inner)
        top_info_frame.grid(row=0, column=0, sticky="nw")

        os_row = ttk.Frame(top_info_frame)
        os_row.pack(anchor="w", fill="x", pady=(0, 3))

        ttk.Label(os_row, text="Kernel:", style="InfoTitle.TLabel").pack(side="left")
        self.os_label = ttk.Label(os_row, text=f" {platform.system()} {platform.release()}", style="InfoValue.TLabel")
        self.os_label.pack(side="left")

        gov_row = ttk.Frame(top_info_frame)
        gov_row.pack(anchor="w", fill="x", pady=(0, 3))

        ttk.Label(gov_row, text="Governor:", style="InfoTitle.TLabel").pack(side="left")
        self.governor_label = ttk.Label(gov_row, text=" N/A", style="InfoValue.TLabel")
        self.governor_label.pack(side="left")

        ttk.Frame(system_inner, height=10).grid(row=1, column=0)

        cpu_info_frame = ttk.Frame(system_inner)
        cpu_info_frame.grid(row=2, column=0, sticky="nw")

        cpu_row = ttk.Frame(cpu_info_frame)
        cpu_row.pack(anchor="w", fill="x", pady=(0, 3))

        ttk.Label(cpu_row, text="CPU:", style="InfoTitle.TLabel").pack(side="left")
        self.model_label = ttk.Label(cpu_row, text=" N/A", style="InfoValue.TLabel")
        self.model_label.pack(side="left")

        cores_row = ttk.Frame(cpu_info_frame)
        cores_row.pack(anchor="w", fill="x", pady=(0, 3))

        ttk.Label(cores_row, text="Cores/Threads:", style="InfoTitle.TLabel").pack(side="left")
        self.cores_label = ttk.Label(cores_row, text=" N/A", style="InfoValue.TLabel")
        self.cores_label.pack(side="left")

        sys_btn_frame = ttk.Frame(system_inner)
        sys_btn_frame.grid(row=3, column=0, sticky="ew", pady=(2, 0))

        sys_btn_frame.columnconfigure(0, weight=1)
        sys_btn_frame.columnconfigure(1, weight=1)

        ttk.Button(
            sys_btn_frame,
            text="◷ Benchmark",
            bootstyle="primary-outline",
            command=self.open_benchmark_window
        ).grid(row=0, column=0, sticky="ew", padx=(0, 2))

        ttk.Button(
            sys_btn_frame,
            text="↻ Refresh",
            bootstyle="info-outline",
            command=lambda: refresh_system_info(self)
        ).grid(row=0, column=1, sticky="ew", padx=(2, 0))

        freq_row = ttk.Frame(cpu_info_frame)
        freq_row.pack(anchor="w", fill="x", pady=(0, 3))

        ttk.Label(freq_row, text="Frequency:", style="InfoTitle.TLabel").pack(side="left")
        self.cpu_freq = ttk.Label(freq_row, text=" N/A", style="InfoValue.TLabel")
        self.cpu_freq.pack(side="left")

        info_row.columnconfigure(2, weight=1)

        clock_frame_top, clock_inner_top = make_section(info_row, "⬆ Peak Clock", padding=10)
        clock_frame_top.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        clock_inner_top.columnconfigure(0, weight=1)
        clock_inner_top.rowconfigure(0, weight=1)

        self.clock_label_top = tk.Label(
            clock_inner_top, text="N/A", font=("Segoe UI", 11, "bold"),
            fg="#17a2b8", bg="#e8f4f8", relief="raised", padx=10, pady=4
        )
        self.clock_label_top.grid(row=0, column=0, sticky="nsew")

        temp_frame_top, temp_inner_top = make_section(info_row, "❈ Peak Temp", padding=10)
        temp_frame_top.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        temp_inner_top.columnconfigure(0, weight=1)
        temp_inner_top.rowconfigure(0, weight=1)

        self.temp_label_top = tk.Label(
            temp_inner_top, text="N/A", font=("Segoe UI", 11, "bold"),
            fg="#17a2b8", bg="#e8f4f8", relief="raised", padx=10, pady=4
        )
        self.temp_label_top.grid(row=0, column=0, sticky="nsew")

        clock_frame_bottom, clock_inner_bottom = make_section(info_row, "◇ Current Action", padding=10)
        clock_frame_bottom.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=(5, 0))
        clock_inner_bottom.columnconfigure(0, weight=1)
        clock_inner_bottom.rowconfigure(0, weight=1)

        self.clock_label_bottom = tk.Label(
            clock_inner_bottom, text="N/A", font=("Segoe UI", 11, "bold"),
            fg="#17a2b8", bg="#e8f4f8", relief="raised", padx=10, pady=4,
            justify="center"
        )
        self.clock_label_bottom.grid(row=0, column=0, sticky="nsew")

        error_frame, error_inner = make_section(main_container, "⁉ Error Status", padding=10)
        error_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 2))
        error_inner.columnconfigure(0, weight=1)

        self.error_indicator = tk.Label(
            error_inner, text="NO ERRORS ✔", font=("Segoe UI", 11, "bold"),
            bg="#d4edda", fg="#155724", relief="raised", padx=10, pady=4
        )
        self.error_indicator.grid(row=0, column=0, sticky="nsew")

        error_btn_frame = ttk.Frame(error_inner)
        error_btn_frame.grid(row=1, column=0, sticky="e", pady=(2, 0))

        ttk.Button(error_btn_frame, text="↻ Refresh", bootstyle="info-outline",
            command=lambda: update_error_status(self)).pack(side="right", padx=2)

        self.toggle_error_btn = ttk.Button(error_btn_frame, text="▶ Error Logs", bootstyle="primary-outline",
            command=lambda: toggle_error_log(self))
        self.toggle_error_btn.pack(side="right", padx=2)

        self.error_log_container, error_log_inner = make_section(main_container, "✎ Error Logs", padding=5)
        self.error_log_container.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 2))
        self.error_log_container.grid_remove()

        self.error_text = scrolledtext.ScrolledText(error_log_inner, width=80, height=6, wrap="word", font=("Segoe UI", 12))
        self.error_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        error_log_inner.columnconfigure(0, weight=1)
        error_log_inner.rowconfigure(0, weight=1)

        error_log_btn_frame = ttk.Frame(error_log_inner)
        error_log_btn_frame.grid(row=1, column=0, sticky="e", pady=(0, 2))

        ttk.Button(error_log_btn_frame, text="↻ Refresh", bootstyle="info-outline",
            command=lambda: update_error_log(self)).pack(side="right", padx=2)

        ttk.Button(error_log_btn_frame, text="⇄ Reset", bootstyle="warning-outline",
            command=lambda: clear_error_log(self)).pack(side="right", padx=2)

        settings_inner = ttk.Frame(main_container, padding=10)
        settings_inner.grid(row=4, column=0, sticky="ew", padx=5, pady=(0, 2))
        settings_inner.columnconfigure(0, weight=1)
        settings_inner.columnconfigure(1, weight=1)
        settings_inner.columnconfigure(2, weight=1)

        def make_entry_row(parent, label, var, row):
            parent.columnconfigure(1, weight=1)

            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 6), pady=1)

            ttk.Entry(parent, textvariable=var).grid(
                row=row,
                column=1,
                sticky="ew",
                pady=1
            )
        high_frame, high_inner = make_section(settings_inner, "▦ All Cores", padding=6)
        high_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 0), pady=(0, 2))
        make_entry_row(high_inner, "Time", self.all_core_time_var, 0)
        make_entry_row(high_inner, "Tests", self.all_core_tests_var, 1)

        low_frame, low_inner = make_section(settings_inner, "≡ Low Load", padding=6)
        low_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 2))
        make_entry_row(low_inner, "Rapid Tests", self.rapid_tests_var, 0)
        make_entry_row(low_inner, "Rapid Time", self.rapid_time_var, 1)
        make_entry_row(low_inner, "Rand Tests", self.random_tests_var, 2)
        make_entry_row(low_inner, "Rand Time", self.random_time_var, 3)

        single_frame, single_inner = make_section(settings_inner, "◫ Single Core", padding=6)
        single_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0), pady=(0, 2))
        make_entry_row(single_inner, "Low Time", self.light_time_var, 0)
        make_entry_row(single_inner, "Medium Time", self.medium_time_var, 1)
        make_entry_row(single_inner, "High Time", self.heavy_time_var, 2)

        bottom_settings = ttk.Frame(settings_inner)
        bottom_settings.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(2, 0))
        bottom_settings.columnconfigure(0, weight=1)
        bottom_settings.columnconfigure(1, weight=1)
        bottom_settings.columnconfigure(2, weight=1)

        browser_frame, browser_inner = make_section(bottom_settings, "☉ WebGL Tests", padding=6)
        browser_inner.columnconfigure(1, weight=1)
        browser_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 0))

        self.browsers_label = ttk.Label(browser_inner, text="Instances")
        self.browsers_label.grid(row=0, column=0, sticky="w", padx=(0, 0), pady=3)

        self.browsers_spinbox = ttk.Spinbox(browser_inner, from_=0, to=99, width=6, textvariable=self.browsers_var)
        self.browsers_spinbox.grid(row=0, column=1, sticky="ew", pady=3)

        if not self.check_browser_dependency():
            self.browsers_label.grid_remove()
            self.browsers_spinbox.grid_remove()
            self.browser_dep_label = ttk.Label(
                browser_inner,
                text="⚠ Please install dependencies for this test",
                foreground="#e67e00",
                font=("Segoe UI", 8, "italic")
            )
            self.browser_dep_label.grid(row=0, column=0, sticky="w", pady=(2, 0))

        cores_frame, cores_inner = make_section(bottom_settings, "∼ Enabled Threads", padding=6)
        cores_inner.columnconfigure(0, weight=1)
        cores_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ttk.Button(cores_inner, text="⚙ Configure", bootstyle="primary-outline",
            command=lambda: open_core_picker(self)
        ).grid(row=0, column=0, sticky="ew")

        other_frame, other_inner = make_section(bottom_settings, "Other Options", padding=6)
        other_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        make_entry_row(other_inner, "Rest Time", self.rest_time_var, 0)

        save_frame = ttk.Frame(settings_inner)
        save_frame.grid(row=5, column=0, columnspan=3, sticky="e", pady=(2, 0))

        self.unsaved_label = ttk.Label(save_frame, text="", foreground="#e67e00", font=("Segoe UI", 11, "italic"))
        self.unsaved_label.pack(side="left", padx=(0, 10))

        ttk.Button(save_frame, text="⤓ Save Settings", bootstyle="success",
            command=lambda: save_settings(self)).pack(side="right")

        output_frame, output_inner = make_section(main_container, "⩾ Test Output", padding=10)
        output_frame.grid(row=5, column=0, sticky="nsew", padx=5, pady=(0, 2))
        output_inner.columnconfigure(0, weight=1)
        output_inner.rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(
            output_inner,
            width=80,
            height=2,
            wrap="word",
            font=("Segoe UI", 11)
        )
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        control_frame = ttk.Frame(main_container)
        control_frame.grid(row=6, column=0, sticky="ew", pady=(0, 4))

        style = ttk.Style()
        style.configure(
            "Uniform.TButton",
            padding=(10, 3),
            font=("Segoe UI", 10)
        )

        self.timer_label = tk.Label(
            control_frame,
            text="00:00:00",
            font=("Segoe UI", 11, "bold"),
            fg="#28a745",
            bg="#f0f0f0",
            relief="sunken",
            width=8,
            height=1,
            padx=4,
            pady=0
        )

        self.timer_label.pack(side="left", padx=(20, 2), fill="y")
        ttk.Frame(control_frame).pack(side="left", fill="x", expand=True)

        runs_frame = ttk.Frame(control_frame)
        runs_frame.pack(side="left", padx=(0, 6))

        ttk.Label(runs_frame, text="Test Runs", font=("Segoe UI", 9)).pack(side="left", padx=(0, 4))
        ttk.Spinbox(runs_frame, from_=1, to=999, width=5, textvariable=self.loops_var).pack(side="left")

        self.start_button = ttk.Button(
            control_frame,
            text="▶ Start",
            bootstyle="success",
            command=self.start_stress_test
        )
        self.start_button.pack(side="left", padx=(5,0))

        self.stop_button = ttk.Button(
            control_frame,
            text="⊠ Stop",
            state="disabled",
            bootstyle="danger",
            command=self.stop_stress_test
        )
        self.stop_button.pack(side="left", padx=(5,0))

        ttk.Button(
            control_frame,
            text="⇄ Reset",
            bootstyle="warning-outline",
            command=lambda: reset_button(self)
        ).pack(side="left", padx=(5,0))

        ttk.Button(
            control_frame,
            text="⎘ View Logs",
            bootstyle="primary-outline",
            command=lambda: open_output_window(self)
        ).pack(side="left", padx=(5,20))

        status_frame = ttk.Frame(main_container)
        status_frame.grid(row=7, column=0, sticky="ew", pady=(2, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=0)

        self.status_bar = ttk.Label(status_frame, text="Ready", relief="sunken")
        self.status_bar.grid(row=0, column=0, sticky="ew", padx=(20, 20))

        style.configure("Green.Horizontal.TProgressbar", troughcolor="#e0e0e0", background="#28a745")
        style.map("Green.Horizontal.TProgressbar", background=[("active", "#28a745"), ("!active", "#28a745")])

        self.progress = ttk.Progressbar(
            status_frame,
            style="Green.Horizontal.TProgressbar",
            mode="determinate",
            length=419
        )
        self.progress.grid(row=0, column=1, sticky="ew", padx=(5, 20))
        self.progress.grid_remove()

        self.setup_styles()
        apply_theme_on_load(self)

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Install.TButton", foreground="blue", font=('Arial', 12),)
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("warning", foreground="orange")
        self.output_text.tag_config("info", foreground="blue")

    def start_timer(self):
        self.timer_seconds = 0
        self.timer_running = True
        self.timer_label.config(fg='#28a745')  
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
            self.timer_thread.start()

    def stop_timer(self):
        self.timer_running = False
        self.timer_label.config(fg='#dc3545') 

    def reset_timer(self):
        self.timer_running = False
        self.timer_seconds = 0
        self.root.after(0, lambda: self.timer_label.config(text="00:00:00", fg='#28a745'))

    def update_timer(self):
        while True:
            if self.timer_running:
                hours = self.timer_seconds // 3600
                minutes = (self.timer_seconds % 3600) // 60
                seconds = self.timer_seconds % 60
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.root.after(0, lambda t=time_str: self.timer_label.config(text=t))
                self.timer_seconds += 1
            time.sleep(1)

    def start_monitors(self):
        threading.Thread(target=monitor_error_status, args=(self,), daemon=True).start()
        threading.Thread(target=monitor_clock_speed, args=(self,), daemon=True).start()
        threading.Thread(target=process_log_queue, args=(self,), daemon=True).start()
        threading.Thread(target=self.monitor_process_status, daemon=True).start()
        threading.Thread(target=monitor_current_test, args=(self,), daemon=True).start()
        threading.Thread(target=monitor_temperature, args=(self,), daemon=True).start() 

    def monitor_process_status(self):
        while True:
            if self.is_running and self.process is not None:
                if self.process.poll() is not None: 
                    self.root.after(0, self.stop_timer)
            time.sleep(0.5)

    def start_stress_test(self):
        if self.benchmark_window_open:
            return
        if self.is_running:
            return
            
        full_reset(self)
        set_current_test(self, "Starting...")
        self.reset_timer()
        self.start_timer()
        self.progress.grid()
        self.progress.start(10)

        subprocess.run([
            "notify-send",
            "Thread Stepper",
            f"Tests started at {datetime.now().strftime('%H:%M:%S')}"
        ])
        
        if not os.path.exists("./threadstepper"):
            log_message(self, "Error: ./threadstepper not found!", "error")
            self.stop_timer()
            return
        
        self.is_running = True
        self.benchmark_mode = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        log_message(self, f"Starting tests at {datetime.now().strftime('%H:%M:%S')}", "info")
        self.status_bar.config(text="Tests running...")
        
        threading.Thread(target=self.run_stress_test, daemon=True).start()

    def run_stress_test(self):
        try:
            os.chmod("./threadstepper", 0o755)
            
            self.process = subprocess.Popen(
                ["./threadstepper"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in self.process.stdout:
                if line:
                    self.log_queue.put(line.strip())
            
            return_code = self.process.wait()
            
            self.log_queue.put(f"\nTesting has completed at {datetime.now().strftime('%H:%M:%S')}")
            subprocess.run([
                "notify-send",
                "Thread Stepper",
                f"Testing has completed at {datetime.now().strftime('%H:%M:%S')}"
            ])
            
            update_error_status(self)
            update_error_log(self)
            
        except Exception as e:
            self.log_queue.put(f"Error running tests: {str(e)}")
        finally:
            self.process = None
            self.is_running = False
            self.benchmark_mode = False
            self.root.after(0, self.on_process_stop)
            clear_current_test(self)

    def stop_stress_test(self):
        if self.process and self.is_running:
            self.process.terminate()
        if self.benchmark_mode:
            log_message(self, "Stopping benchmark...", "warning")
            self.status_bar.config(text="Stopping benchmark...")
            subprocess.run([
                "notify-send",
                "Thread Stepper",
                f"Benchmark stopping at {datetime.now().strftime('%H:%M:%S')}"
            ])
        else:
            log_message(self, "Stopping testing, please wait...", "warning")
            self.status_bar.config(text="Stopping testing...")
            self.stop_timer()
            subprocess.run(["pkill", "-f", "threadstepper"])
            subprocess.run(["pkill", "-f", "logger.sh"])
            subprocess.run(["pkill", "-f", "bash -c"])
            subprocess.run(["pkill", "-f", "load_test.sh"])
            subprocess.run(["pkill", "-f", "load_worker.sh"])
            subprocess.run(["pkill", "-f", "launch.js"])
            self.stop_timer()
            self.progress.stop()
            self.progress.grid_remove()

    def on_process_stop(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.benchmark_mode:
            self.status_bar.config(text="Benchmark stopped")
            update_error_status(self)
            self.stop_timer()
            self.progress.stop()
            self.progress.grid_remove()
        else:
            self.status_bar.config(text="Testing stopped")
            update_error_status(self)
            self.stop_timer()
            self.progress.stop()
            self.progress.grid_remove()
        self.is_running = False
        self.benchmark_mode = False

def main():
    os.makedirs("./logs", exist_ok=True)
    
    if not os.path.exists("./settings"):
        with open("./settings", 'w') as f:
            f.write("#!/bin/bash\n\n# Test Configuration\nTHREADS=4\nDURATION=60\nINTENSITY=high\n")
    
    detect_cpu_topology()

    if not os.path.exists("./logs/clock.log"):
        with open("./logs/clock.log", 'w') as f:
            f.write("0")
    if not os.path.exists("./logs/errors.log"):
        with open("./logs/errors.log", 'w') as f:
            f.write("false")
    if not os.path.exists("./logs/current.log"):
        with open("./logs/current.log", 'w') as f:
            f.write("Waiting...")
    if not os.path.exists("./logs/benchmark.log"):
        with open("./logs/current.log", 'w') as f:
            f.write("")
    if not os.path.exists("./logs/output.log"):
        with open("./logs/current.log", 'w') as f:
            f.write("")
    if not os.path.exists("./logs/threads.log"):
        with open("./logs/threads.log", 'w') as f:
            f.write("0, 0")

    root = tb.Window(themename="flatly") 
    root.resizable(False, False)
    icon = PhotoImage(file="favicon.png")
    root.iconphoto(True, icon)
    app = StressTestGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()