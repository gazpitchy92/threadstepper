import os
import platform
import subprocess
import re
import psutil

from ui.logs import log_message, clear_output, clear_current_test
from ui.errors import clear_error_log, update_error_log, update_error_status
from ui.clocks import update_clock_speed, reset_clock_speed

def reset_button(self):
    clear_output(self)
    reset_clock_speed(self)
    clear_error_log(self)
    refresh_system_info(self)
    log_message(self, "Logs, Clocks and Errors have been reset", "info")

def get_cpu_model():
    with open("/proc/cpuinfo") as f:
        for line in f:
            if line.startswith("model name"):
                name = re.sub(r"model name\s*:\s*", "", line).strip()
                if "Ryzen" in name:
                    name = re.sub(r"Ryzen\s*", "", name)
                    name = re.sub(r"\d+-Core\s*", "", name)
                    name = re.sub(r"Processor\s*", "", name)
                    name = re.sub(r"\b\d\b\s*", "", name)
                return name.strip()
    return "Unknown"

def refresh_system_info(self):
    import psutil

    self.os_label.config(text=f" {platform.system()} {platform.release()}")

    try:
        freq = psutil.cpu_freq()
        min_ghz = freq.min / 1000
        max_ghz = freq.max / 1000
        ram_gb = psutil.virtual_memory().total / 1024**3
        cpu_model = get_cpu_model()

        self.cores_label.config(text=f" {psutil.cpu_count(logical=False)}/{psutil.cpu_count(logical=True)}")
        self.cpu_freq.config(text=f" {min_ghz:.3f}-{max_ghz:.3f} GHz")
        self.model_label.config(text=f" {cpu_model}")

    except ImportError:
        self.cores_label.config(text=" N/A (install psutil)")
        self.cpu_freq.config(text=" N/A")
        self.model_label.config(text=f" N/A")

    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
            governor = f.read().strip()
    except:
        governor = "N/A"

    self.governor_label.config(text=f" {governor}")

def full_reset(self):
    try:
        subprocess.run(["pkill", "-f", "threadstepper"])
        subprocess.run(["pkill", "-f", "logger.sh"])
    except Exception as e:
        log_message(self, f"Error killing logger.sh: {str(e)}", "error")
        
    with open("./logs/errors.log", "w") as f:
        f.write("false")
    with open("./logs/clock.log", "w") as f:
        f.write("0")
    with open("./logs/output.log", "w") as f:
        f.write("-- STARTUP --")

    clear_current_test(self)
    clear_error_log(self)
    clear_output(self)
    refresh_system_info(self)
    update_clock_speed(self)
    update_error_log(self)
    update_error_status(self)

def on_close(self):
    try:
        subprocess.run(["pkill", "-f", "threadstepper"])
        subprocess.run(["pkill", "-f", "logger.sh"])
        subprocess.run(["pkill", "-f", "bash -c"])
        subprocess.run(["pkill", "-f", "load_test.sh"])
        subprocess.run(["pkill", "-f", "load_worker.sh"])
        subprocess.run(["pkill", "-f", "launch.js"])
        if self.is_running and self.process:
            self.process.terminate()
            self.process = None
        full_reset(self)
        clear_current_test(self)
        self.stop_stress_test()
        self.root.destroy()
    except Exception as e:
        log_message(self, f"Error stop_stress_test: {str(e)}", "error")
    
def detect_cpu_topology(settings_path="./settings"):
    import re

    num_logical = os.cpu_count() or 1

    # Build map: cpu_id -> core_id
    cpu_to_core = {}
    try:
        for cpu_path in os.listdir("/sys/devices/system/cpu"):
            if not re.match(r"^cpu\d+$", cpu_path):
                continue
            cpu_id = int(cpu_path[3:])
            core_file = f"/sys/devices/system/cpu/{cpu_path}/topology/core_id"
            if os.path.exists(core_file):
                with open(core_file) as f:
                    cpu_to_core[cpu_id] = int(f.read().strip())
    except Exception:
        pass

    if not cpu_to_core:
        topology = 0
    else:
        # First cpu_id per physical core
        core_to_first_cpu = {}
        for cpu_id, core_id in cpu_to_core.items():
            if core_id not in core_to_first_cpu or cpu_id < core_to_first_cpu[core_id]:
                core_to_first_cpu[core_id] = cpu_id

        sorted_cores = sorted(core_to_first_cpu.keys())
        num_cores = len(sorted_cores)
        half_cores = num_cores // 2

        # cross-die
        cross_matches, cross_checks = 0, 0
        for i in range(half_cores):
            core_a, core_b = sorted_cores[i], sorted_cores[i + half_cores]
            cpu_a, cpu_b = core_to_first_cpu[core_a], core_to_first_cpu[core_b]
            sib_path_a = f"/sys/devices/system/cpu/cpu{cpu_a}/topology/thread_siblings_list"
            sib_path_b = f"/sys/devices/system/cpu/cpu{cpu_b}/topology/thread_siblings_list"
            try:
                with open(sib_path_a) as f:
                    sib_a = set()
                    for part in f.read().strip().split(","):
                        if "-" in part:
                            a, b = part.split("-")
                            sib_a.update(range(int(a), int(b) + 1))
                        else:
                            sib_a.add(int(part))
                with open(sib_path_b) as f:
                    sib_b = set()
                    for part in f.read().strip().split(","):
                        if "-" in part:
                            a, b = part.split("-")
                            sib_b.update(range(int(a), int(b) + 1))
                        else:
                            sib_b.add(int(part))
                cross_checks += 1
                if cpu_b not in sib_a and cpu_a not in sib_b:
                    cross_matches += 1
            except Exception:
                pass

        # adjacent die
        adj_matches, adj_checks = 0, 0
        for i in range(num_cores - 1):
            core_a, core_b = sorted_cores[i], sorted_cores[i + 1]
            cpu_a, cpu_b = core_to_first_cpu[core_a], core_to_first_cpu[core_b]
            die_path_a = f"/sys/devices/system/cpu/cpu{cpu_a}/topology/die_id"
            die_path_b = f"/sys/devices/system/cpu/cpu{cpu_b}/topology/die_id"
            adj_checks += 1
            try:
                with open(die_path_a) as f:
                    die_a = f.read().strip()
                with open(die_path_b) as f:
                    die_b = f.read().strip()
                if die_a == die_b:
                    adj_matches += 1
            except Exception:
                if (core_b - core_a) == 1:
                    adj_matches += 1

        cross_ratio = (cross_matches * 100 // cross_checks) if cross_checks else 0
        adj_ratio   = (adj_matches * 100 // adj_checks)   if adj_checks   else 0

        if cross_ratio >= 80:
            topology = 1
        elif adj_ratio >= 80:
            topology = 2
        else:
            topology = 0

    # Save topology
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                content = f.read()
            if re.search(r"^cpu_topology=", content, re.MULTILINE):
                content = re.sub(r"^cpu_topology=.*", f"cpu_topology={topology}", content, flags=re.MULTILINE)
            else:
                content += f"\ncpu_topology={topology}"
            with open(settings_path, "w") as f:
                f.write(content)
    except Exception:
        pass