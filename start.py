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

from ui.system import refresh_system_info, full_reset
from ui.options import parse_settings_options, update_settings_content, save_settings, register_settings_traces
from ui.errors import clear_error_log, monitor_error_status, update_error_log, toggle_error_log, show_error_log, update_error_status
from ui.clocks import reset_clock_speed, monitor_clock_speed, update_clock_speed
from ui.logs import export_log, log_message, clear_output, monitor_current_test, clear_current_test, set_current_test
from ui.dependencies import install_dependencies

class StressTestGUI:
    def __init__(self, root):
        
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("Thread Stepper (2.8)")
        self.root.geometry("800x1060")
        
        self.process = None
        self.is_running = False
        self.benchmark_mode = False
        self.log_queue = queue.Queue()
        
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
    
    def on_close(self):
        if self.is_running and self.process:
            self.process.terminate()
            self.process = None
        full_reset(self)
        clear_current_test(self)
        self.stop_stress_test()
        self.root.destroy()

    def setup_ui(self):
        self.loops_var = tk.IntVar(value=1)
        self.browsers_var = tk.IntVar(value=1)
        self.light_time_var = tk.IntVar(value=1)
        self.medium_time_var = tk.IntVar(value=1)
        self.heavy_time_var = tk.IntVar(value=1)
        self.all_core_time_var = tk.IntVar(value=1)
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

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        img = Image.open("favicon.png").resize((45, 45))
        icon_img = ImageTk.PhotoImage(img)
        header_label = tk.Label(header_frame, text=" Thread Stepper", font=("Segoe UI", 18, "bold"), image=icon_img, compound="left")
        header_label.pack(side="left")
        header_label.image = icon_img
        ttk.Button(header_frame, text="📦 Install Dependencies", bootstyle="primary", command=lambda: install_dependencies(self)).pack(side="right")

        # System Info
        info_row = ttk.Frame(main_container)
        info_row.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 0))
        info_row.columnconfigure(0, weight=1)
        info_row.columnconfigure(1, weight=1)
        info_row.rowconfigure(0, weight=1)
        info_row.rowconfigure(1, weight=1) 

        system_frame = ttk.LabelFrame(info_row, text="🔎 System Information", padding=10)
        system_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 0))
        system_frame.columnconfigure(0, weight=1)

        labels_frame = ttk.Frame(system_frame)
        labels_frame.grid(row=0, column=0, sticky="nw")
        self.os_label = ttk.Label(labels_frame, text=f"OS: {platform.system()} {platform.release()}")
        self.cores_label = ttk.Label(labels_frame, text="CPU Cores: N/A")
        self.threads_label = ttk.Label(labels_frame, text="CPU Threads: N/A")
        self.cpu_freq = ttk.Label(labels_frame, text="CPU Freq.: N/A")
        self.ram_label = ttk.Label(labels_frame, text="Total RAM: N/A")
        self.governor_label = ttk.Label(labels_frame, text="CPU Governor: N/A")
        for lbl in [self.os_label, self.cores_label, self.threads_label, self.cpu_freq, self.ram_label, self.governor_label]:
            lbl.pack(anchor="w", pady=(0, 2))
        sys_btn_frame = ttk.Frame(system_frame)
        sys_btn_frame.grid(row=1, column=0, sticky="e", pady=(5, 0))
        ttk.Button(sys_btn_frame, text="🔁 Refresh", bootstyle="success-outline", command=lambda: refresh_system_info(self)).pack(side="right")

        # CPU Clock
        clock_frame_top = ttk.LabelFrame(info_row, text="🚀 Highest CPU Clock (GHz)", padding=10)
        clock_frame_top.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        clock_frame_top.columnconfigure(0, weight=1)
        clock_frame_top.rowconfigure(0, weight=1)
        self.clock_label_top = tk.Label(
            clock_frame_top, text="N/A", font=("Segoe UI", 12, "bold"),
            fg="#17a2b8", bg="#e8f4f8", relief="raised", padx=20, pady=10
        )
        self.clock_label_top.grid(row=0, column=0, sticky="nsew")

        # Current Test
        clock_frame_bottom = ttk.LabelFrame(info_row, text="🛠️ Current Action", padding=10)
        clock_frame_bottom.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        clock_frame_bottom.columnconfigure(0, weight=1)
        clock_frame_bottom.rowconfigure(0, weight=1)
        self.clock_label_bottom = tk.Label(
            clock_frame_bottom, text="N/A", font=("Segoe UI", 12, "bold"),
            fg="#17a2b8", bg="#e8f4f8", relief="raised", padx=20, pady=10,
            justify="center"
        )
        self.clock_label_bottom.grid(row=0, column=0, sticky="nsew")

        # Error Status
        error_frame = ttk.LabelFrame(main_container, text="⁉ Error Status", padding=10)
        error_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))
        error_frame.columnconfigure(0, weight=1)
        self.error_indicator = tk.Label(
            error_frame, text="NO ERRORS 🙂", font=("Segoe UI", 12, "bold"),
            bg="#d4edda", fg="#155724", relief="raised", padx=20, pady=10
        )
        self.error_indicator.grid(row=0, column=0, sticky="nsew")
        error_btn_frame = ttk.Frame(error_frame)
        error_btn_frame.grid(row=1, column=0, sticky="e", pady=(5, 0))
        ttk.Button(error_btn_frame, text="🔁 Refresh", bootstyle="success-outline", command=lambda: update_error_status(self)).pack(side="right", padx=2)
        self.toggle_error_btn = ttk.Button(error_btn_frame, text="👇 Show Logs", bootstyle="success-outline", command=lambda: toggle_error_log(self))
        self.toggle_error_btn.pack(side="right", padx=2)

        # Error Logs
        self.error_log_container = ttk.LabelFrame(main_container, text="✎ Error Logs", padding=5)
        self.error_log_container.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.error_log_container.grid_remove()
        self.error_text = scrolledtext.ScrolledText(self.error_log_container, width=80, height=8, wrap="word", font=("Segoe UI", 12))
        self.error_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.error_log_container.columnconfigure(0, weight=1)
        self.error_log_container.rowconfigure(0, weight=1)
        error_log_btn_frame = ttk.Frame(self.error_log_container)
        error_log_btn_frame.grid(row=1, column=0, sticky="e", pady=(0, 5))
        ttk.Button(error_log_btn_frame, text="🔁 Refresh", bootstyle="success-outline", command=lambda: update_error_log(self)).pack(side="right", padx=2)
        ttk.Button(error_log_btn_frame, text="❎ Clear", bootstyle="success-outline", command=lambda: clear_error_log(self)).pack(side="right", padx=2)

        # Settings
        settings_outer = ttk.LabelFrame(main_container, text="🖥 Settings", padding=10)
        settings_outer.grid(row=4, column=0, sticky="ew", padx=5, pady=(0, 5))
        settings_outer.columnconfigure(0, weight=1)
        settings_outer.columnconfigure(1, weight=1)
        settings_outer.columnconfigure(2, weight=1)

        def make_entry_row(parent, label, var, row):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 0), pady=3)
            ttk.Entry(parent, width=6, textvariable=var).grid(row=row, column=1, sticky="w", pady=3)

        # Test Loops
        loops_frame = ttk.Frame(settings_outer)
        loops_frame.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        ttk.Label(loops_frame, text="Full Test Loops", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        ttk.Spinbox(loops_frame, from_=1, to=999, width=6, textvariable=self.loops_var).pack(side="left")

        # High Load
        high_frame = ttk.LabelFrame(settings_outer, text="🔥 High Load", padding=8)
        high_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 0), pady=(0, 5))
        make_entry_row(high_frame, "Load Time", self.heavy_time_var, 0)

        # Low Load
        low_frame = ttk.LabelFrame(settings_outer, text="🌀 Low Load", padding=8)
        low_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 5))
        make_entry_row(low_frame, "Rapid Loops", self.rapid_tests_var, 0)
        make_entry_row(low_frame, "Rapid Time", self.rapid_time_var, 1)
        make_entry_row(low_frame, "Rand Loops", self.random_tests_var, 2)
        make_entry_row(low_frame, "Rand Time", self.random_time_var, 3)

        # Single Core
        single_frame = ttk.LabelFrame(settings_outer, text="🎯 Single Core", padding=8)
        single_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0), pady=(0, 5))
        make_entry_row(single_frame, "Low Time", self.light_time_var, 0)
        make_entry_row(single_frame, "Medium Time", self.medium_time_var, 1)
        make_entry_row(single_frame, "High Time", self.heavy_time_var, 2)

        # Browser Tests + Enabled Cores
        bottom_settings = ttk.Frame(settings_outer)
        bottom_settings.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        bottom_settings.columnconfigure(0, weight=1)
        bottom_settings.columnconfigure(1, weight=1)

        browser_frame = ttk.LabelFrame(bottom_settings, text="🌐 Browser Tests", padding=8)
        browser_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 0))
        ttk.Label(browser_frame, text="Count").grid(row=0, column=0, sticky="w", padx=(0, 0), pady=3)
        ttk.Spinbox(browser_frame, from_=0, to=99, width=6, textvariable=self.browsers_var).grid(row=0, column=1, sticky="w", pady=3)

        cores_frame = ttk.LabelFrame(bottom_settings, text="🧵 Enabled Threads", padding=8)
        cores_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ttk.Button(cores_frame, text="⚙ Select Threads", bootstyle="success-outline",
           command=self.open_core_picker).grid(row=0, column=0, sticky="w")

        # Advanced Options toggle
        def toggle_advanced():
            if self.advanced_visible:
                advanced_frame.grid_remove()
                adv_toggle_btn.config(text="▶ Advanced Options")
                self.advanced_visible = False
            else:
                advanced_frame.grid()
                adv_toggle_btn.config(text="▼ Advanced Options")
                self.advanced_visible = True

        adv_toggle_btn = ttk.Button(settings_outer, text="▶ Advanced Options",
                                    bootstyle="link", command=toggle_advanced)
        adv_toggle_btn.grid(row=3, column=0, columnspan=3, sticky="w", pady=(5, 0))

        advanced_frame = ttk.Frame(settings_outer)
        advanced_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 5))
        advanced_frame.grid_remove()
        make_entry_row(advanced_frame, "Rest Time", self.rest_time_var, 0)
        make_entry_row(advanced_frame, "Max RAM (GB)", self.max_ram_var, 1)

        # Save (moved up to row 5, reduced pady)
        save_frame = ttk.Frame(settings_outer)
        save_frame.grid(row=5, column=0, columnspan=3, sticky="e", pady=(2, 0))
        self.unsaved_label = ttk.Label(save_frame, text="", foreground="#e67e00", font=("Segoe UI", 9, "italic"))
        self.unsaved_label.pack(side="left", padx=(0, 10))
        ttk.Button(save_frame, text="💾 Save Settings", bootstyle="success-outline", command=lambda: save_settings(self)).pack(side="right")

                # Logging output
        output_frame = ttk.LabelFrame(main_container, text="🤖 Test Output", padding=10)
        output_frame.grid(row=5, column=0, sticky="nsew", padx=5, pady=(0, 5))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.output_text = scrolledtext.ScrolledText(output_frame, width=80, height=2, wrap="word", font=("Segoe UI", 12))
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Buttons
        control_frame = ttk.Frame(main_container)
        control_frame.grid(row=6, column=0, sticky="e", pady=(0, 10))
        style = ttk.Style()
        button_height = 40
        style.configure("Uniform.TButton", padding=(10, (button_height - 24) // 2))
        self.timer_label = tk.Label(
            control_frame, text="00:00:00", font=("Segoe UI", 12, "bold"),
            fg="#28a745", bg="#f0f0f0", relief="sunken", width=8, height=1, padx=5, pady=0
        )
        self.timer_label.pack(side="left", padx=(0, 0), fill="y")
        self.start_button = ttk.Button(control_frame, text="🔥 Run Test", style="Uniform.TButton", command=self.start_stress_test)
        self.start_button.pack(side="left", padx=2)
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop", state="disabled", style="Uniform.TButton", command=self.stop_stress_test)
        self.stop_button.pack(side="left", padx=2)
        self.benchmark_button = ttk.Button(control_frame, text="💪 Benchmark", style="Uniform.TButton", command=self.start_benchmark)
        self.benchmark_button.pack(side="left", padx=2)
        ttk.Button(control_frame, text="❎ Clear", bootstyle="success-outline", command=lambda: clear_output(self)).pack(side="left", padx=2)
        ttk.Button(control_frame, text="💾 Save", bootstyle="success-outline", command=lambda: export_log(self)).pack(side="left", padx=2)

        # Status bar
        status_frame = ttk.Frame(main_container)
        status_frame.grid(row=7, column=0, sticky="ew", pady=(5, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=0)
        self.status_bar = ttk.Label(status_frame, text="Ready", relief="sunken")
        self.status_bar.grid(row=0, column=0, sticky="ew", padx=(0, 0))
        style.configure("Green.Horizontal.TProgressbar", troughcolor="#e0e0e0", background="#28a745")
        style.map("Green.Horizontal.TProgressbar", background=[("active", "#28a745"), ("!active", "#28a745")])
        self.progress = ttk.Progressbar(status_frame, style="Green.Horizontal.TProgressbar", mode="determinate", length=419)
        self.progress.grid(row=0, column=1, sticky="ew")
        self.progress.grid_remove()

        self.setup_styles()

    def open_core_picker(self):
        topology = {}
        physical_threads = set()

        # Find CPU Topology
        try:
            import subprocess
            result = subprocess.run(
                ["lscpu", "--parse=CPU,CORE"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.strip().split(",")
                if len(parts) == 2:
                    thread_id, core_id = int(parts[0]), int(parts[1])
                    topology.setdefault(core_id, []).append(thread_id)
        except Exception:
            topology = {}

        # /proc/cpuinfo fallback
        if not topology:
            try:
                current_processor = None
                current_core = None
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("processor"):
                            current_processor = int(line.split(":")[1].strip())
                        elif line.startswith("core id"):
                            current_core = int(line.split(":")[1].strip())
                        elif line == "" and current_processor is not None and current_core is not None:
                            topology.setdefault(current_core, []).append(current_processor)
                            current_processor = None
                            current_core = None
            except Exception:
                topology = {}

        # No SMT fallback
        if not topology:
            num_cores = os.cpu_count() or 1
            topology = {i: [i] for i in range(num_cores)}

        # Check physical and virtual threads
        try:
            seen_sibling_groups = set()
            for core_threads in topology.values():
                for thread_id in sorted(core_threads):
                    sib_path = f"/sys/devices/system/cpu/cpu{thread_id}/topology/thread_siblings_list"
                    with open(sib_path) as f:
                        raw = f.read().strip()
                    siblings = set()
                    for part in raw.split(","):
                        if "-" in part:
                            a, b = part.split("-")
                            siblings.update(range(int(a), int(b) + 1))
                        else:
                            siblings.add(int(part))
                    group_key = frozenset(siblings)
                    if group_key not in seen_sibling_groups:
                        seen_sibling_groups.add(group_key)
                        physical_threads.add(min(siblings))
        except Exception:
            for core_threads in topology.values():
                if core_threads:
                    physical_threads.add(min(core_threads))

        # Check existing blacklist
        current = self.core_blacklist_var.get()
        try:
            blacklisted = {int(x.strip()) for x in current.split(",") if x.strip().isdigit()}
        except ValueError:
            blacklisted = set()

        # Build pop-up window
        win = tk.Toplevel(self.root)
        win.title("Enabled Threads")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Select threads to enable  (red = disabled)",
            font=("Segoe UI", 10)).pack(pady=(2, 2), padx=2)
        ttk.Label(win, text="(P) = Physical  (HT) = Virtual",
            font=("Segoe UI", 10)).pack(pady=(2, 2), padx=2)

        scroll_frame_outer = ttk.Frame(win)
        scroll_frame_outer.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(scroll_frame_outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame_outer, orient="vertical", command=canvas.yview)
        grid_frame = ttk.Frame(canvas)

        grid_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        THREAD_COLS = 4
        btn_vars = {}

        for grid_row, (core_id, threads) in enumerate(sorted(topology.items())):
            ttk.Label(grid_frame, text=f"Core {core_id}",
                    font=("Segoe UI", 9, "bold")).grid(
                row=grid_row * 2, column=0, columnspan=THREAD_COLS,
                sticky="w", padx=6, pady=(8, 0)
            )

            for col, thread_id in enumerate(sorted(threads)):
                is_enabled = thread_id not in blacklisted
                var = tk.BooleanVar(value=is_enabled)
                btn_vars[thread_id] = var

                tag = "(P)" if thread_id in physical_threads else "(HT)"
                label = f"Thread {thread_id} {tag}"

                style = "success-outline" if is_enabled else "danger"
                btn = ttk.Button(grid_frame, text=label, width=14, bootstyle=style)

                def make_toggle(t_id, b):
                    def toggle():
                        btn_vars[t_id].set(not btn_vars[t_id].get())
                        b.config(bootstyle="success-outline" if btn_vars[t_id].get() else "danger")
                    return toggle

                btn.config(command=make_toggle(thread_id, btn))
                btn.grid(row=grid_row * 2 + 1, column=col, padx=4, pady=2)

        win.update_idletasks()
        content_height = min(grid_frame.winfo_reqheight() + 20, 400)
        canvas.config(height=content_height)

        def confirm():
            result = ",".join(
                str(t) for t in sorted(k for k, v in btn_vars.items() if not v.get())
            )
            self.core_blacklist_var.set(result)
            win.destroy()

        btn_row = ttk.Frame(win, padding=(10, 5))
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="✅ Confirm", bootstyle="success",
                command=confirm).pack(side="right", padx=4, pady=(0, 8))
        ttk.Button(btn_row, text="❌ Cancel", bootstyle="secondary-outline",
                command=win.destroy).pack(side="right", padx=4, pady=(0, 8))

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

    def process_log_queue(self):
        while True:
            try:
                message = self.log_queue.get_nowait()
                self.root.after(0, lambda msg=message: log_message(self, msg))
            except queue.Empty:
                time.sleep(0.1)

    def start_monitors(self):
        threading.Thread(target=monitor_error_status, args=(self,), daemon=True).start()
        threading.Thread(target=monitor_clock_speed, args=(self,), daemon=True).start()
        threading.Thread(target=self.process_log_queue,daemon=True).start()
        threading.Thread(target=self.monitor_process_status, daemon=True).start()
        threading.Thread(target=monitor_current_test, args=(self,), daemon=True).start()

    def monitor_process_status(self):
        while True:
            if self.is_running and self.process is not None:
                if self.process.poll() is not None: 
                    self.root.after(0, self.stop_timer)
            time.sleep(0.5)

    def start_stress_test(self):
        if self.is_running:
            return
            
        full_reset(self)
        set_current_test(self, "Starting...")
        self.reset_timer()
        self.start_timer()
        self.progress.grid()
        self.progress.start(10)
        
        if not os.path.exists("./threadstepper"):
            log_message(self, "Error: ./threadstepper not found!", "error")
            self.stop_timer()
            return
        
        self.is_running = True
        self.benchmark_mode = False
        self.start_button.config(state=tk.DISABLED)
        self.benchmark_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        log_message(self, f"Starting stress test at {datetime.now().strftime('%H:%M:%S')}", "info")
        self.status_bar.config(text="Stress test running...")
        
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
            
            self.log_queue.put(f"\nTests completed!")
            
        except Exception as e:
            self.log_queue.put(f"Error running tests: {str(e)}")
        finally:
            self.process = None
            self.is_running = False
            self.benchmark_mode = False
            self.root.after(0, self.on_process_stop)

    def start_benchmark(self):
        if self.is_running:
            return
            
        full_reset(self)
        self.reset_timer()
        self.start_timer()
        self.progress.grid()
        self.progress.start(10)
        
        self.is_running = True
        self.benchmark_mode = True
        self.start_button.config(state=tk.DISABLED)
        self.benchmark_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        log_message(self, f"\033[95mStarting benchmark at {datetime.now().strftime('%H:%M:%S')}\033[0m", "info")
        self.status_bar.config(text="Benchmark running...")
        
        threading.Thread(target=self.run_benchmark, daemon=True).start()

    def run_benchmark(self):
        script_path = "./functions/benchmark.sh"
        if not os.path.exists(script_path):
            self.log_queue.put(f"Error: {script_path} not found!")
            self.root.after(0, self.on_process_stop)
            return
        
        try:
            os.chmod(script_path, 0o755)
            self.process = subprocess.Popen(
                [script_path],
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
            
        except Exception as e:
            self.log_queue.put(f"Error running benchmark: {str(e)}")
        finally:
            self.process = None
            self.is_running = False
            self.root.after(0, self.on_process_stop)

    def stop_stress_test(self):
        clear_current_test(self)
        if self.process and self.is_running:
            self.process.terminate()
            if self.benchmark_mode:
                log_message(self, "Stopping benchmark...", "warning")
                self.status_bar.config(text="Stopping benchmark...")
            else:
                log_message(self, "Stopping test...", "warning")
                self.status_bar.config(text="Stopping test...")
                if not self.benchmark_mode:
                    self.stop_timer()

    def on_process_stop(self):
        clear_current_test(self)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.benchmark_button.config(state=tk.NORMAL)
        if self.benchmark_mode:
            self.status_bar.config(text="Benchmark stopped")
            log_message(self, f"\033[95mBenchmark finished at {datetime.now().strftime('%H:%M:%S')}\033[0m", "info")
            self.stop_timer()
            self.progress.stop()
            self.progress.grid_remove()
        else:
            self.status_bar.config(text="Stress test stopped")
            log_message(self, f"Test stopped at {datetime.now().strftime('%H:%M:%S')}", "info")
            self.stop_timer()
            self.progress.stop()
            self.progress.grid_remove()
        self.is_running = False
        self.benchmark_mode = False

def detect_cpu_topology(settings_path="./settings"):
    import re

    num_logical = os.cpu_count() or 1

    # Build map: cpu_id -> core_id
    cpu_to_core = {}
    try:
        for cpu_path in os.listdir("/sys/devices/system/cpu"):
            if not re.match(r"^cpu\d+$", cpu_path):
                continue
            cpu_id = int(cpu_path[3:])
            core_file = f"/sys/devices/system/cpu/{cpu_path}/topology/core_id"
            if os.path.exists(core_file):
                with open(core_file) as f:
                    cpu_to_core[cpu_id] = int(f.read().strip())
    except Exception:
        pass

    if not cpu_to_core:
        topology = 0
    else:
        # First cpu_id per physical core
        core_to_first_cpu = {}
        for cpu_id, core_id in cpu_to_core.items():
            if core_id not in core_to_first_cpu or cpu_id < core_to_first_cpu[core_id]:
                core_to_first_cpu[core_id] = cpu_id

        sorted_cores = sorted(core_to_first_cpu.keys())
        num_cores = len(sorted_cores)
        half_cores = num_cores // 2

        # cross-die
        cross_matches, cross_checks = 0, 0
        for i in range(half_cores):
            core_a, core_b = sorted_cores[i], sorted_cores[i + half_cores]
            cpu_a, cpu_b = core_to_first_cpu[core_a], core_to_first_cpu[core_b]
            sib_path_a = f"/sys/devices/system/cpu/cpu{cpu_a}/topology/thread_siblings_list"
            sib_path_b = f"/sys/devices/system/cpu/cpu{cpu_b}/topology/thread_siblings_list"
            try:
                with open(sib_path_a) as f:
                    sib_a = set()
                    for part in f.read().strip().split(","):
                        if "-" in part:
                            a, b = part.split("-")
                            sib_a.update(range(int(a), int(b) + 1))
                        else:
                            sib_a.add(int(part))
                with open(sib_path_b) as f:
                    sib_b = set()
                    for part in f.read().strip().split(","):
                        if "-" in part:
                            a, b = part.split("-")
                            sib_b.update(range(int(a), int(b) + 1))
                        else:
                            sib_b.add(int(part))
                cross_checks += 1
                if cpu_b not in sib_a and cpu_a not in sib_b:
                    cross_matches += 1
            except Exception:
                pass

        # adjacent die
        adj_matches, adj_checks = 0, 0
        for i in range(num_cores - 1):
            core_a, core_b = sorted_cores[i], sorted_cores[i + 1]
            cpu_a, cpu_b = core_to_first_cpu[core_a], core_to_first_cpu[core_b]
            die_path_a = f"/sys/devices/system/cpu/cpu{cpu_a}/topology/die_id"
            die_path_b = f"/sys/devices/system/cpu/cpu{cpu_b}/topology/die_id"
            adj_checks += 1
            try:
                with open(die_path_a) as f:
                    die_a = f.read().strip()
                with open(die_path_b) as f:
                    die_b = f.read().strip()
                if die_a == die_b:
                    adj_matches += 1
            except Exception:
                if (core_b - core_a) == 1:
                    adj_matches += 1

        cross_ratio = (cross_matches * 100 // cross_checks) if cross_checks else 0
        adj_ratio   = (adj_matches * 100 // adj_checks)   if adj_checks   else 0

        if cross_ratio >= 80:
            topology = 1
        elif adj_ratio >= 80:
            topology = 2
        else:
            topology = 0

    # Save topology
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                content = f.read()
            if re.search(r"^cpu_topology=", content, re.MULTILINE):
                content = re.sub(r"^cpu_topology=.*", f"cpu_topology={topology}", content, flags=re.MULTILINE)
            else:
                content += f"\ncpu_topology={topology}"
            with open(settings_path, "w") as f:
                f.write(content)
    except Exception:
        pass

def main():
    os.makedirs("./logs", exist_ok=True)
    
    if not os.path.exists("./settings"):
        with open("./settings", 'w') as f:
            f.write("#!/bin/bash\n\n# Stress Test Configuration\nTHREADS=4\nDURATION=60\nINTENSITY=high\n")
    
    detect_cpu_topology()

    if not os.path.exists("./logs/clock.log"):
        with open("./logs/clock.log", 'w') as f:
            f.write("4.2 GHz (Highest Recorded)")
    
    if not os.path.exists("./logs/errors.log"):
        with open("./logs/errors.log", 'w') as f:
            f.write("False\n")

    root = tb.Window(themename="flatly") 
    root.resizable(False, False)
    icon = PhotoImage(file="favicon.png")
    root.iconphoto(True, icon)
    app = StressTestGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()