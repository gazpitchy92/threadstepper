import os
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext
import queue
import time
from datetime import datetime

import ttkbootstrap as tb
from tkinter import ttk


def start_benchmark(app):
    BenchmarkWindow(app)


class BenchmarkWindow:

    SCRIPT = "./functions/benchmark.sh"

    def __init__(self, app):
        self.app = app
        self.process = None
        self.is_running = False
        self.log_queue = queue.Queue()
        self.timer_running = False
        self.timer_seconds = 0

        self.win = tk.Toplevel(app.root)
        self.win.title("Benchmark")
        self.win.geometry("500x300")
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._close)
        self.win.transient(app.root)

        self._build_ui()
        self._drain_log_queue()

    # UI
    def _build_ui(self):
        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(0, weight=1)

        body = ttk.Frame(self.win, padding=10)
        body.grid(row=0, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        # Output log
        log_frame = ttk.LabelFrame(body, text="💪 Benchmark Output", padding=5)
        log_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(
            log_frame, wrap="char", font=("Segoe UI", 11), height=20, state="disabled"
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_text.tag_config("error",   foreground="red")
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("warning", foreground="orange")
        self.output_text.tag_config("info",    foreground="#17a2b8")

        # Controls row
        ctrl = ttk.Frame(body)
        ctrl.grid(row=1, column=0, sticky="ew")
        ctrl.columnconfigure(0, weight=1)

        self.timer_label = tk.Label(
            ctrl, text="00:00:00",
            font=("Segoe UI", 12, "bold"),
            fg="#28a745", bg="#f0f0f0",
            relief="sunken", width=9, padx=5,
        )
        self.timer_label.grid(row=0, column=0, sticky="w")

        btn_frame = ttk.Frame(ctrl)
        btn_frame.grid(row=0, column=1, sticky="e")

        self.start_btn = ttk.Button(btn_frame, text="🔥 Start", bootstyle="success", command=self._start)
        self.start_btn.pack(side="left", padx=(0, 4))

        self.stop_btn = ttk.Button(btn_frame, text="🛑 Stop", bootstyle="danger", state="disabled", command=self._stop)
        self.stop_btn.pack(side="left", padx=(0, 4))

        ttk.Button(btn_frame, text="❎ Close", bootstyle="secondary-outline", command=self._close).pack(side="left")

    # Benchmark control
    def _start(self):
        if self.is_running:
            return
        if not os.path.exists(self.SCRIPT):
            self._log(f"Error: {self.SCRIPT} not found!", "error")
            return

        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._reset_timer()
        self._start_timer()
        self._log(f"Benchmark started at {datetime.now().strftime('%H:%M:%S')}", "info")
        self._log(f"This will take 2 minutes", "info")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            os.chmod(self.SCRIPT, 0o755)
            self.process = subprocess.Popen(
                [self.SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            for line in self.process.stdout:
                if line:
                    self.log_queue.put(("plain", line.rstrip()))
            self.process.wait()
            self.log_queue.put(("info", f"Benchmark finished at {datetime.now().strftime('%H:%M:%S')}"))
        except Exception as e:
            self.log_queue.put(("error", f"Error: {e}"))
        finally:
            self.process = None
            self.is_running = False
            self.win.after(0, self._on_stopped)

    def _stop(self):
        if self.process and self.is_running:
            self.process.terminate()
            self._log("Stopping benchmark...", "warning")

    def _on_stopped(self):
        self._stop_timer()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def _close(self):
        if self.is_running and self.process:
            self.process.terminate()
            self.process.wait()
        self.win.destroy()

    # Log drain

    ANSI_ESCAPE = __import__('re').compile(r'\x1b[\[\(][0-9;]*[A-Za-z]|\x1b[^[\(]')

    def _log(self, message, tag="plain"):
        self.log_queue.put((tag, message))

    def _drain_log_queue(self):
        try:
            while True:
                tag, msg = self.log_queue.get_nowait()
                msg = self.ANSI_ESCAPE.sub('', msg)
                self.output_text.config(state="normal")
                self.output_text.insert("end", msg + "\n", tag if tag != "plain" else "")
                self.output_text.see("end")
                self.output_text.config(state="disabled")
        except queue.Empty:
            pass
        try:
            self.win.after(100, self._drain_log_queue)
        except tk.TclError:
            pass

    # Timer

    def _start_timer(self):
        self.timer_running = True
        self.timer_label.config(fg="#28a745")
        threading.Thread(target=self._tick, daemon=True).start()

    def _stop_timer(self):
        self.timer_running = False
        try:
            self.timer_label.config(fg="#dc3545")
        except tk.TclError:
            pass

    def _reset_timer(self):
        self.timer_seconds = 0
        self.timer_label.config(text="00:00:00", fg="#28a745")

    def _tick(self):
        while self.timer_running:
            h = self.timer_seconds // 3600
            m = (self.timer_seconds % 3600) // 60
            s = self.timer_seconds % 60
            txt = f"{h:02d}:{m:02d}:{s:02d}"
            try:
                self.win.after(0, lambda t=txt: self.timer_label.config(text=t))
            except tk.TclError:
                break
            self.timer_seconds += 1
            time.sleep(1)