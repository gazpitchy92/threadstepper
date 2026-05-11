import threading
import time

def start_timer(self):
    self.timer_seconds = 0
    self.timer_running = True
    self.timer_label.config(fg="#28a745")
    if self.timer_thread is None or not self.timer_thread.is_alive():
        self.timer_thread = threading.Thread(target=update_timer, args=(self,), daemon=True)
        self.timer_thread.start()

def stop_timer(self):
    self.timer_running = False
    self.timer_label.config(fg="#dc3545")

def reset_timer(self):
    self.timer_running = False
    self.timer_seconds = 0
    self.root.after(0, lambda: self.timer_label.config(text="00:00:00", fg="#28a745"))

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

def monitor_process_status(self):
    from python.testing import on_process_stop
    while True:
        if self.is_running and self.process is not None:
            if self.process.poll() is not None:
                self.root.after(0, lambda: on_process_stop(self))
        time.sleep(0.5)