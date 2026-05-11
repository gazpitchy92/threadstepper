import os
import re
import tkinter as tk
from tkinter import ttk

from python.logs import log_message

def parse_settings_options(self, content):
    for line in content.splitlines():
        if line.startswith("loops="):
            self.loops_var.set(int(line.split("=")[1]))
        elif line.startswith("browsers="):
            self.browsers_var.set(int(line.split("=")[1]))
        elif line.startswith("light_time="):
            self.light_time_var.set(int(line.split("=")[1]))
        elif line.startswith("medium_time="):
            self.medium_time_var.set(int(line.split("=")[1]))
        elif line.startswith("heavy_time="):
            self.heavy_time_var.set(int(line.split("=")[1]))
        elif line.startswith("all_core_time="):
            self.all_core_time_var.set(int(line.split("=")[1]))
        elif line.startswith("all_core_tests="):
            self.all_core_tests_var.set(int(line.split("=")[1]))
        elif line.startswith("rapid_tests="):
            self.rapid_tests_var.set(int(line.split("=")[1]))
        elif line.startswith("rapid_time="):
            self.rapid_time_var.set(int(line.split("=")[1]))
        elif line.startswith("random_tests="):
            self.random_tests_var.set(int(line.split("=")[1]))
        elif line.startswith("random_time="):
            self.random_time_var.set(int(line.split("=")[1]))
        elif line.startswith("rest_time="):
            self.rest_time_var.set(int(line.split("=")[1]))
        elif line.startswith("core_blacklist="):
            val = line.split("=", 1)[1].strip().strip('"')
            self.core_blacklist_var.set(val)
        elif line.startswith("max_ram="):
            self.max_ram_var.set(int(line.split("=")[1]))

def sync_group_enabled_states(self):
    self.all_cores_enabled_var.set(
        any(v.get() != 0 for v in self.group_vars["all_cores"])
    )
    self.low_load_enabled_var.set(
        any(v.get() != 0 for v in self.group_vars["low_load"])
    )
    self.single_core_enabled_var.set(
        any(v.get() != 0 for v in self.group_vars["single_core"])
    )
    self.webgl_enabled_var.set(
        any(v.get() != 0 for v in self.group_vars["webgl"])
    )

def validate_core_blacklist(self, value):
    if value == "":
        return True
    return bool(re.fullmatch(r"\d+(,\d+)*", value))

def update_settings_content(self):
    try:
        if os.path.exists("./config/user.settings"):
            with open("./config/user.settings", "r") as f:
                content = f.read()
                parse_settings_options(self, content)
                sync_group_enabled_states(self)
                self.root.update_idletasks()  # Force UI refresh
            self.status_bar.config(text="Settings loaded successfully")
        else:
            self.status_bar.config(
                text="settings not found - create it to configure your test"
            )
    except Exception as e:
        log_message(self, f"Error loading settings: {str(e)}", "error")

def save_settings(self):
    try:
        cb = self.core_blacklist_var.get()
        if cb and not re.fullmatch(r"\d+(,\d+)*", cb):
            self.status_bar.config(text="Invalid core_blacklist format")
            log_message(self, "Invalid core_blacklist format (use e.g. 1,4,7)", "error")
            return
        out = [
            "#!/bin/bash",
            f"loops={self.loops_var.get()}",
            f"browsers={self.browsers_var.get()}",
            f"light_time={self.light_time_var.get()}",
            f"medium_time={self.medium_time_var.get()}",
            f"heavy_time={self.heavy_time_var.get()}",
            f"all_core_time={self.all_core_time_var.get()}",
            f"all_core_tests={self.all_core_tests_var.get()}",
            f"rapid_tests={self.rapid_tests_var.get()}",
            f"rapid_time={self.rapid_time_var.get()}",
            f"random_tests={self.random_tests_var.get()}",
            f"random_time={self.random_time_var.get()}",
            f"rest_time={self.rest_time_var.get()}",
            f'core_blacklist="{cb}"',
            f"max_ram={self.max_ram_var.get()}",
        ]
        preserved_content = ""
        if os.path.exists("./config/user.settings"):
            with open("./config/user.settings", "r") as f:
                lines = f.readlines()
                found_marker = False
                for i, line in enumerate(lines):
                    if line.strip() == "# DO NOT EDIT":
                        preserved_content = "".join(lines[i:])
                        found_marker = True
                        break
        with open("./config/user.settings", "w") as f:
            f.write("\n".join(out) + "\n")
            if preserved_content:
                if not preserved_content.startswith("\n"):
                    f.write("\n")
                f.write(preserved_content)
        self.settings_dirty = False
        self.unsaved_label.config(text="")
        log_message(self, "Settings saved", "success")
    except Exception as e:
        log_message(self, f"Error saving settings: {str(e)}", "error")

def register_settings_traces(self):
    self.settings_dirty = False
    def on_setting_changed(*args):
        if not self.settings_dirty:
            self.settings_dirty = True
            self.unsaved_label.config(text="⚠ Unsaved changes")
    for var in [
        self.loops_var,
        self.browsers_var,
        self.light_time_var,
        self.medium_time_var,
        self.heavy_time_var,
        self.all_core_time_var,
        self.all_core_tests_var,
        self.rapid_tests_var,
        self.rapid_time_var,
        self.random_tests_var,
        self.random_time_var,
        self.rest_time_var,
        self.max_ram_var,
        self.core_blacklist_var,
        self.all_cores_enabled_var,
        self.low_load_enabled_var,
        self.single_core_enabled_var,
        self.webgl_enabled_var,
    ]:
        var.trace_add("write", on_setting_changed)

def toggle_group_enabled(self, group_name, enabled):
    if enabled:
        restore_group_defaults(self, group_name)
    else:
        set_group_values(self, group_name, 0)
    if group_name == "single_core":
        self.webgl_enabled_var.set(enabled)
        if enabled:
            restore_group_defaults(self, "webgl")
        else:
            set_group_values(self, "webgl", 0)

def load_default_settings():
    defaults = {}
    if os.path.exists("./config/default.settings"):
        with open("./config/default.settings", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                defaults[key.strip()] = value.strip().strip('"')
    return defaults

def set_group_values(self, group_name, value):
    for var in self.group_vars[group_name]:
        var.set(value)

def restore_group_defaults(self, group_name):
    defaults = load_default_settings()
    key_map = {
        "all_cores": ["all_core_time", "all_core_tests"],
        "low_load": ["rapid_tests", "rapid_time", "random_tests", "random_time"],
        "single_core": ["light_time", "medium_time", "heavy_time"],
        "webgl": ["browsers"],
    }
    for var, key in zip(self.group_vars[group_name], key_map[group_name]):
        if key in defaults:
            var.set(int(defaults[key]))
