#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKER="$(dirname "$CURRENT_DIR")/functions/stressors/load_worker.sh"
chmod +x "$WORKER"
PHASE_PIDS=()

run_phase() {
    local cores=$1
    local mode=$2

    IFS=',' read -ra core_list <<< "$cores"
    for cpu in "${core_list[@]}"; do
        taskset -c "$cpu" bash "$WORKER" "$mode" "$cpu" 99999 &
        PHASE_PIDS+=($!)
    done
}

kill_phase() {
    if (( ${#PHASE_PIDS[@]} == 0 )); then
        return
    fi
    for pid in "${PHASE_PIDS[@]}"; do
        kill "$pid" 2>/dev/null
    done
    wait "${PHASE_PIDS[@]}" 2>/dev/null
    PHASE_PIDS=()
}

wait_phase() {
    if (( ${#PHASE_PIDS[@]} == 0 )); then
        return
    fi
    wait "${PHASE_PIDS[@]}" 2>/dev/null
    PHASE_PIDS=()
}