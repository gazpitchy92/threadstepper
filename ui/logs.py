import os
import re
import time
import queue
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from datetime import datetime

def export_log(self, text_widget=None):
    try:
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            widget = text_widget if text_widget else self.output_text
            content = widget.get(1.0, tk.END)

            with open(filename, 'w') as f:
                f.write(content)

            log_message(self, f"Log exported to {filename}", "success")

    except Exception as e:
        log_message(self, f"Error exporting log: {str(e)}", "error")

def create_log_tags(widget):
    widget.tag_config("error", foreground="red")
    widget.tag_config("success", foreground="green")
    widget.tag_config("warning", foreground="orange")
    widget.tag_config("info", foreground="blue")

    ansi_color_map = {
        'black': '#000000',
        'red': '#cd0000',
        'green': '#00cd00',
        'yellow': '#cdcd00',
        'blue': '#0000ee',
        'magenta': '#cd00cd',
        'cyan': '#00cdcd',
        'white': '#e5e5e5',
        'bright_black': '#7f7f7f',
        'bright_red': '#ff0000',
        'bright_green': '#00ff00',
        'bright_yellow': '#ffff00',
        'bright_blue': '#5c5cff',
        'bright_magenta': '#ff00ff',
        'bright_cyan': '#00ffff',
        'bright_white': '#ffffff'
    }

    for color_name, color_hex in ansi_color_map.items():
        widget.tag_config(f"ansi_{color_name}", foreground=color_hex)

def insert_log(widget, message, tag="info"):
    timestamp = datetime.now().strftime("[%H:%M:%S] ")

    message = re.sub(r'\x1b\(B|\033\(B', '', message)

    ansi_color_map = {
        '30': 'black', '31': 'red', '32': 'green', '33': 'yellow',
        '34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white',
        '90': 'bright_black', '91': 'bright_red', '92': 'bright_green',
        '93': 'bright_yellow', '94': 'bright_blue', '95': 'bright_magenta',
        '96': 'bright_cyan', '97': 'bright_white'
    }

    widget.insert(tk.END, timestamp, tag)

    ansi_pattern = r'\x1b\[([0-9;]+)m|\033\[([0-9;]+)m|\[([0-9;]+)m'
    reset_pattern = r'\(B\[m|\[m|\x1b\[m|\033\[m'

    current_tag = tag
    last_pos = 0

    full_message = re.sub(reset_pattern, '\x00RESET\x00', message)

    for match in re.finditer(ansi_pattern, full_message):
        text_before = full_message[last_pos:match.start()]

        if text_before:
            parts = text_before.split('\x00RESET\x00')

            for i, part in enumerate(parts):
                if part:
                    widget.insert(tk.END, part, current_tag)

                if i < len(parts) - 1:
                    current_tag = tag

        code = match.group(1) or match.group(2) or match.group(3)

        if code == '0' or code == '':
            current_tag = tag
        else:
            codes = code.split(';')

            for c in codes:
                if c in ansi_color_map:
                    current_tag = f"ansi_{ansi_color_map[c]}"
                    break

        last_pos = match.end()

    remaining = full_message[last_pos:]

    if remaining:
        parts = remaining.split('\x00RESET\x00')

        for i, part in enumerate(parts):
            if part:
                widget.insert(tk.END, part, current_tag)

            if i < len(parts) - 1:
                current_tag = tag

    widget.insert(tk.END, "\n", tag)
    widget.see(tk.END)
    widget.update_idletasks()

def log_message(self, message, tag="info"):
    insert_log(self.output_text, message, tag)

    valid_windows = []

    for window_data in self.output_windows:
        try:
            window = window_data["window"]
            text_widget = window_data["text"]

            if window.winfo_exists():
                insert_log(text_widget, message, tag)
                valid_windows.append(window_data)

        except:
            pass

    self.output_windows = valid_windows

def open_output_window(self):
    window = tk.Toplevel(self.root)
    window.title("Test Output")
    window.geometry("775x675")
    window.resizable(True, True)

    container = ttk.Frame(window, padding=10)
    container.pack(fill="both", expand=True)

    text_widget = scrolledtext.ScrolledText(
        container,
        wrap="word",
        font=("Segoe UI", 12)
    )
    text_widget.pack(fill="both", expand=True, pady=(0, 10))

    create_log_tags(text_widget)

    existing_content = self.output_text.get(1.0, tk.END)
    text_widget.insert(tk.END, existing_content)
    text_widget.see(tk.END)

    btn_frame = ttk.Frame(container)
    btn_frame.pack(fill="x")

    ttk.Button(
        btn_frame,
        text="⎙ Save Logs",
        bootstyle="success-outline",
        command=lambda: export_log(self, text_widget)
    ).pack(side="right", padx=2)

    ttk.Button(
        btn_frame,
        text="⊗ Close",
        bootstyle="danger-outline",
        command=window.destroy
    ).pack(side="right", padx=2)

    self.output_windows.append({
        "window": window,
        "text": text_widget
    })

def clear_output(self):
    self.output_text.delete(1.0, tk.END)

    valid_windows = []

    for window_data in self.output_windows:
        try:
            window = window_data["window"]
            text_widget = window_data["text"]

            if window.winfo_exists():
                text_widget.delete(1.0, tk.END)
                valid_windows.append(window_data)

        except:
            pass

    self.output_windows = valid_windows

    self.reset_timer()

def clear_current_test(self):
    try:
        if os.path.exists("./logs/current.log"):
            with open("./logs/current.log", "w") as f:
                f.write("Waiting...")

            update_current_test(self)

    except Exception as e:
        log_message(self, f"Error clearing test: {str(e)}", "error")

def set_current_test(self, test):
    try:
        if os.path.exists("./logs/current.log"):
            with open("./logs/current.log", "w") as f:
                f.write(test)

            update_current_test(self)

    except Exception as e:
        log_message(self, f"Error setting current test: {str(e)}", "error")

def monitor_current_test(self):
    last_mtime = 0

    while True:
        try:
            if os.path.exists("./logs/current.log"):
                current_mtime = os.path.getmtime("./logs/current.log")

                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    self.root.after(0, lambda: update_current_test(self))

        except:
            pass

        time.sleep(0.5)

def update_current_test(self):
    try:
        lines = []
        threads = "N/A"

        if os.path.exists("./logs/current.log"):
            with open("./logs/current.log", "r") as f:
                lines = f.readlines()

        if os.path.exists("./logs/threads.log"):
            with open("./logs/threads.log", "r") as f:
                threads = f.read().strip()
                core = threads.split(",")[0]

        if lines:
            test_name = lines[0].strip() if len(lines) > 0 else ""
            progress = lines[1].strip() if len(lines) > 1 else ""

            if test_name == "Starting...":
                self.clock_label_bottom.config(
                    text="▷ " + test_name + "\n" + progress,
                    fg="#856404",
                    bg="#fff3cd"
                )
            elif test_name == "Waiting...":
                self.clock_label_bottom.config(
                    text="⏚ " + test_name + "\n" + progress,
                    fg="#343a40",
                    bg="#e9ecef"
                )
            elif test_name == "Failed!":
                self.clock_label_bottom.config(
                    text="✘ " + test_name + "\n Threads: " + threads + "\n Core: " + core,
                    fg="#ffffff",
                    bg="#dc3545"
                )
            elif "Rapid" in test_name or "Random" in test_name:
                self.clock_label_bottom.config(
                    text="≡ " + test_name + "\n" + progress,
                    fg="#28a745",
                    bg="#d4edda"
                )
            elif "Single" in test_name:
                self.clock_label_bottom.config(
                    text="◫ " + test_name + "\n" + progress,
                    fg="#28a745",
                    bg="#d4edda"
                )
            elif "Browser" in test_name:
                self.clock_label_bottom.config(
                    text="☉ " + test_name + "\n" + progress,
                    fg="#28a745",
                    bg="#d4edda"
                )
            else:
                self.clock_label_bottom.config(
                    text="▦ " + test_name + "\n" + progress,
                    fg="#28a745",
                    bg="#d4edda"
                )
        else:
            self.clock_label_bottom.config(
                text="No data",
                fg="#6c757d",
                bg="#f8f9fa"
            )

    except Exception as e:
        self.clock_label_bottom.config(
            text="Error reading",
            fg="#721c24",
            bg="#f8d7da"
        )

def process_log_queue(self):
    while True:
        try:
            message = self.log_queue.get_nowait()
            self.root.after(0, lambda msg=message: log_message(self, msg))

        except queue.Empty:
            time.sleep(0.1)