#!/bin/bash

# Init vars
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
worker="$(dirname "$current_dir")/functions/stressors/load_worker.sh"
chmod +x "$worker"
phase_pids=()

# Start a stressor in bg
run_phase() {
    local cores=$1
    local mode=$2
    ifs=',' read -ra core_list <<< "$cores"
    for cpu in "${core_list[@]}"; do
        taskset -c "$cpu" bash "$worker" "$mode" "$cpu" 99999 &
        phase_pids+=($!)
    done
}

# Kill bg stressor
kill_phase() {
    if (( ${#phase_pids[@]} == 0 )); then
        return
    fi
    for pid in "${phase_pids[@]}"; do
        kill "$pid" 2>/dev/null
    done
    wait "${phase_pids[@]}" 2>/dev/null
    phase_pids=()
}

# Idle workers
wait_phase() {
    if (( ${#phase_pids[@]} == 0 )); then
        return
    fi
    wait "${phase_pids[@]}" 2>/dev/null
    phase_pids=()
}