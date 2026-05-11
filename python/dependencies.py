import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

from python.logs import clear_output, export_log, log_message


def install_dependencies(self):
    clear_output(self)

    install_script = "./install.sh"

    if not os.path.exists(install_script):
        messagebox.showerror(
            "File Not Found",
            f"install.sh not found in current directory.\n\n"
            f"Current directory: {os.getcwd()}\n"
            f"Expected at: {install_script}",
        )
        return

    try:
        os.chmod(install_script, 0o755)
    except:
        pass

    system = platform.system()

    try:
        terminals = [
            [
                "x-terminal-emulator",
                "-e",
                f"bash -c '{install_script}; echo \"Press Enter to close...\"; read'",
            ],
            [
                "gnome-terminal",
                "--",
                "bash",
                "-c",
                f"{install_script}; echo 'Press Enter to close...'; read",
            ],
            [
                "konsole",
                "-e",
                "bash",
                "-c",
                f"{install_script}; echo 'Press Enter to close...'; read",
            ],
            [
                "xterm",
                "-e",
                "bash",
                "-c",
                f"{install_script}; echo 'Press Enter to close...'; read",
            ],
            [
                "terminator",
                "-e",
                f"bash -c '{install_script}; echo \"Press Enter to close...\"; read'",
            ],
            [
                "xfce4-terminal",
                "-e",
                f"bash -c '{install_script}; echo \"Press Enter to close...\"; read'",
            ],
        ]

        for terminal_cmd in terminals:
            try:
                subprocess.Popen(terminal_cmd, start_new_session=True)
                log_message(self, f"Opening terminal to run installer...", "info")
                log_message(
                    self, "Follow installations in the terminal window.", "info"
                )
                return
            except:
                continue

        subprocess.Popen(["bash", install_script], start_new_session=True)
        log_message(self, "Running install.sh in background...", "info")
        self.status_bar.config(text="Running install.sh in new terminal...")

    except Exception as e:
        error_msg = f"Failed to open terminal: {str(e)}"
        log_message(self, error_msg, "error")
        messagebox.showerror("Error", error_msg)
