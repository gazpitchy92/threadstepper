#!/usr/bin/env bash

# Accept an optional core selection argument
SELECTED_CORE="$1"
DURATION=5
RUNS=3
NCPU=$(nproc)
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_LOG="$(dirname "$CURRENT_DIR")/logs/benchmark.log"
if [ ! -f "$OUTPUT_LOG" ]; then
    > "$OUTPUT_LOG"
fi

bench() {
    local cores=$1
    local duration=$2
    local temp_dir=$(mktemp -d)

    for ((c=0; c<cores; c++)); do
        (
            local end=$((SECONDS + duration))
            local ops=0
            local x=123456789
            while [ $SECONDS -lt $end ]; do
                for ((i=0; i<100000; i++)); do
                    x=$(( (x * 1103515245 + 12345) & 0x7fffffff ))
                    ((ops++))
                done
            done
            echo $ops > "$temp_dir/threadsetepper_result_$c"
        ) &
    done
    wait
    local total=0
    for f in "$temp_dir"/threadsetepper_result_*; do
        total=$((total + $(cat "$f")))
    done
    rm -rf "$temp_dir"
    echo $total
}

export -f bench

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

median() {
    local arr=($(printf '%s\n' "$@" | sort -n))
    local len=${#arr[@]}
    if [ $((len % 2)) -eq 1 ]; then
        echo ${arr[$((len/2))]}
    else
        echo $(( (arr[$((len/2 - 1))] + arr[$((len/2))]) / 2 ))
    fi
}

# Determine which core to use
if [ -n "$SELECTED_CORE" ] && [ "$SELECTED_CORE" != "Auto" ]; then
    # User selected core
    if [ -f "/sys/devices/system/cpu/cpu$SELECTED_CORE/acpi_cppc/highest_perf" ]; then
        BEST="$SELECTED_CORE"
        CPPC_VAL=$(cat "/sys/devices/system/cpu/cpu$BEST/acpi_cppc/highest_perf" 2>/dev/null || echo "N/A")
        echo "$(tput setaf 8)[DEBUG] Using user-selected core: ${BEST} (CPPC: ${CPPC_VAL})$(tput sgr0)"
    else
        echo "$(tput setaf 3)[WARNING] Selected core $SELECTED_CORE not found, falling back to auto-selection$(tput sgr0)" >&2
        BEST=$(find_best_core)
        CPPC_VAL=$(cat "/sys/devices/system/cpu/cpu$BEST/acpi_cppc/highest_perf" 2>/dev/null || echo "N/A")
        echo "$(tput setaf 8)[DEBUG] Auto-selected core: ${BEST} (CPPC: ${CPPC_VAL})$(tput sgr0)"
    fi
else
    # Auto cppc best core
    BEST=$(find_best_core)
    CPPC_VAL=$(cat "/sys/devices/system/cpu/cpu$BEST/acpi_cppc/highest_perf" 2>/dev/null || echo "N/A")
    echo "$(tput setaf 8)[DEBUG] Auto mode - best core: ${BEST} (CPPC: ${CPPC_VAL})$(tput sgr0)"
fi

single_vals=()
for ((r=0; r<RUNS; r++)); do
    single_vals+=($(taskset -c "$BEST" bash -c "bench 1 $DURATION"))
done

multi_vals=()
for ((r=0; r<RUNS; r++)); do
    multi_vals+=($(bench $NCPU $DURATION))
done

single=$(median "${single_vals[@]}")
multi=$(median "${multi_vals[@]}")
timestamp=$(date +"%d %b %H:%M")

echo "$(tput setaf 4)Single Core: $((single / DURATION / 1000))$(tput sgr0)"
echo "$(tput setaf 4)Multi Core: $((multi / DURATION / 1000))$(tput sgr0)"

echo "${BEST},$((single / DURATION / 1000)),$((multi / DURATION / 1000)),${timestamp}" >> "$OUTPUT_LOG"
tail -n 5 "$OUTPUT_LOG" > "${OUTPUT_LOG}.tmp" && mv "${OUTPUT_LOG}.tmp" "$OUTPUT_LOG"