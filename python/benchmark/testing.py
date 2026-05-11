import os
import tkinter as tk
from tkinter import scrolledtext, ttk

from python.ui import make_section

def build_benchmark_tab(self):

    self.benchmark_tab.columnconfigure(0, weight=1)
    self.benchmark_tab.rowconfigure(0, weight=1)

    body = ttk.Frame(self.benchmark_tab, padding=10)
    body.grid(row=0, column=0, sticky="nsew")

    body.columnconfigure(0, weight=1)
    body.rowconfigure(0, weight=1)
    body.rowconfigure(1, weight=1)

    # Output log
    log_frame, log_inner = make_section(self, body, "◷ Benchmark Output", padding=6)
    log_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
    log_inner.columnconfigure(0, weight=1)
    log_inner.rowconfigure(0, weight=1)

    self.output_text = scrolledtext.ScrolledText(
        log_inner,
        wrap="char",
        font=("Consolas", 10),
        height=8,
        state="disabled",
        relief="flat",
        borderwidth=0,
    )
    self.output_text.grid(row=0, column=0, sticky="nsew")

    self.output_text.tag_config("error", foreground="red")
    self.output_text.tag_config("success", foreground="green")
    self.output_text.tag_config("warning", foreground="orange")
    self.output_text.tag_config("info", foreground="#17a2b8")
    self.output_text.tag_config("debug", foreground="#777777")
    self.output_text.tag_config("blue", foreground="#4da3ff")

    # History
    hist_frame, hist_inner = make_section(self, body, "☷ Benchmark History", padding=6)
    hist_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 6))

    hist_inner.columnconfigure(0, weight=1)
    hist_inner.rowconfigure(0, weight=1)

    cols = ("date", "single", "multi", "peak", "temp")

    self.history_tree = ttk.Treeview(
        hist_inner,
        columns=cols,
        show="headings",
        height=7,
        selectmode="none",
    )

    self.history_tree.heading("date", text="@ Run Date")
    self.history_tree.heading("single", text="◫ Single Core")
    self.history_tree.heading("multi", text="▦ All Core")
    self.history_tree.heading("peak", text="⬆ Peak Clock")
    self.history_tree.heading("temp", text="❈ Peak Temp")

    self.history_tree.column("date", width=150, anchor="center", stretch=False)
    self.history_tree.column("single", width=125, anchor="center", stretch=False)
    self.history_tree.column("multi", width=125, anchor="center", stretch=False)
    self.history_tree.column("peak", width=110, anchor="center", stretch=False)
    self.history_tree.column("temp", width=110, anchor="center", stretch=False)

    scrollbar = ttk.Scrollbar(
        hist_inner,
        orient="vertical",
        command=self.history_tree.yview,
    )

    self.history_tree.configure(yscrollcommand=scrollbar.set)

    self.history_tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    hist_inner.columnconfigure(1, weight=0)

    self.history_tree.tag_configure(
        "latest",
        foreground="#28a745",
        font=("Segoe UI", 9, "bold"),
    )

    style = ttk.Style()
    style.configure("Treeview", rowheight=14, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    # Controls
    ctrl = ttk.Frame(body)
    ctrl.grid(row=2, column=0, sticky="ew")

    ctrl.columnconfigure(0, weight=1)
    ctrl.columnconfigure(1, weight=1)

    # Timer
    top = ttk.Frame(ctrl)
    top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
    top.columnconfigure(0, weight=1)

    self.timer_label = tk.Label(
        top,
        text="00:00:00",
        font=("Segoe UI", 11, "bold"),
        fg="#28a745",
        bg=self.win.cget("bg"),
        relief="sunken",
        width=9,
        padx=5,
    )
    self.timer_label.pack(side="right")

    # Core selector
    left = ttk.Frame(ctrl)
    left.grid(row=1, column=0, sticky="w")

    ttk.Label(
        left,
        font=("Segoe UI", 8),
        text="Single Core:",
    ).pack(side="left", padx=(0, 5))

    self.core_var = tk.StringVar(value="Auto")

    core_options = ["Auto"] + [
        str(i) for i in range(max(1, os.cpu_count() // 2))
    ]

    self.core_select = ttk.Combobox(
        left,
        textvariable=self.core_var,
        values=core_options,
        width=8,
        state="readonly",
    )
    self.core_select.pack(side="left")

    # Buttons
    right = ttk.Frame(ctrl)
    right.grid(row=1, column=1, sticky="e")

    self.start_btn = ttk.Button(
        right,
        text="▶ Start",
        bootstyle="success",
        command=self._start,
    )
    self.start_btn.pack(side="left", padx=(0, 4))

    self.stop_btn = ttk.Button(
        right,
        text="⊠ Stop",
        bootstyle="danger",
        state="disabled",
        command=self._stop,
    )
    self.stop_btn.pack(side="left", padx=(0, 4))

    ttk.Button(
        right,
        text="⇄ Reset",
        bootstyle="warning-outline",
        command=self._reset_log,
    ).pack(side="left", padx=(0, 4))

    ttk.Button(
        right,
        text="⊗ Close",
        bootstyle="danger-outline",
        command=self._close,
    ).pack(side="left")

def _close(self):
    subprocess.run(["pkill", "-f", "launch.js"])
    subprocess.run(["pkill", "-f", "rank.sh"])
    subprocess.run(["pkill", "-f", "rank.sh"])
    subprocess.run(["pkill", "-f", "bash -c"])
    if self.is_running and self.process:
        self.process.terminate()
        self.process.wait()

    self.app.benchmark_window_open = False
    self.win.destroy()