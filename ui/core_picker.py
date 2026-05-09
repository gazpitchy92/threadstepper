import os
import tkinter as tk
from tkinter import ttk


def open_core_picker(self):
    topology = {}
    physical_threads = set()

    # Find CPU topology
    try:
        import subprocess
        result = subprocess.run(
            ["lscpu", "--parse=CPU,CORE"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(",")
            if len(parts) == 2:
                thread_id, core_id = int(parts[0]), int(parts[1])
                topology.setdefault(core_id, []).append(thread_id)
    except Exception:
        topology = {}

    # /proc/cpuinfo fallback
    if not topology:
        try:
            current_processor = None
            current_core = None
            with open("/proc/cpuinfo") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("processor"):
                        current_processor = int(line.split(":")[1].strip())
                    elif line.startswith("core id"):
                        current_core = int(line.split(":")[1].strip())
                    elif line == "" and current_processor is not None and current_core is not None:
                        topology.setdefault(current_core, []).append(current_processor)
                        current_processor = None
                        current_core = None
        except Exception:
            topology = {}

    # No SMT fallback
    if not topology:
        num_cores = os.cpu_count() or 1
        topology = {i: [i] for i in range(num_cores)}

    # Detect physical vs HT threads
    try:
        seen_sibling_groups = set()
        for core_threads in topology.values():
            for thread_id in sorted(core_threads):
                sib_path = f"/sys/devices/system/cpu/cpu{thread_id}/topology/thread_siblings_list"
                with open(sib_path) as f:
                    raw = f.read().strip()
                siblings = set()
                for part in raw.split(","):
                    if "-" in part:
                        a, b = part.split("-")
                        siblings.update(range(int(a), int(b) + 1))
                    else:
                        siblings.add(int(part))
                group_key = frozenset(siblings)
                if group_key not in seen_sibling_groups:
                    seen_sibling_groups.add(group_key)
                    physical_threads.add(min(siblings))
    except Exception:
        for core_threads in topology.values():
            if core_threads:
                physical_threads.add(min(core_threads))

    # Parse existing blacklist
    current = self.core_blacklist_var.get()
    try:
        blacklisted = {int(x.strip()) for x in current.split(",") if x.strip().isdigit()}
    except ValueError:
        blacklisted = set()

    # Container
    win = tk.Toplevel(self.root)
    win.title("Thread Selection")
    win.resizable(False, False)
    win.grab_set()
    win.configure(padx=0, pady=0)

    # Header
    header_frame = ttk.Frame(win, padding=(14, 10, 14, 4))
    header_frame.pack(fill="x")
    ttk.Label(
        header_frame,
        text="Thread Selection",
        font=("Segoe UI", 12, "bold"),
    ).pack(anchor="w")
    ttk.Label(
        header_frame,
        text="Toggle threads to include in the test run.",
        font=("Segoe UI", 9),
        foreground="#888888",
    ).pack(anchor="w", pady=(1, 0))

    ttk.Separator(win, orient="horizontal").pack(fill="x")

    # Legend
    legend_frame = ttk.Frame(win, padding=(14, 6, 14, 0))
    legend_frame.pack(fill="x")
    ttk.Label(
        legend_frame,
        text="(P) = Physical  ·  (HT) = Hyper-Thread",
        font=("Segoe UI", 9),
        foreground="#888888",
    ).pack(anchor="w")

    # Threads grid
    outer = ttk.Frame(win, padding=(10, 8, 10, 4))
    outer.pack(fill="both", expand=False)

    canvas = tk.Canvas(outer, highlightthickness=0, borderwidth=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    grid_frame = ttk.Frame(canvas, padding=(2, 0))

    grid_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=grid_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left")
    scrollbar.pack(side="right", fill="y")

    THREAD_COLS = 4
    btn_vars = {}

    for grid_row, (core_id, threads) in enumerate(sorted(topology.items())):
        # Core separator row
        sep_frame = ttk.Frame(grid_frame)
        sep_frame.grid(
            row=grid_row * 2, column=0, columnspan=THREAD_COLS,
            sticky="ew", padx=4, pady=(10 if grid_row > 0 else 4, 3)
        )
        ttk.Label(
            sep_frame,
            text=f"  CORE {core_id}",
            font=("Segoe UI", 8, "bold"),
            foreground="#aaaaaa",
        ).pack(side="left")
        ttk.Separator(sep_frame, orient="horizontal").pack(
            side="left", fill="x", expand=True, padx=(6, 0), pady=1
        )

        # Thread buttons
        for col, thread_id in enumerate(sorted(threads)):
            is_enabled = thread_id not in blacklisted
            var = tk.BooleanVar(value=is_enabled)
            btn_vars[thread_id] = var

            tag = "(P)" if thread_id in physical_threads else "(HT)"
            label = f"T{thread_id}  {tag}"

            style = "success-outline" if is_enabled else "danger-outline"
            btn = ttk.Button(grid_frame, text=label, width=11, bootstyle=style)

            def make_toggle(t_id, b):
                def toggle():
                    new_state = not btn_vars[t_id].get()
                    btn_vars[t_id].set(new_state)
                    b.config(bootstyle="success-outline" if new_state else "danger-outline")
                return toggle

            btn.config(command=make_toggle(thread_id, btn))
            btn.grid(row=grid_row * 2 + 1, column=col, padx=3, pady=2, sticky="w")

    # Adjust window size
    win.update_idletasks()
    content_height = min(grid_frame.winfo_reqheight() + 16, 420)
    content_width = grid_frame.winfo_reqwidth() + 20
    canvas.config(height=content_height, width=content_width)

    # Footer
    ttk.Separator(win, orient="horizontal").pack(fill="x", pady=(4, 0))

    footer = ttk.Frame(win, padding=(10, 7, 10, 9))
    footer.pack(fill="x")

    ttk.Button(
        footer, text="✔ Confirm", bootstyle="success", width=12,
        command=lambda: [
            self.core_blacklist_var.set(
                ",".join(str(t) for t in sorted(k for k, v in btn_vars.items() if not v.get()))
            ),
            win.destroy()
        ]
    ).pack(side="right", padx=(4, 0))

    ttk.Button(
        footer, text="⊗ Cancel", bootstyle="secondary-outline", width=12,
        command=win.destroy
    ).pack(side="right")