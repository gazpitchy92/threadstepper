#!/bin/bash

mode=$1
cpu=$(echo "$cpu" | tr -d ' ') 
duration=$3
error_count=0
iteration=0

# Validate test result
cpu_validate() {
    local n=10000
    local expected=$(( n * (n + 1) / 2 ))
    local actual=0
    for ((i = 0; i <= n; i++)); do
        (( actual += i ))
    done
    if (( actual != expected )); then
        logger -p err "Thread Stepper: CPU $cpu arithmetic mismatch on iteration $iteration: expected $expected, got $actual"
        echo "[ERROR] cpu $cpu arithmetic mismatch on iteration $iteration: expected $expected, got $actual"
        (( error_count++ ))
    fi
}

# Stress algo
busy_work() {
    local size=5000
    local arr=()
    local x=0
    for ((i = 0; i < size; i++)); do
        arr[$i]=$(( (i * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFF ))
        (( x ^= arr[$i] ))
    done
}

# Run test iteration
run_iteration() {
    (( iteration++ ))
    busy_work
    cpu_validate
}

# Main
end=$(( $(date +%s) + duration ))
case $mode in
    low)
        while (( $(date +%s) < end )); do
            busy_until=$(( $(date +%s%3N) + 200 ))
            while (( $(date +%s%3N) < busy_until && $(date +%s) < end )); do
                run_iteration
            done
            sleep 0.80
        done
        ;;
    medium)
        while (( $(date +%s) < end )); do
            busy_until=$(( $(date +%s%3N) + 550 ))
            while (( $(date +%s%3N) < busy_until && $(date +%s) < end )); do
                run_iteration
            done
            sleep 0.45
        done
        ;;
    high)
        while (( $(date +%s) < end )); do
            run_iteration
        done
        ;;
esac
if (( error_count != 0 )); then
    logger -p err "Thread Stepper: [cpu $cpu] Iterations: $iteration | Errors: $error_count | FAIL"
fi