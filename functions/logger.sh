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
    LOG_PRIORITY="err"
    EXCLUDE=("libinput" "bluetooth" "cityfailed" "plasmashell" "mouse" "keyboard" "chrome" "firefox" "librewold" "floorp" "discord" "brave" "electron" "udev")
    ERRORS_HARDWARE=$(journalctl --since="@${start_time}" -p "$LOG_PRIORITY" -k --no-pager -q 2>/dev/null | grep -E 'MCE|Machine Check|Hardware Error|EDAC|ECC|NVRM|Xid|amdgpu|i915|GPU fault|GPU HANG')
    ERRORS_FLAG=$(journalctl --since="@${start_time}" -p "$LOG_PRIORITY" --no-pager -q 2>/dev/null)
    ERRORS_DUMPED=$(journalctl --since="@${start_time}" --no-pager | grep -i "dumped core")
    ERRORS_SEGFAULT=$(journalctl --since="@${start_time}" --no-pager | grep -i "segfault")
    COREDUMPS=$(coredumpctl --since "@${start_time}" list --no-pager 2>/dev/null | awk 'gsub(/ /,"")>=5')
    [ -z "$COREDUMPS" ] && COREDUMPS=""
    # Check for excluded
    for word in "${EXCLUDE[@]}"; do
        ERRORS_HARDWARE=$(echo "$ERRORS_HARDWARE" | grep -vi "$word")
        ERRORS_FLAG=$(echo "$ERRORS_FLAG" | grep -vi "$word")
        ERRORS_DUMPED=$(echo "$ERRORS_DUMPED" | grep -vi "$word")
        ERRORS_SEGFAULT=$(echo "$ERRORS_SEGFAULT" | grep -vi "$word")
        COREDUMPS=$(echo "$COREDUMPS" | grep -vi "$word")
    done
    # Format error
    ERRORS_HARDWARE=$(echo "$ERRORS_HARDWARE" | awk 'gsub(/ /,"")>=5')
    ERRORS_FLAG=$(echo "$ERRORS_FLAG" | awk 'gsub(/ /,"")>=5')
    ERRORS_DUMPED=$(echo "$ERRORS_DUMPED" | awk 'gsub(/ /,"")>=5')
    ERRORS_SEGFAULT=$(echo "$ERRORS_SEGFAULT" | awk 'gsub(/ /,"")>=5')
    # Save error to file
    if [ -n "$ERRORS_DUMPED" ] || [ -n "$ERRORS_SEGFAULT" ] || [ -n "$COREDUMPS" ] || [ -n "$ERRORS_FLAG" ] || [ -n "$ERRORS_HARDWARE" ]; then
        {
            echo "true"
            echo "=== Errors detected at $(date -Iseconds) ==="
            [ -n "$ERRORS_HARDWARE" ] && echo "$ERRORS_HARDWARE"
            [ -n "$ERRORS_FLAG" ] && echo "$ERRORS_FLAG"
            [ -n "$ERRORS_DUMPED" ] && echo "$ERRORS_DUMPED"
            [ -n "$ERRORS_SEGFAULT" ] && echo "$ERRORS_SEGFAULT"
            [ -n "$COREDUMPS" ] && echo "=== Coredumps ===" && echo "$COREDUMPS"
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