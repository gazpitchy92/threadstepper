import os
import queue
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, ttk
import ttkbootstrap as tb

from python.benchmark.testing import build_benchmark_tab
from python.benchmark.ranking import build_core_ranks_tab

def start_benchmark(app):
    BenchmarkWindow(app)


class BenchmarkWindow:

    SCRIPT = "./functions/benchmark/launch.sh"
    LOG_PATH = "./logs/benchmark.log"

    def __init__(self, app):
        self.app = app
        self.process = None
        self.is_running = False
        self.log_queue = queue.Queue()
        self.timer_running = False
        self.timer_seconds = 0

        self.win = tk.Toplevel(app.root)
        self.win.title("Benchmark")
        self.win.geometry("720x600")
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._close)
        self.win.transient(app.root)

        self._build_ui()
        self._drain_log_queue()
        self._refresh_history()

    # UI
    def _build_ui(self):
        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.win)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self.benchmark_tab = ttk.Frame(self.notebook)
        self.core_ranks_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.benchmark_tab, text="◷ Benchmark")
        self.notebook.add(self.core_ranks_tab, text="⚃ Core Rankings")

        build_benchmark_tab(self)
        build_core_ranks_tab(self)

    def _on_tab_change(self, event):
        if self.is_running:
            self.win.after(0, lambda: self.notebook.select(self.benchmark_tab))
            return
        if getattr(self, "_cr_running", False):
            self.win.after(0, lambda: self.notebook.select(self.core_ranks_tab))

    # History
    def _refresh_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        if not os.path.exists(self.LOG_PATH):
            return

        try:
            with open(self.LOG_PATH, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
        except OSError:
            return

        lines = list(reversed(lines))
        parsed = []
        for line in lines:
            parts = line.split(",", 5)
            if len(parts) != 6:
                continue
            parsed.append(parts)

        best_single = max((int(p[3]) for p in parsed), default=0)
        best_multi = max((int(p[4]) for p in parsed), default=0)
        best_clock = max((float(p[1]) for p in parsed), default=0)
        best_temp = max((float(p[0]) for p in parsed), default=0)

        for i, parts in enumerate(parsed):
            peak_temp, peak_ghz, core_used, single_score, multi_score, date = parts
            single_star = "➤ " if int(single_score) == best_single else ""
            multi_star = "➤ " if int(multi_score) == best_multi else ""
            clock_star = "➤ " if float(peak_ghz) == best_clock else ""
            temp_star = "➤ " if float(peak_temp) == best_temp else ""
            single_display = f"{single_star}Core {core_used}: {single_score}"
            multi_display = f"{multi_star}{multi_score}"
            peak_display = f"{clock_star}{peak_ghz} GHz"
            temp_display = f"{temp_star}{peak_temp}°C"
            tag = ("latest",) if i == 0 else ()
            self.history_tree.insert(
                "",
                "end",
                values=(
                    date,
                    single_display,
                    multi_display,
                    peak_display,
                    temp_display,
                ),
                tags=tag,
            )

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
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            os.chmod(self.SCRIPT, 0o755)
            core_value = self.core_var.get()
            self.process = subprocess.Popen(
                [self.SCRIPT, core_value],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in self.process.stdout:
                if line:
                    self.log_queue.put(("plain", line.rstrip()))
            self.process.wait()
        except Exception as e:
            self.log_queue.put(("error", f"Error: {e}"))
        finally:
            self.process = None
            self.is_running = False
            self.win.after(0, self._on_stopped)

    def _stop(self):
        subprocess.run(["pkill", "-f", "launch.js"])
        subprocess.run(["pkill", "-f", "rank.js"])
        subprocess.run(["pkill", "-f", "bash -c"])
        subprocess.run(["pkill", "-9", "-f", r"rank\.sh"], check=False)
        if self.process and self.is_running:
            self.process.terminate()
            self._log("Stopping benchmark...", "warning")

    def _on_stopped(self):
        subprocess.run(["pkill", "-f", "launch.js"])
        subprocess.run(["pkill", "-f", "rank.sh"])
        subprocess.run(["pkill", "-f", "bash -c"])
        subprocess.run(["pkill", "-9", "-f", r"rank\.sh"], check=False)
        self._stop_timer()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._refresh_history()

    def _close(self):
        subprocess.run(["pkill", "-f", "launch.js"])
        subprocess.run(["pkill", "-f", "rank.sh"])
        subprocess.run(["pkill", "-f", "bash -c"])
        subprocess.run(["pkill", "-f", "bash.*rank.sh"])
        if self.is_running and self.process:
            self.process.terminate()
            self.process.wait()

        self.app.benchmark_window_open = False
        self.win.destroy()

    # Logs
    def _reset_log(self):
        if self.is_running:
            return

        try:
            open(self.LOG_PATH, "w").close()
        except OSError:
            self._log("Error: could not clear log file.", "error")
            return

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")

        self._refresh_history()
        self._log("Benchmark history cleared.", "warning")

    ANSI_ESCAPE = __import__("re").compile(r"\x1b[\[\(][0-9;]*[A-Za-z]|\x1b[^[\(]")

    def _log(self, message, tag="plain"):
        self.log_queue.put((tag, message))

    def _drain_log_queue(self):
        try:
            while True:
                tag, msg = self.log_queue.get_nowait()
                msg = self.ANSI_ESCAPE.sub("", msg)
                lower = msg.lower()
                if lower.startswith("debug "):
                    tag = "debug"
                    msg = msg[6:]
                elif lower.startswith("info "):
                    tag = "blue"
                    msg = msg[5:]
                elif lower.startswith("error "):
                    tag = "error"
                    msg = msg[6:]
                self.output_text.config(state="normal")
                self.output_text.insert(
                    "end", msg + "\n", tag if tag != "plain" else ""
                )
                self.output_text.see("end")
                self.output_text.config(state="disabled")
        except queue.Empty:
            pass
        try:
            self.win.after(100, self._drain_log_queue)
        except tk.TclError:
            pass

    # Timers
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
