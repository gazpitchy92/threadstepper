#!/bin/bash

MODE=$1
CPU=$(echo "$cpu" | tr -d ' ') DURATION=$3
ERROR_COUNT=0
ITERATION=0

cpu_validate() {
    local n=10000
    local expected=$(( n * (n + 1) / 2 ))
    local actual=0
    for ((i = 0; i <= n; i++)); do
        (( actual += i ))
    done
    if (( actual != expected )); then
        logger -p err "Thread Stepper: CPU $CPU arithmetic mismatch on iteration $ITERATION: expected $expected, got $actual"
        echo "[ERROR] CPU $CPU arithmetic mismatch on iteration $ITERATION: expected $expected, got $actual"
        (( ERROR_COUNT++ ))
    fi
}

busy_work() {
    local size=5000
    local arr=()
    local x=0
    for ((i = 0; i < size; i++)); do
        arr[$i]=$(( (i * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFF ))
        (( x ^= arr[$i] ))
    done
}

run_iteration() {
    (( ITERATION++ ))
    busy_work
    cpu_validate
}

end=$(( $(date +%s) + DURATION ))

case $MODE in
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

if (( ERROR_COUNT != 0 )); then
    logger -p err "Thread Stepper: [CPU $CPU] Iterations: $ITERATION | Errors: $ERROR_COUNT | FAIL"
fi