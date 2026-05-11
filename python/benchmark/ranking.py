import os
import subprocess
import threading
import signal
import time
import tkinter as tk
from tkinter import ttk

from python.ui import make_section

RANKS_LOG  = "./logs/ranks.log"
RANK_SCRIPT = "./functions/benchmark/rank.sh"

def build_core_ranks_tab(self):

    tab = self.core_ranks_tab
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(0, weight=1)

    # Container
    outer = tk.Frame(tab)
    outer.grid(row=0, column=0, sticky="nsew")
    outer.columnconfigure(0, weight=1)
    outer.rowconfigure(1, weight=1)
    outer.rowconfigure(2, weight=0)

    # Header
    header_frame, header_inner = make_section(self, outer, "⚃ Core Rankings", padding=6)
    header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))

    tk.Label(
        header_inner,
        text="CPPC preference  ·  SMT threads  ·  benchmark score",
        font=("Segoe UI", 9),
    ).pack(anchor="w")

    # Scrollable area
    scroll_host = tk.Frame(outer)
    scroll_host.grid(row=1, column=0, sticky="nsew")
    scroll_host.columnconfigure(0, weight=1)
    scroll_host.rowconfigure(0, weight=1)
    canvas = tk.Canvas(scroll_host, highlightthickness=0, bd=0)
    vscroll = ttk.Scrollbar(scroll_host, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vscroll.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    vscroll.grid(row=0, column=1, sticky="ns")
    inner = tk.Frame(canvas)
    window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    def _on_frame_configure(_evt):
        canvas.configure(scrollregion=canvas.bbox("all"))
    def _on_canvas_configure(evt):
        canvas.itemconfigure(window_id, width=evt.width)
    inner.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_canvas_configure)
    inner.columnconfigure(0, weight=1)

    # Data
    topology = _get_cpu_topology()
    cppc_raw = _get_cppc_ranking()
    cppc_by_cpu = {cpu: score for cpu, score in cppc_raw}
    core_cppc: dict[int, tuple[int, int]] = {}
    sorted_cores = sorted(topology.keys())
    for core_id in sorted_cores:
        threads = topology[core_id]
        rep_thread = min(threads)
        score = cppc_by_cpu.get(rep_thread)
        core_cppc[core_id] = score

    # Rank cores
    cores_with_score = [(c, s) for c, s in core_cppc.items() if s is not None]
    cores_with_score.sort(key=lambda x: x[1], reverse=True)
    cppc_rank: dict[int, int] = {c: i + 1 for i, (c, _) in enumerate(cores_with_score)}
    total_cores = len(sorted_cores)
    cppc_available = bool(cores_with_score)
    self.core_score_labels = {}

    # Build card for core
    for row_idx, core_id in enumerate(sorted_cores):
        threads   = sorted(topology[core_id])
        cppc_score = core_cppc.get(core_id)
        rank       = cppc_rank.get(core_id)

        _build_core_card(
            parent         = inner,
            row            = row_idx,
            core_id        = core_id,
            threads        = threads,
            cppc_score     = cppc_score,
            cppc_rank      = rank,
            total_cores    = total_cores,
            cppc_available = cppc_available,
            score_labels   = self.core_score_labels,
        )

    if not sorted_cores:
        tk.Label(
            inner, text="No CPU topology data found.",
            font=("Segoe UI", 10),
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")

    # Load previous
    _apply_log_scores(self.core_score_labels)

    # Benchmark state
    self._cr_running    = False
    self._cr_stop_flag  = threading.Event()
    self._cr_thread     = None
    self._cr_timer_secs = 0

    # Bottom
    toolbar = tk.Frame(outer, pady=8, padx=12)
    toolbar.grid(row=2, column=0, sticky="ew")
    toolbar.columnconfigure(0, weight=1)

    # Timer
    cr_timer_label = tk.Label(
        toolbar,
        text="00:00:00",
        font=("Segoe UI", 11, "bold"),
        relief="sunken",
        width=9,
        padx=5,
    )
    cr_timer_label.pack(side="right", padx=(8, 0))
    self._cr_timer_label = cr_timer_label

    # Status label
    cr_status = tk.Label(
        toolbar,
        text="Ready",
        font=("Segoe UI", 9),
    )
    cr_status.pack(side="left")
    self._cr_status_label = cr_status

    # Timers
    def _tick():
        if not self._cr_running:
            return
        h, rem = divmod(self._cr_timer_secs, 3600)
        m, s   = divmod(rem, 60)
        cr_timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self._cr_timer_secs += 1
        self.win.after(1000, _tick)

    # Start / Stop buttons
    def _do_start():
        if self._cr_running:
            return
        self._cr_running    = True
        self._cr_timer_secs = 0
        self._cr_stop_flag.clear()
        cr_status.config(text="Starting…")
        cr_start_btn.config(state="disabled")
        cr_stop_btn.config(state="normal")

        try:
            os.makedirs("./logs", exist_ok=True)
            open(RANKS_LOG, "w").close()
        except OSError:
            pass

        for lbl in self.core_score_labels.values():
            lbl.config(text="…")

        _tick()

        self._cr_thread = threading.Thread(
            target=_run_rank_benchmark,
            args=(self, sorted_cores, topology, cr_status, cr_start_btn, cr_stop_btn),
            daemon=False,
        )
        self._cr_thread.start()

    def _do_stop():
        self._cr_stop_flag.set()
        self._cr_running = False
        _kill_rank_group(self)
        cr_status.config(text="Stopped")
        cr_start_btn.config(state="normal")
        cr_stop_btn.config(state="disabled")

    # Buttons
    ttk.Button(
        toolbar,
        text="⊗ Close",
        bootstyle="danger-outline",
        command=self._close,
    ).pack(side="right", padx=(4, 0))

    cr_stop_btn = ttk.Button(
        toolbar,
        text="⊠ Stop",
        bootstyle="danger",
        state="disabled",
        command=_do_stop,
    )
    cr_stop_btn.pack(side="right", padx=(4, 0))
    self._cr_stop_btn = cr_stop_btn

    cr_start_btn = ttk.Button(
        toolbar,
        text="▶ Start",
        bootstyle="success",
        command=_do_start,
    )
    cr_start_btn.pack(side="right", padx=(4, 0))
    self._cr_start_btn = cr_start_btn

# Core card
def _build_core_card(
    parent, row, core_id, threads,
    cppc_score, cppc_rank, total_cores,
    cppc_available, score_labels,
):
    """Render one core as a self-contained card row."""

    pad_x, pad_y = 12, 4

    card = tk.Frame(
        parent,
        highlightthickness=1,
    )
    card.grid(row=row, column=0, sticky="ew", padx=pad_x, pady=pad_y)
    card.columnconfigure(1, weight=1)

    # CPPC
    left = tk.Frame(card, width=120, padx=10, pady=8)
    left.grid(row=0, column=0, sticky="ns")
    left.pack_propagate(False)

    tk.Label(
        left, text=f"CORE {core_id:02d}",
        font=("Consolas", 11, "bold"),
    ).pack(anchor="w")

    if cppc_available:
        if cppc_rank is not None:
            badge_text = _rank_badge(cppc_rank, total_cores)
            tk.Label(
                left,
                text=f"CPPC #{cppc_rank}  {badge_text}",
                font=("Segoe UI", 8),
            ).pack(anchor="w", pady=(2, 0))

            if cppc_score is not None:
                tk.Label(
                    left,
                    text=f"score {cppc_score}",
                    font=("Segoe UI", 7),
                ).pack(anchor="w")
    else:
        tk.Label(
            left, text="CPPC N/A",
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(2, 0))
    sep = tk.Frame(card, width=1)
    sep.grid(row=0, column=1, sticky="ns", padx=(0, 0))

    # Details
    mid = tk.Frame(card, padx=10, pady=8)
    mid.grid(row=0, column=2, sticky="nsew")
    card.columnconfigure(2, weight=1)

    tk.Label(
        mid, text="THREADS",
        font=("Segoe UI", 7, "bold"),
    ).pack(anchor="w")

    pills = tk.Frame(mid)
    pills.pack(anchor="w", pady=(3, 0))

    for tid in threads:
        pill = tk.Frame(pills, padx=6, pady=2)
        pill.pack(side="left", padx=(0, 4))
        tk.Label(
            pill, text=f"T{tid}",
            font=("Consolas", 9, "bold"),
        ).pack()

    # Scores
    sep2 = tk.Frame(card, width=1)
    sep2.grid(row=0, column=3, sticky="ns")

    right = tk.Frame(card, width=130, padx=10, pady=8)
    right.grid(row=0, column=4, sticky="ns")
    right.pack_propagate(False)

    tk.Label(
        right, text="BENCH SCORE",
        font=("Segoe UI", 7, "bold"),
    ).pack(anchor="w")

    score_lbl = tk.Label(
        right, text="—",
        font=("Consolas", 13, "bold"),
    )
    score_lbl.pack(anchor="w", pady=(2, 0))

    score_labels[core_id] = score_lbl


def _rank_badge(rank: int, total: int) -> str:
    if rank == 1:
        return "★ best"
    pct = rank / total
    if pct <= 0.25:
        return "▲ top"
    if pct <= 0.60:
        return "● mid"
    return "▼ low"


# Benchmarks
def _run_rank_benchmark(self, sorted_cores, topology, cr_status, cr_start_btn, cr_stop_btn):
    for core_id in sorted_cores:
        if self._cr_stop_flag.is_set():
            break

        threads = sorted(topology[core_id])

        self.win.after(0, lambda c=core_id: cr_status.config(
            text=f"Testing core {c:02d}…",
        ))

        try:
            os.chmod(RANK_SCRIPT, 0o755)
        except OSError:
            pass

        try:
            proc = subprocess.Popen(
                [RANK_SCRIPT, str(core_id)] + [str(t) for t in threads],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid 
            )

            self._cr_proc = proc
            self._cr_pgid = os.getpgid(proc.pid)

            stdout_lines = []
            
            while True:
                if self._cr_stop_flag.is_set():
                    try:
                        os.killpg(proc.pid, signal.SIGTERM)
                        time.sleep(0.1)
                        os.killpg(proc.pid, signal.SIGKILL)
                    except Exception:
                        pass
                    break
                
                line = proc.stdout.readline()
                if line:
                    stdout_lines.append(line)
                
                if proc.poll() is not None:
                    break
                
                time.sleep(0.01)
            
            proc.wait()
            stdout = "".join(stdout_lines)
            
        except Exception as e:
            self.win.after(0, lambda msg=str(e): cr_status.config(
                text=f"Error: {msg}",
            ))
            break

        if self._cr_stop_flag.is_set():
            break

        score_str = stdout.strip().splitlines()[-1] if stdout.strip() else ""
        try:
            score = int(score_str)
        except ValueError:
            score = None

        def _post(c=core_id, s=score):
            lbl = self.core_score_labels.get(c)
            if lbl:
                if s is not None:
                    lbl.config(text=f"{s:,}", font=("Consolas", 13, "bold"))
                else:
                    lbl.config(text="err")
        self.win.after(0, _post)

    # Done
    if not self._cr_stop_flag.is_set():
        def _done():
            cr_status.config(text="Complete ✓")
            cr_start_btn.config(state="normal")
            cr_stop_btn.config(state="disabled")
            self._cr_running = False
        self.win.after(0, _done)
    else:
        def _partial():
            for lbl in self.core_score_labels.values():
                if lbl.cget("text") == "…":
                    lbl.config(text="—")
            cr_status.config(text="Stopped")
            cr_start_btn.config(state="normal")
            cr_stop_btn.config(state="disabled")
            self._cr_running = False
        self.win.after(0, _partial)

# Logging

def _read_ranks_log() -> dict[int, int]:
    scores: dict[int, int] = {}
    if not os.path.exists(RANKS_LOG):
        return scores
    try:
        with open(RANKS_LOG) as f:
            for line in f:
                line = line.strip()
                if not line or "," not in line:
                    continue
                core_str, score_str = line.split(",", 1)
                scores[int(core_str)] = int(score_str)
    except (OSError, ValueError):
        pass
    return scores


def _apply_log_scores(score_labels: dict):
    """Populate card labels from the last run's log file."""
    scores = _read_ranks_log()
    for core_id, score in scores.items():
        lbl = score_labels.get(core_id)
        if lbl:
            lbl.config(text=f"{score:,}", font=("Consolas", 13, "bold"))


# System

def _get_cpu_topology() -> dict[int, list[int]]:
    topology: dict[int, list[int]] = {}
    try:
        result = subprocess.run(
            ["lscpu", "--parse=CPU,CORE"],
            capture_output=True, text=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            cpu, core = line.split(",")
            topology.setdefault(int(core), []).append(int(cpu))
        if topology:
            return topology
    except Exception:
        pass
    try:
        cur_cpu = cur_core = None
        with open("/proc/cpuinfo") as f:
            for line in f:
                line = line.strip()
                if line.startswith("processor"):
                    cur_cpu = int(line.split(":")[1])
                elif line.startswith("core id"):
                    cur_core = int(line.split(":")[1])
                elif line == "" and cur_cpu is not None and cur_core is not None:
                    topology.setdefault(cur_core, []).append(cur_cpu)
                    cur_cpu = cur_core = None
        if topology:
            return topology
    except Exception:
        pass
    n = os.cpu_count() or 1
    return {i: [i] for i in range(n)}

def _get_cppc_ranking() -> list[tuple[int, int]]:
    cppc: list[tuple[int, int]] = []
    cpu_base = "/sys/devices/system/cpu"
    try:
        for cpu in os.listdir(cpu_base):
            if not cpu.startswith("cpu") or not cpu[3:].isdigit():
                continue
            idx  = int(cpu[3:])
            path = f"{cpu_base}/{cpu}/acpi_cppc/highest_perf"
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        val = int(f.read().strip())
                    cppc.append((idx, val))
                except Exception:
                    continue
    except Exception:
        return []
    return sorted(cppc, key=lambda x: x[1], reverse=True)

def _close(self):
    self._cr_stop_flag.set()
    self._cr_running = False
    _kill_rank_group(self)

def _kill_rank_group(self):
    pgid = getattr(self, "_cr_pgid", None)
    if pgid:
        try:
            os.killpg(pgid, signal.SIGTERM)
        except Exception:
            pass
        time.sleep(0.2)
        try:
            os.killpg(pgid, signal.SIGKILL)
        except Exception:
            pass

