import os
import tkinter as tk
from tkinter import ttk

def open_core_picker(self):
    topology = {}
    physical_threads = set()

    # Find CPU Topology
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

    # Check physical and virtual threads
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

    # Check existing blacklist
    current = self.core_blacklist_var.get()
    try:
        blacklisted = {int(x.strip()) for x in current.split(",") if x.strip().isdigit()}
    except ValueError:
        blacklisted = set()

    # Build pop-up window
    win = tk.Toplevel(self.root)
    win.title("Enabled Threads")
    win.resizable(False, False)
    win.grab_set()

    ttk.Label(win, text="Select threads to enable  (red = disabled)",
        font=("Segoe UI", 10)).pack(pady=(2, 2), padx=2)
    ttk.Label(win, text="(P) = Physical  (HT) = Virtual",
        font=("Segoe UI", 10)).pack(pady=(2, 2), padx=2)

    scroll_frame_outer = ttk.Frame(win)
    scroll_frame_outer.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(scroll_frame_outer, highlightthickness=0)
    scrollbar = ttk.Scrollbar(scroll_frame_outer, orient="vertical", command=canvas.yview)
    grid_frame = ttk.Frame(canvas)

    grid_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=grid_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    THREAD_COLS = 4
    btn_vars = {}

    for grid_row, (core_id, threads) in enumerate(sorted(topology.items())):
        ttk.Label(grid_frame, text=f"Core {core_id}",
                font=("Segoe UI", 9, "bold")).grid(
            row=grid_row * 2, column=0, columnspan=THREAD_COLS,
            sticky="w", padx=6, pady=(8, 0)
        )

        for col, thread_id in enumerate(sorted(threads)):
            is_enabled = thread_id not in blacklisted
            var = tk.BooleanVar(value=is_enabled)
            btn_vars[thread_id] = var

            tag = "(P)" if thread_id in physical_threads else "(HT)"
            label = f"Thread {thread_id} {tag}"

            style = "success-outline" if is_enabled else "danger"
            btn = ttk.Button(grid_frame, text=label, width=14, bootstyle=style)

            def make_toggle(t_id, b):
                def toggle():
                    btn_vars[t_id].set(not btn_vars[t_id].get())
                    b.config(bootstyle="success-outline" if btn_vars[t_id].get() else "danger")
                return toggle

            btn.config(command=make_toggle(thread_id, btn))
            btn.grid(row=grid_row * 2 + 1, column=col, padx=4, pady=2)

    win.update_idletasks()
    content_height = min(grid_frame.winfo_reqheight() + 20, 400)
    canvas.config(height=content_height)

    def confirm():
        result = ",".join(
            str(t) for t in sorted(k for k, v in btn_vars.items() if not v.get())
        )
        self.core_blacklist_var.set(result)
        win.destroy()

    btn_row = ttk.Frame(win, padding=(10, 5))
    btn_row.pack(fill="x")
    ttk.Button(btn_row, text="✔ Confirm", bootstyle="success",
            command=confirm).pack(side="right", padx=4, pady=(0, 4))
    ttk.Button(btn_row, text="⊗ Cancel", bootstyle="secondary-outline",
            command=win.destroy).pack(side="right", padx=4, pady=(0, 4))