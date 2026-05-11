import os
import subprocess
import threading
from datetime import datetime

import tkinter as tk

from python.errors import update_error_status, update_error_log
from python.logs import log_message, set_current_test, clear_current_test
from python.system import full_reset
from python.timers import start_timer, stop_timer, reset_timer


def start_stress_test(self):
    if self.benchmark_window_open:
        return
    if self.is_running:
        return

    full_reset(self)
    set_current_test(self, "Starting...")
    reset_timer(self)
    start_timer(self)
    self.progress.grid()
    self.progress.start(10)

    subprocess.run(
        [
            "notify-send",
            "Thread Stepper",
            f"Tests started at {datetime.now().strftime('%H:%M:%S')}",
        ]
    )

    if not os.path.exists("./threadstepper"):
        log_message(self, "Error: ./threadstepper not found!", "error")
        stop_timer(self)
        return

    self.is_running = True
    self.benchmark_mode = False
    self.start_button.config(state=tk.DISABLED)
    self.stop_button.config(state=tk.NORMAL)

    log_message(
        self, f"Starting tests at {datetime.now().strftime('%H:%M:%S')}", "info"
    )
    self.status_bar.config(text="Tests running...")

    threading.Thread(target=run_stress_test, args=(self,), daemon=True).start()


def run_stress_test(self):
    try:
        os.chmod("./threadstepper", 0o755)

        self.process = subprocess.Popen(
            ["./threadstepper"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        for line in self.process.stdout:
            if line:
                self.log_queue.put(line.strip())

        self.process.wait()

        self.log_queue.put(
            f"\nTesting has completed at {datetime.now().strftime('%H:%M:%S')}"
        )
        subprocess.run(
            [
                "notify-send",
                "Thread Stepper",
                f"Testing has completed at {datetime.now().strftime('%H:%M:%S')}",
            ]
        )

        update_error_status(self)
        update_error_log(self)

    except Exception as e:
        self.log_queue.put(f"Error running tests: {str(e)}")
    finally:
        self.process = None
        self.is_running = False
        self.benchmark_mode = False
        self.root.after(0, lambda: on_process_stop(self))
        clear_current_test(self)


def stop_stress_test(self):
    if self.process and self.is_running:
        self.process.terminate()
    if self.benchmark_mode:
        log_message(self, "Stopping benchmark...", "warning")
        self.status_bar.config(text="Stopping benchmark...")
        subprocess.run(
            [
                "notify-send",
                "Thread Stepper",
                f"Benchmark stopping at {datetime.now().strftime('%H:%M:%S')}",
            ]
        )
    else:
        log_message(self, "Stopping testing, please wait...", "warning")
        self.status_bar.config(text="Stopping testing...")
        stop_timer(self)
        subprocess.run(["pkill", "-f", "threadstepper"])
        subprocess.run(["pkill", "-f", "logger.sh"])
        subprocess.run(["pkill", "-f", "bash -c"])
        subprocess.run(["pkill", "-f", "load_test.sh"])
        subprocess.run(["pkill", "-f", "load_worker.sh"])
        subprocess.run(["pkill", "-f", "launch.js"])
        self.progress.stop()
        self.progress.grid_remove()


def on_process_stop(self):
    self.start_button.config(state=tk.NORMAL)
    self.stop_button.config(state=tk.DISABLED)
    if self.benchmark_mode:
        self.status_bar.config(text="Benchmark stopped")
        update_error_status(self)
        stop_timer(self)
        self.progress.stop()
        self.progress.grid_remove()
    else:
        self.status_bar.config(text="Testing stopped")
        update_error_status(self)
        stop_timer(self)
        self.progress.stop()
        self.progress.grid_remove()
    self.is_running = False
    self.benchmark_mode = False