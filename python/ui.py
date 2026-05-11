import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox, scrolledtext, ttk

def make_section(self, parent, title, **kwargs):
    outer = ttk.Frame(parent, **kwargs)
    header = ttk.Frame(outer)
    header.pack(fill="x", pady=(0, 6))

    lbl = ttk.Label(
        header, text=title, font=("Segoe UI", 11, "bold"), foreground="#000000"
    )

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

def setup_styles(self):
    style = ttk.Style()
    style.configure(
        "Install.TButton",
        foreground="blue",
        font=("Arial", 12),
    )
    self.output_text.tag_config("error", foreground="red")
    self.output_text.tag_config("success", foreground="green")
    self.output_text.tag_config("warning", foreground="orange")
    self.output_text.tag_config("info", foreground="blue")
