import platform
import tkinter as tk
from tkinter import scrolledtext, ttk

from PIL import Image, ImageTk

from python.core_picker import open_core_picker
from python.dependencies import install_dependencies
from python.errors import clear_error_log, toggle_error_log, update_error_log, update_error_status
from python.logs import open_output_window
from python.options import (
    parse_settings_options,
    register_settings_traces,
    save_settings,
    update_settings_content,
    load_default_settings,
    set_group_values,
    restore_group_defaults,
    toggle_group_enabled
)
from python.styling import toggle_dark_mode
from python.system import check_browser_dependency, refresh_system_info, reset_button
from python.testing import start_stress_test, stop_stress_test


def make_section(self, parent, title, **kwargs):
    outer = ttk.Frame(parent, **kwargs)
    header = ttk.Frame(outer)
    header.pack(fill="x", pady=(0, 6))
    title_wrap = ttk.Frame(header)
    title_wrap.pack(side="left")
    lbl = ttk.Label(title_wrap, text=title, font=("Segoe UI", 11, "bold"), foreground="#000000")
    lbl.pack(side="left")
    lbl.pack(side="left")
    ttk.Separator(header, orient="horizontal").pack(
        side="left", fill="x", expand=True, padx=(6, 0), pady=1
    )
    inner = ttk.Frame(outer)
    inner.pack(fill="both", expand=True)
    if not hasattr(self, "_section_labels"):
        self._section_labels = []
    self._section_labels.append(lbl)
    return outer, inner

def configure_numeric_spinbox(self, spinbox):
    spinbox.configure(
        validate="key",
        validatecommand=(
            spinbox.register(lambda value: value.isdigit() or value == ""),
            "%P",
        ),
    )
    return spinbox

def make_entry_row(self, parent, label, var, row):
    parent.columnconfigure(1, weight=1)
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 6), pady=1)
    spinbox = configure_numeric_spinbox(self, ttk.Spinbox(parent, from_=0, to=999999, textvariable=var))
    spinbox.grid(row=row, column=1, sticky="ew", pady=1)

def setup_styles(self):
    style = ttk.Style()
    style.configure("Install.TButton", foreground="blue", font=("Arial", 12))
    self.output_text.tag_config("error", foreground="red")
    self.output_text.tag_config("success", foreground="green")
    self.output_text.tag_config("warning", foreground="orange")
    self.output_text.tag_config("info", foreground="blue")

def build_header(self, parent):
    header_frame = ttk.Frame(parent)
    header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
    img = Image.open("favicon.png").resize((45, 45))
    icon_img = ImageTk.PhotoImage(img)
    self.header_label = tk.Label(
        header_frame,
        text=" Thread Stepper",
        font=("Segoe UI", 18, "bold"),
        image=icon_img,
        compound="left",
    )
    self.header_label.pack(side="left")
    self.header_label.image = icon_img
    button_frame = ttk.Frame(header_frame)
    button_frame.pack(side="right")
    self.dark_mode_btn = ttk.Button(
        button_frame,
        text="☾ Dark Mode",
        bootstyle="info-outline",
        command=lambda: toggle_dark_mode(self),
    )
    self.dark_mode_btn.pack(side="left", padx=(0, 10))
    self.install_dep_btn = ttk.Button(
        button_frame,
        text="⌂ Install Dependencies",
        bootstyle="info",
        command=lambda: install_dependencies(self),
    )
    self.install_dep_btn.pack(side="left")
    if check_browser_dependency(self):
        self.install_dep_btn.pack_forget()

def build_info_row(self, parent):
    info_row = ttk.Frame(parent)
    info_row.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 0))
    info_row.columnconfigure(0, weight=1)
    info_row.columnconfigure(1, weight=1)
    info_row.columnconfigure(2, weight=1)
    info_row.rowconfigure(0, weight=1)
    info_row.rowconfigure(1, weight=1)
    # System info
    system_frame, system_inner = make_section(self, info_row, "⌕ System Information", padding=10)
    system_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
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
    ttk.Button(sys_btn_frame, text="◷ Benchmark", bootstyle="primary-outline", command=self.open_benchmark_window).grid(
        row=0, column=0, sticky="ew", padx=(0, 2)
    )
    ttk.Button(sys_btn_frame, text="↻ Refresh", bootstyle="info-outline", command=lambda: refresh_system_info(self)).grid(
        row=0, column=1, sticky="ew", padx=(2, 0)
    )
    freq_row = ttk.Frame(cpu_info_frame)
    freq_row.pack(anchor="w", fill="x", pady=(0, 3))
    ttk.Label(freq_row, text="Frequency:", style="InfoTitle.TLabel").pack(side="left")
    self.cpu_freq = ttk.Label(freq_row, text=" N/A", style="InfoValue.TLabel")
    self.cpu_freq.pack(side="left")
    # Peak clock
    clock_frame_top, clock_inner_top = make_section(self, info_row, "⬆ Peak Clock", padding=10)
    clock_frame_top.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    clock_inner_top.columnconfigure(0, weight=1)
    clock_inner_top.rowconfigure(0, weight=1)
    self.clock_label_top = tk.Label(
        clock_inner_top,
        text="N/A",
        font=("Segoe UI", 11, "bold"),
        fg="#17a2b8",
        bg="#e8f4f8",
        relief="raised",
        padx=10,
        pady=4,
    )
    self.clock_label_top.grid(row=0, column=0, sticky="nsew")
    # Peak temp
    temp_frame_top, temp_inner_top = make_section(self, info_row, "❈ Peak Temp", padding=10)
    temp_frame_top.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
    temp_inner_top.columnconfigure(0, weight=1)
    temp_inner_top.rowconfigure(0, weight=1)
    self.temp_label_top = tk.Label(
        temp_inner_top,
        text="N/A",
        font=("Segoe UI", 11, "bold"),
        fg="#17a2b8",
        bg="#e8f4f8",
        relief="raised",
        padx=10,
        pady=4,
    )
    self.temp_label_top.grid(row=0, column=0, sticky="nsew")
    # Current action
    clock_frame_bottom, clock_inner_bottom = make_section(self, info_row, "◇ Current Action", padding=10)
    clock_frame_bottom.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=(5, 0))
    clock_inner_bottom.columnconfigure(0, weight=1)
    clock_inner_bottom.rowconfigure(0, weight=1)
    self.clock_label_bottom = tk.Label(
        clock_inner_bottom,
        text="N/A",
        font=("Segoe UI", 11, "bold"),
        fg="#17a2b8",
        bg="#e8f4f8",
        relief="raised",
        padx=10,
        pady=4,
        justify="center",
    )
    self.clock_label_bottom.grid(row=0, column=0, sticky="nsew")

def build_error_section(self, parent):
    error_frame, error_inner = make_section(self, parent, "⁉ Error Status", padding=10)
    error_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 2))
    error_inner.columnconfigure(0, weight=1)
    self.error_indicator = tk.Label(
        error_inner,
        text="NO ERRORS ✔",
        font=("Segoe UI", 11, "bold"),
        bg="#d4edda",
        fg="#155724",
        relief="raised",
        padx=10,
        pady=4,
    )
    self.error_indicator.grid(row=0, column=0, sticky="nsew")
    error_btn_frame = ttk.Frame(error_inner)
    error_btn_frame.grid(row=1, column=0, sticky="e", pady=(2, 0))
    ttk.Button(error_btn_frame, text="↻ Refresh", bootstyle="info-outline", command=lambda: update_error_status(self)).pack(
        side="right", padx=2
    )
    self.toggle_error_btn = ttk.Button(
        error_btn_frame,
        text="▶ Error Logs",
        bootstyle="primary-outline",
        command=lambda: toggle_error_log(self),
    )
    self.toggle_error_btn.pack(side="right", padx=2)
    # Error log
    self.error_log_container, error_log_inner = make_section(self, parent, "✎ Error Logs", padding=5)
    self.error_log_container.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 2))
    self.error_log_container.grid_remove()
    self.error_text = scrolledtext.ScrolledText(error_log_inner, width=80, height=6, wrap="word", font=("Segoe UI", 12))
    self.error_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    error_log_inner.columnconfigure(0, weight=1)
    error_log_inner.rowconfigure(0, weight=1)
    error_log_btn_frame = ttk.Frame(error_log_inner)
    error_log_btn_frame.grid(row=1, column=0, sticky="e", pady=(0, 2))
    ttk.Button(error_log_btn_frame, text="↻ Refresh", bootstyle="info-outline", command=lambda: update_error_log(self)).pack(
        side="right", padx=2
    )
    ttk.Button(error_log_btn_frame, text="⇄ Reset", bootstyle="warning-outline", command=lambda: clear_error_log(self)).pack(
        side="right", padx=2
    )

def build_settings(self, parent):
    settings_inner = ttk.Frame(parent, padding=10)
    settings_inner.grid(row=4, column=0, sticky="ew", padx=5, pady=(0, 2))
    settings_inner.columnconfigure(0, weight=1)
    settings_inner.columnconfigure(1, weight=1)
    settings_inner.columnconfigure(2, weight=1)
    # Test sections
    high_frame, high_inner = make_section(self, settings_inner, "▦ All Cores", padding=6)
    high_inner.columnconfigure(0, weight=1, minsize=90)
    ttk.Checkbutton(
        high_inner,
        text="Enabled",
        variable=self.all_cores_enabled_var,
        command=lambda: toggle_group_enabled(self, "all_cores", self.all_cores_enabled_var.get()),
    ).grid(row=0, column=0, sticky="w", pady=(0, 2), padx=2)
    high_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 2))
    make_entry_row(self, high_inner, "Time", self.all_core_time_var, 1)
    make_entry_row(self, high_inner, "Tests", self.all_core_tests_var, 2)

    low_frame, low_inner = make_section(self, settings_inner, "≡ Low Load", padding=6)
    low_inner.columnconfigure(0, weight=1, minsize=90)
    ttk.Checkbutton(
        low_inner,
        text="Enabled",
        variable=self.low_load_enabled_var,
        command=lambda: toggle_group_enabled(self, "low_load", self.low_load_enabled_var.get()),
    ).grid(row=0, column=0, sticky="w", pady=(0, 2), padx=2)
    low_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 2))
    make_entry_row(self, low_inner, "Rapid Tests", self.rapid_tests_var, 1)
    make_entry_row(self, low_inner, "Rapid Time", self.rapid_time_var, 2)
    make_entry_row(self, low_inner, "Rand Tests", self.random_tests_var, 3)
    make_entry_row(self, low_inner, "Rand Time", self.random_time_var, 4)

    single_frame, single_inner = make_section(self, settings_inner, "◫ Single Core", padding=6)
    single_inner.columnconfigure(0, weight=1, minsize=90)
    ttk.Checkbutton(
        single_inner,
        text="Enabled",
        variable=self.single_core_enabled_var,
        command=lambda: toggle_group_enabled(self, "single_core", self.single_core_enabled_var.get()),
    ).grid(row=0, column=0, sticky="w", pady=(0, 2), padx=2)
    single_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0), pady=(0, 2))
    make_entry_row(self, single_inner, "Low Time", self.light_time_var, 1)
    make_entry_row(self, single_inner, "Medi Time", self.medium_time_var, 2)
    make_entry_row(self, single_inner, "High Time", self.heavy_time_var, 3)
    # Bottom row
    bottom_settings = ttk.Frame(settings_inner)
    bottom_settings.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(2, 0))
    bottom_settings.columnconfigure(0, weight=1)
    bottom_settings.columnconfigure(1, weight=1)
    bottom_settings.columnconfigure(2, weight=1)
    browser_frame, browser_inner = make_section(self, bottom_settings, "☉ WebGL Tests", padding=6)
    ttk.Checkbutton(
        browser_frame,
        text="Enabled",
        variable=self.webgl_enabled_var,
        command=lambda: toggle_group_enabled(self, "webgl", self.webgl_enabled_var.get()),
    ).pack(side="left")
    browser_inner.columnconfigure(1, weight=1)
    browser_frame.grid(row=0, column=0, sticky="nsew")
    self.browsers_label = ttk.Label(browser_inner, text="Instances")
    self.browsers_label.grid(row=0, column=0, sticky="w", pady=3)
    self.browsers_spinbox = configure_numeric_spinbox(
        self, ttk.Spinbox(browser_inner, from_=0, to=99, width=6, textvariable=self.browsers_var)
    )
    self.browsers_spinbox.grid(row=0, column=1, sticky="ew", pady=3)
    if not check_browser_dependency(self):
        self.browsers_label.grid_remove()
        self.browsers_spinbox.grid_remove()
        self.browser_dep_label = ttk.Label(
            browser_inner,
            text="⚠ Please install dependencies for this test",
            foreground="#e67e00",
            font=("Segoe UI", 8, "italic"),
        )
        self.browser_dep_label.grid(row=0, column=0, sticky="w", pady=(2, 0))
    cores_frame, cores_inner = make_section(self, bottom_settings, "∼ Cores / Threads", padding=6)
    cores_inner.columnconfigure(0, weight=1)
    cores_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    ttk.Button(cores_inner, text="⚙ Configure", bootstyle="primary-outline", command=lambda: open_core_picker(self)).grid(
        row=0, column=0, sticky="ew"
    )
    other_frame, other_inner = make_section(self, bottom_settings, "⍼ Other Options", padding=6)
    other_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
    make_entry_row(self, other_inner, "Rest Time", self.rest_time_var, 0)
    # Save
    save_frame = ttk.Frame(settings_inner)
    save_frame.grid(row=5, column=0, columnspan=3, sticky="e", pady=(2, 0))
    self.unsaved_label = ttk.Label(save_frame, text="", foreground="#e67e00", font=("Segoe UI", 11, "italic"))
    self.unsaved_label.pack(side="left", padx=(0, 10))
    ttk.Button(save_frame, text="⤓ Save Settings", bootstyle="success", command=lambda: save_settings(self)).pack(
        side="right"
    )

def build_controls(self, parent):
    # Output log
    output_frame, output_inner = make_section(self, parent, "⩾ Test Output", padding=10)
    output_frame.grid(row=5, column=0, sticky="nsew", padx=5, pady=(0, 2))
    output_inner.columnconfigure(0, weight=1)
    output_inner.rowconfigure(0, weight=1)
    self.output_text = scrolledtext.ScrolledText(output_inner, width=80, height=2, wrap="word", font=("Segoe UI", 11))
    self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    # Controls
    control_frame = ttk.Frame(parent)
    control_frame.grid(row=6, column=0, sticky="ew", pady=(0, 4))
    style = ttk.Style()
    style.configure("Uniform.TButton", padding=(10, 3), font=("Segoe UI", 10))
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
        pady=0,
    )
    self.timer_label.pack(side="left", padx=(20, 2), fill="y")
    ttk.Frame(control_frame).pack(side="left", fill="x", expand=True)
    runs_frame = ttk.Frame(control_frame)
    runs_frame.pack(side="left", padx=(0, 6))
    ttk.Label(runs_frame, text="Test Runs", font=("Segoe UI", 9)).pack(side="left", padx=(0, 4))
    configure_numeric_spinbox(self, ttk.Spinbox(runs_frame, from_=1, to=999, width=5, textvariable=self.loops_var)).pack(
        side="left"
    )
    self.start_button = ttk.Button(
        control_frame,
        text="▶ Start",
        bootstyle="success",
        command=lambda: start_stress_test(self),
    )
    self.start_button.pack(side="left", padx=(5, 0))
    self.stop_button = ttk.Button(
        control_frame,
        text="⊠ Stop",
        state="disabled",
        bootstyle="danger",
        command=lambda: stop_stress_test(self),
    )
    self.stop_button.pack(side="left", padx=(5, 0))
    ttk.Button(control_frame, text="⇄ Reset", bootstyle="warning-outline", command=lambda: reset_button(self)).pack(
        side="left", padx=(5, 0)
    )
    ttk.Button(control_frame, text="⎘ View Logs", bootstyle="primary-outline", command=lambda: open_output_window(self)).pack(
        side="left", padx=(5, 20)
    )
    # Status bar
    status_frame = ttk.Frame(parent)
    status_frame.grid(row=7, column=0, sticky="ew", pady=(2, 0))
    status_frame.columnconfigure(0, weight=1)
    status_frame.columnconfigure(1, weight=0)
    self.status_bar = ttk.Label(status_frame, text="Ready", relief="sunken")
    self.status_bar.grid(row=0, column=0, sticky="ew", padx=(20, 20))
    style.configure("Green.Horizontal.TProgressbar", troughcolor="#e0e0e0", background="#28a745")
    style.map(
        "Green.Horizontal.TProgressbar",
        background=[("active", "#28a745"), ("!active", "#28a745")],
    )
    self.progress = ttk.Progressbar(
        status_frame,
        style="Green.Horizontal.TProgressbar",
        mode="determinate",
        length=419,
    )
    self.progress.grid(row=0, column=1, sticky="ew", padx=(5, 20))
    self.progress.grid_remove()