#!/usr/bin/env bash

# Get SMT threads for core
get_threads() {
    local cpu=$1
    local file="/sys/devices/system/cpu/cpu${cpu}/topology/thread_siblings_list"

    if [ ! -f "$file" ]; then
        echo "$cpu"
        return
    fi

    cat "$file" | tr ',' ' ' | tr -d '\n'
}

# Normalize CPU list
normalize_core_group() {
    echo "$@" | tr ' ' '\n' | sort -n | uniq | tr '\n' ' ' | xargs
}

# Convert CPU list for taskset
to_taskset() {
    echo "$1" | tr ' ' ','
}

# Find best core
find_best_core() {
    local best=-1 max=-1
    for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
        local perf_file="$cpu/acpi_cppc/highest_perf"

        if [ -f "$perf_file" ]; then
            local val=$(cat "$perf_file")
            local num=${cpu##*/cpu}

            if [ "$val" -gt "$max" ]; then
                max=$val
                best=$num
            fi
        fi
    done

    echo ${best:-0}
}

# Select core
select_core() {
    if [ -n "$SELECTED_CORE" ] && [ "$SELECTED_CORE" != "Auto" ]; then
        BASE_CORE="$SELECTED_CORE"

        if [ ! -f "/sys/devices/system/cpu/cpu$BASE_CORE/acpi_cppc/highest_perf" ]; then
            BASE_CORE=$(find_best_core)
        fi
    else
        BASE_CORE=$(find_best_core)
    fi
}

# Resolve SMT group
resolve_threads() {
    THREADS=$(get_threads "$BASE_CORE")
    CORE_GROUP=$(normalize_core_group $THREADS)
    CPUS=$(to_taskset "$CORE_GROUP")
    CORE_COUNT=$(echo $CORE_GROUP | wc -w)
}

# Sample cpu clock
get_clock_mhz() {
    local max=0
    for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
        local v=$(<"$f")
        (( v > max )) && max=$v
    done
    echo "$max"
}

# Sample cpu temp
get_cpu_temp() {
    local hwmon
    hwmon=$(grep -rl "k10temp" /sys/class/hwmon/hwmon*/name 2>/dev/null | head -n1 | xargs dirname)
    local raw=$(<"${hwmon}/temp1_input")
    echo "$raw"
}