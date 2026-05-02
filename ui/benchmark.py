import os
import subprocess
import threading
import tkinter as tk
from datetime import datetime

from ui.system import full_reset
from ui.logs import log_message

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
    
    threading.Thread(target=run_benchmark, args=(self,), daemon=True).start()

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