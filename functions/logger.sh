#!/bin/bash

# Init vars
current_dir=$(pwd)
error_log="$current_dir/logs/errors.log"
clock_log="$current_dir/logs/clock.log"
temperature_log="$current_dir/logs/temperature.log"
start_time=$(date +%s)

# Check files
mkdir -p "$current_dir/logs"
echo "0.0" > "$clock_log"
echo "0.0" > "$temperature_log"
echo "false" > "$error_log"

# Log peak cpu
log_cpu_clock() {
    max=0
    for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
        v=$(<"$f")
        (( v > max )) && max=$v
    done
    ghz=$(awk "BEGIN { printf \"%.3f\", $max / 1000000 }")
    last=$(<"$clock_log")
    awk -v cur="$ghz" -v last="$last" 'BEGIN { exit !(cur > last) }' && {
        printf "%s\n" "$ghz" > "$clock_log"
    }
}

# Log peak
log_cpu_temperature() {
    hwmon=$(grep -rl "k10temp" /sys/class/hwmon/hwmon*/name 2>/dev/null | head -n1 | xargs dirname)
    raw=$(<"${hwmon}/temp1_input")
    temperature=$(awk "BEGIN {printf \"%.1f\", $raw / 1000}")
    if [[ -f "$temperature_log" ]]; then
        stored=$(<"$temperature_log")
        if awk "BEGIN {exit !($temperature > $stored)}"; then
            echo "$temperature" > "$temperature_log"
        fi
    else
        echo "$temperature" > "$temperature_log"
    fi
}

check_for_errors() {
    # Fetch errors
    log_priority="err"
    exclude=("libinput" "bluetooth" "cityfailed" "plasmashell" "mouse" "keyboard" "chrome" "firefox" "librewold" "floorp" "discord" "brave" "electron" "udev")
    errors_hardware=$(journalctl --since="@${start_time}" -p "$log_priority" -k --no-pager -q 2>/dev/null | grep -E 'MCE|Machine Check|Hardware Error|EDAC|ECC|NVRM|Xid|amdgpu|i915|GPU fault|GPU HANG')
    errors_flag=$(journalctl --since="@${start_time}" -p "$log_priority" --no-pager -q 2>/dev/null)
    errors_dumped=$(journalctl --since="@${start_time}" --no-pager | grep -i "dumped core")
    errors_segfault=$(journalctl --since="@${start_time}" --no-pager | grep -i "segfault")
    coredumps=$(coredumpctl --since "@${start_time}" list --no-pager 2>/dev/null | awk 'gsub(/ /,"")>=5')
    [ -z "$coredumps" ] && coredumps=""
    # Check for excluded
    for word in "${exclude[@]}"; do
        errors_hardware=$(echo "$errors_hardware" | grep -vi "$word")
        errors_flag=$(echo "$errors_flag" | grep -vi "$word")
        errors_dumped=$(echo "$errors_dumped" | grep -vi "$word")
        errors_segfault=$(echo "$errors_segfault" | grep -vi "$word")
        coredumps=$(echo "$coredumps" | grep -vi "$word")
    done
    # Format error
    errors_hardware=$(echo "$errors_hardware" | awk 'gsub(/ /,"")>=5')
    errors_flag=$(echo "$errors_flag" | awk 'gsub(/ /,"")>=5')
    errors_dumped=$(echo "$errors_dumped" | awk 'gsub(/ /,"")>=5')
    errors_segfault=$(echo "$errors_segfault" | awk 'gsub(/ /,"")>=5')
    # Save error to file
    if [ -n "$errors_dumped" ] || [ -n "$errors_segfault" ] || [ -n "$coredumps" ] || [ -n "$errors_flag" ] || [ -n "$errors_hardware" ]; then
        {
            echo "true"
            echo "=== Errors detected at $(date -Iseconds) ==="
            [ -n "$errors_hardware" ] && echo "$errors_hardware"
            [ -n "$errors_flag" ] && echo "$errors_flag"
            [ -n "$errors_dumped" ] && echo "$errors_dumped"
            [ -n "$errors_segfault" ] && echo "$errors_segfault"
            [ -n "$coredumps" ] && echo "=== Coredumps ===" && echo "$coredumps"
            echo "========================================"
        } > "$error_log"
        exit 1
    fi
}

# Main loop
while :; do
    log_cpu_clock
    log_cpu_temperature
    check_for_errors
    sleep 2
done